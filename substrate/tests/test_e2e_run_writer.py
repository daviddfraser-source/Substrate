import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'substrate' / 'scripts' / 'e2e-run.py'
STORE = ROOT / 'substrate' / '.governance' / 'e2e-runs.json'


class E2ERunWriterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._backup = STORE.read_bytes() if STORE.exists() else None

    @classmethod
    def tearDownClass(cls):
        if cls._backup is None:
            STORE.unlink(missing_ok=True)
        else:
            STORE.write_bytes(cls._backup)

    def test_writer_appends_normalized_run_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [
                sys.executable,
                str(SCRIPT),
                '--suite', 'writer-test',
                '--agent', 'codex',
                '--trigger', 'manual',
                '--cmd', 'python3 -m unittest substrate/tests/test_root_docs_paths.py -v',
            ]
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

        data = json.loads(STORE.read_text())
        self.assertGreaterEqual(len(data.get('runs', [])), 1)
        latest = data['runs'][0]
        self.assertEqual(latest['suite'], 'writer-test')
        self.assertEqual(latest['trigger'], 'manual')
        self.assertIn('summary', latest)
        self.assertIn('artifacts', latest)


if __name__ == '__main__':
    unittest.main()
