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


if __name__ == "__main__":
    unittest.main()
