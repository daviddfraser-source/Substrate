import json
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
            f"command failed: {' '.join(args)}\\nrc={proc.returncode}\\nstdout={proc.stdout}\\nstderr={proc.stderr}"
        )
    return proc


class CliTransitionEdgeTests(unittest.TestCase):
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
        fixture = ROOT / 'tests' / 'fixtures' / 'wbs_linear.json'
        run_cli(['init', str(fixture)])

    def test_claim_blocked_by_dependency(self):
        proc = run_cli(['claim', 'FX-2', 'agent'], expect=1)
        self.assertIn('WBS-E-003', proc.stdout)

    def test_done_wrong_agent_fails(self):
        proc = run_cli(['done', 'UNKNOWN', 'agent-b', 'bad id'], expect=1)
        self.assertIn('WBS-E-001', proc.stdout)

    def test_reset_only_in_progress(self):
        proc = run_cli(['reset', 'FX-1'], expect=1)
        self.assertIn('WBS-E-004', proc.stdout)


if __name__ == '__main__':
    unittest.main()
