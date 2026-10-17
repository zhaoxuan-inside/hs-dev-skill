import copy
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from read_cache import inspect, load
from skill_ref_index import SkillRefIndex
from skill_router import load_registry, validate_registry
from template_parts import main as render_main, render_template


class TestDocumentSections(unittest.TestCase):
    root = Path(__file__).resolve().parent.parent

    def test_all_sections_are_owned_and_reachable_from_entry(self):
        manifest = json.loads((self.root / "resources/reference_sections.json").read_text(encoding="utf-8"))
        validate_registry(self.root, load_registry(self.root))
        for group in manifest["references"]:
            entry = self.root / group["entry"]
            content = entry.read_text(encoding="utf-8")
            self.assertIn("HS_SECTION_INDEX", content)
            for section in group["sections"]:
                child = self.root / section["path"]
                self.assertTrue(child.is_file(), child)
                self.assertIn(child.name, content)
                self.assertLess(child.stat().st_size, 12000, child)
                text = child.read_text(encoding="utf-8")
                # Check actual rebased local file links, not just their labels.
                for target in re.findall(r"\]\(([^\s)]+)\)", text):
                    if re.match(r"^(?:[a-zA-Z][\w+.-]*:|/|#)", target):
                        continue
                    self.assertTrue((child.parent / target.split("#")[0]).is_file(),
                                    "{} -> {}".format(child, target))

    def test_missing_nested_reference_is_rejected(self):
        registry = copy.deepcopy(load_registry(self.root))
        registry["skills"][0]["references"].append("references/lifecycle/missing.md")
        with self.assertRaisesRegex(ValueError, "Missing bundle file"):
            validate_registry(self.root, registry)

    def test_search_finds_a_business_section_directly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(self.root / "references", root / "references")
            index = SkillRefIndex(root)
            try:
                index.rebuild()
                paths = [row["path"] for row in index.search(q="P4 移动客户端", limit=3)["hits"]]
                self.assertIn("references/project_types/mobile.md", paths)
            finally:
                index.close()

    def test_editing_one_business_section_preserves_other_cached_section(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [root / "task_planning.md", root / "implementation.md"]
            for path in paths:
                shutil.copy2(self.root / "references/lifecycle" / path.name, path)
            state = {"schema_version": 1, "entries": {}}
            for path in paths:
                load(state, path)
            paths[0].write_text("changed task planning", encoding="utf-8")
            self.assertEqual(inspect(state, paths[0], verify=True)["action"], "RELOAD")
            self.assertEqual(inspect(state, paths[1], verify=True)["action"], "REUSE")

    def test_template_include_failures_do_not_silently_drop_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entry = root / "entry.md"
            entry.write_text("<!-- HS_TEMPLATE_INCLUDE: missing.md -->\n", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                render_template(entry)
            entry.write_text("<!-- HS_TEMPLATE_INCLUDE: entry.md -->\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cycle"):
                render_template(entry)
            entry.write_text("<!-- HS_TEMPLATE_INCLUDE: ../outside.md -->\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes"):
                render_template(entry)

    def test_render_command_writes_complete_template_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "prototype.md"
            source = self.root / "resources/templates/product_design/prototype_template.md"
            command = ["--path", str(source), "--output", str(output)]
            self.assertEqual(render_main(command), 0)
            rendered = output.read_text(encoding="utf-8")
            for text in ("正常数据态", "空白引导态", "数据加载态", "异常错误态", "开发者可视化确认签收单"):
                self.assertIn(text, rendered)
            self.assertNotIn("HS_TEMPLATE_INCLUDE", rendered)
            self.assertEqual(render_main(command), 1)
            self.assertEqual(output.read_text(encoding="utf-8"), rendered)


if __name__ == "__main__":
    unittest.main()
