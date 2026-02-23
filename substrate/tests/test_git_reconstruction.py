import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from governed_platform.governance.git_ledger import (
    build_closeout_tag,
    create_tag,
    reconstruct_governance_history,
    run_governance_auto_commit,
)


def run_git(cwd: Path, args):
    proc = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode != 0:
        raise AssertionError(f"git failed: {' '.join(args)}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return proc.stdout.strip()


class GitReconstructionTests(unittest.TestCase):
    def _init_repo(self, td: str) -> Path:
        repo = Path(td)
        run_git(repo, ["init"])
        run_git(repo, ["config", "user.email", "t@example.com"])
        run_git(repo, ["config", "user.name", "tester"])
        gov = repo / ".governance"
        gov.mkdir(parents=True, exist_ok=True)
        state = gov / "wbs-state.json"
        state.write_text(json.dumps({"packets": {}, "log": [], "area_closeouts": {}}, indent=2) + "\n")
        run_git(repo, ["add", ".governance/wbs-state.json"])
        run_git(repo, ["commit", "-m", "init"])
        return repo

    def test_reconstruct_reads_protocol_commits(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._init_repo(td)
            state = repo / ".governance" / "wbs-state.json"

            state.write_text(json.dumps({"step": 1}, indent=2) + "\n")
            ok, reason, commit1, _ = run_governance_auto_commit(
                repo_root=repo,
                packet_id="UPG-058",
                action="claim",
                actor="codex",
                stage_files=[".governance/wbs-state.json"],
            )
            self.assertTrue(ok, reason)
            self.assertTrue(commit1)

            state.write_text(json.dumps({"step": 2}, indent=2) + "\n")
            ok, reason, commit2, _ = run_governance_auto_commit(
                repo_root=repo,
                packet_id="UPG-058",
                action="done",
                actor="codex",
                stage_files=[".governance/wbs-state.json"],
            )
            self.assertTrue(ok, reason)
            self.assertTrue(commit2)

            ok, entries, reason = reconstruct_governance_history(repo, limit=20)
            self.assertTrue(ok, reason)
            actions = [entry.get("action") for entry in entries]
            self.assertIn("claim", actions)
            self.assertIn("done", actions)
            self.assertTrue(all(entry.get("commit") for entry in entries))

    def test_closeout_tag_generation_and_creation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = self._init_repo(td)
            head = run_git(repo, ["rev-parse", "HEAD"]).strip()

            tag = build_closeout_tag("11.0", "2026-02-17T12:34:56+00:00")
            self.assertEqual(tag, "substrate-closeout-11-0-20260217123456")

            ok, reason = create_tag(repo, tag_name=tag, commit_hash=head)
            self.assertTrue(ok, reason)
            tagged = run_git(repo, ["rev-parse", tag]).strip()
            self.assertEqual(tagged, head)


if __name__ == "__main__":
    unittest.main()
