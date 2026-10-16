#!/usr/bin/env python3
import shutil
import sys
import logging
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from global_index_db import GlobalIndexDB  # noqa: E402


class TestGlobalIndexDB(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        (self.root / "tech_learning").mkdir(parents=True)
        shutil.copy2(
            ROOT / "resources" / "templates" / "hs_global" / "tag_synonyms.yaml",
            self.root / "tag_synonyms.yaml",
        )
        shutil.copy2(
            ROOT / "resources" / "templates" / "hs_global" / "preferences.yaml",
            self.root / "preferences.yaml",
        )
        note = self.root / "tech_learning" / "nginx_notes.md"
        note.write_text(
            "# 技术学习笔记：Nginx\n\n"
            "- **标签**：`后端`, `组件`, `反向代理`, `正向代理`, `WEB服务器`\n\n"
            "## 1. 为何需要学\n\n用作反向代理与静态资源网关。\n",
            encoding="utf-8",
        )

    def tearDown(self):
        try:
            self.tmp.cleanup()
        except PermissionError:
            logging.debug("tearDown: optional operation failed; retaining fallback", exc_info=True)

    def test_tag_search_finds_nginx(self):
        db = GlobalIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertTrue(info["ok"])
            self.assertGreaterEqual(info["inserted"], 1)

            by_tag = db.search(tag="反向代理", limit=5)
            self.assertTrue(by_tag["ok"])
            self.assertGreaterEqual(by_tag["count"], 1)
            keys = {r["entry_key"] for r in by_tag["results"]}
            self.assertIn("note:nginx", keys)
            tags = by_tag["results"][0]["tags"]
            self.assertTrue(any("反向代理" in t or t == "反向代理" for t in tags))

            by_q = db.search(query="nginx", limit=5)
            self.assertGreaterEqual(by_q["count"], 1)

            # 同义词展开：只搜「负载均衡」也应命中 nginx（来自 synonyms）
            by_syn = db.search(tag="负载均衡", limit=5)
            self.assertGreaterEqual(by_syn["count"], 1)
            self.assertIn("note:nginx", {r["entry_key"] for r in by_syn["results"]})

            prefs = db.search(query="api", kind="preference", limit=5)
            self.assertTrue(prefs["ok"])

            tag_list = db.tags()
            self.assertGreaterEqual(tag_list["count"], 1)
        finally:
            db.close()

    def test_paths_are_relative_under_global_root(self):
        db = GlobalIndexDB(self.root)
        try:
            db.rebuild()
            hit = db.search(tag="后端", kind="note", limit=1)
            self.assertEqual(hit["results"][0]["path"], "tech_learning/nginx_notes.md")
            self.assertTrue(hit["results"][0]["abs_path"].replace("\\", "/").endswith(
                "tech_learning/nginx_notes.md"
            ))
        finally:
            db.close()

    def test_auto_extract_tags_from_body_without_explicit(self):
        # 无显式标签行，仅正文含「反向代理」也应抽到特性标签并被检索到
        note = self.root / "tech_learning" / "gateway_notes.md"
        note.write_text(
            "# 网关实践\n\n部署时使用反向代理把流量转到上游。\n",
            encoding="utf-8",
        )
        db = GlobalIndexDB(self.root)
        try:
            db.rebuild()
            hit = db.search(tag="反向代理", kind="note", limit=10)
            keys = {r["entry_key"] for r in hit["results"]}
            self.assertIn("note:gateway", keys)

            suggested = db.extract_feature_tags(
                "使用反向代理与 WEB服务器",
                title="网关",
                slug="gateway",
            )
            self.assertTrue(any(t in suggested for t in ("反向代理", "nginx", "WEB服务器", "web服务器")))
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
