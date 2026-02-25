import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.validation import (
    detect_dependency_cycle,
    validate_claim,
    validate_claim_pipeline,
    validate_done,
    validate_fail,
    validate_state_shape,
)


class ValidationTests(unittest.TestCase):
    def _state(self):
        return {
            "packets": {
                "A": {"status": "pending"},
                "B": {"status": "pending"},
            },
            "log": [],
        }

    def test_claim_rejects_unmet_dependencies(self):
        state = self._state()
        ok, msg = validate_claim("B", {"B": ["A"]}, state)
        self.assertFalse(ok)
        self.assertIn("Blocked by A", msg)

    def test_claim_accepts_when_dependency_done(self):
        state = self._state()
        state["packets"]["A"]["status"] = "done"
        ok, msg = validate_claim("B", {"B": ["A"]}, state)
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

    def test_done_rejects_invalid_state(self):
        state = self._state()
        ok, msg = validate_done("A", state)
        self.assertFalse(ok)
        self.assertIn("not in_progress", msg)

    def test_fail_rejects_done_status(self):
        state = self._state()
        state["packets"]["A"]["status"] = "done"
        ok, msg = validate_fail("A", state)
        self.assertFalse(ok)
        self.assertIn("cannot fail", msg)

    def test_validate_state_shape_checks_log_type(self):
        state = self._state()
        state["log"] = {}
        ok, msg = validate_state_shape(state)
        self.assertFalse(ok)
        self.assertIn("log", msg)

    def test_claim_pipeline_deterministic_trace_order(self):
        state = self._state()
        state["packets"]["A"]["status"] = "done"
        ok, msg, trace = validate_claim_pipeline("B", {"B": ["A"]}, state)
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")
        self.assertEqual(trace, ["referential_integrity", "invariant_cycle_check", "dependency_gate"])

    def test_detect_dependency_cycle(self):
        cycle = detect_dependency_cycle({"A": ["B"], "B": ["A"]})
        self.assertTrue(cycle)
        self.assertEqual(cycle[0], cycle[-1])


if __name__ == "__main__":
    unittest.main()
