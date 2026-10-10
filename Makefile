.PHONY: test verify scan-dead-code init-docs init-global paths help

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
	@echo "  make scan-dead-code - dead / orphan method scan"
	@echo "  make init-docs      - init hs_dev_docs skeleton in cwd"
	@echo "  make init-global    - init ~/.hs-dev-skill (cross-project)"
	@echo "  make paths          - print resolved global paths for this OS"
	@echo "  Override interpreter: make test PYTHON=python3   or   make test PYTHON=\"py -3\""

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"
	$(PYTHON) -m unittest discover -s examples/order_service/test/_01_method_test -p "test_*.py"

verify:
	$(PYTHON) scripts/verify_consistency.py --root .

scan-dead-code:
	$(PYTHON) scripts/dead_code_scanner.py --root .

init-docs:
	$(PYTHON) scripts/init_hs_dev_docs.py --root .

init-global:
	$(PYTHON) scripts/init_hs_global.py

paths:
	$(PYTHON) scripts/hs_paths.py
