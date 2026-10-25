"""Doc-first creation: the document system exists first, code is then driven from it.

Phase 1 designs behavior kernels with unimplemented_reason (no code exists yet);
phase 2 implements strictly from the kernel specs, backfills implemented_by and
declares the verification gate; phase 3 reviews against the contracts and accepts.
A negative case proves an implementation that violates the documented behavior
cannot even commit.
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.cli import main
from hs_dev import task_store as store
from hs_dev import blueprint as blueprint_module

DOC_FIRST = """# 便笺：文档先行

## 创建便笺

:::contract
{"id": "feature:note.create", "title": "创建便笺"}
:::

:::contract
{"id": "behavior:note.create", "feature": "feature:note.create",
 "trigger": "提交非空标题",
 "precondition": "会话已建立",
 "output": {"note": "含 title 的便笺对象"},
 "postcondition": "便笺可被后续查询",
 "covered_by": ["case:note.create.ok", "case:note.create.reject"],
 "implemented_by": [],
 "unimplemented_reason": "文档先行：等待 G 阶段实现"}
:::

## 拒绝空标题

:::contract
{"id": "behavior:note.create.reject", "feature": "feature:note.create",
 "trigger": "提交空标题",
 "output": {"error": "ValueError(empty title)"},
 "covered_by": ["case:note.create.reject"],
 "implemented_by": [],
 "unimplemented_reason": "文档先行：等待 G 阶段实现"}
:::

