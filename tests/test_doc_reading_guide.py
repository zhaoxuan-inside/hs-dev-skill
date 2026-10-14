#!/usr/bin/env python3
"""
test_doc_reading_guide.py
验证项目文档阅读说明模板、自动生成逻辑、直接索引导航、跨 Agent 契约及 CLI 指令。
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from init_hs_dev_docs import init_full_workspace, generate_doc_reading_guide  # noqa: E402
from idx_manager import IdxManager  # noqa: E402
from doc_index_db import DocIndexDB  # noqa: E402
from verify_consistency import ConsistencyVerifier  # noqa: E402


class TestDocReadingGuide(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)

    def tearDown(self):
        try:
            self.tmp.cleanup()
        except PermissionError:
            pass

    def test_template_structure_and_guardrails(self):
        tmpl_file = ROOT / "resources" / "templates" / "hs_dev_docs" / "doc_reading_guide_template.md"
        self.assertTrue(tmpl_file.exists(), "Template file must exist")
        content = tmpl_file.read_text(encoding="utf-8")

        # 检查关键要素
        self.assertIn("[VIBE_CONTRACT]", content)
        self.assertIn("vibe_index_contract:", content)
        self.assertIn("agent_cli_shortcuts:", content)
        self.assertIn("三层数据收敛漏斗", content)
        self.assertIn("全功能域直接索引导航目录表", content)
        self.assertIn("Agent Query Playbook", content)
        self.assertIn("BUILD (从零构建)", content)
        self.assertIn("EXPLORE (只读理解)", content)
        self.assertIn("FIX (Bug修复)", content)
        self.assertIn("REFACTOR (等价重构)", content)
        self.assertIn("RESUME (任务续做)", content)
        self.assertIn("Ubiquitous Language", content)
        self.assertIn("Symbol Anchor", content)

    def test_generate_in_initialized_workspace(self):
        init_full_workspace(str(self.root))
        guide_file = self.root / "hs_dev_docs" / "README.md"
        self.assertTrue(guide_file.exists(), "hs_dev_docs/README.md must be generated")

        text = guide_file.read_text(encoding="utf-8")
        self.assertIn("项目文档阅读说明与全局索引导航", text)
        self.assertIn("[VIBE_CONTRACT]", text)
        self.assertIn("agent_cli_shortcuts:", text)

        # 校验 _00_hs_dev_docs.idx 注册
        root_idx = self.root / "hs_dev_docs" / "_00_hs_dev_docs.idx"
        mgr = IdxManager(str(root_idx))
        entry_ids = [e["id"] for e in mgr.entries]
        self.assertIn("doc_reading_guide", entry_ids)

        valid, errs = mgr.verify()
        self.assertTrue(valid, f"Index verification failed: {errs}")

        # 校验子目录说明
        sub_readme = self.root / "hs_dev_docs" / "_00_project_foundation" / "_05_doc_index" / "README.md"
        self.assertTrue(sub_readme.exists())

        # 校验 ConsistencyVerifier 通过
        verifier = ConsistencyVerifier(str(self.root), strict=True)
        self.assertTrue(verifier.check_all())

    def test_dynamic_key_documents_aggregation(self):
        init_full_workspace(str(self.root))

        # 模拟生成具体设计资产
        adr_dir = self.root / "hs_dev_docs" / "_00_project_foundation" / "_03_decision_record"
        (adr_dir / "ADR_002_cache_strategy.md").write_text("# ADR-002: Redis 缓存策略\n", encoding="utf-8")

        prd_dir = self.root / "hs_dev_docs" / "_02_feature_spec" / "_01_human_prd"
        (prd_dir / "user_auth_prd.md").write_text("# 用户认证 PRD\n", encoding="utf-8")

        # 重新生成阅读说明
        generate_doc_reading_guide(str(self.root), project_name="my_test_app")
        guide_file = self.root / "hs_dev_docs" / "README.md"
        text = guide_file.read_text(encoding="utf-8")

        self.assertIn("my_test_app", text)
        self.assertIn("当前项目已归档关键契约与文档索引", text)
        self.assertIn("ADR_002_cache_strategy.md", text)
        self.assertIn("user_auth_prd.md", text)

    def test_doc_index_db_generate_guide_subcommand(self):
        init_full_workspace(str(self.root))
        db = DocIndexDB(self.root)
        db.close()

        # 测试 python scripts/doc_index_db.py --root . generate-guide
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "doc_index_db.py"),
            "--root",
            str(self.root),
            "generate-guide",
            "--project-name",
            "cli_test_project",
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertTrue(data.get("ok"))
        self.assertTrue(Path(data["guide_path"]).exists())

        # 验证 SQLite 搜索能命中
        db2 = DocIndexDB(self.root)
        try:
            results = db2.search("阅读说明")
            self.assertTrue(results.get("ok"))
            self.assertGreaterEqual(results.get("count", 0), 1)
            paths = [r["path"] for r in results.get("results", [])]
            self.assertTrue(any("README.md" in p for p in paths))
        finally:
            db2.close()


if __name__ == "__main__":
    unittest.main()
