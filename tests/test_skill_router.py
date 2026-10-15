import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from skill_router import load_registry, route, validate_registry
from skill_ref_index import SkillRefIndex


class TestSkillRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.registry = load_registry(cls.root)

    def test_bundle_has_complete_routes_and_unique_reference_owners(self):
        validate_registry(self.root, self.registry)
        self.assertEqual({e["axis"] for e in self.registry["skills"]}, {"process", "functional"})

    def test_build_uses_current_phase_and_only_touched_domains(self):
        plan = route(self.root, self.registry, "BUILD", 3, ["backend", "frontend", "backend"])
        self.assertEqual(plan["process_skill"]["id"], "hs-dev-design")
        self.assertEqual([e["id"] for e in plan["functional_skills"]],
                         ["hs-dev-backend", "hs-dev-frontend"])
        self.assertFalse(plan["stage_accepted"])
        for phase, expected in [(0, "hs-dev-discovery"), (4, "hs-dev-planning"),
                                (5, "hs-dev-implementation"), (6, "hs-dev-acceptance")]:
            with self.subTest(phase=phase):
                self.assertEqual(route(self.root, self.registry, "BUILD", phase)["process_skill"]["id"], expected)

    def test_readonly_analysis_never_becomes_delivery(self):
        plan = route(self.root, self.registry, "EXPLORE", domains=["testing"])
        self.assertTrue(plan["read_only"])
        self.assertEqual(plan["work_mode"], "READONLY")
        self.assertEqual(plan["process_skill"]["id"], "hs-dev-exploration")
        for event in ("change", "acceptance"):
            with self.assertRaises(ValueError):
                route(self.root, self.registry, "EXPLORE", event=event)

    def test_resume_restores_context_before_selecting_build_phase(self):
        plan = route(self.root, self.registry, "RESUME")
        self.assertEqual(plan["process_skill"]["id"], "hs-dev-continuity")
        self.assertTrue(plan["requires_context_restore"])
        self.assertIsNone(plan["phase"])
        self.assertIsNone(plan["work_mode"])
        self.assertEqual(plan["functional_skills"], [])

    def test_existing_engineering_intents_do_not_restart_product_discovery(self):
        for intent, expected in [("FIX", "hs-dev-debugging"), ("REFACTOR", "hs-dev-refactoring"),
                                 ("REVERSE", "hs-dev-reverse")]:
            with self.subTest(intent=intent):
                self.assertEqual(route(self.root, self.registry, intent)["process_skill"]["id"], expected)

    def test_change_and_acceptance_are_events_on_existing_goal(self):
        for event, expected in [("change", "hs-dev-continuity"), ("acceptance", "hs-dev-acceptance")]:
            plan = route(self.root, self.registry, "BUILD", 3, ["backend"], event)
            self.assertEqual(plan["intent"], "BUILD")
            self.assertEqual(plan["phase"], 3)
            self.assertEqual(plan["process_skill"]["id"], expected)
            self.assertFalse(plan["stage_accepted"])

    def test_invalid_inputs_do_not_silently_guess(self):
        for kwargs in [dict(intent="BUILD"), dict(intent="BUILD", phase=8),
                       dict(intent="FIX", phase=0), dict(intent="UNKNOWN"),
                       dict(intent="BUILD", phase=5, domains=["unknown"])]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                route(self.root, self.registry, **kwargs)

    def test_broken_and_duplicate_registry_entries_fail(self):
        for mutation in ("missing", "duplicate", "escape", "wrong_axis", "unregistered", "default_domain"):
            registry = copy.deepcopy(self.registry)
            if mutation == "missing":
                registry["skills"][0]["path"] = "skills/missing/SKILL.md"
            elif mutation == "duplicate":
                registry["skills"].append(registry["skills"][0])
            elif mutation == "escape":
                registry["skills"][0]["path"] = "../SKILL.md"
            elif mutation == "wrong_axis":
                registry["phases"]["0"] = registry["domains"]["backend"]
            elif mutation == "unregistered":
                registry["skills"].pop()
            else:
                registry["default_domains"]["0"] = ["unknown"]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate_registry(self.root, registry)

    def test_relocated_install_works_from_unrelated_project_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            installed = base / "installed" / "hs-dev-skill"
            for name in ("skills", "references", "scripts"):
                shutil.copytree(self.root / name, installed / name, ignore=shutil.ignore_patterns("__pycache__"))
            (installed / "resources").mkdir()
            shutil.copy2(self.root / "resources" / "skill_routes.json", installed / "resources" / "skill_routes.json")
            shutil.copy2(self.root / "SKILL.md", installed / "SKILL.md")
            project = base / "project"
            project.mkdir()
            cmd = [sys.executable, str(installed / "scripts" / "skill_router.py"),
                   "route", "--intent", "FIX", "--domains", "frontend"]
            result = subprocess.run(cmd, cwd=project, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(plan["bundle_root"], str(installed.resolve()))
            self.assertTrue(Path(plan["process_skill"]["absolute_path"]).is_file())
            self.assertEqual(list(project.iterdir()), [])

    def test_reference_search_can_find_child_entrypoints(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(self.root / "references", root / "references")
            shutil.copytree(self.root / "skills", root / "skills")
            index = SkillRefIndex(root)
            try:
                index.rebuild()
                hits = index.search(q="hs-dev-debugging", limit=5)["hits"]
                self.assertTrue(any(h["path"] == "skills/hs-dev-debugging/SKILL.md" for h in hits), hits)
                hits = index.search(q="幂等", limit=8)["hits"]
                self.assertTrue(any(h["path"] == "references/api_engineering.md" for h in hits), hits)
            finally:
                index.close()


if __name__ == "__main__":
    unittest.main()
