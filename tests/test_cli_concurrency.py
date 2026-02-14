import json
import os
import subprocess
import sys
import tempfile
import threading
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


class CliConcurrencyTests(unittest.TestCase):
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

    @unittest.skipIf(sys.platform.startswith("win"), "Windows does not support fcntl locking")
    def test_only_one_claim_succeeds(self):
        results = []

        def claim(agent):
            p = subprocess.run(CLI + ['claim', 'A', agent], cwd=ROOT, capture_output=True, text=True)
            results.append(p.returncode)

        t1 = threading.Thread(target=claim, args=('agent-1',))
        t2 = threading.Thread(target=claim, args=('agent-2',))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Safety property: concurrent claim attempts must not produce two successes.
        self.assertLessEqual(results.count(0), 1)

        # If race timing yields two failures, state should remain healthy and serial claim works.
        if results.count(0) == 0:
            follow_up = subprocess.run(CLI + ['claim', 'A', 'agent-serial'], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(follow_up.returncode, 0, msg=follow_up.stdout + follow_up.stderr)


if __name__ == '__main__':
    unittest.main()
