import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "governance-state-guard.sh"


def run_guard(args=None, env=None, expect=0):
    args = args or []
    merged = os.environ.copy()
    if env:
        merged.update(env)
    proc = subprocess.run(
        ["bash", str(SCRIPT)] + args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=merged,
    )
    if proc.returncode != expect:
        raise AssertionError(
            f"guard failed\nargs={args}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class GovernanceStateGuardTests(unittest.TestCase):
    def test_passes_when_state_file_not_changed(self):
        run_guard(env={"GOV_STATE_GUARD_CHANGED_FILES": "README.md"})

    def test_blocks_direct_state_file_change_without_override(self):
        proc = run_guard(
            env={"GOV_STATE_GUARD_CHANGED_FILES": ".governance/wbs-state.json"},
            expect=1,
        )
        self.assertIn("direct changes to .governance/wbs-state.json are blocked", proc.stderr)

    def test_blocks_legacy_activity_log_change_without_override(self):
        proc = run_guard(
            env={"GOV_STATE_GUARD_CHANGED_FILES": ".governance/activity-log.jsonl"},
            expect=1,
        )
        self.assertIn("direct changes to .governance/activity-log.jsonl are blocked", proc.stderr)

    def test_blocks_residual_risk_register_change_without_override(self):
        proc = run_guard(
            env={"GOV_STATE_GUARD_CHANGED_FILES": ".governance/residual-risk-register.json"},
            expect=1,
        )
        self.assertIn("direct changes to .governance/residual-risk-register.json are blocked", proc.stderr)

    def test_allows_env_override(self):
        run_guard(
            env={
                "GOV_STATE_GUARD_CHANGED_FILES": ".governance/wbs-state.json",
                "ALLOW_WBS_STATE_EDIT": "1",
            }
        )

    def test_allows_commit_message_override_token(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("manual fix [allow-wbs-state-edit]\n")
            msg_path = f.name
        try:
            run_guard(
                args=["--commit-msg", msg_path],
                env={"GOV_STATE_GUARD_CHANGED_FILES": ".governance/wbs-state.json"},
            )
        finally:
            Path(msg_path).unlink(missing_ok=True)

    def test_allows_ci_override_token(self):
        run_guard(
            args=["--ci"],
            env={
                "GOV_STATE_GUARD_CHANGED_FILES": ".governance/wbs-state.json",
                "GOV_STATE_GUARD_COMMIT_MESSAGES": "hotfix [allow-wbs-state-edit]",
            },
        )

    def test_check_tracked_mode_fails_when_runtime_file_tracked(self):
        proc = run_guard(
            args=["--check-tracked"],
            env={"GOV_STATE_GUARD_TRACKED_FILES": ".governance/activity-log.jsonl"},
            expect=1,
        )
        self.assertIn("runtime governance artifacts are tracked in git", proc.stderr)


if __name__ == "__main__":
    unittest.main()
