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


class ClaudeIntegrationTests(unittest.TestCase):
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

    def test_claim_as_claude(self):
        res = run_cli(['claim', 'FX-1', 'claude'])
        self.assertIn('claimed by claude', res.stdout.lower())

    def test_done_with_evidence_as_claude(self):
        run_cli(['claim', 'FX-1', 'claude'])
        run_cli(['done', 'FX-1', 'claude', 'Updated src/x.py, validated via unit tests', '--risk', 'none'])
        state = json.loads(STATE.read_text())
        self.assertEqual(state['packets']['FX-1']['status'], 'done')
        self.assertIn('validated', state['packets']['FX-1']['notes'])

    def test_status_json_has_claude_assignment(self):
        run_cli(['claim', 'FX-1', 'claude'])
        payload = json.loads(run_cli(['--json', 'status']).stdout)
        found = False
        for area in payload.get('areas', []):
            for pkt in area.get('packets', []):
                if pkt['id'] == 'FX-1':
                    found = True
                    self.assertEqual(pkt.get('assigned_to'), 'claude')
        self.assertTrue(found)


if __name__ == '__main__':
    unittest.main()
