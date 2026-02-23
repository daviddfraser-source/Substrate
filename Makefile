.PHONY: bootstrap status briefing ready validate test e2e-smoke root-hygiene hygiene publish-git-ready

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
