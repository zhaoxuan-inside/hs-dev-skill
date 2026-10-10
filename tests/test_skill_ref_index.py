import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from skill_ref_index import SkillRefIndex, skill_root_from_here


class TestSkillRefIndex(unittest.TestCase):
    def setUp(self):
        self.skill_root = skill_root_from_here()
        self.assertTrue((self.skill_root / "SKILL.md").is_file())
        self.assertTrue((self.skill_root / "references").is_dir())
        self.temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        # Use a copy-like isolated cache under temp by pointing skill_root to real
        # refs but overriding db via temporary skill layout
        self.work = Path(self.temp.name) / "skill"
        self.work.mkdir()
        (self.work / "SKILL.md").write_text("---\nname: hs-dev-skill\n---\n", encoding="utf-8")
        ref_src = self.skill_root / "references"
        ref_dst = self.work / "references"
        ref_dst.mkdir()
        for name in (
            "_index.md",
            "right_sizing.md",
            "api_engineering.md",
            "frontend_craft.md",
            "design_md.md",
            "dev_paradigm.md",
            "ddd_design.md",
            "frontend_arch.md",
            "backend_arch.md",
            "token_budget.md",
        ):
            src = ref_src / name
            if src.is_file():
                (ref_dst / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_rebuild_and_search_scenarios(self):
        db = SkillRefIndex(self.work)
        payload = db.rebuild()
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(payload["inserted"], 4)

        db = SkillRefIndex(self.work)
        found = db.search(scenario="幂等", limit=8)
        self.assertTrue(found["ok"])
        paths = [h["path"] for h in found["hits"]]
        self.assertTrue(
            any("api_engineering" in p for p in paths),
            msg=json.dumps(found, ensure_ascii=False),
        )

        ui = db.search(q="UI", limit=8)
        self.assertTrue(any("frontend_craft" in h["path"] for h in ui["hits"]))

        design = db.search(q="DESIGN.md", limit=8)
        self.assertTrue(
            any("design_md" in h["path"] for h in design["hits"]),
            msg=json.dumps(design, ensure_ascii=False),
        )

        para = db.search(q="范式", limit=8)
        self.assertTrue(
            any("dev_paradigm" in h["path"] for h in para["hits"]),
            msg=json.dumps(para, ensure_ascii=False),
        )

        ddd = db.search(q="DDD", limit=8)
        self.assertTrue(
            any("ddd_design" in h["path"] for h in ddd["hits"]),
            msg=json.dumps(ddd, ensure_ascii=False),
        )

        fsd = db.search(q="FSD", limit=8)
        self.assertTrue(
            any("frontend_arch" in h["path"] for h in fsd["hits"]),
            msg=json.dumps(fsd, ensure_ascii=False),
        )

        size = db.search(tag="change_size", limit=5)
        self.assertTrue(any("right_sizing" in h["path"] for h in size["hits"]))

        stats = db.stats()
        self.assertGreaterEqual(stats["count"], 4)
        db.close()

    def test_skill_root_detection(self):
        root = skill_root_from_here()
        self.assertEqual(root.name, "hs-dev-skill")


if __name__ == "__main__":
    unittest.main()
