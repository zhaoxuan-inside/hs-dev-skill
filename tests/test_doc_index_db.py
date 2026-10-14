#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from doc_index_db import DocIndexDB, db_path_for_root  # noqa: E402
from idx_manager import IdxManager  # noqa: E402


class TestDocIndexDB(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        docs = self.root / "hs_dev_docs"
        product = docs / "_01_product_design" / "_02_product_design"
        product.mkdir(parents=True)
        prd = product / "demo_prd.md"
        prd.write_text(
            "# Demo PRD\n\n支付流程与账户冻结。\n\n## DoD\n- 超时触发补偿\n",
            encoding="utf-8",
        )
        idx = docs / "_01_product_design" / "_00_product_design.idx"
        mgr = IdxManager(str(idx))
        mgr.init_idx("product_design", "_01_product_design")
        mgr.add_entry(
            "demo_prd",
            "Demo PRD 支付",
            "_02_product_design/demo_prd.md",
            auto_digest=True,
        )

    def tearDown(self):
        try:
            self.tmp.cleanup()
        except PermissionError:
            # Windows: 偶发句柄延迟释放
            pass

    def test_db_path_under_docs_index(self):
        p = db_path_for_root(self.root)
        self.assertTrue(str(p).replace("\\", "/").endswith(
            "hs_dev_docs/_00_project/_18_doc_index/doc_index.sqlite"
        ))

    def test_rebuild_search_slice_cross_platform_paths(self):
        db = DocIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertTrue(info["ok"])
            self.assertGreaterEqual(info["inserted"], 1)
            self.assertTrue(Path(info["db_path"]).is_file())

            # 中文 LIKE 回退；内容文档应排在 idx 之前
            zh = db.search("支付", limit=5)
            self.assertTrue(zh["ok"])
            self.assertGreaterEqual(zh["count"], 1)
            hit = next(
                (r for r in zh["results"] if r["path"].endswith("demo_prd.md")),
                zh["results"][0],
            )
            self.assertTrue(hit["path"].endswith("demo_prd.md"))
            self.assertIn("hs_dev_docs/", hit["path"])

            # ASCII / FTS 或 LIKE
            en = db.search("Demo", limit=5)
            self.assertTrue(en["ok"])
            self.assertGreaterEqual(en["count"], 1)

            path = hit["path"]
            sl = db.slice(path, start=1, end=3, max_lines=10)
            self.assertTrue(sl["ok"])
            self.assertEqual(sl["start"], 1)
            self.assertIn("Demo PRD", sl["text"])
            # 路径一律 posix 相对根
            self.assertNotIn("\\", sl["path"])

            got = db.get(path)
            self.assertTrue(got["ok"])
            self.assertIn("支付", got["result"]["summary"] + got["result"]["title"])
        finally:
            db.close()

    def test_cli_search_json(self):
        from doc_index_db import main

        db = DocIndexDB(self.root)
        try:
            db.rebuild()
        finally:
            db.close()

        code = main(["--root", str(self.root), "stats"])
        self.assertEqual(code, 0)

    def test_method_search_anti_explosion(self):
        docs = self.root / "hs_dev_docs"
        method_dir = docs / "_06_method_design" / "_01_privacy"
        method_dir.mkdir(parents=True, exist_ok=True)
        m_file = method_dir / "_01_mask_phone_design.md"
        m_file.write_text(
            "# 方法设计规范：mask_phone\n\n"
            "## 1. 基础与位置画像 (Location & Profile)\n"
            "- **所属层次**：领域核心层\n"
            "- **所属模块**：`privacy`\n"
            "- **文件路径**：`src/utils/privacy.py`\n"
            "- **代码定位**：第 `20` 行，共 `15` 行（行范围：`20-34`）\n"
            "- **方法签名**：`str mask_phone(phone: str, country_code: str = '')`\n"
            "- **方法类型**：`TRANSFORM`\n"
            "- **功能描述**：手机号脱敏掩码，保留前3后4位\n\n"
            "## 2. 特征与属性契约 (Attributes Contract)\n"
            "- **改动敏感度**：`LOW`\n"
            "- **副作用类型**：`NONE`\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            db.rebuild()
            stats = db.stats()
            self.assertGreaterEqual(stats["methods"], 1)

            # 语义 / 关键词检索
            res = db.method_search("脱敏")
            self.assertTrue(res["ok"])
            self.assertEqual(res["count"], 1)
            candidate = res["candidates"][0]
            self.assertEqual(candidate["name"], "mask_phone")
            self.assertEqual(candidate["archetype"], "TRANSFORM")
            self.assertEqual(candidate["lines"], "20-34")
            self.assertIn("REUSE_OR_EXTEND", candidate["action_recommendation"])

            # 英文符号查询
            res_en = db.method_search("mask_phone", archetype="TRANSFORM")
            self.assertTrue(res_en["ok"])
            self.assertEqual(res_en["count"], 1)

            # 空查询或无匹配
            res_none = db.method_search("不存在的复杂计算方法XYZ")
            self.assertEqual(res_none["count"], 0)
            self.assertIn("No matching method found", res_none["guidance"])
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
