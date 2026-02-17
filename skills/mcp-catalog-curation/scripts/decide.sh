#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: decide.sh <approve|reject> <server-name> <url> <rationale>"
  exit 1
fi

decision="$1"
name="$2"
url="$3"
rationale="$4"

if [[ "${decision}" != "approve" && "${decision}" != "reject" ]]; then
  echo "Decision must be approve or reject"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ALLOWLIST="${ROOT_DIR}/skills/mcp-catalog-curation/assets/allowlist.json"
OUT_DIR="${ROOT_DIR}/docs/codex-migration/skills/mcp-curation"
mkdir -p "${OUT_DIR}"

ts="$(date -u +"%Y%m%dT%H%M%SZ")"
record="${OUT_DIR}/${ts}-${decision}-${name}.md"

cat > "${record}" <<EOF
# MCP Curation Decision

- Decision: ${decision}
- Server: ${name}
- URL: ${url}
- Timestamp: ${ts}

## Rationale
${rationale}

## Checklist
See: skills/mcp-catalog-curation/assets/review-checklist.md
EOF

if [[ "${decision}" == "approve" ]]; then
  python3 - "${ALLOWLIST}" "${name}" "${url}" <<'PY'
import json
import sys
from pathlib import Path

allowlist_path = Path(sys.argv[1])
name = sys.argv[2]
url = sys.argv[3]

data = json.loads(allowlist_path.read_text())
servers = data.setdefault("approved_servers", [])
if not any(s.get("name") == name for s in servers):
    servers.append({"name": name, "url": url})
allowlist_path.write_text(json.dumps(data, indent=2) + "\n")
PY
fi

echo "Recorded decision: ${record}"
