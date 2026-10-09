.PHONY: test verify scan-dead-code init-docs help

PYTHON ?= python3

help:
	@echo "hs-dev-skill 常用开发命令:"
	@echo "  make test           - 运行全量单元测试"
	@echo "  make verify         - 执行提交前全量一致性与质量门禁自检"
	@echo "  make scan-dead-code - 扫描死代码与未登记的孤儿方法"
	@echo "  make init-docs      - 在当前目录初始化完整的 hs_dev_docs 骨架与索引"

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"
	$(PYTHON) -m unittest discover -s examples/order_service/test/_01_method_test -p "test_*.py"

verify:
	$(PYTHON) scripts/verify_consistency.py --root .

scan-dead-code:
	$(PYTHON) scripts/dead_code_scanner.py --root .

init-docs:
	$(PYTHON) scripts/init_hs_dev_docs.py --root .
