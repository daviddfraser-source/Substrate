#!/usr/bin/env python3
"""WBS Web Dashboard — JSON-based with editing support."""

import json
import logging
import mimetypes
import os
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from wbs_common import GOV, WBS_DEF, load_definition, load_state, get_counts
from governed_platform.governance.file_lock import atomic_write_json
from governed_platform.governance.status import normalize_runtime_status

STATIC = GOV / "static"
CLI = GOV / "wbs_cli.py"

DOC_INCLUDED_TOP_LEVEL = {"docs", "prompts", "templates", "examples", ".governance", "skills"}
DOC_SKIP_PARTS = {"__pycache__", ".git", "dist", "node_modules", ".venv", "venv"}
DOC_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".adoc", ".json", ".yml", ".yaml", ".csv", ".log"}
DOC_MARKDOWN_EXTENSIONS = {".md", ".markdown"}
DOC_ROOT_HINT_FILES = {
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "constitution.md",
}

SESSION_COOKIE = "wbs_session"
SESSION_MAX_AGE_SECONDS = int(os.environ.get("WBS_SESSION_MAX_AGE", "28800"))
DEVELOPER_USERS = {
    u.strip().lower()
    for u in os.environ.get("WBS_DEVELOPER_USERS", "developer,developer@example.com").split(",")
    if u.strip()
}
SESSIONS: Dict[str, Dict] = {}


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("wbs_server")
    if logger.handlers:
        return logger
    level_name = str(os.environ.get("WBS_LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    fmt = os.environ.get("WBS_LOG_FORMAT", "text").lower()
    if fmt == "json":
        handler.setFormatter(logging.Formatter('{"level":"%(levelname)s","msg":"%(message)s"}'))
    else:
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


LOGGER = _build_logger()


def save_definition(defn: dict):
    """Save WBS definition with cross-platform lock + atomic replace."""
    atomic_write_json(WBS_DEF, defn)


class Handler(BaseHTTPRequestHandler):
    def _write_json(self, data: Dict, status: int = 200, headers: Optional[Dict[str, str]] = None) -> None:
        """Send a JSON HTTP response with consistent headers and status code."""
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _cookie_value(self, name: str) -> str:
        raw = self.headers.get("Cookie", "")
        if not raw:
            return ""
        cookie = SimpleCookie()
        try:
            cookie.load(raw)
        except Exception:
            return ""
        morsel = cookie.get(name)
        return morsel.value if morsel else ""

    def _session_for_request(self) -> Dict:
        token = self._cookie_value(SESSION_COOKIE)
        if not token:
            return {}
        sess = SESSIONS.get(token) or {}
        expires_at = float(sess.get("expires_at") or 0)
        if not sess or expires_at <= time.time():
            if token in SESSIONS:
                del SESSIONS[token]
            return {}
        return sess

    def _deny_auth(self, status: int = 401, message: str = "Authentication required") -> None:
        self._write_json({"success": False, "message": message}, status=status)

    def _is_developer(self, session: Dict) -> bool:
        return str(session.get("role", "")).lower() == "developer"

    def _require_developer(self) -> bool:
        session = self._session_for_request()
        if not session:
            self._deny_auth(401, "Authentication required")
            return False
        if not self._is_developer(session):
            self._deny_auth(403, "Developer role required")
            return False
        return True

    def _session_user(self, session: Dict) -> Dict:
        return {
            "name": session.get("name", ""),
            "email": session.get("email", ""),
            "role": session.get("role", "Viewer"),
            "logged_in_at": session.get("logged_in_at", ""),
        }

    def api_auth_session(self) -> Dict:
        session = self._session_for_request()
        if not session:
            return {"success": True, "authenticated": False}
        return {"success": True, "authenticated": True, "user": self._session_user(session)}

    def api_auth_login(self, body: Dict):
        name = str(body.get("name", "")).strip()
        email = str(body.get("email", "")).strip()
        if not name or not email:
            return {"success": False, "message": "name and email are required"}, 400, None

        role = "Developer" if (name.lower() in DEVELOPER_USERS or email.lower() in DEVELOPER_USERS) else "Viewer"
        token = secrets.token_urlsafe(32)
        now = time.time()
        SESSIONS[token] = {
            "name": name,
            "email": email,
            "role": role,
            "logged_in_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": now + SESSION_MAX_AGE_SECONDS,
        }
        cookie = f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_MAX_AGE_SECONDS}"
        return (
            {"success": True, "authenticated": True, "user": self._session_user(SESSIONS[token])},
            200,
            {"Set-Cookie": cookie},
        )

    def api_auth_logout(self):
        token = self._cookie_value(SESSION_COOKIE)
        if token and token in SESSIONS:
            del SESSIONS[token]
        expired = f"{SESSION_COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
        return {"success": True, "authenticated": False}, 200, {"Set-Cookie": expired}

    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)

        if path in ("/", "/index.html"):
            return self.serve_file("index.html")

        routes = {
            "/api/auth/session": self.api_auth_session,
            "/api/status": self.api_status,
            "/api/ready": self.api_ready,
            "/api/progress": self.api_progress,
            "/api/log": lambda: self.api_log(int(query.get("limit", [20])[0])),
            "/api/packet": lambda: self.api_packet(query.get("id", [""])[0]),
            "/api/file": lambda: self.api_file(query.get("path", [""])[0]),
            "/api/docs-index": lambda: self.api_docs_index(query),
            "/api/deps-graph": self.api_deps_graph,
        }
        if path in routes:
            if path.startswith("/api/") and path != "/api/auth/session" and not self._require_developer():
                return
            return self._write_json(routes[path](), status=200)

        if path.startswith("/api/"):
            return self._write_json(
                {"success": False, "message": f"Route not found: {path}"},
                status=404,
            )

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        LOGGER.debug("POST %s", path)

        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode() if length > 0 else "{}"
            LOGGER.debug("Body: %s", raw[:200])
            body = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as e:
            LOGGER.warning("Invalid JSON body: %s", e)
            return self._write_json({"success": False, "message": "Invalid JSON body"}, status=400)

        routes = {
            "/api/auth/login": lambda: self.api_auth_login(body),
            "/api/auth/logout": self.api_auth_logout,
            "/api/claim": lambda: self.run_cmd("claim", body),
            "/api/done": lambda: self.run_cmd("done", body),
            "/api/note": lambda: self.run_cmd("note", body),
            "/api/fail": lambda: self.run_cmd("fail", body),
            "/api/reset": lambda: self.run_cmd("reset", body),
            "/api/closeout-l2": lambda: self.api_closeout_l2(body),
            "/api/add-packet": lambda: self.api_add_packet(body),
            "/api/add-area": lambda: self.api_add_area(body),
            "/api/add-dep": lambda: self.api_add_dep(body),
            "/api/remove-dep": lambda: self.api_remove_dep(body),
            "/api/edit-packet": lambda: self.api_edit_packet(body),
            "/api/edit-area": lambda: self.api_edit_area(body),
            "/api/remove-packet": lambda: self.api_remove_packet(body),
            "/api/save-wbs": lambda: self.api_save_wbs(body),
        }

        if path in routes:
            try:
                if path.startswith("/api/") and path not in {"/api/auth/login", "/api/auth/logout"} and not self._require_developer():
                    return
                result = routes[path]()
                status = 200
                headers = None
                if isinstance(result, tuple):
                    payload = result[0]
                    status = result[1] if len(result) > 1 else 200
                    headers = result[2] if len(result) > 2 else None
                else:
                    payload = result
                LOGGER.debug("Result: %s", result)
                return self._write_json(payload, status=status, headers=headers)
            except Exception as e:
                LOGGER.exception("Route handler failed: %s", e)
                return self._write_json({"success": False, "message": str(e)}, status=500)

        LOGGER.warning("Route not found: %s", path)
        if path.startswith("/api/"):
            return self._write_json(
                {"success": False, "message": f"Route not found: {path}"},
                status=404,
            )
        self.send_response(404)
        self.end_headers()

    def serve_file(self, name):
        fp = STATIC / name
        if not fp.exists():
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(fp.read_bytes())

    def api_status(self) -> Dict:
        """Return definition/state snapshot used by the dashboard grid."""
        defn = load_definition()
        state = load_state()
        area_closeouts = state.get("area_closeouts", {})
        areas = []
        for area in defn.get("work_areas", []):
            pkts = []
            for p in defn.get("packets", []):
                if p.get("area_id") == area["id"]:
                    ps = state["packets"].get(p["id"], {})
                    pkts.append({
                        "id": p["id"], "wbs_ref": p["wbs_ref"], "title": p["title"],
                        "scope": p.get("scope", ""),
                        "status": normalize_runtime_status(ps.get("status", "pending")),
                        "assigned_to": ps.get("assigned_to"),
                        "notes": ps.get("notes")
                    })
            areas.append({
                "id": area["id"],
                "title": area["title"],
                "description": area.get("description", ""),
                "packets": pkts,
                "closeout": area_closeouts.get(area["id"]),
            })

        return {
            "metadata": defn.get("metadata", {}),
            "areas": areas,
            "area_closeouts": area_closeouts,
            "dependencies": defn.get("dependencies", {}),
            "counts": get_counts(state),
            "timestamp": datetime.now().isoformat()
        }

    def api_closeout_l2(self, body):
        area_id = body.get("area_id", "").strip()
        agent = body.get("agent_name", "").strip()
        assessment_path = body.get("assessment_path", "").strip()
        notes = body.get("notes", "").strip()

        if not area_id or not agent or not assessment_path:
            return {"success": False, "message": "Missing area_id, agent_name, or assessment_path"}

        args = [
            "python3",
            str(CLI),
            "closeout-l2",
            area_id,
            agent,
            assessment_path,
        ]
        if notes:
            args.append(notes)

        r = subprocess.run(args, capture_output=True, text=True)
        return {"success": r.returncode == 0, "message": (r.stdout + r.stderr).strip()}

    def api_ready(self) -> Dict:
        """Return packets that are pending and dependency-ready."""
        defn = load_definition()
        state = load_state()
        deps = defn.get("dependencies", {})
        ready = []
        for p in defn.get("packets", []):
            pid = p["id"]
            if normalize_runtime_status(state["packets"].get(pid, {}).get("status", "pending")) == "pending":
                ok = all(
                    normalize_runtime_status(state["packets"].get(d, {}).get("status")) == "done"
                    for d in deps.get(pid, [])
                )
                if ok:
                    ready.append({"id": pid, "wbs_ref": p["wbs_ref"], "title": p["title"]})
        return {"ready": ready}

    def api_progress(self) -> Dict:
        """Return aggregate packet status counts."""
        state = load_state()
        counts = get_counts(state)
        return {"counts": counts, "total": sum(counts.values())}

    def api_deps_graph(self) -> Dict:
        """Return dependency graph nodes and edges for dashboard visualization."""
        defn = load_definition()
        state = load_state()
        packets = defn.get("packets", [])
        deps = defn.get("dependencies", {})

        nodes = []
        for packet in packets:
            pid = packet["id"]
            pstate = state.get("packets", {}).get(pid, {})
            nodes.append(
                {
                    "id": pid,
                    "title": packet.get("title", ""),
                    "wbs_ref": packet.get("wbs_ref", ""),
                    "status": normalize_runtime_status(pstate.get("status", "pending")),
                }
            )

        edges = []
        for target, sources in deps.items():
            for source in sources:
                edges.append({"from": source, "to": target})

        return {"nodes": nodes, "edges": edges}

    def api_log(self, limit: int = 20) -> Dict:
        """Return the most recent lifecycle log entries."""
        state = load_state()
        entries = state.get("log", [])[-limit:]
        return {"log": entries}

    def _scan_document_files(self, repo_root: Path) -> List[Path]:
        """Discover documentation-related files from curated top-level locations."""
        out = []
        for root, dirs, files in os.walk(repo_root):
            root_path = Path(root)
            rel_root = root_path.relative_to(repo_root)
            rel_parts = rel_root.parts
            top = rel_parts[0] if rel_parts else ""

            # Prune ignored directories at every level.
            dirs[:] = [d for d in dirs if d not in DOC_SKIP_PARTS]

            # Keep traversal limited to curated top-level documentation areas.
            if rel_parts and top not in DOC_INCLUDED_TOP_LEVEL:
                dirs[:] = []
                continue

            for fname in files:
                fpath = root_path / fname
                rel_file = fpath.relative_to(repo_root)
                rel_file_parts = rel_file.parts
                ext = fpath.suffix.lower()

                if any(part in DOC_SKIP_PARTS for part in rel_file_parts):
                    continue

                if not rel_parts:
                    if fname in DOC_ROOT_HINT_FILES or ext in DOC_EXTENSIONS:
                        out.append(fpath)
                    continue

                if ext in DOC_EXTENSIONS:
                    out.append(fpath)
        return out

    def _doc_kind(self, ext: str) -> str:
        ext = (ext or "").lower()
        if ext in DOC_MARKDOWN_EXTENSIONS:
            return "markdown"
        if ext == ".json":
            return "json"
        if ext in {".yml", ".yaml"}:
            return "yaml"
        if ext == ".csv":
            return "csv"
        if ext == ".log":
            return "log"
        return "text"

    def _doc_title_and_summary(self, path: Path, ext: str) -> Dict:
        title = path.stem.replace("-", " ").replace("_", " ").strip().title() or path.name
        summary = ""
        try:
            text = path.read_text(errors="replace")[:12_000]
        except Exception:
            return {"title": title, "summary": summary}

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            return {"title": title, "summary": summary}

        if ext in DOC_MARKDOWN_EXTENSIONS:
            heading = next((ln for ln in lines if ln.startswith("#")), "")
            if heading:
                title = heading.lstrip("#").strip() or title
            body = next((ln for ln in lines if not ln.startswith("#")), "")
            if body:
                summary = body[:180]
        else:
            summary = lines[0][:180]
        return {"title": title, "summary": summary}

    def api_docs_index(self, query: Dict[str, List[str]]) -> Dict:
        """Return project documentation index metadata for documentation explorer UI."""
        repo_root = GOV.parent.resolve()

        q = (query.get("q", [""])[0] or "").strip().lower()
        kind_filter = (query.get("kind", [""])[0] or "").strip().lower()
        category_filter = (query.get("category", [""])[0] or "").strip()
        try:
            limit = int((query.get("limit", ["800"])[0] or "800").strip())
        except ValueError:
            limit = 800
        limit = max(1, min(limit, 5000))

        docs = []
        for file_path in self._scan_document_files(repo_root):
            rel = file_path.relative_to(repo_root).as_posix()
            ext = file_path.suffix.lower()
            kind = self._doc_kind(ext)
            category = rel.split("/", 1)[0] if "/" in rel else "root"

            if kind_filter and kind != kind_filter:
                continue
            if category_filter and category != category_filter:
                continue

            title_meta = self._doc_title_and_summary(file_path, ext)
            stat = file_path.stat()
            item = {
                "path": rel,
                "name": file_path.name,
                "title": title_meta["title"],
                "summary": title_meta["summary"],
                "category": category,
                "kind": kind,
                "ext": ext or "",
                "size": stat.st_size,
                "updated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
            haystack = " ".join(
                [item["path"], item["name"], item["title"], item["summary"], item["category"], item["kind"]]
            ).lower()
            if q and q not in haystack:
                continue
            docs.append(item)

        docs.sort(key=lambda d: (d["category"].lower(), d["path"].lower()))
        total = len(docs)
        categories = sorted({d["category"] for d in docs})
        limited_docs = docs[:limit]
        kinds = sorted({d["kind"] for d in docs})

        return {
            "success": True,
            "query": {
                "q": q,
                "kind": kind_filter,
                "category": category_filter,
                "limit": limit,
            },
            "total": total,
            "returned": len(limited_docs),
            "categories": categories,
            "kinds": kinds,
            "documents": limited_docs,
        }

    def _extract_doc_paths(self, *texts: str) -> List[Dict]:
        """Extract repository-relative file paths from free-form packet text fields."""
        repo_root = GOV.parent.resolve()
        candidates = set()
        token_re = re.compile(r"[A-Za-z0-9_./-]+")
        spaced_path_re = re.compile(
            r"([A-Za-z0-9_./-]+(?: [A-Za-z0-9_./-]+)+\.(?:md|txt|json|py|sh|yml|yaml|html|js|ts|tsx|csv|log))",
            re.IGNORECASE,
        )
        allowed_ext = {
            ".md", ".txt", ".json", ".py", ".sh", ".yml", ".yaml",
            ".html", ".js", ".ts", ".tsx", ".csv", ".log"
        }

        for text in texts:
            if not text:
                continue
            for match in spaced_path_re.findall(text):
                token = match.strip(".,;:()[]{}<>\"'`")
                if token:
                    candidates.add(token)
            for token in token_re.findall(text):
                token = token.strip(".,;:()[]{}<>\"'`")
                if token.startswith("http://") or token.startswith("https://"):
                    continue
                if token.startswith("."):
                    token = token.lstrip("./")
                if not token:
                    continue
                has_path_sep = "/" in token
                ext = Path(token).suffix.lower()
                if not has_path_sep and ext not in allowed_ext:
                    continue
                candidates.add(token)

        docs = []
        for rel in sorted(candidates):
            path = (repo_root / rel).resolve()
            exists = str(path).startswith(str(repo_root)) and path.is_file()
            docs.append({
                "path": rel,
                "exists": bool(exists)
            })
        return docs

    def _collect_text_values(self, value) -> List[str]:
        """Collect all string values recursively for document path extraction."""
        out = []
        if isinstance(value, str):
            out.append(value)
        elif isinstance(value, list):
            for item in value:
                out.extend(self._collect_text_values(item))
        elif isinstance(value, dict):
            for item in value.values():
                out.extend(self._collect_text_values(item))
        return out

    def api_packet(self, packet_id: str) -> Dict:
        """Return full packet definition, runtime state, linked docs, and packet events."""
        packet_id = packet_id.strip()
        if not packet_id:
            return {"success": False, "message": "Missing id"}

        defn = load_definition()
        state = load_state()

        pkt = next((p for p in defn.get("packets", []) if p["id"] == packet_id), None)
        if not pkt:
            return {"success": False, "message": f"Packet {packet_id} not found"}

        area = next((a for a in defn.get("work_areas", []) if a["id"] == pkt.get("area_id")), {})
        pkt_state = state.get("packets", {}).get(packet_id, {})
        deps = defn.get("dependencies", {}).get(packet_id, [])
        dependents = [pid for pid, dep_list in defn.get("dependencies", {}).items() if packet_id in dep_list]
        events = [e for e in state.get("log", []) if e.get("packet_id") == packet_id]
        docs = self._extract_doc_paths(*self._collect_text_values(pkt), pkt_state.get("notes", ""))

        return {
            "success": True,
            "packet_definition": pkt,
            "packet": {
                "id": pkt["id"],
                "wbs_ref": pkt.get("wbs_ref"),
                "area_id": pkt.get("area_id"),
                "area_title": area.get("title", ""),
                "title": pkt.get("title", ""),
                "scope": pkt.get("scope", ""),
                "status": normalize_runtime_status(pkt_state.get("status", "pending")),
                "assigned_to": pkt_state.get("assigned_to"),
                "started_at": pkt_state.get("started_at"),
                "completed_at": pkt_state.get("completed_at"),
                "notes": pkt_state.get("notes"),
                "dependencies": deps,
                "dependents": dependents,
            },
            "documents": docs,
            "events": events[-50:],
        }

    def api_file(self, rel_path: str) -> Dict:
        """Return safe file preview content for a repository-relative path."""
        rel_path = (rel_path or "").strip().lstrip("./")
        if not rel_path:
            return {"success": False, "message": "Missing path"}

        repo_root = GOV.parent.resolve()
        file_path = (repo_root / rel_path).resolve()
        if not str(file_path).startswith(str(repo_root)):
            return {"success": False, "message": "Invalid path"}
        if not file_path.is_file():
            return {"success": False, "message": "File not found"}

        max_bytes = 200_000
        data = file_path.read_text(errors="replace")[:max_bytes]
        return {
            "success": True,
            "path": rel_path,
            "content": data,
            "truncated": file_path.stat().st_size > max_bytes,
            "mime": mimetypes.guess_type(str(file_path))[0] or "text/plain",
        }

    def api_add_packet(self, body):
        pid = body.get("id", "").strip()
        area_id = body.get("area_id", "").strip()
        wbs_ref = body.get("wbs_ref", "").strip()
        title = body.get("title", "").strip()
        scope = body.get("scope", "").strip()

        if not all([area_id, title]):
            return {"success": False, "message": "Missing required fields (area_id, title)"}

        defn = load_definition()

        # Check area exists
        areas = defn.get("work_areas", [])
        if not any(a["id"] == area_id for a in areas):
            return {"success": False, "message": f"Work area {area_id} not found"}

        # Auto-generate packet ID if needed
        area_packets = [p for p in defn.get("packets", []) if p.get("area_id") == area_id]
        if not pid:
            pkt_num = len(area_packets) + 1
            pid = f"{area_id}-{str(pkt_num).zfill(3)}"

        # Check for duplicate ID
        if any(p["id"] == pid for p in defn.get("packets", [])):
            return {"success": False, "message": f"Packet {pid} already exists"}

        # Auto-generate wbs_ref if not provided
        if not wbs_ref:
            area_idx = next((i for i, a in enumerate(areas) if a["id"] == area_id), 0) + 1
            pkt_num = len(area_packets) + 1
            wbs_ref = f"{area_idx}.{pkt_num}"

        defn.setdefault("packets", []).append({
            "id": pid, "wbs_ref": wbs_ref, "area_id": area_id,
            "title": title, "scope": scope
        })
        save_definition(defn)

        # Initialize state for new packet
        from wbs_common import WBS_STATE
        state = load_state()
        if pid not in state["packets"]:
            state["packets"][pid] = {
                "status": "pending",
                "assigned_to": None,
                "started_at": None,
                "completed_at": None,
                "notes": None
            }
            atomic_write_json(WBS_STATE, state)

        return {"success": True, "message": f"Packet {pid} added"}

    def api_add_area(self, body):
        aid = body.get("id", "").strip()
        title = body.get("title", "").strip()
        desc = body.get("description", "").strip()

        if not all([aid, title]):
            return {"success": False, "message": "ID and title required"}

        defn = load_definition()

        # Ensure proper structure
        if not defn.get("metadata"):
            defn["metadata"] = {
                "project_name": "My Project",
                "approved_by": "user",
                "approved_at": datetime.now().isoformat()
            }
        if "work_areas" not in defn:
            defn["work_areas"] = []
        if "packets" not in defn:
            defn["packets"] = []
        if "dependencies" not in defn:
            defn["dependencies"] = {}

        if any(a["id"] == aid for a in defn["work_areas"]):
            return {"success": False, "message": f"Area {aid} already exists"}

        defn["work_areas"].append({
            "id": aid, "title": title, "description": desc
        })
        save_definition(defn)
        return {"success": True, "message": f"Area {aid} added"}

    def api_add_dep(self, body):
        packet = body.get("packet", "").strip()
        depends_on = body.get("depends_on", "").strip()

        if not all([packet, depends_on]):
            return {"success": False, "message": "packet and depends_on required"}

        if packet == depends_on:
            return {"success": False, "message": "Packet cannot depend on itself"}

        defn = load_definition()
        packets = [p["id"] for p in defn.get("packets", [])]

        if packet not in packets:
            return {"success": False, "message": f"Packet {packet} not found"}
        if depends_on not in packets:
            return {"success": False, "message": f"Packet {depends_on} not found"}

        deps = defn.setdefault("dependencies", {})
        pkt_deps = deps.setdefault(packet, [])

        if depends_on in pkt_deps:
            return {"success": False, "message": "Dependency already exists"}

        pkt_deps.append(depends_on)

        # Check for circular dependency
        from wbs_cli import detect_circular
        cycle = detect_circular(deps)
        if cycle:
            pkt_deps.remove(depends_on)
            return {"success": False, "message": f"Would create circular dependency: {' -> '.join(cycle)}"}

        save_definition(defn)
        return {"success": True, "message": "Dependency added"}

    def api_remove_dep(self, body):
        packet = body.get("packet", "").strip()
        depends_on = body.get("depends_on", "").strip()

        if not all([packet, depends_on]):
            return {"success": False, "message": "packet and depends_on required"}

        defn = load_definition()
        deps = defn.get("dependencies", {})

        if packet not in deps or depends_on not in deps[packet]:
            return {"success": False, "message": "Dependency not found"}

        deps[packet].remove(depends_on)
        if not deps[packet]:
            del deps[packet]

        save_definition(defn)
        return {"success": True, "message": "Dependency removed"}

    def api_edit_packet(self, body):
        pid = body.get("id", "").strip()
        field = body.get("field", "").strip()
        value = body.get("value", "")

        if not pid:
            return {"success": False, "message": "Packet ID required"}

        defn = load_definition()
        packet = next((p for p in defn.get("packets", []) if p["id"] == pid), None)

        if not packet:
            return {"success": False, "message": f"Packet {pid} not found"}

        if field in ("title", "scope", "wbs_ref"):
            packet[field] = value
            save_definition(defn)
            return {"success": True, "message": "Packet updated"}

        return {"success": False, "message": f"Cannot edit field: {field}"}

    def api_edit_area(self, body):
        aid = body.get("id", "").strip()
        field = body.get("field", "").strip()
        value = body.get("value", "")

        if not aid:
            return {"success": False, "message": "Area ID required"}

        defn = load_definition()
        area = next((a for a in defn.get("work_areas", []) if a["id"] == aid), None)

        if not area:
            return {"success": False, "message": f"Area {aid} not found"}

        if field in ("title", "description"):
            area[field] = value
            save_definition(defn)
            return {"success": True, "message": "Area updated"}

        return {"success": False, "message": f"Cannot edit field: {field}"}

    def api_remove_packet(self, body):
        pid = body.get("id", "").strip()
        if not pid:
            return {"success": False, "message": "Packet ID required"}

        defn = load_definition()
        state = load_state()

        # Check packet exists
        packet = next((p for p in defn.get("packets", []) if p["id"] == pid), None)
        if not packet:
            return {"success": False, "message": f"Packet {pid} not found"}

        # Check status
        pkt_state = state["packets"].get(pid, {})
        packet_status = normalize_runtime_status(pkt_state.get("status"))
        if packet_status in ("in_progress", "done"):
            return {"success": False, "message": f"Cannot delete {packet_status} packet"}

        # Remove packet
        defn["packets"] = [p for p in defn["packets"] if p["id"] != pid]

        # Remove from dependencies
        deps = defn.get("dependencies", {})
        if pid in deps:
            del deps[pid]
        for p in list(deps.keys()):
            if pid in deps[p]:
                deps[p].remove(pid)
                if not deps[p]:
                    del deps[p]

        save_definition(defn)

        # Remove from state
        if pid in state["packets"]:
            del state["packets"][pid]
            from wbs_common import WBS_STATE
            atomic_write_json(WBS_STATE, state)

        return {"success": True, "message": f"Packet {pid} deleted"}

    def api_save_wbs(self, body):
        """Save entire WBS definition and initialize state."""
        if not body.get("work_areas") and not body.get("packets"):
            return {"success": False, "message": "No work areas or packets provided"}

        # Save definition
        save_definition(body)

        # Initialize/update state for all packets
        from wbs_common import WBS_STATE
        state = load_state()

        # Add new packets to state, preserve existing status
        existing_ids = set(state["packets"].keys())
        new_ids = {p["id"] for p in body.get("packets", [])}

        # Add new packets
        for packet in body.get("packets", []):
            pid = packet["id"]
            if pid not in state["packets"]:
                state["packets"][pid] = {
                    "status": "pending",
                    "assigned_to": None,
                    "started_at": None,
                    "completed_at": None,
                    "notes": None
                }

        # Remove deleted packets from state
        for pid in list(state["packets"].keys()):
            if pid not in new_ids:
                del state["packets"][pid]

        # Save state
        atomic_write_json(WBS_STATE, state)

        return {"success": True, "message": f"Saved {len(body.get('work_areas', []))} areas, {len(body.get('packets', []))} packets"}

    def run_cmd(self, cmd: str, body: Dict) -> Dict:
        """Run lifecycle commands through CLI to keep transition behavior centralized."""
        pid = body.get("packet_id", "").strip()
        agent = body.get("agent_name", "").strip()
        notes = body.get("notes", body.get("reason", ""))
        risk_ack = str(body.get("residual_risk_ack", "")).strip()
        risk_file = str(body.get("residual_risk_file", "")).strip()
        risk_json = body.get("residual_risk_json", "")

        if cmd != "reset" and (not pid or not agent):
            return {"success": False, "message": "Missing packet_id or agent_name"}
        if not pid:
            return {"success": False, "message": "Missing packet_id"}
        if cmd == "done" and not risk_ack:
            return {
                "success": False,
                "message": "Missing residual_risk_ack (use 'none' or 'declared')",
            }
        if cmd == "done" and risk_file and risk_json:
            return {"success": False, "message": "Use either residual_risk_file or residual_risk_json"}

        args = ["python3", str(CLI), cmd, pid]
        if cmd != "reset":
            args += [agent]
            if notes:
                args.append(notes)
            if cmd == "done":
                args += ["--risk", risk_ack]
                if risk_file:
                    args += ["--risk-file", risk_file]
                elif risk_json:
                    args += ["--risk-json", json.dumps(risk_json)]

        r = subprocess.run(args, capture_output=True, text=True)
        return {"success": r.returncode == 0, "message": (r.stdout + r.stderr).strip()}

    def log_message(self, format, *args):
        LOGGER.info("%s %s", self.log_date_time_string(), format % args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"WBS Dashboard: http://127.0.0.1:{port}")
    try:
        HTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == "__main__":
    main()