叙述：行为规格以内核为权威，实现阶段不得偏离。
"""

BLUEPRINT = {"schema_version": 1,
             "features": [{"id": "feature:note.create", "title": "创建便笺"}],
             "scenarios": [
                 {"id": "scenario:note.create.normal", "feature": "feature:note.create", "title": "正常创建", "kind": "normal"},
                 {"id": "scenario:note.create.error", "feature": "feature:note.create", "title": "空标题被拒", "kind": "error"}],
             "cases": [
                 {"id": "case:note.create.ok", "scenario": "scenario:note.create.normal", "evidence": "test_note.py"},
                 {"id": "case:note.create.reject", "scenario": "scenario:note.create.error", "evidence": "test_note.py"}]}

# Phase-2 implementation generated strictly from the kernel specs above.
CODE_FROM_DOC = "def create_note(title):\n    if not title:\n        raise ValueError('empty title')\n    return {'title': title}\n"
TESTS_FROM_DOC = ("import pytest\nfrom app.service import create_note\n\n"
                  "def test_ok():\n    assert create_note('a') == {'title': 'a'}\n\n"
                  "def test_reject():\n    with pytest.raises(ValueError):\n        create_note('')\n")
GATES = {"schema_version": 1, "entries": [
    {"id": "unit", "argv": ["python3", "-m", "pytest", "test_note.py", "-q",
                            "--junitxml=hs-dev-skill/reports/junit.xml"],
     "report": {"format": "junit", "path": "hs-dev-skill/reports/junit.xml"}}]}


class DocFirstTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def call(self, *args, success=True):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(self.root), "--output", "json", *args])
        payload = None
        if out.getvalue().strip():
            try:
                payload = json.loads(out.getvalue())["result"]
            except (json.JSONDecodeError, KeyError):
                payload = None
        if success:
            self.assertEqual(code, 0, err.getvalue())
            return payload
        self.assertEqual(code, 1)
        return payload if payload is not None else err.getvalue()

    def bind(self, task, consumer, producer, unit="file:hs_dev_docs/README.md"):
        self.call("dependency-bind", task, consumer, producer, unit,
                  "--actor", "model", "--confirmation", "模型：绑定基线")

    def test_01_design_only_document_system(self):
        """Phase 1: kernels ship with unimplemented_reason; nothing exists to run yet."""
        self.call("init")
        task = self.call("task-start", "文档先行设计", "--activities", "B2", "--mode", "mute")["task_id"]
        self.bind(task, "B2", "B1")
        self.call("commit", task, "--activity", "B2", "--changes", json.dumps({
            "docs/notes.md": DOC_FIRST,
            "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT, ensure_ascii=False)}),
            "--checks", json.dumps([["true"]]))  # bootstrap：门禁尚未声明，自由命令可用
        for check in store.definition("B2")["checks"]:
            self.call("check", task, "B2", check["id"], "NA", "--reason", "文档先行")
        done = self.call("complete", task, "--checks", json.dumps([["true"]]))
        self.assertEqual(done["status"], "COMPLETED")
        report = self.call("kernel")
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["counts"]["kernels"], 3)
        # 用例证据尚不存在：准备度如实未就绪，但不阻断设计阶段。
        result = blueprint_module.reconcile(BLUEPRINT, root=self.root)
        self.assertFalse(result["ok"])
        self.assertTrue(any("evidence file missing" in e for e in result["errors"]), result["errors"])

    def test_02_implementation_driven_from_docs(self):
        """Phase 2: implement per kernel specs, backfill implemented_by, declare the gate."""
        task = self.call("task-start", "按文档实现", "--activities", "G1", "--mode", "mute")["task_id"]
        self.bind(task, "G1", "F4", "file:docs/notes.md")
        backfilled = DOC_FIRST.replace('"implemented_by": [],\n "unimplemented_reason": "文档先行：等待 G 阶段实现"',
                                       '"implemented_by": ["symbol:app/service.py:create_note"]')
        self.assertNotEqual(backfilled, DOC_FIRST)  # 两处内核都被回填
        backfilled = backfilled.replace('"implemented_by": ["symbol:app/service.py:create_note"],\n "unimplemented_reason": "文档先行：等待 G 阶段实现"',
                                        '"implemented_by": ["symbol:app/service.py:create_note"]')
        self.assertNotIn("unimplemented_reason", backfilled)
        self.call("commit", task, "--activity", "G1", "--changes", json.dumps({
            "docs/notes.md": backfilled,
            "app/__init__.py": "",
            "app/service.py": CODE_FROM_DOC,
            "test_note.py": TESTS_FROM_DOC,
            "hs_dev_docs/foundation/gates.json": json.dumps(GATES)}),
            "--checks", json.dumps([["gate:unit"]]))  # 门禁随实现一同就位并立即生效
        # G1 回填了自己消费的行为文档：上游演进后重新锚定基线，再进入检查。
        self.bind(task, "G1", "F4", "file:docs/notes.md")
        for check in store.definition("G1")["checks"]:
            self.call("check", task, "G1", check["id"], "NA", "--reason", "按文档实现")
        done = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")
        evidence = json.loads((self.root / done["verification"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["reports"][0]["cases"], 2)
        self.assertEqual(evidence["reports"][0]["failures"], [])
        self.assertTrue(blueprint_module.report(self.root)["ok"])

    def test_03_violating_implementation_cannot_commit(self):
        """The docs constrain the code: an implementation that breaks the documented
        rejection behavior fails its own gate at commit time."""
        task = self.call("task-start", "违背文档的实现", "--activities", "G1", "--mode", "mute")["task_id"]
        self.bind(task, "G1", "F4", "file:docs/notes.md")
        violating = "def create_note(title):\n    return {'title': title or 'default'}\n"
        error = self.call("commit", task, "--activity", "G1", "--changes", json.dumps(
            {"app/service.py": violating}), "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("Behavior verification failed", str(error))
        operations = sorted((self.root / "hs-dev-skill/recovery/operations").glob("*.json"))
        stuck = [json.loads(p.read_text(encoding="utf-8")) for p in operations
                 if json.loads(p.read_text(encoding="utf-8"))["state"] in {"PREPARED", "INTERRUPTED"}]
        self.call("rollback", stuck[-1]["operation_id"], "--decision", "rollback")
        self.call("task-rollback", task, "--decision", "rollback")
        self.assertEqual((self.root / "app/service.py").read_text(), CODE_FROM_DOC)

    def test_04_review_and_acceptance_close_the_loop(self):
        task = self.call("task-start", "评审与验收", "--activities", "R1,H3", "--mode", "mute")["task_id"]
        for producer in ("H1", "H2", "R1"):
            self.bind(task, "H3", producer, "file:docs/notes.md")
        for activity in ("R1", "H3"):
            for check in store.definition(activity)["checks"]:
                self.call("check", task, activity, check["id"], "NA", "--reason", "对照契约评审")
        done = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")
        self.assertTrue(self.call("status")["ok"])
        self.assertEqual(self.call("doc-debt")["counts"]["blocking"], 0)


if __name__ == "__main__":
    unittest.main()
