#!/bin/bash
# WBS Smoke Tests (JSON-based)
cd "$(dirname "$0")"
PASS=0; FAIL=0
pass() { echo "PASS: $1"; PASS=$((PASS+1)); return 0; }
fail() { echo "FAIL: $1"; FAIL=$((FAIL+1)); return 0; }

rm -f .governance/wbs-state.json

echo "WBS Smoke Tests"
echo "==============="

# Syntax
python3 -m py_compile .governance/wbs_cli.py 2>/dev/null && pass "cli syntax" || fail "cli syntax"
python3 -m py_compile .governance/wbs_server.py 2>/dev/null && pass "server syntax" || fail "server syntax"

# Init
python3 .governance/wbs_cli.py init .governance/wbs.json >/dev/null 2>&1 && pass "init" || fail "init"

# State file created
[ -f .governance/wbs-state.json ] && pass "state file" || fail "state file"

# Commands
for cmd in status ready progress next; do
  python3 .governance/wbs_cli.py $cmd >/dev/null 2>&1 && pass "$cmd" || fail "$cmd"
done

# Workflow
ID=$(python3 -c "import json;print(json.load(open('.governance/wbs.json'))['packets'][0]['id'])" 2>/dev/null)
[ -n "$ID" ] && python3 .governance/wbs_cli.py claim "$ID" test-agent >/dev/null 2>&1 && pass "claim" || fail "claim"
[ -n "$ID" ] && python3 .governance/wbs_cli.py done "$ID" test-agent "tested" >/dev/null 2>&1 && pass "done" || fail "done"

# Verify state is JSON
python3 -c "import json;json.load(open('.governance/wbs-state.json'))" 2>/dev/null && pass "valid json" || fail "valid json"

# Circular detection
echo '{"metadata":{},"work_areas":[{"id":"T","title":"T"}],"packets":[{"id":"A","wbs_ref":"1","area_id":"T","title":"A","scope":""},{"id":"B","wbs_ref":"2","area_id":"T","title":"B","scope":""}],"dependencies":{"A":["B"],"B":["A"]}}' > /tmp/c.json
python3 .governance/wbs_cli.py init /tmp/c.json 2>&1 | grep -q "Circular" && pass "circular" || fail "circular"
rm -f /tmp/c.json

rm -f .governance/wbs-state.json
echo ""; echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && exit 0 || exit 1
