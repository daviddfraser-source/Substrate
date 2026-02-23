import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / '.governance'
sys.path.insert(0, str(GOV))

from wbs_server import Handler  # noqa: E402
from http.server import HTTPServer  # noqa: E402

CLI = [sys.executable, str(GOV / 'wbs_cli.py')]
WBS = GOV / 'wbs.json'
STATE = GOV / 'wbs-state.json'
E2E_RUNS = GOV / 'e2e-runs.json'
BREAK_FIX_LOG = GOV / 'break-fix-log.json'


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def post_json(base, path, payload):
    req = Request(
        base + path,
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode())


def get_json(base, path):
    with urlopen(base + path, timeout=5) as r:
        return json.loads(r.read().decode())


def request_json(base, path, method='GET'):
    req = Request(base + path, method=method)
    try:
        with urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        body = e.read().decode()
        data = json.loads(body) if body else None
        return e.code, data


class ServerApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None
        cls._e2e_backup = E2E_RUNS.read_bytes() if E2E_RUNS.exists() else None
        cls._break_fix_backup = BREAK_FIX_LOG.read_bytes() if BREAK_FIX_LOG.exists() else None

        cls.server = HTTPServer(('127.0.0.1', 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.1)

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

        if cls._e2e_backup is None:
            E2E_RUNS.unlink(missing_ok=True)
        else:
            E2E_RUNS.write_bytes(cls._e2e_backup)
        if cls._break_fix_backup is None:
            BREAK_FIX_LOG.unlink(missing_ok=True)
        else:
            BREAK_FIX_LOG.write_bytes(cls._break_fix_backup)

    def setUp(self):
        STATE.unlink(missing_ok=True)
        e2e_payload = {
            'schema_version': '1.0',
            'updated_at': '2026-02-22T00:00:00Z',
            'runs': [
                {
                    'run_id': 'e2e-test-1',
                    'timestamp': '2026-02-22T00:00:00Z',
                    'agent': 'codex',
                    'packet_id': 'A',
                    'trigger': 'local',
                    'suite': 'server-api-smoke',
                    'status': 'pass',
                    'duration_sec': 0.123,
                    'command': 'python3 -m unittest substrate/tests/test_root_docs_paths.py -v',
                    'exit_code': 0,
                    'summary': {'passed': 2, 'failed': 0, 'skipped': 0, 'total': 2},
                    'failures': [],
                    'artifacts': ['substrate/reports/e2e/e2e-test-1.log'],
                }
            ],
        }
        E2E_RUNS.write_text(json.dumps(e2e_payload, indent=2) + '\n')
        break_fix_payload = {
            'schema_version': '1.0',
            'created_at': '2026-02-22T00:00:00Z',
            'updated_at': '2026-02-22T00:00:00Z',
            'items': [],
        }
        BREAK_FIX_LOG.write_text(json.dumps(break_fix_payload, indent=2) + '\n')
        payload = {
            'metadata': {'project_name': 'server-test', 'approved_by': 't', 'approved_at': '2026-01-01T00:00:00'},
            'work_areas': [{'id': '1.0', 'title': 'Area'}],
            'packets': [
                {'id': 'A', 'wbs_ref': '1.1', 'area_id': '1.0', 'title': 'A', 'scope': ''},
                {'id': 'B', 'wbs_ref': '1.2', 'area_id': '1.0', 'title': 'B', 'scope': ''}
            ],
            'dependencies': {'B': ['A']}
        }
        fd, path = tempfile.mkstemp(suffix='-wbs.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(payload, f)
        try:
            run_cli(['init', path])
        finally:
            os.unlink(path)

    def test_claim_and_done_endpoints(self):
        r1 = post_json(self.base, '/api/claim', {'packet_id': 'A', 'agent_name': 'op'})
        self.assertTrue(r1['success'])

        r2 = post_json(self.base, '/api/done', {'packet_id': 'A', 'agent_name': 'op', 'notes': 'done via api'})
        self.assertFalse(r2['success'])
        self.assertIn('residual_risk_ack', r2['message'])

        r2 = post_json(
            self.base,
            '/api/done',
            {
                'packet_id': 'A',
                'agent_name': 'op',
                'notes': 'done via api',
                'residual_risk_ack': 'none',
            },
        )
        self.assertTrue(r2['success'])

        status = get_json(self.base, '/api/status')
        pkt = next(p for a in status['areas'] for p in a['packets'] if p['id'] == 'A')
        self.assertEqual(pkt['status'], 'done')

    def test_note_endpoint_updates_notes(self):
        post_json(self.base, '/api/claim', {'packet_id': 'A', 'agent_name': 'op'})
        post_json(
            self.base,
            '/api/done',
            {'packet_id': 'A', 'agent_name': 'op', 'notes': 'initial', 'residual_risk_ack': 'none'},
        )
        note_res = post_json(
            self.base,
            '/api/note',
            {'packet_id': 'A', 'agent_name': 'op', 'notes': 'updated evidence path'}
        )
        self.assertTrue(note_res['success'])

        status = get_json(self.base, '/api/status')
        pkt = next(p for a in status['areas'] for p in a['packets'] if p['id'] == 'A')
        self.assertEqual(pkt['notes'], 'updated evidence path')

    def test_fail_and_reset_endpoints(self):
        post_json(self.base, '/api/claim', {'packet_id': 'A', 'agent_name': 'op'})
        fail_res = post_json(self.base, '/api/fail', {'packet_id': 'A', 'agent_name': 'op', 'reason': 'broken'})
        self.assertTrue(fail_res['success'])

        # reset requires in_progress; create fresh in-progress packet for reset path
        self.setUp()
        post_json(self.base, '/api/claim', {'packet_id': 'A', 'agent_name': 'op'})
        reset_res = post_json(self.base, '/api/reset', {'packet_id': 'A'})
        self.assertTrue(reset_res['success'])

    def test_missing_fields_validation(self):
        r = post_json(self.base, '/api/claim', {'packet_id': 'A'})
        self.assertFalse(r['success'])
        self.assertIn('Missing packet_id or agent_name', r['message'])

    def test_packet_documents_detect_paths_with_spaces(self):
        # Add a notes path containing spaces and ensure packet endpoint detects it as existing.
        post_json(
            self.base,
            '/api/note',
            {
                'packet_id': 'A',
                'agent_name': 'op',
                'notes': 'Evidence: docs/example-packets/AG-EXECUTE-CES-ROLLIN-002.md',
            },
        )
        packet = get_json(self.base, '/api/packet?id=A')
        self.assertTrue(packet['success'])
        docs = packet.get('documents', [])
        target = next((d for d in docs if d['path'] == 'docs/example-packets/AG-EXECUTE-CES-ROLLIN-002.md'), None)
        self.assertIsNotNone(target)
        self.assertTrue(target['exists'])

    def test_packet_endpoint_returns_full_payload(self):
        post_json(self.base, '/api/claim', {'packet_id': 'A', 'agent_name': 'op'})
        post_json(
            self.base,
            '/api/done',
            {'packet_id': 'A', 'agent_name': 'op', 'notes': 'done via packet test', 'residual_risk_ack': 'none'},
        )
        packet = get_json(self.base, '/api/packet?id=A')
        self.assertTrue(packet['success'])
        self.assertIn('packet', packet)
        self.assertIn('packet_definition', packet)
        self.assertEqual(packet['packet']['id'], 'A')
        self.assertEqual(packet['packet']['status'], 'done')
        self.assertTrue(isinstance(packet.get('events', []), list))
        self.assertTrue(isinstance(packet.get('documents', []), list))

    def test_deps_graph_endpoint_returns_nodes_and_edges(self):
        data = get_json(self.base, '/api/deps-graph')
        self.assertIn('nodes', data)
        self.assertIn('edges', data)
        self.assertTrue(any(n['id'] == 'A' for n in data['nodes']))
        self.assertTrue(any(e['from'] == 'A' and e['to'] == 'B' for e in data['edges']))

    def test_file_endpoint_returns_document_content(self):
        res = get_json(self.base, '/api/file?path=docs/architecture.md')
        self.assertTrue(res['success'])
        self.assertEqual(res['path'], 'docs/architecture.md')
        self.assertIn('##', res['content'])

    def test_docs_index_endpoint_returns_project_documents(self):
        res = get_json(self.base, '/api/docs-index?limit=2000')
        self.assertTrue(res['success'])
        self.assertIn('documents', res)
        self.assertGreater(res['returned'], 0)
        self.assertTrue(any(d['path'] == 'docs/architecture.md' for d in res['documents']))
        self.assertIn('docs', res.get('categories', []))

    def test_docs_index_endpoint_supports_filters(self):
        res = get_json(self.base, '/api/docs-index?kind=markdown&q=architecture&category=docs&limit=200')
        self.assertTrue(res['success'])
        docs = res.get('documents', [])
        self.assertGreater(len(docs), 0)
        self.assertTrue(all(d.get('kind') == 'markdown' for d in docs))
        self.assertTrue(all(d.get('category') == 'docs' for d in docs))
        self.assertTrue(any(d.get('path') == 'docs/architecture.md' for d in docs))

    def test_unknown_api_route_returns_json_404(self):
        status, body = request_json(self.base, '/api/does-not-exist')
        self.assertEqual(status, 404)
        self.assertIsNotNone(body)
        self.assertFalse(body['success'])
        self.assertIn('Route not found', body['message'])

    def test_closeout_l2_endpoint(self):
        post_json(self.base, '/api/claim', {'packet_id': 'A', 'agent_name': 'op'})
        post_json(
            self.base,
            '/api/done',
            {'packet_id': 'A', 'agent_name': 'op', 'notes': 'done', 'residual_risk_ack': 'none'},
        )
        post_json(self.base, '/api/claim', {'packet_id': 'B', 'agent_name': 'op'})
        post_json(
            self.base,
            '/api/done',
            {'packet_id': 'B', 'agent_name': 'op', 'notes': 'done', 'residual_risk_ack': 'none'},
        )

        fd, path = tempfile.mkstemp(suffix='-drift.md')
        with os.fdopen(fd, 'w') as f:
            f.write(
                "\n".join(
                    [
                        "## Scope Reviewed",
                        "## Expected vs Delivered",
                        "## Drift Assessment",
                        "## Evidence Reviewed",
                        "## Residual Risks",
                        "## Immediate Next Actions",
                    ]
                )
            )
        try:
            closeout = post_json(
                self.base,
                '/api/closeout-l2',
                {'area_id': '1', 'agent_name': 'op', 'assessment_path': path, 'notes': 'done'},
            )
            self.assertTrue(closeout['success'])

            status = get_json(self.base, '/api/status')
            self.assertIn('area_closeouts', status)
            self.assertIn('1.0', status['area_closeouts'])
            self.assertEqual(status['area_closeouts']['1.0']['status'], 'closed')
            self.assertIsNotNone(status['areas'][0]['closeout'])
        finally:
            os.unlink(path)

    def test_status_endpoints_normalize_uppercase_runtime_values(self):
        state = json.loads(STATE.read_text())
        state['packets']['A']['status'] = 'DONE'
        state['packets']['B']['status'] = 'PENDING'
        STATE.write_text(json.dumps(state))

        ready = get_json(self.base, '/api/ready')
        ready_ids = [p['id'] for p in ready['ready']]
        self.assertIn('B', ready_ids)

        status = get_json(self.base, '/api/status')
        packet_a = next(p for a in status['areas'] for p in a['packets'] if p['id'] == 'A')
        self.assertEqual(packet_a['status'], 'done')

    def test_e2e_runs_endpoint_returns_summary_records(self):
        res = get_json(self.base, '/api/e2e/runs?limit=10')
        self.assertTrue(res['success'])
        self.assertGreaterEqual(res['returned'], 1)
        first = res['runs'][0]
        self.assertEqual(first['run_id'], 'e2e-test-1')
        self.assertEqual(first['suite'], 'server-api-smoke')
        self.assertEqual(first['status'], 'pass')

    def test_e2e_run_endpoint_returns_single_record(self):
        res = get_json(self.base, '/api/e2e/run?id=e2e-test-1')
        self.assertTrue(res['success'])
        run = res['run']
        self.assertEqual(run['run_id'], 'e2e-test-1')
        self.assertEqual(run['summary']['total'], 2)

    def test_break_fix_endpoints_lifecycle_and_summary(self):
        opened = post_json(
            self.base,
            '/api/break-fix/open',
            {
                'actor': 'op',
                'title': 'Fix smoke flake',
                'description': 'Intermittent test timeout',
                'severity': 'high',
                'packet_id': 'A',
            },
        )
        self.assertTrue(opened['success'])
        fix_id = opened['fix_id']

        started = post_json(self.base, '/api/break-fix/start', {'fix_id': fix_id, 'actor': 'op'})
        self.assertTrue(started['success'])

        missing_evidence = post_json(
            self.base,
            '/api/break-fix/resolve',
            {'fix_id': fix_id, 'actor': 'op', 'resolution_summary': 'done'},
        )
        self.assertFalse(missing_evidence['success'])
        self.assertIn('evidence', missing_evidence['message'].lower())

        resolved = post_json(
            self.base,
            '/api/break-fix/resolve',
            {
                'fix_id': fix_id,
                'actor': 'op',
                'resolution_summary': 'increased timeout',
                'evidence': ['tests/test_server_api.py'],
            },
        )
        self.assertTrue(resolved['success'])

        listed = get_json(self.base, '/api/break-fix/items?status=resolved&limit=20')
        self.assertTrue(listed['success'])
        self.assertTrue(any(i.get('fix_id') == fix_id for i in listed.get('items', [])))

        single = get_json(self.base, f'/api/break-fix/item?id={fix_id}')
        self.assertTrue(single['success'])
        self.assertEqual(single['item']['status'], 'resolved')

        summary = get_json(self.base, '/api/break-fix/summary')
        self.assertTrue(summary['success'])
        self.assertEqual(summary['summary']['counts']['resolved'], 1)

    def test_status_endpoint_includes_break_fix_fields(self):
        opened = post_json(
            self.base,
            '/api/break-fix/open',
            {'actor': 'op', 'title': 'Open issue', 'description': 'needs triage', 'packet_id': 'A'},
        )
        fix_id = opened['fix_id']
        post_json(self.base, '/api/break-fix/start', {'fix_id': fix_id, 'actor': 'op'})

        status = get_json(self.base, '/api/status')
        self.assertIn('break_fix_summary', status)
        packet = next(p for a in status['areas'] for p in a['packets'] if p['id'] == 'A')
        self.assertGreaterEqual(packet.get('break_fix_active', 0), 1)


if __name__ == '__main__':
    unittest.main()
