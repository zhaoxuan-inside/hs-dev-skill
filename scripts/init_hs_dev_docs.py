#!/usr/bin/env python3
"""
init_hs_dev_docs.py
一键初始化符合《产品开发 Skill 规格定义书 v2.4》的完整项目目录结构、文档体系及所有 .idx JSONL 索引文件。
"""

import os
import sys
import argparse
from pathlib import Path
from idx_manager import IdxManager


def init_full_workspace(workspace_root: str, from_existing: bool = False):
    root = Path(workspace_root).resolve()
    docs_root = root / "hs_dev_docs"
    mock_root = root / "mock"
    test_root = root / "test"

    print(f"[*] Initializing hs-dev workspace at: {root} (from_existing={from_existing})")

    # 1. 基础项目层级目录 (多端架构与产出收敛规划)
    base_dirs = [
        "apps", "packages", "deploy", "assets",
        "backend", "frontend", "linux", "mac", "windows", "android", "ios",
        "output/web_desktop", "output/app_desktop", "output/app_mobile/android",
        "output/app_mobile/ios", "output/server", "logs", "config", "scripts",
        "test/_00_e2e", "test/_01_method_test", "test/_02_integration_test",
        "test/_03_contract_test", "test/_04_regression_test", "test/_05_performance_test",
        "test/_06_security_test", "test/_07_compatibility_test", "test/_08_test_data",
        "mock/_01_mock_server/_01_route", "mock/_01_mock_server/_02_handler",
        "mock/_01_mock_server/_03_middleware", "mock/_01_mock_server/_04_config",
        "mock/_01_mock_server/_05_start_script",
        "mock/_02_mock_data/_01_dataset", "mock/_02_mock_data/_02_schema",
        "mock/_02_mock_data/_03_fixture",
        "mock/_03_scenario", "mock/_04_error_inject", "mock/_05_delay_inject",
        "mock/_06_test_profile"
    ]
    for d in base_dirs:
        (root / d).mkdir(parents=True, exist_ok=True)

    # 默认创建环境配置模板
    env_example = root / "config" / ".env.example"
    if not env_example.exists():
        env_example.write_text("# Global Environment Variables Template\n# PORT=8080\n# DATABASE_URL=\n", encoding="utf-8")

    # 2. hs_dev_docs 目录层级（一级功能 + 二级子功能严格按 _01_ 序号组织）
    doc_dirs = [
        # _00_project_foundation (基座)
        "_00_project_foundation/_01_dev_rule",
        "_00_project_foundation/_02_dictionary",
        "_00_project_foundation/_03_decision_record",
        "_00_project_foundation/_04_code_map",
        "_00_project_foundation/_05_doc_index",

        # _01_product_vision (功能一：愿景与定界)
        "_01_product_vision/_01_design_charter",
        "_01_product_vision/_02_phased_roadmap",
        "_01_product_vision/_03_business_plan",

        # _02_feature_spec (功能二：特性规格与原型契约)
        "_02_feature_spec/_01_human_prd",
        "_02_feature_spec/_02_vibe_spec",
        "_02_feature_spec/_03_prototype_html",
        "_02_feature_spec/_04_prototype_wireframe",

        # _03_architecture_design (功能三：技术架构与蓝图)
        "_03_architecture_design/_01_system_architecture",
        "_03_architecture_design/_02_pattern_clusters",
        "_03_architecture_design/_03_adapter_spec",

        # _04_engineering_contract (功能四：工程四要素详细契约)
        "_04_engineering_contract/_01_db_schema",
        "_04_engineering_contract/_02_interface_design",
        "_04_engineering_contract/_03_mock_contract",
        "_04_engineering_contract/_04_method_design",
        "_04_engineering_contract/_05_call_chain",

        # _05_task_orchestration (功能五：任务编排与上下文装载)
        "_05_task_orchestration/_01_task_brief",
        "_05_task_orchestration/_02_task_detail",
        "_05_task_orchestration/_03_task_context_pack",
        "_05_task_orchestration/_04_task_archive",

        # _06_dev_process (功能六：开发过程与治理记录)
        "_06_dev_process/_01_plan_log",
        "_06_dev_process/_02_change_log",
        "_06_dev_process/_03_verify_log",
        "_06_dev_process/_04_error_recovery/snapshots",
        "_06_dev_process/_05_tech_debt",
    ]
    for d in doc_dirs:
        (docs_root / d).mkdir(parents=True, exist_ok=True)

    # 3. 初始化所有核心 .idx 索引文件 (JSONL)
    print("[*] Initializing JSONL .idx indices...")

    # 全局根索引
    root_idx = docs_root / "_00_hs_dev_docs.idx"
    r_mgr = IdxManager(str(root_idx))
    r_mgr.init_idx("root", "hs_dev_docs")
    r_mgr.add_entry("domain_foundation", "项目基座与全局规范", "_00_project_foundation/_00_project_foundation.idx", auto_digest=False)
    r_mgr.add_entry("domain_vision", "产品愿景与分阶段定界", "_01_product_vision/_00_product_vision.idx", auto_digest=False)
    r_mgr.add_entry("domain_feature_spec", "特性详细规格与原型契约", "_02_feature_spec/_00_feature_spec.idx", auto_digest=False)
    r_mgr.add_entry("domain_architecture", "系统架构设计与模式集群", "_03_architecture_design/_00_architecture_design.idx", auto_digest=False)
    r_mgr.add_entry("domain_contract", "工程四要素详细契约", "_04_engineering_contract/_00_engineering_contract.idx", auto_digest=False)
    r_mgr.add_entry("domain_task", "任务编排与极速装配", "_05_task_orchestration/_00_task_orchestration.idx", auto_digest=False)
    r_mgr.add_entry("domain_process", "开发过程与治理审计", "_06_dev_process/_00_dev_process.idx", auto_digest=False)

    # 各一级功能域索引
    domains = [
        ("_00_project_foundation/_00_project_foundation.idx", "project_foundation", "_00_project_foundation"),
        ("_01_product_vision/_00_product_vision.idx", "product_vision", "_01_product_vision"),
        ("_02_feature_spec/_00_feature_spec.idx", "feature_spec", "_02_feature_spec"),
        ("_03_architecture_design/_00_architecture_design.idx", "architecture_design", "_03_architecture_design"),
        ("_04_engineering_contract/_00_engineering_contract.idx", "engineering_contract", "_04_engineering_contract"),
        ("_05_task_orchestration/_00_task_orchestration.idx", "task_orchestration", "_05_task_orchestration"),
        ("_06_dev_process/_00_dev_process.idx", "dev_process", "_06_dev_process"),
    ]
    for rel_idx, cat, r_name in domains:
        mgr = IdxManager(str(docs_root / rel_idx))
        mgr.init_idx(cat, r_name)

    # 二级子域索引（工程契约四要素）
    sub_contract_domains = [
        ("_04_engineering_contract/_01_db_schema/_00_db_schema.idx", "db_schema", "_01_db_schema"),
        ("_04_engineering_contract/_02_interface_design/_00_interface_design.idx", "interface_design", "_02_interface_design"),
        ("_04_engineering_contract/_04_method_design/_00_method_design.idx", "method_design", "_04_method_design"),
        ("_04_engineering_contract/_05_call_chain/_00_call_chain.idx", "call_chain", "_05_call_chain"),
    ]
    for rel_idx, cat, r_name in sub_contract_domains:
        mgr = IdxManager(str(docs_root / rel_idx))
        mgr.init_idx(cat, r_name)

    # 任务体系索引（位于 _05_task_orchestration）
    task_idx = docs_root / "_05_task_orchestration/_00_task.idx"
    t_mgr = IdxManager(str(task_idx))
    t_mgr.init_idx("task_active", "_05_task_orchestration")

    task_archive_idx = docs_root / "_05_task_orchestration/_00_task_archive.idx"
    ta_mgr = IdxManager(str(task_archive_idx))
    ta_mgr.init_idx("task_archive", "_05_task_orchestration")

    task_brief_idx = docs_root / "_05_task_orchestration/_01_task_brief/_00_task_brief.idx"
    tb_mgr = IdxManager(str(task_brief_idx))
    tb_mgr.init_idx("task_brief", "_01_task_brief")

    task_detail_idx = docs_root / "_05_task_orchestration/_02_task_detail/_00_task_detail.idx"
    td_mgr = IdxManager(str(task_detail_idx))
    td_mgr.init_idx("task_detail", "_02_task_detail")

    task_cp_idx = docs_root / "_05_task_orchestration/_03_task_context_pack/_00_context_pack.idx"
    tcp_mgr = IdxManager(str(task_cp_idx))
    tcp_mgr.init_idx("task_context_pack", "_03_task_context_pack")

    # Mock 索引
    mock_idx = mock_root / "_00_mock.idx"
    m_mgr = IdxManager(str(mock_idx))
    m_mgr.init_idx("mock_root", "mock")

    # 4. 生成统一术语词典模板（置于 _00_project_foundation/_02_dictionary）
    dict_file = docs_root / "_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml"
    if not dict_file.exists():
        tmpl_file = Path(__file__).resolve().parent.parent / "resources" / "templates" / "project_word.dict.yaml"
        if tmpl_file.exists():
            dict_file.write_text(tmpl_file.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            dict_file.write_text(
                "# 统一项目术语词典\nterms:\n  - term: \"示例实体\"\n    en_name: \"example_entity\"\n    abbr: \"ex_ent\"\n    scope: \"domain_model\"\n",
                encoding="utf-8"
            )

    # 4.1 若为已有项目反向重建 (from_existing)，探测技术栈并写入基线 ADR
    if from_existing:
        adr_file = docs_root / "_00_project_foundation/_03_decision_record/ADR_001_tech_baseline.md"
        if not adr_file.exists():
            detected_stacks = []
            if (root / "package.json").exists():
                detected_stacks.append("Node.js / JavaScript/TypeScript Ecosystem")
            if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
                detected_stacks.append("Python Ecosystem")
            if (root / "go.mod").exists():
                detected_stacks.append("Go Ecosystem")
            if (root / "pom.xml").exists() or (root / "build.gradle").exists():
                detected_stacks.append("JVM / Java/Kotlin Ecosystem")
            if (root / "Cargo.toml").exists():
                detected_stacks.append("Rust Ecosystem")

            stack_summary = ", ".join(detected_stacks) if detected_stacks else "Standard Polyglot Stack"
            adr_content = f"""# ADR-001: 存量项目技术栈基线固化

## [VIBE_CONTRACT] 机器执行契约
- 状态：ACCEPTED
- 场景：已有项目反向重建（intent=REVERSE）
- 锁定技术栈：{stack_summary}
- 执行禁令：禁止在未明确发起新选型 ADR 前破坏当前技术栈基线

## [HUMAN_RATIONALE]
通过 init_hs_dev_docs.py --from-existing 自动扫描已有工程并锁定技术栈基线，供后续四要素与索引构建对齐。
"""
            adr_file.write_text(adr_content, encoding="utf-8")
            print(f"[*] Generated reverse engineering baseline ADR: {adr_file.name}")

    # 5. 重建跨平台 SQLite 文档索引（FTS5 + LIKE，可重复执行）
    try:
        from doc_index_db import DocIndexDB

        db = DocIndexDB(root)
        try:
            db_info = db.rebuild()
        finally:
            db.close()
        print(
            f"[*] Doc index DB rebuilt: {db_info.get('inserted', 0)} rows, "
            f"fts={db_info.get('fts')}, path={db_info.get('db_path')}"
        )
    except Exception as ex:
        print(f"[WARN] Doc index DB rebuild skipped: {ex}")

    print("[SUCCESS] Complete hs-dev-skill file tree and JSONL indices initialized successfully!")
    print(
        "[NOTE] Cross-project preferences & tech learning: Path.home()/.hs-dev-skill "
        "(Windows/Linux/macOS) — run: python scripts/init_hs_global.py"
    )
    print(
        "[NOTE] Token-saving doc query: python scripts/doc_index_db.py --root . search --q <keywords>"
    )


def main():
    parser = argparse.ArgumentParser(description="Initialize hs-dev-docs directory structure")
    parser.add_argument("--root", default=".", help="Target workspace root directory")
    parser.add_argument("--from-existing", action="store_true", help="Reverse engineer and onboard an existing codebase")
    args = parser.parse_args()
    init_full_workspace(args.root, from_existing=args.from_existing)


if __name__ == "__main__":
    main()
