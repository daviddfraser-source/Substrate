#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

OUT="reports/nfr-baseline.json"
mkdir -p reports

python3 - <<'PY'
import json
import time
from pathlib import Path
import sys

sys.path.insert(0, 'src')
from app.api.operations import health_endpoint, MetricsStore, metrics_endpoint
from app.auth.rbac import RoleBinding
from app.api.server import route_request

result = {
    'timestamp': time.time(),
    'checks': [],
}

start = time.time()
health = health_endpoint()
latency_ms = (time.time() - start) * 1000
result['checks'].append({
    'name': 'health_endpoint_latency',
    'value_ms': latency_ms,
    'target_ms': 200,
    'passed': latency_ms < 200,
})

store = MetricsStore()
store.record('api_latency_ms', latency_ms)
metrics = metrics_endpoint(store)
result['checks'].append({
    'name': 'metrics_endpoint_available',
    'passed': metrics.get('count', 0) >= 1,
})

# RBAC deny check
try:
    route_request('/packets', 'POST', bindings=(RoleBinding(role='viewer', tenant_id='t1'),), tenant_id='t1', project_id='p1')
    deny_passed = False
except Exception:
    deny_passed = True
result['checks'].append({
    'name': 'rbac_denies_unauthorized_write',
    'passed': deny_passed,
})

# RBAC allow check
allow = route_request('/packets', 'POST', bindings=(RoleBinding(role='project_admin', tenant_id='t1', project_id='p1'),), tenant_id='t1', project_id='p1')
result['checks'].append({
    'name': 'rbac_allows_authorized_write',
    'passed': bool(allow.get('ok')),
})

result['summary'] = {
    'passed': all(item.get('passed', False) for item in result['checks']),
    'total': len(result['checks']),
}

Path('reports/nfr-baseline.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
PY

echo "Wrote ${OUT}"
