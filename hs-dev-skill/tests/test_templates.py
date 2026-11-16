"""Output contracts must reject paper completion and preserve unrelated sections."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import json
import re
import subprocess
from urllib.parse import unquote
import zipfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from hsdev import templates
from hsdev.knowledge import register_source, source_state


class TemplateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        file = self.root / "hs-dev/deliveries/d1/data-rule.md"
        file.parent.mkdir(parents=True)
        file.write_text("# Order schema\norder_id is required and uniquely enforced in storage.\n")
        register_source(self.root, {"id": "data-rule-v1", "kind": "document", "path": "hs-dev/deliveries/d1/data-rule.md",
                        "version": "1.0.0", "scope": "order-v1", "claim_type": "requirement",
                        "observed_at": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()})

    def validate_sources(self, ids):
        if not isinstance(ids, list) or not ids:
            raise ValueError("Concrete evidence source references required")
        for id in ids:
            state = source_state(self.root, id)
            if not state["usable"] or state["scope"] not in {"order-v1", "*"}:
                raise ValueError("Source is missing, unusable, or outside task scope")

    def record(self):
        spec = templates.contract("E1", "E1.O1")["outputs"][0]
        answers = ["order_id为必填字符串；不存在与空字符串均拒绝，未设置应用或存储默认值。",
                   "order_id唯一性由存储唯一约束保证；客户端重复提示只改善体验，不能代替并发约束。",
                   "未核验真实并发时不声称唯一约束有效；保留数据库并发写入检查作为后续动作。"]
        return {"id": "E1.O1", "scope": "order-v1",
                "answers": [{"id": question["id"], "answer": answers[i], "status": "supported", "source_ids": ["data-rule-v1"]}
                            for i, question in enumerate(spec["questions"])],
                "limitations": "本次核验字段定义与有效规则，尚未执行真实数据库的并发写入验证。",
                "acceptance": [{"id": check["id"], "status": "supported",
                                "judgment": "字段定义与已登记规则使用一致的必填字符串语义。" if i == 0 else "存储约束是唯一性保证的责任位置，客户端提示没有被认作并发验证。",
                                "source_ids": ["data-rule-v1"]}
                               for i, check in enumerate(spec["acceptance_checks"])]}

    def test_catalog_has_all_nine_stages_38_activities_and_114_outputs(self):
        result = templates.verify_catalog()
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual((result["stages"], result["activities"], result["outputs"]), (9, 38, 114))
        for stage in templates.catalog()["stages"]:
            self.assertIn(stage["questioning"], {"exploratory", "focused", "exception"})
            for activity in stage["activities"]:
                contract = templates.contract(activity["id"])
                self.assertTrue(contract["minimum"])
                self.assertTrue(contract["risks"])
                for output in contract["outputs"]:
                    self.assertTrue(output["questions"])
                    self.assertTrue(output["evidence"])
                    self.assertTrue(output["acceptance"])
                    self.assertEqual(len({q["id"] for q in output["questions"]}), len(output["questions"]))
                    for risk in contract["risks"]:
                        self.assertTrue(all(risk.get(field) for field in ("condition", "action", "blocks")))

    def test_concrete_answer_and_real_source_are_accepted_without_claiming_execution(self):
        spec, ready = templates.validate_output("E1", self.record(), self.validate_sources)
        self.assertTrue(ready)
        self.assertEqual(spec["id"], "E1.O1")
        self.assertIn("尚未执行", templates.render(spec, self.record()))

    def test_blank_placeholder_and_bare_completion_do_not_count_as_answers(self):
        for answer in ("", " ", "TODO", "TBD", "{{contract}}", "已完成", "符合要求", "同上", "待填写"):
            value = self.record()
            value["answers"][0]["answer"] = answer
            with self.assertRaises(ValueError, msg=answer):
                templates.validate_output("E1", value, self.validate_sources)

    def test_repeating_same_answer_cannot_cover_different_questions(self):
        value = self.record()
        for answer in value["answers"]:
            answer["answer"] = "order_id是必填字符串且由存储唯一约束保证，具体规则见已登记来源。"
        with self.assertRaisesRegex(ValueError, "Repeating"):
            templates.validate_output("E1", value, self.validate_sources)

    def test_missing_duplicate_and_unknown_question_ids_are_rejected(self):
        for kind in ("missing", "duplicate", "unknown"):
            value = self.record()
            if kind == "missing":
                value["answers"].pop()
            elif kind == "duplicate":
                value["answers"][1]["id"] = value["answers"][0]["id"]
            else:
                value["answers"][0]["id"] = "E1.O1.Q999"
            with self.assertRaises(ValueError, msg=kind):
                templates.validate_output("E1", value, self.validate_sources)

    def test_supported_answer_needs_existing_usable_source(self):
        for ids in ([], ["missing-source"]):
            value = self.record()
            value["answers"][0]["source_ids"] = ids
            with self.assertRaises(ValueError):
                templates.validate_output("E1", value, self.validate_sources)
        evidence = self.root / "hs-dev/deliveries/d1/data-rule.md"
        evidence.write_text("# Changed rule\nStorage does not promise uniqueness.\n")
        with self.assertRaises(ValueError):
            templates.validate_output("E1", self.record(), self.validate_sources)

    def test_unknown_and_conflict_are_recordable_but_block_readiness(self):
        for status in ("unknown", "conflict"):
            value = self.record()
            value["answers"][0].update(status=status, source_ids=[], reason="尚未取得存储层实际唯一约束定义。",
                                       next_action="读取当前数据库DDL并与order_id规则逐字段核对。")
            _, ready = templates.validate_output("E1", value, self.validate_sources)
            self.assertFalse(ready)
            value["answers"][0].pop("next_action")
            with self.assertRaises(ValueError):
                templates.validate_output("E1", value, self.validate_sources)

    def test_not_applicable_requires_evidence_reason_and_next_action(self):
        value = self.record()
        value["answers"][0].update(status="not-applicable", answer="此交付不持久化订单，字段约束由提供方契约限定。",
                                   reason="本次仅交付读取现有订单的消费者，不创建或迁移存储。",
                                   next_action="在接口契约核验提供方返回的order_id类型和缺失行为。")
        self.assertTrue(templates.validate_output("E1", value, self.validate_sources)[1])
        value["answers"][0]["source_ids"] = []
        with self.assertRaises(ValueError):
            templates.validate_output("E1", value, self.validate_sources)

    def test_missing_or_duplicate_acceptance_checks_do_not_count_as_goal_achievement(self):
        for kind in ("missing", "duplicate", "placeholder", "unreferenced"):
            value = self.record()
            if kind == "missing":
                value.pop("acceptance")
            elif kind == "duplicate":
                value["acceptance"][1]["id"] = value["acceptance"][0]["id"]
            elif kind == "placeholder":
                value["acceptance"][0]["judgment"] = "已完成"
            else:
                value["acceptance"][0]["source_ids"] = []
            with self.assertRaises(ValueError, msg=kind):
                templates.validate_output("E1", value, self.validate_sources)

    def test_unresolved_acceptance_blocks_even_when_every_question_was_answered(self):
        for status in ("unknown", "conflict"):
            value = self.record()
            value["acceptance"][0].update(status=status, source_ids=[], judgment="业务字段与存储字段是否一致尚不能判断。",
                                           reason="尚未取得实际存储模型，只有业务方的定义。",
                                           next_action="取得存储DDL后逐字段比较类型、空值与默认。")
            self.assertFalse(templates.validate_output("E1", value, self.validate_sources)[1])

    def test_section_update_changes_only_target_output(self):
        spec, _ = templates.validate_output("E1", self.record(), self.validate_sources)
        initial = "# Existing architecture\n\nThis unrelated decision must remain exact.\n"
        first = templates.insert(initial, spec, self.record())
        suffix = "\n\n## Existing rollout\nLeave the rollout instructions intact.\n"
        original = first + suffix
        changed = self.record()
        changed["answers"][0]["answer"] = "order_id为不可变的必填字符串；拒绝缺失、空值和空字符串，不再允许后续修改。"
        result = templates.insert(original, spec, changed)
        self.assertTrue(result.startswith(initial.rstrip()))
        self.assertTrue(result.endswith(suffix))
        self.assertEqual(result.count("<!-- hs-output:E1.O1:start -->"), 1)
        self.assertIn("不可变", templates.section(result, "E1.O1"))
        self.assertNotIn("不可变", result.split("<!-- hs-output:E1.O1:start -->")[0])

    def test_duplicate_or_incomplete_section_markers_block_replacement(self):
        spec = templates.contract("E1", "E1.O1")["outputs"][0]
        block = templates.render(spec, self.record())
        for text in (block + block, block.replace("<!-- hs-output:E1.O1:end -->", "")):
            with self.assertRaises(ValueError):
                templates.insert(text, spec, self.record())

    def test_unknown_output_and_activity_do_not_fall_back_to_another_contract(self):
        with self.assertRaises(ValueError):
            templates.contract("E1", "E1.O999")
        with self.assertRaises(ValueError):
            templates.contract("Z1")
        value = self.record()
        value["id"] = "E1.O999"
        with self.assertRaises(ValueError):
            templates.validate_output("E1", value, self.validate_sources)


class PackageTests(unittest.TestCase):
    def test_every_zip_has_resolvable_references_and_independent_cli(self):
        skill_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            output = base / "packages"
            result = subprocess.run([sys.executable, str(skill_root / "scripts/build.py"), "--output", str(output)],
                                    capture_output=True, text=True, check=True, timeout=60)
            self.assertEqual(json.loads(result.stdout)["artifacts"], 10)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(len(manifest["artifacts"]), 10)
            for entry in manifest["artifacts"]:
                with self.subTest(package=entry["name"]):
                    installed = base / "installed" / entry["name"]
                    installed.mkdir(parents=True)
                    with zipfile.ZipFile(output / entry["file"]) as archive:
                        self.assertTrue(all(".." not in Path(name).parts and not Path(name).is_absolute() for name in archive.namelist()))
                        self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in archive.namelist()))
                        archive.extractall(installed)
                    package = installed / entry["name"]
                    for document in package.rglob("*.md"):
                        for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
                            target = target.split("#", 1)[0].strip("<>")
                            if not target or "://" in target or target.startswith("mailto:"):
                                continue
                            self.assertTrue((document.parent / unquote(target)).is_file(), f"{entry['name']}: {document.relative_to(package)} -> {target}")
                    cli = package / "scripts/hs-dev.py"
                    project = base / "projects" / entry["name"]
                    project.mkdir(parents=True)
                    version = subprocess.run([sys.executable, str(cli), "--version"], cwd=project,
                                             capture_output=True, text=True, check=True, timeout=20)
                    self.assertEqual(version.stdout.strip(), "0.0.2")
                    def invoke(*args):
                        result = subprocess.run([sys.executable, str(cli), "--root", str(project), *args], cwd=project,
                                                capture_output=True, text=True, check=True, timeout=20)
                        return json.loads(result.stdout)["result"]
                    self.assertEqual(invoke("catalog-check")["outputs"], 114)
                    self.assertEqual(invoke("template", "--activity", "E1", "--output", "E1.O1")["outputs"][0]["id"], "E1.O1")
                    (project / "rules.md").write_text("# Cancellation\nOnly unshipped orders may be cancelled.\n")
                    self.assertTrue(invoke("reindex")["ok"])
                    cards = invoke("locate", "--query", "Cancellation")["results"]
                    self.assertEqual(cards[0]["path"], "rules.md")
                    self.assertIn("unshipped", invoke("read", "--path", "rules.md", "--digest", cards[0]["source_digest"])["text"])
                    self.assertTrue(invoke("init")["ok"])
                    self.assertEqual(invoke("start", "--title", "Inspect bounded cancellation rules", "--activity", "B2", "--scope", "unshipped-cancellation")["activity"], "B2")


if __name__ == "__main__":
    unittest.main()
