#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${ROOT_DIR}/skills/manifest.json"

usage() {
  cat <<'EOF'
Usage:
  scripts/skills-manifest.sh list
  scripts/skills-manifest.sh enable <skill-name>
  scripts/skills-manifest.sh disable <skill-name>
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

cmd="$1"
name="${2:-}"

case "${cmd}" in
  list)
    python3 - "${MANIFEST}" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
for s in data.get("skills", []):
    state = "enabled" if s.get("enabled") else "disabled"
    print(f"{s.get('name')}: {state}")
PY
    ;;
  enable|disable)
    if [[ -z "${name}" ]]; then
      echo "Missing skill name"
      usage
      exit 1
    fi
    python3 - "${MANIFEST}" "${name}" "${cmd}" <<'PY'
import json, sys
manifest_path, target, action = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(manifest_path))
skills = data.get("skills", [])
for skill in skills:
    if skill.get("name") == target:
        skill["enabled"] = action == "enable"
        with open(manifest_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"{target}: {'enabled' if skill['enabled'] else 'disabled'}")
        break
else:
    print(f"Skill not found: {target}")
    sys.exit(1)
PY
    ;;
  *)
    usage
    exit 1
    ;;
esac
