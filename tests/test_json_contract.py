import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = [sys.executable, str(ROOT / '.governance' / 'wbs_cli.py')]
WBS = ROOT / '.governance' / 'wbs.json'
STATE = ROOT / '.governance' / 'wbs-state.json'


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class JsonContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._wbs_backup = WBS.read_bytes() if WBS.exists() else None
        cls._state_backup = STATE.read_bytes() if STATE.exists() else None

    @classmethod
    def tearDownClass(cls):
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
            'metadata': {'project_name': 't', 'approved_by': 't', 'approved_at': '2026-01-01T00:00:00'},
            'work_areas': [{'id': '1.0', 'title': 'Area'}],
            'packets': [
                {'id': 'A', 'wbs_ref': '1.1', 'area_id': '1.0', 'title': 'A', 'scope': ''}
            ],
            'dependencies': {}
        }
        fd, path = tempfile.mkstemp(suffix='-wbs.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(payload, f)
        try:
            run_cli(['init', path])
        finally:
            os.unlink(path)

    def test_json_shapes(self):
        progress = json.loads(run_cli(['--json', 'progress']).stdout)
        self.assertIn('counts', progress)
        self.assertIn('total', progress)

        ready = json.loads(run_cli(['--json', 'ready']).stdout)
        self.assertIn('ready', ready)

        status = json.loads(run_cli(['--json', 'status']).stdout)
        self.assertIn('metadata', status)
        self.assertIn('areas', status)
        self.assertIn('counts', status)
        self.assertIn('closeout', status['areas'][0])

        log = json.loads(run_cli(['--json', 'log', '5']).stdout)
        self.assertIn('log', log)

    def test_lifecycle_json_includes_shared_decision_envelope(self):
        claim = json.loads(run_cli(['--json', 'claim', 'A', 'agent-a']).stdout)
        self.assertTrue(claim['success'])
        self.assertIn('decision', claim)
        self.assertEqual(claim['decision']['action'], 'claim')
        self.assertEqual(claim['decision']['packet_id'], 'A')
        self.assertEqual(claim['decision']['status'], 'allowed')

        done = json.loads(run_cli(['--json', 'done', 'A', 'agent-a', 'notes', '--risk', 'none']).stdout)
        self.assertTrue(done['success'])
        self.assertIn('decision', done)
        self.assertEqual(done['decision']['action'], 'done')
        self.assertEqual(done['decision']['packet_id'], 'A')


if __name__ == '__main__':
    unittest.main()
