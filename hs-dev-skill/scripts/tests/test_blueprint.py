"""Blueprint registry reconciliation and the E9 readiness gate."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.cli import main
from hs_dev import blueprint
from hs_dev import task_store as store
from hs_dev.workspace import Workspace


def registry(features=(), scenarios=(), cases=(), copy=()):
    value = {"schema_version": 1, "features": list(features),
             "scenarios": list(scenarios), "cases": list(cases)}
    if copy:
        value["copy"] = list(copy)
    return value


def complete_feature(fid="F1", title="用户登录", **extra):
    feature = {"id": fid, "title": title, **extra}
    scenarios = [
        {"id": fid + "-S1", "feature": fid, "title": "密码错误锁定", "kind": "error"},
        {"id": fid + "-S2", "feature": fid, "title": "正常登录", "kind": "normal"},
    ]
    cases = [
        {"id": fid + "-C1", "scenario": fid + "-S1", "evidence": "test/test_login.py::test_lock"},
        {"id": fid + "-C2", "scenario": fid + "-S2", "evidence": "test/test_login.py::test_ok"},
    ]
    return feature, scenarios, cases


class ReconcileTests(unittest.TestCase):
    def test_clean_mapping_passes(self):
        feature, scenarios, cases = complete_feature()
        result = blueprint.reconcile(registry([feature], scenarios, cases))
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["counts"]["features"], 1)
        self.assertEqual(result["counts"]["cases"], 2)

    def test_feature_without_scenarios_fails(self):
        result = blueprint.reconcile(registry([{"id": "F1", "title": "登录"}]))
        self.assertFalse(result["ok"])
        self.assertIn("Feature has no behavior scenarios: F1", result["errors"])

    def test_missing_required_kinds_fail_and_waiver_exempts(self):
        feature, scenarios, cases = complete_feature()
        normal_only = [s for s in scenarios if s["kind"] == "normal"]
        cases_normal = [c for c in cases if c["scenario"].endswith("-S2")]
        result = blueprint.reconcile(registry([feature], normal_only, cases_normal))
        self.assertIn("Feature lacks a error scenario: F1", result["errors"])
        waived = dict(feature, not_applicable_reason="外部组件，仅登记")
        result = blueprint.reconcile(registry([waived], normal_only, cases_normal))
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["counts"]["waived"], 1)

    def test_planned_case_does_not_cover_scenario(self):
        feature, scenarios, cases = complete_feature()
        planned = [dict(cases[0], status="planned")]
        result = blueprint.reconcile(registry([feature], scenarios, planned + [cases[1]]))
        self.assertFalse(result["ok"])
        self.assertIn("Scenario has no current test case: F1-S1", result["errors"])
        self.assertEqual(result["counts"]["planned_cases"], 1)

    def test_dangling_references_fail(self):
        result = blueprint.reconcile(registry(
            [{"id": "F1", "title": "登录"}],
            [{"id": "S1", "feature": "F9", "title": "锁定"}],
            [{"id": "C1", "scenario": "S9", "evidence": "test/t.py::a"}]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("unknown feature" in e for e in result["errors"]))
        self.assertTrue(any("unknown scenario" in e for e in result["errors"]))

    def test_deferred_requires_reason(self):
        result = blueprint.reconcile(registry([{"id": "F1", "title": "登录", "deferred": {}}]))
        self.assertFalse(result["ok"])
        self.assertTrue(any("Deferred requires a reason" in e for e in result["errors"]))
        result = blueprint.reconcile(registry([{"id": "F1", "title": "登录", "deferred": {"reason": "本轮范围外"}}]))
        self.assertTrue(result["ok"], result["errors"])

    def test_deferred_scenarios_satisfy_design_and_need_no_case(self):
        result = blueprint.reconcile(registry(
            [{"id": "F1", "title": "登录"}],
            [{"id": "S1", "feature": "F1", "title": "锁定", "kind": "error", "deferred": {"reason": "下轮补"}},
             {"id": "S2", "feature": "F1", "title": "登录", "kind": "normal", "deferred": {"reason": "下轮补"}}]))
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["counts"]["deferred"], 2)

    def test_superseded_feature_is_exempt(self):
        result = blueprint.reconcile(registry([{"id": "F1", "title": "旧登录", "status": "superseded"}]))
        self.assertTrue(result["ok"], result["errors"])

    def test_ui_feature_requires_authoritative_copy(self):
        feature, scenarios, cases = complete_feature(surface="ui")
        result = blueprint.reconcile(registry([feature], scenarios, cases))
        self.assertFalse(result["ok"])
        self.assertIn("UI feature has no authoritative copy: F1", result["errors"])
        copy = [{"id": "T1", "feature": "F1", "scenario": "F1-S1", "key": "error.locked.title", "text": "账户已锁定"}]
        result = blueprint.reconcile(registry([feature], scenarios, cases, copy=copy))
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["counts"]["copy"], 1)

    def test_copy_structure_rules(self):
        feature, scenarios, cases = complete_feature(surface="ui")
        rows = [
            {"id": "T1", "feature": "F1", "scenario": "F1-S1", "key": "error.locked.title", "text": "已锁定"},
            {"id": "T2", "feature": "F1", "key": "error.locked.title", "text": "重复键"},
            {"id": "T3", "feature": "F9", "key": "k", "text": "未知功能"},
            {"id": "T4", "feature": "F1", "scenario": "S9", "key": "k", "text": "未知场景"},
            {"id": "T5", "feature": "F1", "key": "", "text": "缺键"},
            {"id": "T6", "feature": "F1", "key": "k", "text": " "},
        ]
        errors = blueprint.reconcile(registry([feature], scenarios, cases, copy=rows))["errors"]
        self.assertTrue(any("Duplicate copy key" in e for e in errors))
        self.assertTrue(any("Copy references unknown feature" in e for e in errors))
        self.assertTrue(any("Copy references unknown scenario" in e for e in errors))
        self.assertTrue(any("Copy missing key" in e for e in errors))
        self.assertTrue(any("Copy missing text" in e for e in errors))

    def test_structure_and_evidence_rules(self):
        result = blueprint.reconcile(registry(
            [{"id": "F1", "title": "登录"}, {"id": "F1", "title": "重复"}],
            [{"id": "S1", "feature": "F1", "title": "锁定", "kind": "weird"}],
            [{"id": "C1", "scenario": "S1", "evidence": "test/missing.py::a"}]), root=Path("/"))
        self.assertFalse(result["ok"])
        self.assertTrue(any("Duplicate feature id" in e for e in result["errors"]))
        self.assertTrue(any("Unknown scenario kind" in e for e in result["errors"]))
        self.assertTrue(any("Case evidence file missing" in e for e in result["errors"]))


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

    def start_e9(self):
        task = self.call("task-start", "准备度核验", "--activities", "E9", "--mode", "mute")["task_id"]
        for producer in store.definition("E9")["upstream"]:
            self.call("dependency-bind", task, "E9", producer,
                      "file:hs_dev_docs/README.md", "--actor", "model", "--confirmation", "模型：绑定基线")
        return task

    def test_report_without_registry_and_gate_blocks_missing(self):
        self.assertFalse(self.call("blueprint")["registry"])
        task = self.start_e9()
        error = self.call("check", task, "E9", "E9.1", "NA", "--reason", "n/a", success=False)
        self.assertIn("Blueprint registry missing", error)

    def test_e9_blocks_incomplete_blueprint_and_finish_rechecks(self):
        task = self.start_e9()
        incomplete = registry([{"id": "F1", "title": "登录"}])
        self.call("commit", task, "--activity", "E9", "--changes", json.dumps(
            {"hs_dev_docs/foundation/blueprint.json": json.dumps(incomplete, ensure_ascii=False)}),
            "--checks", json.dumps([["true"]]))
        error = self.call("check", task, "E9", "E9.1", "NA", "--reason", "n/a", success=False)
        self.assertIn("Feature has no behavior scenarios", error)

        feature, scenarios, cases = complete_feature()
        self.call("commit", task, "--activity", "E9", "--changes", json.dumps({
            "hs_dev_docs/foundation/blueprint.json": json.dumps(registry([feature], scenarios, cases), ensure_ascii=False),
            "test/test_login.py": "def test_lock():\n    assert True\n\n\ndef test_ok():\n    assert True\n"}),
            "--checks", json.dumps([["true"]]))
        report = self.call("blueprint")
        self.assertTrue(report["ok"], report["errors"])
        for check in store.definition("E9")["checks"]:
            self.call("check", task, "E9", check["id"], "NA", "--reason", "n/a")

        broken = registry([feature], scenarios)
        self.call("commit", task, "--activity", "E9", "--changes", json.dumps(
            {"hs_dev_docs/foundation/blueprint.json": json.dumps(broken, ensure_ascii=False)}),
            "--checks", json.dumps([["true"]]))
        error = self.call("complete", task, "--checks", json.dumps([["true"]]), success=False)
        self.assertIn("Blueprint reconciliation failed", error)
        self.assertIn("Scenario has no current test case", error)


class GraphGateTests(unittest.TestCase):
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

    def test_required_waiver_no_longer_exempts(self):
        from hs_dev.verification import coverage
        self.assertFalse(coverage([{"id": "O1", "required": False}], [])["ok"])
        self.assertTrue(coverage([{"id": "O1", "not_applicable_reason": "外部组件"}], [])["ok"])
        self.assertFalse(coverage({"objects": []}, [])["ok"])

    def test_missing_object_registry_blocks_verify_and_new_tasks(self):
        (self.root / "hs_dev_docs/foundation/object_graph.json").unlink()
        result = self.call("verify", success=False)
        self.assertFalse(result["ok"])
        self.assertTrue(any("Object registry missing" in e for e in result["errors"]))
        error = self.call("task-start", "新任务", "--activities", "H1", "--mode", "activity", success=False)
        self.assertIn("RECOVERY_REQUIRED", error)
        self.assertEqual(Workspace(self.root).inspect()["status"], "RECOVERY_REQUIRED")


if __name__ == "__main__":
    unittest.main()
