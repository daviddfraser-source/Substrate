import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from substrate_core.state import ActorContext  # noqa: E402
from substrate_core.trust import compute_trust_score, register_trust_model, score_with_active_model  # noqa: E402


class TrustTests(unittest.TestCase):
    def test_compute_trust_score_deterministic(self):
        weights = {"quality": 0.5, "policy": 0.3, "drift": 0.2}
        signals = {"quality": 0.8, "policy": 0.9, "drift": 0.5}
        out1 = compute_trust_score(signals, weights)
        out2 = compute_trust_score(signals, weights)
        self.assertEqual(out1["score"], out2["score"])
        self.assertEqual(out1["contributions"], out2["contributions"])

    def test_register_and_score_active_model(self):
        state = {}
        actor = ActorContext("governance", "admin", "api")
        ok, msg = register_trust_model(
            state,
            version_id="1.0",
            weights={"quality": 0.6, "policy": 0.4},
            actor=actor,
            rationale="Initial trust model",
            approvals=["security-lead"],
        )
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

        ok, msg, payload = score_with_active_model(state, {"quality": 0.9, "policy": 0.8})
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")
        self.assertEqual(payload["model_version"], "1.0")
        self.assertGreater(payload["score"], 0.0)


if __name__ == "__main__":
    unittest.main()
