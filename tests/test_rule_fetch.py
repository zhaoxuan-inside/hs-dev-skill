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
        self.assertIn("local.backend.arch", ids)
        self.assertIn("local.dev.paradigm", ids)
        self.assertIn("local.ddd.design", ids)
        self.assertIn("local.frontend.arch", ids)
        self.assertIn("fsd.skill", ids)
        self.assertIn("kgrzybek.modular-monolith", ids)
        self.assertIn("vercel.react-rules", ids)
        self.assertIn("antislop.core", ids)
        self.assertIn("lottie.motion-design", ids)
        self.assertIn("vercel.web-interface", ids)
        self.assertIn("educlopez.ui-craft", ids)
        self.assertIn("local.design.md", ids)
        self.assertIn("voltagent.design-md", ids)
        self.assertIn("google.design-md-spec", ids)
        self.assertIn("bergside.design-skills", ids)
        self.assertIn("bergside.design-skill-md", ids)
        self.assertIn("wshobson.architecture-patterns", ids)
        self.assertIn("clean-arch.skill", ids)
        self.assertIn("wshobson.saga-orchestration", ids)
        self.assertIn("ciembor.architecture-books", ids)
        self.assertIn("muthub.c4designer", ids)
        self.assertIn("muthub.adr-scribe", ids)

        found = search_catalog(self.catalog, "幂等", limit=5)
        self.assertTrue(any("api" in str(h["id"]) for h in found["hits"]))

        react = search_catalog(self.catalog, "React", limit=5)
        self.assertTrue(any("vercel" in str(h["id"]) or "frontend" in str(h["id"]) for h in react["hits"]))

        slop = search_catalog(self.catalog, "anti-slop", limit=5)
        self.assertTrue(any("antislop" in str(h["id"]) for h in slop["hits"]))

        design = search_catalog(self.catalog, "DESIGN.md", limit=8)
        self.assertTrue(any("voltagent" in str(h["id"]) or "design" in str(h["id"]) for h in design["hits"]))

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

    def test_design_md_nested_file_template(self):
        fake = "# DESIGN.md\nStripe-like tokens\n"
        with patch("rule_fetch._download", return_value=(True, fake, "https://example.test/stripe", "")) as dl:
            out = resolve_source(
                self.skill_root,
                self.catalog,
                "voltagent.design-md",
                rule="stripe",
                force=True,
                cache_root=self.cache,
            )
        self.assertTrue(out["ok"], msg=json.dumps(out, ensure_ascii=False))
        self.assertIn("design-md/stripe/DESIGN.md", dl.call_args[0][0][0])
        self.assertTrue(Path(out["path"]).is_file())

    def test_bergside_aesthetic_file_template(self):
        fake = "# DESIGN.md\nEditorial aesthetic\n"
        with patch("rule_fetch._download", return_value=(True, fake, "https://example.test/editorial", "")) as dl:
            out = resolve_source(
                self.skill_root,
                self.catalog,
                "bergside.design-skills",
                rule="editorial",
                force=True,
                cache_root=self.cache,
            )
        self.assertTrue(out["ok"], msg=json.dumps(out, ensure_ascii=False))
        self.assertIn("skills/editorial/DESIGN.md", dl.call_args[0][0][0])

    def test_resolve_local_design_md(self):
        out = resolve_source(self.skill_root, self.catalog, "local.design.md", cache_root=self.cache)
        self.assertTrue(out["ok"], msg=json.dumps(out, ensure_ascii=False))
        self.assertIn("design_md", out["path"].replace("\\", "/"))

    def test_resolve_local_backend_arch(self):
        out = resolve_source(self.skill_root, self.catalog, "local.backend.arch", cache_root=self.cache)
        self.assertTrue(out["ok"], msg=json.dumps(out, ensure_ascii=False))
        self.assertIn("backend_arch", out["path"].replace("\\", "/"))

    def test_resolve_local_paradigm_ddd_and_frontend_arch(self):
        para = resolve_source(self.skill_root, self.catalog, "local.dev.paradigm", cache_root=self.cache)
        self.assertTrue(para["ok"], msg=json.dumps(para, ensure_ascii=False))
        self.assertIn("dev_paradigm", para["path"].replace("\\", "/"))
        ddd = resolve_source(self.skill_root, self.catalog, "local.ddd.design", cache_root=self.cache)
        self.assertTrue(ddd["ok"], msg=json.dumps(ddd, ensure_ascii=False))
        self.assertIn("ddd_design", ddd["path"].replace("\\", "/"))
        fe = resolve_source(self.skill_root, self.catalog, "local.frontend.arch", cache_root=self.cache)
        self.assertTrue(fe["ok"], msg=json.dumps(fe, ensure_ascii=False))
        self.assertIn("frontend_arch", fe["path"].replace("\\", "/"))
        para_hits = search_catalog(self.catalog, "范式", limit=8)
        self.assertTrue(any(h["id"] == "local.dev.paradigm" for h in para_hits["hits"]))
        ddd_hits = search_catalog(self.catalog, "DDD", limit=8)
        self.assertTrue(any(h["id"] == "local.ddd.design" for h in ddd_hits["hits"]))

    def test_ciembor_book_file_template(self):
        fake = "# Clean Architecture mini\n"
        with patch("rule_fetch._download", return_value=(True, fake, "https://example.test/ca", "")) as dl:
            out = resolve_source(
                self.skill_root,
                self.catalog,
                "ciembor.architecture-books",
                rule="clean-architecture",
                force=True,
                cache_root=self.cache,
            )
        self.assertTrue(out["ok"], msg=json.dumps(out, ensure_ascii=False))
        self.assertIn("clean-architecture/clean-architecture.mini.md", dl.call_args[0][0][0])

        arch = search_catalog(self.catalog, "DDD", limit=8)
        self.assertTrue(
            any(
                h["id"] == "local.ddd.design"
                or "backend" in str(h["id"])
                or "wshobson" in str(h["id"])
                or "ciembor" in str(h["id"])
                for h in arch["hits"]
            ),
            msg=json.dumps(arch, ensure_ascii=False),
        )


if __name__ == "__main__":
    unittest.main()
