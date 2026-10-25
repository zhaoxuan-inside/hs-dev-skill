"""End-to-end dogfood: build the whole document system through managed CLI flow.

No handwritten registries. A fresh workspace gets its behavior kernels, blueprint,
gates and implementation through task-start/commit/check/complete only — then debt,
waiver, dangling-chain rejection and review-before-acceptance are exercised on top.
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

REPORT = "hs-dev-skill/reports/junit.xml"
JUNIT_GATE = ('import pathlib\n'
              'fail = pathlib.Path("flag").exists() and pathlib.Path("flag").read_text().strip() == "fail"\n'
              'pathlib.Path("hs-dev-skill/reports").mkdir(parents=True, exist_ok=True)\n'
              'case = ("<testcase classname=\\"test_note\\" name=\\"test_ok\\"/>" if not fail else\n'
              '         "<testcase classname=\\"test_note\\" name=\\"test_ok\\"><failure message=\\"broken\\"/></testcase>")\n'
              'pathlib.Path("' + REPORT + '").write_text('
              '"<testsuite name=\\"s\\" tests=\\"1\\" failures=\\"" + str(int(fail)) + "\\">" + case + "</testsuite>")\n')

DOC = """# 便笺行为契约

:::contract
{"id": "feature:note.create", "title": "创建便笺"}
:::

:::contract
{"id": "behavior:note.create", "feature": "feature:note.create",
 "covered_by": ["case:note.create.ok", "case:note.create.fail"],
 "implemented_by": ["symbol:app/service.py:create_note"]}
:::

叙述外壳：AI 驱动文档，文档驱动代码。
"""

BLUEPRINT = {"schema_version": 1,
             "features": [{"id": "feature:note.create", "title": "创建便笺"}],
             "scenarios": [
                 {"id": "scenario:note.create.normal", "feature": "feature:note.create", "title": "正常创建", "kind": "normal"},
                 {"id": "scenario:note.create.error", "feature": "feature:note.create", "title": "标题为空被拒", "kind": "error"}],
             "cases": [
                 {"id": "case:note.create.ok", "scenario": "scenario:note.create.normal", "evidence": "test_note.py"},
                 {"id": "case:note.create.fail", "scenario": "scenario:note.create.error", "evidence": "test_note.py"}]}

GATES = {"schema_version": 1, "entries": [
    {"id": "unit", "argv": [sys.executable, "-c", JUNIT_GATE],
     "report": {"format": "junit", "path": REPORT}}]}

CODE = "def create_note(title):\n    if not title:\n        raise ValueError('empty title')\n    return {'title': title}\n"
TESTS = "def test_ok():\n    assert True\n"


class EndToEndDogfood(unittest.TestCase):
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

    def pass_na(self, task, activity):
        for check in store.definition(activity)["checks"]:
            self.call("check", task, activity, check["id"], "NA", "--reason", "演示流程")

    def test_01_init_creates_empty_foundation(self):
        self.call("init")
        for name in ("object_graph.json", "contracts.json", "gates.json", "decisions.jsonl"):
            self.assertTrue((self.root / "hs_dev_docs/foundation" / name).is_file(), name)
        self.assertTrue(self.call("status")["ok"])

    def test_02_document_system_built_through_managed_task(self):
        task = self.call("task-start", "建立行为契约与实现", "--activities", "H1", "--mode", "mute")["task_id"]
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps({
            "docs/notes.md": DOC,
            "app/service.py": CODE,
            "test_note.py": TESTS,
            "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT, ensure_ascii=False),
            "hs_dev_docs/foundation/gates.json": json.dumps(GATES)}), "--checks", json.dumps([["gate:unit"]]))
        self.pass_na(task, "H1")
        done = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")
        evidence = json.loads((self.root / done["verification"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["gates"], "declared")
        self.assertEqual(evidence["reports"][0]["failures"], [])

        report = self.call("kernel")
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["counts"]["kernels"], 2)
        self.assertTrue(self.call("blueprint")["ok"])
        # Anchor the implementation with a decision so later code drift becomes debt.
        self.call("decision-record", "--title", "便笺行为登记确认", "--actor", "model",
                  "--confirmation", "模型：登记与实现一致", "--units", "symbol:app/service.py:create_note")

    def test_03_dangling_kernel_rejected_at_publish(self):
        task = self.call("task-start", "错误登记", "--activities", "H1", "--mode", "mute")["task_id"]
        error = self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"docs/notes.md": DOC.replace("case:note.create.fail", "case:note.create.gone")}),
            "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("unknown case", str(error))
        # The failed commit leaves an interrupted operation; roll it back, then the task.
        operations = sorted((self.root / "hs-dev-skill/recovery/operations").glob("*.json"))
        interrupted = [json.loads(p.read_text(encoding="utf-8")) for p in operations
                       if json.loads(p.read_text(encoding="utf-8"))["state"] in {"PREPARED", "INTERRUPTED"}]
        self.assertTrue(interrupted)
        self.call("rollback", interrupted[-1]["operation_id"], "--decision", "rollback")
        self.call("task-rollback", task, "--decision", "rollback")
        self.assertTrue(self.call("status")["ok"])

    def test_04_code_drift_becomes_blocking_debt_then_waiver_releases(self):
        task = self.call("task-start", "扩展实现", "--activities", "H1", "--mode", "mute")["task_id"]
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"app/service.py": CODE.replace("return {'title': title}",
                                            "return {'title': title, 'v': 2}")}),
            "--checks", json.dumps([["gate:unit"]]))
        self.pass_na(task, "H1")
        debt = self.call("doc-debt", success=False)
        self.assertEqual(debt["counts"]["blocking"], 2, debt)
        error = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("Documentation debt blocks release", str(error))
        for row in debt["rows"]:
            self.call("doc-debt-waive", "--key", row["key"], "--reason", "演示：人工裁决放行", "--actor", "human")
        done = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")

    def test_05_review_precedes_acceptance(self):
        task = self.call("task-start", "评审与验收", "--activities", "R1,H3", "--mode", "mute")["task_id"]
        for consumer, producer in (("H3", "H1"), ("H3", "H2"), ("H3", "R1")):
            self.call("dependency-bind", task, consumer, producer, "file:docs/notes.md",
                      "--actor", "model", "--confirmation", "模型：绑定上游基线")
        self.pass_na(task, "R1")
        self.pass_na(task, "H3")
        done = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")
        self.assertTrue(self.call("status")["ok"])
        self.assertEqual(self.call("doc-debt")["counts"]["blocking"], 0)


if __name__ == "__main__":
    unittest.main()
