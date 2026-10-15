.PHONY: test verify scan-dead-code init-docs doc-guide init-global paths index-rebuild index-search global-index-rebuild global-index-search skill-ref-rebuild skill-ref-search rule-list rule-search rule-resolve version version-now help

# 跨平台：Linux/macOS 默认 python3；Windows 可 make PYTHON="py -3" 或 PYTHON=python
ifeq ($(OS),Windows_NT)
  PYTHON ?= python
else
  PYTHON ?= python3
endif

help:
	@echo "hs-dev-skill commands (Windows / Linux / macOS):"
	@echo "  make test           - run unit tests"
	@echo "  make verify         - pre-commit consistency gates"
	@echo "  make version        - generate 4-segment timestamp version (MMddHHmmss)"
	@echo "  make version-now    - get current MMddHHmmss timestamp"
	@echo "  make governance-status - show governance feature toggle status"
	@echo "  make scan-dead-code - dead / orphan method scan"
	@echo "  make init-docs      - init hs_dev_docs skeleton in cwd"
	@echo "  make doc-guide      - generate or refresh hs_dev_docs/README.md reading guide"
	@echo "  make init-global    - init ~/.hs-dev-skill (cross-project)"
	@echo "  make paths          - print resolved global paths for this OS"
	@echo "  make index-rebuild  - rebuild SQLite doc index (token-saving query cache)"
	@echo "  make index-search Q=\"keywords\" - search doc index"
	@echo "  make skill-ref-rebuild - rebuild Skill references scenario index"
	@echo "  make skill-ref-search Q=\"幂等\" - search Skill references"
	@echo "  make rule-list        - list local+remote rule sources"
	@echo "  make rule-search Q=\"React\" - search rule catalog"
	@echo "  make rule-resolve ID=vercel.react-rules RULE=async-parallel"
	@echo "  make global-index-rebuild - rebuild ~/.hs-dev-skill tag index"
	@echo "  make global-index-search TAG=反向代理  or  Q=nginx"
	@echo "  Override interpreter: make test PYTHON=python3   or   make test PYTHON=\"py -3\""

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"
	$(PYTHON) -m unittest discover -s examples/order_service/test/_01_method_test -p "test_*.py"

verify:
	$(PYTHON) scripts/verify_consistency.py --root . --strict

version:
	$(PYTHON) scripts/version_tool.py generate

version-now:
	$(PYTHON) scripts/version_tool.py now

governance-status:
	$(PYTHON) scripts/governance_toggle.py status

scan-dead-code:
	$(PYTHON) scripts/dead_code_scanner.py --root .

init-docs:
	$(PYTHON) scripts/init_hs_dev_docs.py --root .

doc-guide:
	$(PYTHON) scripts/doc_index_db.py --root . generate-guide

init-global:
	$(PYTHON) scripts/init_hs_global.py

paths:
	$(PYTHON) scripts/hs_paths.py

index-rebuild:
	$(PYTHON) scripts/doc_index_db.py --root . rebuild

index-search:
	$(PYTHON) scripts/doc_index_db.py --root . search --q "$(Q)" --limit 8

index-embed-search:
	$(PYTHON) scripts/doc_index_db.py --root . embed-search --q "$(Q)" --limit 8

skill-ref-rebuild:
	$(PYTHON) scripts/skill_ref_index.py rebuild

skill-ref-search:
	$(PYTHON) scripts/skill_ref_index.py search --q "$(Q)" --scenario "$(SCENARIO)" --limit 8

rule-list:
	$(PYTHON) scripts/rule_fetch.py list

rule-search:
	$(PYTHON) scripts/rule_fetch.py search --q "$(Q)" --limit 8

rule-resolve:
	$(PYTHON) scripts/rule_fetch.py resolve --id "$(ID)" --rule "$(RULE)"

global-index-rebuild:
	$(PYTHON) scripts/global_index_db.py rebuild

global-index-search:
	$(PYTHON) scripts/global_index_db.py search --q "$(Q)" --tag "$(TAG)" --limit 8
