"""Declared verification gates and machine test reports."""
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
# 报告随工作区 flag 文件翻转：声明门禁时是绿的；后续任务把代码改坏（写下 flag）
# 后同一门禁变红——真实项目中"改坏代码"的机械等价物。
JUNIT = ('import pathlib\n'
         'fail = pathlib.Path("flag").exists() and pathlib.Path("flag").read_text().strip() == "fail"\n'
         'pathlib.Path("hs-dev-skill/reports").mkdir(parents=True, exist_ok=True)\n'
         'case = ("<testcase classname=\\"test_note\\" name=\\"test_ok\\"/>" if not fail else\n'
         '         "<testcase classname=\\"test_note\\" name=\\"test_ok\\"><failure message=\\"broken\\"/></testcase>")\n'
         'pathlib.Path("' + REPORT + '").write_text('
         '"<testsuite name=\\"s\\" tests=\\"1\\" failures=\\"" + str(int(fail)) + "\\">" + case + "</testsuite>")\n')


def gates(entries):
    return {"schema_version": 1, "entries": entries}


def unit_gate():
    return {"id": "unit", "argv": [sys.executable, "-c", JUNIT],
            "report": {"format": "junit", "path": REPORT}}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.call("init")

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

    def declare(self, entries):
        task = self.call("task-start", "门禁登记", "--activities", "H1", "--mode", "mute")["task_id"]
        selectors = [["gate:" + entry["id"]] for entry in entries]
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/foundation/gates.json": json.dumps(gates(entries), ensure_ascii=False)}),
            "--checks", json.dumps(selectors))
        for check in store.definition("H1")["checks"]:
            self.call("check", task, "H1", check["id"], "NA", "--reason", "n/a")
        self.call("complete", task, "--checks", json.dumps(selectors))

    def start_task(self, activities):
        task = self.call("task-start", "任务", "--activities", activities, "--mode", "mute")["task_id"]
        for activity in activities.split(","):
            for producer in store.definition(activity)["upstream"]:
                self.call("dependency-bind", task, activity, producer,
                          "file:hs_dev_docs/README.md", "--actor", "model", "--confirmation", "模型：绑定基线")
            for check in store.definition(activity)["checks"]:
                self.call("check", task, activity, check["id"], "NA", "--reason", "n/a")
        return task

    def rollback(self, task):
        self.call("task-rollback", task, "--decision", "rollback")

    def test_init_creates_empty_gates_and_freeform_still_allowed(self):
        self.assertTrue((self.root / "hs_dev_docs/foundation/gates.json").is_file())
        task = self.start_task("H1")
        done = self.call("complete", task, "--checks", json.dumps([["true"]]))
        self.assertEqual(done["status"], "COMPLETED")

    def test_declared_gate_selector_runs_and_parses_report(self):
        self.declare([unit_gate()])
        task = self.start_task("H1")
        done = self.call("complete", task, "--checks", json.dumps([["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")
        evidence = json.loads((self.root / done["verification"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["gates"], "declared")
        self.assertEqual(len(evidence["reports"]), 1)
        self.assertEqual(evidence["reports"][0]["cases"], 1)
        self.assertEqual(evidence["reports"][0]["failures"], [])

    def test_breaking_change_fails_its_own_commit_with_report(self):
        self.declare([unit_gate()])
        task = self.start_task("H1")
        error = self.call("commit", task, "--activity", "H1", "--changes", json.dumps({"flag": "fail"}),
                          "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("Behavior verification failed", str(error))

    def test_freeform_rejected_once_gates_declared(self):
        self.declare([unit_gate()])
        task = self.start_task("H1")
        error = self.call("complete", task, "--checks", json.dumps([["true"]]), success=False)
        self.assertIn("Gates are declared", str(error))
        error = self.call("complete", task, "--checks", json.dumps([["gate:missing"]]), success=False)
        self.assertIn("Unknown verification gate", str(error))

    def test_engineering_task_requires_machine_report(self):
        self.declare([
            {"id": "lint", "argv": [sys.executable, "-c", "print('lint ok')"]},
            unit_gate()])
        task = self.start_task("G1")
        error = self.call("complete", task, "--checks", json.dumps([["gate:lint"]]), success=False)
        self.assertIn("machine test report", str(error))
        done = self.call("complete", task, "--checks", json.dumps([["gate:lint"], ["gate:unit"]]))
        self.assertEqual(done["status"], "COMPLETED")

    def test_corrupt_gates_registry_blocks(self):
        self.declare([unit_gate()])
        task = self.start_task("H1")
        error = self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/foundation/gates.json": '{"schema_version": 9}'}),
            "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("Unsupported gates registry format", str(error))

    def test_report_path_must_stay_in_runtime_directory(self):
        task = self.start_task("H1")
        outside = {"id": "unit", "argv": [sys.executable, "-c", JUNIT],
                   "report": {"format": "junit", "path": "reports/junit.xml"}}
        error = self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/foundation/gates.json": json.dumps(gates([outside]))}),
            "--checks", json.dumps([["gate:unit"]]), success=False)
        self.assertIn("runtime directory", str(error))


if __name__ == "__main__":
    unittest.main()
