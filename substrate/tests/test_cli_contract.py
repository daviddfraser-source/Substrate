import json
import os
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
            f"command failed: {' '.join(args)}\nrc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def write_def(payload):
    fd, path = tempfile.mkstemp(suffix='-wbs.json')
    with os.fdopen(fd, 'w') as f:
        json.dump(payload, f)
    return path


def write_temp_file(content, suffix=".md"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class CliContractTests(unittest.TestCase):
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

    def _init_single_packet(self):
        payload = {
            'metadata': {'project_name': 't', 'approved_by': 't', 'approved_at': '2026-01-01T00:00:00'},
            'work_areas': [{'id': '1.0', 'title': 'Area'}],
            'packets': [
                {'id': 'A-1', 'wbs_ref': '1.1', 'area_id': '1.0', 'title': 'A1', 'scope': 'scope'}
            ],
            'dependencies': {}
        }
        path = write_def(payload)
        try:
            run_cli(['init', path])
        finally:
            os.unlink(path)

    def test_init_without_argument_uses_default_wbs_path(self):
        payload = {
            'metadata': {'project_name': 'default-init', 'approved_by': 't', 'approved_at': '2026-01-01T00:00:00'},
            'work_areas': [{'id': '1.0', 'title': 'Area'}],
            'packets': [
                {'id': 'D-1', 'wbs_ref': '1.1', 'area_id': '1.0', 'title': 'D1', 'scope': 'scope'}
            ],
            'dependencies': {}
        }
        WBS.write_text(json.dumps(payload))
        run_cli(['init'])
        state = json.loads(STATE.read_text())
        self.assertIn('D-1', state['packets'])

    def test_init_with_argument_overrides_default_wbs_path(self):
        payload = {
            'metadata': {'project_name': 'arg-init', 'approved_by': 't', 'approved_at': '2026-01-01T00:00:00'},
            'work_areas': [{'id': '1.0', 'title': 'Area'}],
            'packets': [
                {'id': 'B-1', 'wbs_ref': '1.1', 'area_id': '1.0', 'title': 'B1', 'scope': 'scope'}
            ],
            'dependencies': {}
        }
        path = write_def(payload)
        try:
            run_cli(['init', path])
        finally:
            os.unlink(path)
        definition = json.loads(WBS.read_text())
        self.assertEqual(definition['packets'][0]['id'], 'B-1')

    def test_claim_requires_pending(self):
        self._init_single_packet()
        run_cli(['claim', 'A-1', 'agent-a'])
        proc = run_cli(['claim', 'A-1', 'agent-b'], expect=1)
        self.assertIn('not pending', proc.stdout)

    def test_done_requires_in_progress(self):
        self._init_single_packet()
        proc = run_cli(['done', 'A-1', 'agent-a', 'notes', '--risk', 'none'], expect=1)
        self.assertIn('not in_progress', proc.stdout)

    def test_note_updates_done_packet(self):
        self._init_single_packet()
        run_cli(['claim', 'A-1', 'agent-a'])
        run_cli(['done', 'A-1', 'agent-a', 'initial', '--risk', 'none'])
        run_cli(['note', 'A-1', 'agent-a', 'evidence: docs/x.md'])

        state = json.loads(STATE.read_text())
        self.assertEqual(state['packets']['A-1']['status'], 'done')
        self.assertEqual(state['packets']['A-1']['notes'], 'evidence: docs/x.md')
        self.assertEqual(state['log'][-1]['event'], 'noted')

    def test_handover_and_resume_commands(self):
        self._init_single_packet()
        run_cli(['claim', 'A-1', 'agent-a'])
        run_cli(
            [
                'handover',
                'A-1',
                'agent-a',
                'session-timeout',
                '--to',
                'agent-b',
                '--progress',
                'halfway done',
                '--files',
                'src/a.py,tests/test_a.py',
                '--remaining',
                'run-tests|update-docs',
            ]
        )

        proc = run_cli(['done', 'A-1', 'agent-b', 'done', '--risk', 'none'], expect=1)
        self.assertIn('active handover', proc.stdout)

        run_cli(['resume', 'A-1', 'agent-b'])
        run_cli(['done', 'A-1', 'agent-b', 'done', '--risk', 'none'])

        state = json.loads(STATE.read_text())
        handovers = state['packets']['A-1'].get('handovers', [])
        self.assertEqual(len(handovers), 1)
        self.assertFalse(handovers[0]['active'])
        self.assertEqual(handovers[0]['resumed_by'], 'agent-b')

    def test_closeout_l2_requires_all_packets_done(self):
        self._init_single_packet()
        drift_doc = write_temp_file(
            "\n".join(
                [
                    "## Scope Reviewed",
                    "## Expected vs Delivered",
                    "## Drift Assessment",
                    "## Evidence Reviewed",
                    "## Residual Risks",
                    "## Immediate Next Actions",
                ]
            )
        )
        try:
            proc = run_cli(['closeout-l2', '1', 'agent-a', drift_doc, 'closeout'], expect=1)
            self.assertIn('incomplete packets', proc.stdout)
        finally:
            os.unlink(drift_doc)

    def test_closeout_l2_records_area_closeout(self):
        self._init_single_packet()
        run_cli(['claim', 'A-1', 'agent-a'])
        run_cli(['done', 'A-1', 'agent-a', 'done', '--risk', 'none'])
        drift_doc = write_temp_file(
            "\n".join(
                [
                    "## Scope Reviewed",
                    "## Expected vs Delivered",
                    "## Drift Assessment",
                    "## Evidence Reviewed",
                    "## Residual Risks",
                    "## Immediate Next Actions",
                    "",
                    "no hash required",
                ]
            )
        )
        try:
            run_cli(['closeout-l2', '1', 'agent-a', drift_doc, 'ready for handoff'])
            state = json.loads(STATE.read_text())
            self.assertIn('1.0', state.get('area_closeouts', {}))
            closeout = state['area_closeouts']['1.0']
            self.assertEqual(closeout['status'], 'closed')
            self.assertEqual(closeout['closed_by'], 'agent-a')
            self.assertIn('drift_assessment_path', closeout)
            self.assertEqual(state['log'][-1]['event'], 'area_closed')
        finally:
            os.unlink(drift_doc)

    def test_help_lists_template_validate_command(self):
        proc = run_cli(['help'])
        self.assertIn('template-validate', proc.stdout)

    def test_done_requires_explicit_residual_risk_ack(self):
        self._init_single_packet()
        run_cli(['claim', 'A-1', 'agent-a'])
        proc = run_cli(['done', 'A-1', 'agent-a', 'notes'], expect=1)
        self.assertIn('Residual risk acknowledgement is required', proc.stdout)


if __name__ == '__main__':
    unittest.main()
