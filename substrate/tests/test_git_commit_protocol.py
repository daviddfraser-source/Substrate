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
    format_governance_commit,
    parse_governance_commit,
)

CLI = [sys.executable, str(ROOT / ".governance" / "wbs_cli.py")]


def run_cli(args, expect=0):
    proc = subprocess.run(CLI + args, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != expect:
        raise AssertionError(
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


class GitCommitProtocolTests(unittest.TestCase):
    def test_format_is_deterministic(self):
        a = format_governance_commit(
            packet_id="IMP-001",
            action="claim",
            actor="codex",
            event_id="evt-00000001",
            timestamp="2026-02-17T00:00:00+00:00",
        )
        b = format_governance_commit(
            packet_id="IMP-001",
            action="claim",
            actor="codex",
            event_id="evt-00000001",
            timestamp="2026-02-17T00:00:00+00:00",
        )
        self.assertEqual(a, b)

    def test_parse_valid_protocol_message(self):
        msg = format_governance_commit(
            packet_id="IMP-001",
            action="done",
            actor="codex",
            event_id="evt-00000009",
            timestamp="2026-02-17T10:12:13+00:00",
            area_id="11.0",
        )
        parsed = parse_governance_commit(msg)
        self.assertEqual(parsed["packet_id"], "IMP-001")
        self.assertEqual(parsed["action"], "done")
        self.assertEqual(parsed["actor"], "codex")
        self.assertEqual(parsed["event_id"], "evt-00000009")
        self.assertEqual(parsed["area_id"], "11.0")

    def test_parse_rejects_missing_required_trailer(self):
        msg = (
            "substrate(packet=IMP-001,action=claim,actor=codex)\n\n"
            "Substrate-Protocol: 1\n"
            "Substrate-Event-ID: evt-00000001\n"
            "Substrate-Packet: IMP-001\n"
            "Substrate-Action: claim\n"
            "Substrate-Actor: codex\n"
        )
        with self.assertRaisesRegex(ValueError, "missing required trailer"):
            parse_governance_commit(msg)

    def test_parse_rejects_subject_trailer_mismatch(self):
        msg = (
            "substrate(packet=IMP-001,action=claim,actor=codex)\n\n"
            "Substrate-Protocol: 1\n"
            "Substrate-Event-ID: evt-00000001\n"
            "Substrate-Packet: IMP-002\n"
            "Substrate-Action: claim\n"
            "Substrate-Actor: codex\n"
            "Substrate-Timestamp: 2026-02-17T00:00:00+00:00\n"
        )
        with self.assertRaisesRegex(ValueError, "subject/trailer mismatch"):
            parse_governance_commit(msg)

    def test_cli_git_protocol_help_output(self):
        proc = run_cli(["git-protocol"])
        self.assertIn("Git Governance Commit Protocol", proc.stdout)
        self.assertIn("substrate(packet=<PACKET_ID>,action=<ACTION>,actor=<ACTOR>)", proc.stdout)

    def test_cli_git_protocol_parse_mode(self):
        msg = format_governance_commit(
            packet_id="IMP-003",
            action="note",
            actor="codex",
            event_id="evt-00000011",
            timestamp="2026-02-17T11:00:00+00:00",
        )
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tmp:
            tmp.write(msg)
            path = tmp.name
        try:
            proc = run_cli(["git-protocol", "--parse", path])
            self.assertIn("Protocol parse OK", proc.stdout)
            self.assertIn("packet: IMP-003", proc.stdout)
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
