.PHONY: bootstrap status briefing ready validate test e2e-smoke root-hygiene hygiene publish-git-ready sandbox sandbox-reset sandbox-status sandbox-destroy red-team

bootstrap:
	./bootstrap.sh

status:
	python3 start.py --status

briefing:
	python3 substrate/.governance/wbs_cli.py briefing --format json

ready:
	python3 substrate/.governance/wbs_cli.py ready

validate:
	python3 substrate/.governance/wbs_cli.py validate
	python3 substrate/.governance/wbs_cli.py validate-packet substrate/.governance/wbs.json

test:
	./substrate/scripts/quality-gates.sh

e2e-smoke:
	python3 substrate/scripts/e2e-run.py --suite governance-viewer-smoke --trigger local --agent codex --cmd "python3 -m unittest substrate/tests/test_root_docs_paths.py -v"

root-hygiene:
	./substrate/scripts/check-root-hygiene.sh

hygiene:
	rm -rf __pycache__ .pytest_cache .mypy_cache
	./substrate/scripts/check-root-hygiene.sh
	python3 substrate/.governance/wbs_cli.py validate
	python3 substrate/.governance/wbs_cli.py validate-packet substrate/.governance/wbs.json
	./substrate/scripts/scaffold-check.sh
	python3 substrate/.governance/wbs_cli.py template-validate
	python3 -m unittest substrate/tests/test_root_docs_paths.py -v

publish-git-ready:
	@test -n "$(SNAPSHOT)" || (echo "Usage: make publish-git-ready SNAPSHOT=<name>" && exit 1)
	./substrate/scripts/publish-git-ready.sh "$(SNAPSHOT)"

# ---------------------------------------------------------------------------
# Sandbox — isolated governance project for safe experimentation
# ---------------------------------------------------------------------------
# Uses the existing multi-project system (substrate/projects/sandbox/).
# All governance rules apply; changes here are fully isolated from main.

sandbox:
	python3 substrate/scripts/sandbox.py create $(SEED:%=--seed %)

sandbox-reset:
	python3 substrate/scripts/sandbox.py reset $(SEED:%=--seed %)

sandbox-status:
	python3 substrate/scripts/sandbox.py status

sandbox-destroy:
	python3 substrate/scripts/sandbox.py destroy

# ---------------------------------------------------------------------------
# Red Team Review — adversarial governance + code review (Gemini skill)
# ---------------------------------------------------------------------------
# This target prints instructions; the review is executed by Gemini.
# Scope: any packet id, area id, keyword, or 'general' for full sweep.

red-team:
	@echo ""
	@echo "Red Team Review — invoke via Gemini with the red-team-review skill"
	@echo ""
	@echo "  Skill location: .gemini/skills/red-team-review/SKILL.md"
	@echo ""
	@echo "  To run: ask Gemini to 'run the red-team-review skill'"
	@echo "  Provide a focus: packet id, area id, keyword, or 'general'"
	@echo ""
	@echo "  The review will:"
	@echo "    1. Load governance context for the given scope"
	@echo "    2. Run adversarial checks (approval bypass, evidence quality, etc.)"
	@echo "    3. Probe in sandbox if available (make sandbox first)"
	@echo "    4. Output structured findings: Critical / Medium / Low"
	@echo ""

