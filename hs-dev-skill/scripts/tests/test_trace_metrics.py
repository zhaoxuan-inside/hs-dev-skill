"""Observed span timing, retries and exact context provenance."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.support import trace
from hs_dev.support.trace_metrics import observe, record_context


class TraceMetricsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        token = trace.ENABLED.set(True)
        self.addCleanup(trace.ENABLED.reset, token)

    def events(self, **filters):
        return trace.query(self.root, limit=100, **filters)["events"]

    def test_spans_accumulate_across_calls_and_stop_at_approval(self):
        with patch("hs_dev.support.trace_metrics.time.time", return_value=100):
            observe(self.root, "task", "enter", "A1", selected=["A1", "A2"])
        with patch("hs_dev.support.trace_metrics.time.time", return_value=102):
            observe(self.root, "task", "enter", "A2", selected=["A1", "A2"])
        with patch("hs_dev.support.trace_metrics.time.time", return_value=105):
            observe(self.root, "task", "approve", selected=["A1", "A2"])
        activities = self.events(event="activity", outcome="completed")
        self.assertEqual({e["attributes"]["activity_id"]: e["attributes"]["duration_ms"] for e in activities},
                         {"A1": 2000, "A2": 3000})
        self.assertEqual(self.events(event="stage", outcome="completed")[0]["attributes"]["duration_ms"], 5000)

    def test_retry_is_previous_failed_check_not_each_check(self):
        observe(self.root, "task", "enter", "A1", selected=["A1"])
        for item, result in [("A1.1", "FAIL"), ("A1.2", "PASS"), ("A1.1", "FAIL"), ("A1.1", "PASS"), ("A1.1", "PASS")]:
            observe(self.root, "task", "check", "A1", item=item, result=result)
        self.assertEqual(self.events(event="activity", outcome="check")[-1]["attributes"]["retry_count"], 2)
        self.assertEqual(self.events(event="stage", outcome="check")[-1]["attributes"]["retry_count"], 2)

    def test_context_counts_unicode_and_preserves_long_paths_without_text(self):
        source = "docs/" + "目录/" * 70 + "说明.md"
        context = {"body": [{"path": source, "start": 2, "end": 4, "text": "你好\n世界"}],
                   "usage": {"output_bytes": 200}, "status": "complete"}
        observe(self.root, "task", "enter", "A1", selected=["A1"])
        record_context(self.root, "task", "A1", context, 12)
        event = self.events(event="context")[0]["attributes"]
        self.assertEqual(event["context_chars"], 5)
        sources = self.events(context_id=event["context_id"], event="context_source")
        self.assertEqual(sources[0]["attributes"]["source_path"], source)
        self.assertEqual(sources[0]["attributes"]["start_line"], 2)
        self.assertNotIn("你好", json.dumps(self.events(), ensure_ascii=False))
        self.assertEqual(self.events(event="stage", outcome="context")[0]["attributes"]["context_chars"], 5)

    def test_disabled_creates_no_trace_files(self):
        token = trace.ENABLED.set(False)
        try:
            observe(self.root, "task", "enter", "A1", selected=["A1"])
            record_context(self.root, None, None, {"body": [], "usage": {"output_bytes": 0}, "status": "complete"}, 0)
        finally:
            trace.ENABLED.reset(token)
        self.assertFalse((self.root / "hs-dev-skill/trace").exists())

    def test_metrics_lock_contention_does_not_block_business(self):
        folder = self.root / "hs-dev-skill/trace"
        folder.mkdir(parents=True)
        (folder / ".metrics.lock").touch()
        before = trace.DROPPED
        observe(self.root, "task", "enter", "A1", selected=["A1"])
        self.assertEqual(trace.DROPPED, before + 1)
