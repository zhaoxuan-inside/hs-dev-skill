"""Contract kernels: :::contract parsing, ID-chain reconciliation and documentation debt."""
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
from hs_dev import kernel as kernel_module

DOC = """# 行为设计

## 创建便笺

:::contract
{"id": "feature:note.create", "title": "创建便笺"}
:::

:::contract
{"id": "behavior:note.create", "feature": "feature:note.create",
 "covered_by": ["case:note.create.ok", "case:note.create.fail"],
 "implemented_by": ["symbol:app/service.py:create_note"]}
:::

叙述外壳，不参与校验。
"""

BLUEPRINT = {"schema_version": 1,
             "features": [{"id": "feature:note.create", "title": "创建便笺"}],
             "scenarios": [
                 {"id": "scenario:note.create.normal", "feature": "feature:note.create", "title": "正常创建", "kind": "normal"},
                 {"id": "scenario:note.create.error", "feature": "feature:note.create", "title": "创建失败", "kind": "error"}],
             "cases": [
                 {"id": "case:note.create.ok", "scenario": "scenario:note.create.normal", "evidence": "test_note.py"},
                 {"id": "case:note.create.fail", "scenario": "scenario:note.create.error", "evidence": "test_note.py"}]}

CODE = "def create_note(title):\n    return {'title': title}\n"


class KernelTests(unittest.TestCase):
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

    def commit(self, changes, checks=(["true"],), success=True):
        task = self.call("task-start", "登记", "--activities", "H1", "--mode", "mute")["task_id"]
        result = self.call("commit", task, "--activity", "H1", "--changes", json.dumps(changes, ensure_ascii=False),
                           "--checks", json.dumps([list(c) for c in checks]), success=success)
        if success:
            for check in store.definition("H1")["checks"]:
                self.call("check", task, "H1", check["id"], "NA", "--reason", "n/a")
            self.call("complete", task, "--checks", json.dumps([["true"]]))
        return result

    def seed(self, doc=DOC, code=CODE, complete=True):
        self.commit({"hs_dev_docs/behavior.md": doc, "app/service.py": code,
                     "hs_dev_docs/foundation/blueprint.json": json.dumps(BLUEPRINT, ensure_ascii=False),
                     "test_note.py": "def test_ok():\n    assert True\n"})

    def test_valid_chain_reconciles_and_task_completes(self):
        self.seed()
        report = self.call("kernel")
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["counts"]["kernels"], 2)
        task = self.call("task-start", "验收", "--activities", "H1", "--mode", "mute")["task_id"]
        for check in store.definition("H1")["checks"]:
            self.call("check", task, "H1", check["id"], "NA", "--reason", "n/a")
        self.call("complete", task, "--checks", json.dumps([["true"]]))
        self.assertTrue(self.call("status")["ok"])

    def test_dangling_links_block_publish(self):
        self.seed()
        task = self.call("task-start", "悬空链", "--activities", "H1", "--mode", "mute")["task_id"]
        error = self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/behavior.md": DOC.replace("case:note.create.fail", "case:note.create.missing")}),
            "--checks", json.dumps([["true"]]), success=False)
        self.assertIn("unknown case", str(error))

    def test_dangling_symbol_reference_blocks(self):
        self.seed()
        task = self.call("task-start", "悬空符号", "--activities", "H1", "--mode", "mute")["task_id"]
        error = self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/behavior.md": DOC.replace("symbol:app/service.py:create_note", "symbol:app/service.py:gone")}),
            "--checks", json.dumps([["true"]]), success=False)
        self.assertIn("unknown code unit", str(error))

    def test_malformed_kernel_fails_publish(self):
        broken = DOC.replace('{"id": "behavior:note.create"', '{"id": "behavior:')
        error = self.commit({"hs_dev_docs/behavior.md": broken}, success=False)
        self.assertIn("Contract kernel", str(error))

    def test_missing_implemented_by_requires_reason(self):
        doc = DOC.replace('"implemented_by": ["symbol:app/service.py:create_note"]', '"unimplemented_reason": "尚未实现"')
        self.seed(doc=doc)
        self.assertTrue(self.call("kernel")["ok"])

    def test_code_drift_creates_debt_and_blocks_completion_until_waived(self):
        self.seed()
        self.call("decision-record", "--title", "行为登记确认", "--actor", "model",
                  "--confirmation", "模型：登记核对通过", "--units", "symbol:app/service.py:create_note")
        task = self.call("task-start", "改代码", "--activities", "H1", "--mode", "mute")["task_id"]
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"app/service.py": "def create_note(title):\n    return {'title': title, 'v': 2}\n"}), "--checks", json.dumps([["true"]]))
        debt = self.call("doc-debt", success=False)
        self.assertEqual(debt["counts"]["blocking"], 2, debt)
        keys = {row["key"] for row in debt["rows"]}
        self.assertIn("kernel:behavior:note.create", keys)
        self.assertTrue(any(key.startswith("decision:") for key in keys))
        for check in store.definition("H1")["checks"]:
            self.call("check", task, "H1", check["id"], "NA", "--reason", "n/a")
        error = self.call("complete", task, "--checks", json.dumps([["true"]]), success=False)
        self.assertIn("Documentation debt blocks release", str(error))

        with self.assertRaises(ValueError):
            kernel_module.waive(self.root, "kernel:behavior:note.create", "模型豁免", "model")
        self.call("doc-debt-waive", "--key", "kernel:none", "--reason", "x", "--actor", "human", success=False)
        for row in debt["rows"]:
            self.call("doc-debt-waive", "--key", row["key"], "--reason", "演示豁免：" + row["key"], "--actor", "human")
        self.call("complete", task, "--checks", json.dumps([["true"]]))

        task = self.call("task-start", "再改代码", "--activities", "H1", "--mode", "mute")["task_id"]
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"app/service.py": "def create_note(title):\n    return {'title': title, 'v': 3}\n"}), "--checks", json.dumps([["true"]]))
        debt = self.call("doc-debt", success=False)
        self.assertTrue(any(row["key"] == "kernel:behavior:note.create" for row in debt["rows"]), debt)
        self.assertEqual(debt["counts"]["blocking"], 1, debt)

    def test_stale_decision_surfaces_in_debt(self):
        self.seed()
        self.call("decision-record", "--title", "文档决定", "--actor", "model",
                  "--confirmation", "模型：确认", "--units", "file:hs_dev_docs/behavior.md")
        task = self.call("task-start", "改文档", "--activities", "H1", "--mode", "mute")["task_id"]
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"hs_dev_docs/behavior.md": DOC + "\n补充叙述。\n"}), "--checks", json.dumps([["true"]]))
        debt = self.call("doc-debt", success=False)
        self.assertTrue(any(key.startswith("decision:") for key in {row["key"] for row in debt["rows"]}), debt)


if __name__ == "__main__":
    unittest.main()
