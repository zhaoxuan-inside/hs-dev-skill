"""Behavioral regression suite. Every workspace lives in a temporary directory."""
import contextlib
import io
import json
import multiprocessing
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hs_dev.cli import main
from hs_dev.workspace import Workspace, OperationPermit, operation
from hs_dev.intent import decide
from hs_dev import task_store as store
from hs_dev.acceptance import approval_valid
from hs_dev.indexing.engine import Index, PUBLICATION, DATABASE
from hs_dev.support import trace
from hs_dev.context import ContextProvider
from hs_dev.indexing.service import Resident, dispatch


def contender(root, queue):
    try:
        queue.put(Workspace(root).acquire().operation_id)
    except ValueError:
        queue.put(None)


class SystemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.call("init")

    def call(self, *args, success=True, global_args=()):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(self.root), "--output", "json", *global_args, *args])
        if success:
            self.assertEqual(code, 0, err.getvalue())
            return json.loads(out.getvalue())["result"]
        self.assertEqual(code, 1, out.getvalue())
        return err.getvalue()

    def start(self, activities="H1", mode="stage"):
        return self.call("task-start", "测试任务", "--activities", activities, "--mode", mode)["task_id"]

    def pass_na(self, task, activity="H1"):
        for check in store.definition(activity)["checks"]:
            self.call("check", task, activity, check["id"], "NA", "--reason", "本场景无该对象")

    def test_sparse_layout_and_clean_status(self):
        self.assertTrue(self.call("status")["ok"])
        self.assertFalse(list((self.root/"hs_dev_docs").rglob("checklist.md")))
        self.assertFalse(list((self.root/"hs_dev_docs").rglob("*index*")))

    def test_scope_required_without_poisoning_workspace(self):
        self.call("task-start", "缺少范围", success=False)
        self.assertEqual(Workspace(self.root).inspect()["status"], "SAFE")

    def test_typed_checks_and_task_context(self):
        task = self.start()
        rows = store.checks(self.root, task, "H1")
        self.assertEqual(rows[0].check_id, "H1.1")
        result = self.call("context", "--task", task)
        self.assertIn("测试任务", result["active"][0]["text"])
        self.assertTrue(result["ok"])

    def test_complete_all_modes(self):
        task = self.start(mode="mute")
        self.pass_na(task)
        self.assertTrue(approval_valid(self.root, store.load_task(self.root, task), "H"))
        done = self.call("complete", task, "--checks", json.dumps([[sys.executable, "-c", "print('ok')"]]))
        self.assertEqual(done["status"], "COMPLETED")

    def test_manual_scope_confirmation_without_material_ceremony(self):
        task = self.start(mode="activity")
        self.pass_na(task)
        self.call("approve", task, "H1", "--actor", "human", "--confirmation", "用户：通过")
        self.assertTrue(approval_valid(self.root, store.load_task(self.root, task), "H1"))

    def test_wrong_uuid_and_fence_rejected(self):
        permit = Workspace(self.root).acquire()
        with self.assertRaises(ValueError):
            Workspace(self.root).assert_owner(OperationPermit(str(self.root), "wrong", permit.fence, 1))
        self.call("search", "--query", "任务", success=False, global_args=("--wait", "0"))
        self.call("operation-finish", global_args=("--operation", permit.operation_id, "--fence", str(permit.fence)))
        with self.assertRaises(ValueError):
            Workspace(self.root).assert_owner(permit)

    def test_concurrent_acquisition_has_one_winner(self):
        queue = multiprocessing.Queue()
        children = [multiprocessing.Process(target=contender, args=(str(self.root), queue)) for _ in range(3)]
        for child in children:
            child.start()
        for child in children:
            child.join(5)
            self.assertEqual(child.exitcode, 0)
        winners = [queue.get(timeout=2) for _ in children]
        self.assertEqual(sum(w is not None for w in winners), 1)
        self.call("operation-revoke", "--reason", "已终止测试子进程")
        self.assertEqual(Workspace(self.root).inspect()["status"], "RECOVERY_REQUIRED")
        self.call("repair-index")

    def test_external_drift_not_silently_accepted(self):
        (self.root/"outside.md").write_text("external")
        self.call("status", success=False)
        self.assertEqual(Workspace(self.root).inspect()["status"], "RECOVERY_REQUIRED")
        self.call("repair-index", success=False)

    def test_index_missing_read_does_not_rebuild(self):
        (self.root/DATABASE).unlink()
        self.call("search", success=False)
        self.assertFalse((self.root/DATABASE).exists())
        self.call("repair-index")
        self.assertTrue(self.call("verify")["ok"])

    def test_unchanged_publish_preserves_revision(self):
        before = self.call("verify")["generation"]
        self.call("repair-index")
        self.assertEqual(self.call("verify")["generation"], before)

    def test_recovery_data_excluded(self):
        task = self.start()
        self.call("context", f"hs-dev-skill/recovery/snapshots/private", "--task", task, success=False)
        self.call("read", "hs-dev-skill/recovery/audit.jsonl", success=False)

    def test_commit_recovery_and_source_bound_approval(self):
        task = self.start(mode="activity")
        changes = json.dumps({"example.py": "def hello():\n    return 1\n"})
        operation_result = self.call("commit", task, "--activity", "H1", "--changes", changes,
                                    "--checks", json.dumps([[sys.executable,"-c","import example; assert example.hello()==1"]]))
        self.pass_na(task)
        self.call("approve", task, "H1", "--actor", "human", "--confirmation", "用户：通过")
        with operation(self.root):
            (self.root/"unrelated.md").write_text("new activity")
            with Index(self.root) as index:
                index.publish()
        self.assertTrue(approval_valid(self.root, store.load_task(self.root, task), "H1"))
        (self.root/"example.py").write_text("def hello():\n    return 2\n")
        self.assertFalse(approval_valid(self.root, store.load_task(self.root, task), "H1"))

    def test_failed_verification_can_rollback(self):
        task = self.start()
        self.call("commit", task, "--activity", "H1", "--changes", '{"bad.txt":"bad"}',
                  "--checks", json.dumps([[sys.executable,"-c","raise SystemExit(1)"]]), success=False)
        operations = list((self.root/"hs-dev-skill/recovery/operations").glob("*.json"))
        self.assertEqual(len(operations), 1)
        op = json.loads(operations[0].read_text())
        self.call("rollback", op["operation_id"], "--decision", "rollback")
        self.assertFalse((self.root/"bad.txt").exists())
        self.assertEqual(Workspace(self.root).inspect()["status"], "SAFE")

    def test_trace_off_and_explicit_on(self):
        self.assertFalse((self.root/"hs-dev-skill/trace").exists())
        self.call("status", global_args=("--trace",))
        events = self.call("trace-query")["events"]
        self.assertTrue(events)
        self.assertTrue(events[0]["run_id"])
        self.assertNotIn("text", events[0])

    def test_cold_body_not_in_fts(self):
        with operation(self.root):
            (self.root/"cold.md").write_text('<!-- hs: {"tier":"cold"} -->\n# Archive\nprivatecoldword')
            with Index(self.root) as index:
                index.publish()
        self.assertEqual(self.call("search", "--query", "privatecoldword"), [])
        self.assertIn("privatecoldword", self.call("read", "cold.md")["text"])

    def test_real_dependency_preserves_upstream_and_tracks_changed_baseline(self):
        task = self.start("H3,H1", mode="activity")
        self.call("commit", task, "--activity", "H1", "--changes", '{"baseline.md":"accepted baseline"}',
                  "--checks", json.dumps([[sys.executable,"-c","print('baseline')"]]))
        self.pass_na(task)
        self.call("approve", task, "H1", "--actor", "human", "--confirmation", "用户：H1通过")
        self.call("dependency-bind", task, "H3", "H2", "baseline.md", "--actor", "human",
                  "--confirmation", "用户：引用已验收的恢复验证基线")
        self.call("commit", task, "--activity", "H3", "--changes", '{"later.md":"downstream result"}',
                  "--checks", json.dumps([[sys.executable,"-c","print('downstream')"]]))
        self.assertTrue(approval_valid(self.root, store.load_task(self.root, task), "H1"))
        self.pass_na(task, "H3")
        self.call("approve", task, "H3", "--actor", "human", "--confirmation", "用户：H3通过")
        self.assertTrue(approval_valid(self.root, store.load_task(self.root, task), "H3"))
        (self.root/"baseline.md").write_text("changed contract")
        self.assertFalse(approval_valid(self.root, store.load_task(self.root, task), "H3"))

    def test_material_pass_is_one_scope_confirmation(self):
        task = self.start()
        self.call("commit", task, "--activity", "H1", "--changes", '{"design.md":"review this result"}',
                  "--checks", json.dumps([[sys.executable,"-c","print('ok')"]]))
        self.pass_na(task)
        self.call("acceptance-material", task, "H1", "design.md", "--title", "结果", "--focus", "行为是否符合")
        view = self.call("acceptance", task)
        result = self.call("acceptance-decide", task, "H", "--materials", view["materials"][0]["id"],
                           "--decision", "pass", "--actor", "human", "--confirmation", "用户：展示的结果通过",
                           "--view-digest", view["view_digest"])
        self.assertTrue(result["approved"])

    def test_evidence_is_not_a_material_card(self):
        task = self.start()
        evidence = self.root / f"hs-dev-skill/tasks/{task}/evidence/log.txt"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("actual check result")
        self.call("check", task, "H1", "H1.1", "PASS", "--evidence", str(evidence.relative_to(self.root)))
        self.assertEqual(self.call("acceptance", task)["materials"], [])

    def test_required_context_is_not_silently_truncated(self):
        with operation(self.root):
            (self.root/"big.md").write_text("required constraint\n"*4000)
            with Index(self.root) as index:
                index.publish()
        result = ContextProvider(self.root).obtain(required=["big.md"], maximum=100)
        self.assertFalse(result["ok"])
        self.assertIn("big.md", result["missing_requirements"])

    def test_query_reads_matching_slice_beyond_first_page(self):
        with operation(self.root):
            (self.root/"long.md").write_text("line\n"*100 + "needlecontext\n" + "tail\n"*20)
            with Index(self.root) as index:
                index.publish()
        result = self.call("context", "--query", "needlecontext")
        self.assertTrue(any("needlecontext" in c["text"] for c in result["active"]))

    def test_resident_context_uses_hot_original(self):
        task = self.start()
        with Index(self.root) as index:
            result = dispatch(index, Resident(self.root, 100_000), {"action":"context", "task_id":task})
        self.assertEqual(result["active"][0]["source"], "hot")

    def test_cancel_and_stale_read_ticket(self):
        workspace = Workspace(self.root)
        ticket = workspace.ticket()
        permit = workspace.acquire()
        with self.assertRaises(ValueError):
            workspace.validate_ticket(ticket)
        self.call("operation-cancel", global_args=("--operation", permit.operation_id, "--fence", str(permit.fence)))
        self.assertEqual(workspace.inspect()["status"], "SAFE")

    def test_trace_rotation_filters_and_sensitive_fields(self):
        config = self.root/"hs-dev-skill/config/config.json"
        config.write_text(json.dumps({"trace":{"enabled":True,"max_event_bytes":500,"max_file_bytes":600,"max_files":2}}))
        for number in range(8):
            trace.emit(self.root, "diagnostic", {"task_id":"task-a", "ok":True,"secret":"credential","text":"private"})
        files = list((self.root/"hs-dev-skill/trace").glob("events*.jsonl"))
        self.assertLessEqual(len(files), 2)
        for path in files:
            self.assertLessEqual(path.stat().st_size, 600)
            self.assertNotIn("credential", path.read_text())
        self.assertTrue(trace.query(self.root, task_id="task-a")["events"])
        self.assertEqual(trace.query(self.root, task_id="task-b")["events"], [])

    def test_task_rollback_keeps_coordination_state(self):
        task = self.start()
        self.call("commit", task, "--activity", "H1", "--changes", '{"temporary.txt":"created"}',
                  "--checks", json.dumps([[sys.executable,"-c","print('ok')"]]))
        result = self.call("task-rollback", task, "--decision", "rollback")
        self.assertEqual(result["task"]["status"], "ROLLED_BACK")
        self.assertFalse((self.root/"temporary.txt").exists())
        self.assertEqual(Workspace(self.root).inspect()["status"], "SAFE")

    def test_same_uuid_has_only_one_active_writer(self):
        workspace = Workspace(self.root)
        permit = workspace.acquire()
        with operation(self.root, operation_id=permit.operation_id, fence=permit.fence):
            with self.assertRaises(ValueError):
                workspace.writer(permit)
        self.call("operation-finish", global_args=("--operation", permit.operation_id, "--fence", str(permit.fence)))

    def test_uuid_task_and_path_scope_are_enforced(self):
        task = self.start()
        permit = self.call("operation-start", "--task", task, "--scope", "allowed")
        credentials = ("--operation", permit["operation_id"], "--fence", str(permit["fence"]))
        self.call("commit", task, "--activity", "H1", "--changes", '{"outside.txt":"x"}',
                  "--checks", json.dumps([[sys.executable,"-c","print('ok')"]]),
                  global_args=credentials, success=False)
        self.assertFalse((self.root/"outside.txt").exists())
        workspace = Workspace(self.root)
        self.assertEqual(workspace.inspect()["status"], "MUTATING")
        with self.assertRaises(ValueError):
            with operation(self.root, operation_id=permit["operation_id"], fence=permit["fence"], task_id="another-task"):
                pass
        self.call("operation-finish", global_args=credentials)


class IntentTests(unittest.TestCase):
    def test_bare_keyword_requires_model(self):
        self.assertEqual(decide("设计")["route"], "NEEDS_MODEL")

    def test_conflicting_signals_require_model(self):
        result = decide("不要回滚，继续实现接口")
        self.assertEqual(result["route"], "NEEDS_MODEL")
        self.assertTrue(any(s["intent"]=="ROLLBACK" and s["polarity"]=="negative" for s in result["signals"]))
        result = decide("不要回滚，继续实现接口", model={"intent":"RESUME", "reason":"继续当前工作"})
        self.assertEqual(result["route"], "RESUME")

    def test_readonly_constraint_wins(self):
        self.assertEqual(decide("只分析代码，不要实现接口", model={"intent":"BUILD","reason":"wrong"})["route"], "EXPLORE")

    def test_invalid_model_fails(self):
        with self.assertRaises(ValueError):
            decide("弄一下", model={"intent":"BUILD"})

    def test_negated_readonly_is_not_forced_to_exploration(self):
        self.assertNotEqual(decide("不要只分析，要实现接口")["route"], "EXPLORE")


if __name__ == "__main__":
    unittest.main()
