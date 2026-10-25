"""Decision ledger behavior: approval promotion, finish gate, tamper detection, staleness and supersede."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.cli import main
from hs_dev import decisions
from hs_dev import task_store as store


class DecisionLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.call("init")

    def call(self, *args, success=True):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(self.root), "--output", "json", *args])
        if success:
            self.assertEqual(code, 0, err.getvalue())
            return json.loads(out.getvalue())["result"]
        self.assertEqual(code, 1, err.getvalue())
        return err.getvalue()

    def start(self):
        return self.call("task-start", "决策测试", "--activities", "H1", "--mode", "activity")["task_id"]

    def pass_na(self, task):
        for check in store.definition("H1")["checks"]:
            self.call("check", task, "H1", check["id"], "NA", "--reason", "本场景无该对象")

    def test_init_creates_empty_ledger(self):
        self.assertTrue((self.root / decisions.LEDGER).is_file())
        self.assertTrue((self.root / decisions.OVERVIEW).is_file())
        self.assertEqual(self.call("decision-list")["count"], 0)

    def test_approval_is_promoted_and_overview_derived(self):
        task = self.start()
        self.pass_na(task)
        self.call("approve", task, "H1", "--actor", "human", "--confirmation", "用户：通过")
        view = self.call("decision-list")
        self.assertEqual(view["count"], 1)
        entry = view["entries"][0]
        self.assertEqual(entry["scope"], "H1")
        self.assertEqual(entry["task_id"], task)
        self.assertEqual(entry["status"], "current")
        self.assertEqual(entry["event"], "accepted")
        text = (self.root / decisions.OVERVIEW).read_text(encoding="utf-8")
        self.assertTrue(text.startswith("<!-- hs:"))
        self.assertIn("验收通过：H1", text)
        self.assertIn(task, text)

    def test_finish_requires_ledger_records_and_valid_chain(self):
        task = self.start()
        self.pass_na(task)
        self.call("approve", task, "H1", "--actor", "human", "--confirmation", "用户：通过")
        (self.root / decisions.LEDGER).write_text("", encoding="utf-8")
        error = self.call("complete", task, "--checks", json.dumps([[sys.executable, "-c", "print('ok')"]]), success=False)
        self.assertIn("missing approval records", error)

    def test_tampered_history_breaks_the_chain(self):
        self.call("decision-record", "--title", "采用A方案", "--reason", "成本更低", "--actor", "human", "--confirmation", "确认A")
        self.call("decision-record", "--title", "接口走REST", "--reason", "生态成熟", "--actor", "human", "--confirmation", "确认REST")
        path = self.root / decisions.LEDGER
        lines = path.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["title"] = "被篡改的标题"
        lines[0] = json.dumps(first, ensure_ascii=False)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        error = self.call("decision-list", success=False)
        self.assertIn("chain break", error)

    def test_manual_record_stale_detection_and_supersede(self):
        doc = self.root / "hs_dev_docs/foundation/notes.md"
        doc.write_text("# 备忘\n\n采用A方案。\n", encoding="utf-8")
        self.call("decision-record", "--title", "采用A方案", "--reason", "成本更低",
                  "--actor", "human", "--confirmation", "确认A",
                  "--units", "file:hs_dev_docs/foundation/notes.md",
                  "--alternatives", "B方案|自研C")
        view = self.call("decision-list")
        self.assertEqual(view["entries"][0]["status"], "current")
        doc.write_text("# 备忘\n\n改用B方案。\n", encoding="utf-8")
        view = self.call("decision-list")
        self.assertEqual(view["stale_count"], 1)
        self.assertEqual(view["entries"][0]["status"], "stale")
        decision_id = view["entries"][0]["decision_id"]
        self.call("decision-supersede", decision_id, "--reason", "切换到B方案",
                  "--actor", "human", "--confirmation", "确认切换")
        view = self.call("decision-list")
        states = {e["decision_id"]: e["status"] for e in view["entries"]}
        self.assertEqual(states[decision_id], "superseded")
        self.assertEqual(states[view["entries"][1]["decision_id"]], "superseding")
        self.assertEqual(view["superseded_count"], 1)
        error = self.call("decision-supersede", decision_id, "--reason", "重复推翻",
                          "--actor", "human", "--confirmation", "再次", success=False)
        self.assertIn("already superseded", error)

    def test_code_change_stales_describing_decisions(self):
        task = self.start()
        graph = {"objects": [{"id": "O1", "kind": "module", "path": "srv.py", "not_applicable_reason": "示例注册"}],
                 "relations": []}
        doc = ('<!-- hs: {"id": "design", "relations": [{"source": "design", "target": "O1", "kind": "describes"}]} -->\n'
               "# 登录设计\n\n描述 srv.py 的登录行为。\n")
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps({
            "srv.py": "def login():\n    return True\n",
            "hs_dev_docs/design.md": doc,
            "hs_dev_docs/foundation/object_graph.json": json.dumps(graph)}), "--checks", json.dumps([["true"]]))
        self.call("decision-record", "--title", "登录设计定稿", "--actor", "human", "--confirmation", "确认定稿",
                  "--units", "file:hs_dev_docs/design.md")
        view = self.call("decision-list")
        self.assertEqual(view["entries"][0]["status"], "current")
        self.assertEqual(view["entries"][0]["describes"][0]["unit_id"], "file:srv.py")
        self.call("commit", task, "--activity", "H1", "--changes", json.dumps(
            {"srv.py": "def login():\n    return False\n"}), "--checks", json.dumps([["true"]]))
        view = self.call("decision-list")
        self.assertEqual(view["entries"][0]["status"], "stale")

    def test_record_rejects_invalid_input_and_unknown_units(self):
        self.call("decision-record", "--title", "缺确认", "--actor", "human", "--confirmation", "", success=False)
        error = self.call("decision-record", "--title", "未知单元", "--actor", "human",
                          "--confirmation", "确认", "--units", "file:hs_dev_docs/missing.md", success=False)
        self.assertIn("Unknown semantic unit", error)
        self.assertEqual(self.call("decision-list")["count"], 0)


if __name__ == "__main__":
    unittest.main()
