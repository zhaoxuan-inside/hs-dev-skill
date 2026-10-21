"""Persisted causal links and graph rendering over retained trace events."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.support import trace
from hs_dev.support.trace_graph import graph, mermaid
from hs_dev.support.trace_metrics import record_context


class TraceGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        token = trace.ENABLED.set(True)
        self.addCleanup(trace.ENABLED.reset, token)

    def emit(self, event, **attributes):
        return trace.emit(self.root, event, {"task_id": "task", **attributes})

    def test_cross_run_sequence_hierarchy_and_task_isolation(self):
        root = self.emit("task_state")
        token = trace.RUN.set("another-process-run")
        try:
            stage = self.emit("stage", stage_id="A", outcome="entered")
            activity = self.emit("activity", activity_id="A1", outcome="entered")
            trace.emit(self.root, "task_state", {"task_id": "other"})
            check = self.emit("check", activity_id="A1", check_id="A1.1", outcome="PASS")
        finally:
            trace.RUN.reset(token)
        value = graph(self.root, "task")
        edges = {(e["source"], e["target"], e["kind"]) for e in value["edges"]}
        self.assertIn((root, stage, "next"), edges)
        self.assertIn((root, stage, "contains"), edges)
        self.assertIn((stage, activity, "contains"), edges)
        self.assertIn((activity, check, "contains"), edges)
        self.assertEqual(len(value["nodes"]), 4)
        self.assertEqual(value["missing_event_ids"], [])

    def test_retry_edges_link_exact_failed_check(self):
        failed = self.emit("check", activity_id="A1", check_id="A1.1", outcome="FAIL")
        self.emit("check", activity_id="A1", check_id="A1.2", outcome="PASS")
        retried = self.emit("check", activity_id="A1", check_id="A1.1", outcome="PASS")
        self.emit("check", activity_id="A1", check_id="A1.1", outcome="PASS")
        self.assertEqual([e for e in graph(self.root, "task")["edges"] if e["kind"] == "retry"],
                         [{"source": failed, "target": retried, "kind": "retry"}])

    def test_context_sources_are_children_of_delivery_event(self):
        record_context(self.root, "task", "A1", {"body": [{"path": "a.md", "start": 1, "end": 2, "text": "中文"}],
                       "usage": {"output_bytes": 100}, "status": "complete"}, 2)
        value = graph(self.root, "task")
        context = next(n for n in value["nodes"] if n["event"] == "context")
        source = next(n for n in value["nodes"] if n["event"] == "context_source")
        self.assertIn({"source": context["id"], "target": source["id"], "kind": "contains"}, value["edges"])

    def test_limit_preserves_missing_links_and_mermaid_escapes_labels(self):
        for _ in range(4):
            self.emit("check", name='bad"] --> injected["<script>')
        value = graph(self.root, "task", limit=2)
        self.assertTrue(value["truncated"])
        self.assertTrue(value["missing_event_ids"])
        self.assertFalse(value["history_complete"])
        rendered = mermaid(value)
        self.assertIn("unavailable event", rendered)
        self.assertNotIn('bad"]', rendered)
        self.assertNotIn("<script>", rendered)
        self.assertEqual(len(value["nodes"]), 2)

    def test_dropped_event_is_not_persisted_as_predecessor(self):
        first = self.emit("task_state")
        folder = self.root / "hs-dev-skill/trace"
        (folder / ".write.lock").touch()
        self.assertIsNone(self.emit("check"))
        (folder / ".write.lock").unlink()
        last = self.emit("command")
        self.assertIn({"source": first, "target": last, "kind": "next"}, graph(self.root, "task")["edges"])

    def test_empty_and_disabled_graph_are_read_only(self):
        self.assertEqual(graph(self.root, "unknown")["nodes"], [])
        self.assertFalse((self.root / "hs-dev-skill/trace").exists())
        with self.assertRaises(ValueError):
            graph(self.root, "task", limit=0)

    def test_bad_log_is_reported(self):
        self.emit("task_state")
        (self.root / "hs-dev-skill/trace/events.jsonl").write_text("broken json")
        with self.assertRaises(ValueError):
            graph(self.root, "task")

    def test_graph_does_not_use_query_sample_limit(self):
        for _ in range(110):
            self.emit("command", name="check")
        value = graph(self.root, "task")
        self.assertEqual(len(value["nodes"]), 110)
        self.assertFalse(value["truncated"])

    def test_legacy_events_are_not_connected_by_inference(self):
        self.emit("command")
        path = self.root / "hs-dev-skill/trace/events.jsonl"
        row = json.loads(path.read_text())
        row.pop("previous_event_id")
        row.pop("parent_event_id")
        path.write_text(json.dumps(row) + "\n")
        value = graph(self.root, "task")
        self.assertEqual(value["edges"], [])
        self.assertEqual(value["unlinked_event_ids"], [row["event_id"]])
