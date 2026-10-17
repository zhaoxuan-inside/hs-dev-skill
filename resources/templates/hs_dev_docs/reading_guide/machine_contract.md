## [VIBE_CONTRACT] 机器极速索引契约 (Machine-Actionable Index Manifest)
<!--
  【专供 AI Agent / LLM 极速切片检索（顶部 [VIBE_CONTRACT] 至下一同级标题）】
  说明：本区块为机器可解析的索引契约与快速检索指令集。外部 Agent 接入本系统时，
  优先执行以下专用检索子命令获取精准行段，绝对禁止对 hs_dev_docs 进行整目录扫描！
-->
```yaml
vibe_index_contract:
  docs_root: "hs_dev_docs"
  index_db_path: "hs_dev_docs/_00_project_foundation/_05_doc_index/doc_index.sqlite"
  root_idx_path: "hs_dev_docs/_00_hs_dev_docs.idx"
  dictionary_path: "hs_dev_docs/_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml"

  # 一级功能域与权威索引映射
  domain_routing:
    _00_project_foundation: "hs_dev_docs/_00_project_foundation/_00_project_foundation.idx"
    _01_product_vision: "hs_dev_docs/_01_product_vision/_00_product_vision.idx"
    _02_feature_spec: "hs_dev_docs/_02_feature_spec/_00_feature_spec.idx"
    _03_architecture_design: "hs_dev_docs/_03_architecture_design/_00_architecture_design.idx"
    _04_engineering_contract: "hs_dev_docs/_04_engineering_contract/_00_engineering_contract.idx"
    _05_task_orchestration: "hs_dev_docs/_05_task_orchestration/_00_task_orchestration.idx"
    _06_dev_process: "hs_dev_docs/_06_dev_process/_00_dev_process.idx"

  # Agent 极速检索 CLI（跨平台标准库执行，免扫全盘，Token 节省 90%+）
  agent_cli_shortcuts:
    feature_search: "python scripts/doc_index_db.py --root . feature-search --q <关键词>"
    page_search: "python scripts/doc_index_db.py --root . page-search --q <页面/功能>"
    pattern_search: "python scripts/doc_index_db.py --root . pattern-search --q <模式名>"
    schema_search: "python scripts/doc_index_db.py --root . schema-search --q <表名>"
    dep_graph: "python scripts/doc_index_db.py --root . dep-graph --symbol <类名.方法名>"
    method_search: "python scripts/doc_index_db.py --root . method-search --q <业务意图>"
    symbol_slice: "python scripts/doc_index_db.py --root . symbol-slice --name <符号名>"
    test_search: "python scripts/doc_index_db.py --root . test-search --q <方法/类名>"
    audit_search: "python scripts/doc_index_db.py --root . audit-search --since <YYYY-MM-DD>"
    embed_search: "python scripts/doc_index_db.py --root . embed-search --q <语义查询>"
    text_search: "python scripts/doc_index_db.py --root . search --q <关键词>"
    line_slice: "python scripts/doc_index_db.py --root . slice --path <相对路径> --start <行> --end <行>"

guardrails:
  - "FORBIDDEN: 严禁全量通读 hs_dev_docs 目录大文件（Token 预算硬性拦截）"
  - "MUST: 查阅代码与文档优先使用 doc_index_db 专属子命令进行局部切片"
  - "MUST: 跨 Agent 遵循统一术语单一事实源（_02_project_word.dict.yaml）"
  - "MUST: 代码与契约变更后必须执行 python scripts/doc_index_db.py --root . rebuild 自愈索引"
```

---
