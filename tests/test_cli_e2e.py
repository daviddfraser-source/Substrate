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


class CliE2ETests(unittest.TestCase):
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

    def _init_dep_graph(self):
        payload = {
            'metadata': {'project_name': 't', 'approved_by': 't', 'approved_at': '2026-01-01T00:00:00'},
            'work_areas': [{'id': '1.0', 'title': 'Area'}],
            'packets': [
                {'id': 'A', 'wbs_ref': '1.1', 'area_id': '1.0', 'title': 'A', 'scope': ''},
                {'id': 'B', 'wbs_ref': '1.2', 'area_id': '1.0', 'title': 'B', 'scope': ''},
                {'id': 'C', 'wbs_ref': '1.3', 'area_id': '1.0', 'title': 'C', 'scope': ''}
            ],
            'dependencies': {'B': ['A'], 'C': ['B']}
        }
        fd, path = tempfile.mkstemp(suffix='-wbs.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(payload, f)
        try:
            run_cli(['init', path])
        finally:
            os.unlink(path)

    def test_ready_progresses_by_dependency(self):
        self._init_dep_graph()
        ready1 = json.loads(run_cli(['--json', 'ready']).stdout)['ready']
        self.assertEqual([x['id'] for x in ready1], ['A'])

        run_cli(['claim', 'A', 'agent'])
        run_cli(['done', 'A', 'agent', 'ok'])

        ready2 = json.loads(run_cli(['--json', 'ready']).stdout)['ready']
        self.assertEqual([x['id'] for x in ready2], ['B'])

    def test_fail_cascades_to_blocked(self):
        self._init_dep_graph()
        run_cli(['claim', 'A', 'agent'])
        run_cli(['done', 'A', 'agent', 'ok'])
        run_cli(['claim', 'B', 'agent'])
        run_cli(['fail', 'B', 'agent', 'broken'])

        state = json.loads(STATE.read_text())
        self.assertEqual(state['packets']['B']['status'], 'failed')
        self.assertEqual(state['packets']['C']['status'], 'blocked')

    def test_graph_dot_export(self):
        self._init_dep_graph()
        with tempfile.TemporaryDirectory() as td:
            dot_path = Path(td) / 'deps.dot'
            proc = run_cli(['graph', '--output', str(dot_path)])
            self.assertIn('DOT graph exported', proc.stdout)
            content = dot_path.read_text()
            self.assertIn('digraph wbs_dependencies', content)
            self.assertIn('"A" -> "B"', content)


if __name__ == '__main__':
    unittest.main()
