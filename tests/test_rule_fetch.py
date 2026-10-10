import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from rule_fetch import (
    load_catalog,
    list_sources,
    resolve_source,
    search_cache,
    search_catalog,
    skill_root_from_here,
)


class TestRuleFetch(unittest.TestCase):
    def setUp(self):
        self.skill_root = skill_root_from_here()
        self.catalog = load_catalog(self.skill_root)
        self.assertTrue(self.catalog.get("sources"), msg="rule_sources.yaml missing/empty")
        self.temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.cache = Path(self.temp.name) / "rule_cache"
        self.cache.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_list_and_search_catalog(self):
        listed = list_sources(self.catalog)
        self.assertTrue(listed["ok"])
        ids = {s["id"] for s in listed["sources"]}
        self.assertIn("local.frontend.core", ids)
        self.assertIn("vercel.react-rules", ids)

        found = search_catalog(self.catalog, "幂等", limit=5)
        self.assertTrue(any("api" in str(h["id"]) for h in found["hits"]))

        react = search_catalog(self.catalog, "React", limit=5)
        self.assertTrue(any("vercel" in str(h["id"]) or "frontend" in str(h["id"]) for h in react["hits"]))

    def test_resolve_local(self):
        out = resolve_source(self.skill_root, self.catalog, "local.api.core", cache_root=self.cache)
        self.assertTrue(out["ok"], msg=json.dumps(out, ensure_ascii=False))
        self.assertTrue(Path(out["path"]).is_file())
        self.assertIn("api_engineering", out["path"].replace("\\", "/"))

    def test_github_tree_requires_rule(self):
        out = resolve_source(self.skill_root, self.catalog, "vercel.react-rules", cache_root=self.cache)
        self.assertFalse(out["ok"])
        self.assertIn("rule", out.get("error", "").lower() + out.get("hint", "").lower())

    def test_resolve_remote_uses_cache_without_network(self):
        rule_dir = self.cache / "vercel.react-rules"
        rule_dir.mkdir(parents=True)
        body = rule_dir / "async-parallel.md"
        meta = rule_dir / "async-parallel.meta.json"
        body.write_text("# async-parallel\nUse Promise.all\n", encoding="utf-8")
        meta.write_text(
            json.dumps({"fetched_epoch": 10**12, "id": "vercel.react-rules"}),
            encoding="utf-8",
        )
        with patch("rule_fetch._download") as dl:
            out = resolve_source(
                self.skill_root,
                self.catalog,
                "vercel.react-rules",
                rule="async-parallel",
                cache_root=self.cache,
            )
            dl.assert_not_called()
        self.assertTrue(out["ok"])
        self.assertTrue(out.get("cached"))

    def test_search_cache(self):
        body = self.cache / "demo.md"
        body.write_text("alpha\nIdempotency-Key must be stable\nbeta\n", encoding="utf-8")
        hits = search_cache(self.cache, "idempotency", limit=5)
        self.assertTrue(hits["ok"])
        self.assertEqual(len(hits["hits"]), 1)
        self.assertEqual(hits["hits"][0]["line"], 2)


if __name__ == "__main__":
    unittest.main()
