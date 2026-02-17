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


class CliExportTests(unittest.TestCase):
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
        run_cli(['claim', 'FX-1', 'agent'])
        run_cli(['done', 'FX-1', 'agent', 'evidence', '--risk', 'none'])

    def test_export_state_and_log(self):
        with tempfile.TemporaryDirectory() as td:
            state_out = Path(td) / 'state.json'
            log_out = Path(td) / 'log.csv'

            run_cli(['export', 'state-json', str(state_out)])
            run_cli(['export', 'log-csv', str(log_out)])

            state_payload = json.loads(state_out.read_text())
            self.assertIn('packets', state_payload)
            self.assertIn('FX-1', state_payload['packets'])

            csv_text = log_out.read_text()
            self.assertIn('packet_id,event,agent,timestamp,notes', csv_text.splitlines()[0])
            self.assertIn('FX-1', csv_text)


if __name__ == '__main__':
    unittest.main()
