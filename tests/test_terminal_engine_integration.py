import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.cookiejar import CookieJar
from http.server import HTTPServer
from pathlib import Path
from urllib.request import HTTPCookieProcessor, Request, build_opener
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / ".governance"
sys.path.insert(0, str(GOV))

from wbs_server import Handler  # noqa: E402

CLI = [sys.executable, str(GOV / "wbs_cli.py")]
WBS = GOV / "wbs.json"
STATE = GOV / "wbs-state.json"


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def post_json(base, path, payload, opener):
    req = Request(
        base + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with opener.open(req, timeout=5) as r:
        return json.loads(r.read().decode())


class TerminalEngineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None
        os.environ["WBS_TERMINAL_MODE"] = "production"

        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.1)

        jar = CookieJar()
        cls.opener = build_opener(HTTPCookieProcessor(jar))
        post_json(
            cls.base,
            "/api/auth/login",
            {"name": "Developer", "email": "developer@example.com", "password": "developer"},
            cls.opener,
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=2)
        cls.server.server_close()

        if cls._wbs_backup is None:
            WBS.unlink(missing_ok=True)
        else:
            WBS.write_bytes(cls._wbs_backup)

        if cls._state_backup is None:
            STATE.unlink(missing_ok=True)
        else:
            STATE.write_bytes(cls._state_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        payload = {
            "metadata": {"project_name": "terminal-test", "approved_by": "t", "approved_at": "2026-01-01T00:00:00"},
            "work_areas": [{"id": "1.0", "title": "Area"}],
            "packets": [{"id": "A", "wbs_ref": "1.1", "area_id": "1.0", "title": "A", "scope": ""}],
            "dependencies": {},
        }
        fd, path = tempfile.mkstemp(suffix="-wbs.json")
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f)
        try:
            run_cli(["init", path])
        finally:
            os.unlink(path)

    def test_substrate_terminal_claim_does_not_use_cli_subprocess(self):
        with patch("wbs_server.subprocess.run", side_effect=AssertionError("subprocess should not be used")):
            res = post_json(self.base, "/api/terminal/execute", {"command": "substrate claim A"}, self.opener)
        self.assertTrue(res["success"])
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("claimed", res["output"])

    def test_substrate_terminal_validate_does_not_use_cli_subprocess(self):
        with patch("wbs_server.subprocess.run", side_effect=AssertionError("subprocess should not be used")):
            res = post_json(self.base, "/api/terminal/execute", {"command": "substrate validate"}, self.opener)
        self.assertTrue(res["success"])
        self.assertEqual(res["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
