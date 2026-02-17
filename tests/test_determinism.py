import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from governed_platform.determinism.fingerprint import (  # noqa: E402
    fingerprint_json,
    fingerprint_execution,
    fingerprint_file,
)
from governed_platform.determinism.validator import (  # noqa: E402
    build_reproducibility_record,
    compare_records,
)


class DeterminismTests(unittest.TestCase):
    def test_json_fingerprint_stable_for_key_order(self):
        a = {"x": 1, "y": 2}
        b = {"y": 2, "x": 1}
        self.assertEqual(fingerprint_json(a), fingerprint_json(b))

    def test_execution_fingerprint_changes_on_output_change(self):
        f1 = fingerprint_execution(["echo", "a"], 0, "a", "")
        f2 = fingerprint_execution(["echo", "a"], 0, "b", "")
        self.assertNotEqual(f1, f2)

    def test_reproducibility_record_compare(self):
        with tempfile.TemporaryDirectory() as td:
            fp = Path(td) / "x.txt"
            fp.write_text("hello")
            exec_payload = {"command": ["python3"], "returncode": 0, "stdout": "", "stderr": ""}
            state = {"version": "1.0", "packets": {}, "log": []}
            r1 = build_reproducibility_record(exec_payload, state, [fp])
            r2 = build_reproducibility_record(exec_payload, state, [fp])
            self.assertTrue(compare_records(r1, r2))

    def test_file_fingerprint_changes_when_file_changes(self):
        with tempfile.TemporaryDirectory() as td:
            fp = Path(td) / "f.txt"
            fp.write_text("a")
            h1 = fingerprint_file(fp)
            fp.write_text("b")
            h2 = fingerprint_file(fp)
            self.assertNotEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
