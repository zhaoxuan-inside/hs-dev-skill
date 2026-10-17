import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).parent.parent / "scripts"
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS))

from skill_trace import (  # noqa: E402
    MAX_EVENT_BYTES,
    SESSION_ID_PATTERN,
    TraceRuntimeError,
    _append_event_line,
    is_trace_enabled,
    load_skill_execution_config,
    record_event,
    save_skill_execution_config,
    sessions_dir,
    start_session,
    summarize,
    validate_session,
)
import skill_trace  # noqa: E402


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "skill_trace.py"), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO_ROOT),
    )


def session_lines(root: Path, session_id: str):
    path = sessions_dir(root) / f"{session_id}.jsonl"
    return path, [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def seed_session(root: Path, host="codex", task_id=None):
    result = start_session(root, host=host)
    session_id = result["session_id"]
    record_event(
        root,
        session_id,
        "intent_sizing",
        data={"intent": "BUILD", "change_size": "M", "work_mode": "DESIGN", "confirmed": True, "source": "O4"},
    )
    if task_id:
        record_event(root, session_id, "task_link", data={"task_id": task_id}, ref=f"{task_id}_plan.md")
    record_event(root, session_id, "session_end", data={"reason": "completed"})
    return session_id


class TestSkillTrace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self._tmp.name)
        save_skill_execution_config(self.root, {"version": "1.0", "features": {"skill_trace": True}})

    def tearDown(self):
        self._tmp.cleanup()

    # T1 配置生命周期
    def test_t1_config_lifecycle(self):
        fresh = Path(self._tmp.name) / "fresh"
        fresh.mkdir()
        cfg = load_skill_execution_config(fresh)
        self.assertFalse(cfg["features"]["skill_trace"])
        self.assertIsNone(cfg["config_file"])
        self.assertFalse(is_trace_enabled(fresh))

        status = run_cli("status", "--root", str(fresh))
        self.assertEqual(status.returncode, 0)
        self.assertFalse(json.loads(status.stdout)["enabled"])

        enable = run_cli("enable", "--root", str(fresh))
        self.assertEqual(enable.returncode, 0)
        self.assertTrue(json.loads(enable.stdout)["enabled"])
        self.assertTrue((fresh / "config" / "skill_execution.yaml").is_file())
        self.assertTrue(is_trace_enabled(fresh))

        disable = run_cli("disable", "--root", str(fresh))
        self.assertEqual(disable.returncode, 0)
        self.assertFalse(is_trace_enabled(fresh))

        broken = fresh / "config" / "skill_execution.yaml"
        broken.write_text("features: {\n  skill_trace: true\n", encoding="utf-8")
        self.assertTrue(is_trace_enabled(fresh))

    # T2 项目隔离
    def test_t2_project_isolation(self):
        other = Path(self._tmp.name) / "other"
        other.mkdir()
        result_a = run_cli("start", "--root", str(self.root), "--host", "codex")
        self.assertEqual(result_a.returncode, 0)
        self.assertTrue(json.loads(result_a.stdout)["ok"])

        result_b = run_cli("start", "--root", str(other), "--host", "codex")
        self.assertEqual(result_b.returncode, 0)
        self.assertEqual(json.loads(result_b.stdout)["skipped"], "trace_disabled")

        self.assertEqual(len(list(sessions_dir(self.root).glob("*.jsonl"))), 1)
        self.assertFalse((other / "hs_dev_docs").exists())

    # T3 序列、有序性与校验
    def test_t3_sequence_and_validate(self):
        result = start_session(self.root, host="codex")
        session_id = result["session_id"]
        self.assertRegex(session_id, SESSION_ID_PATTERN)
        record_event(self.root, session_id, "skill_load", data={"skill_id": "hs-dev-implementation"})
        record_event(
            self.root,
            session_id,
            "route_decision",
            data={"intent": "BUILD", "phase": 3, "process_skill": "hs-dev-design", "functional_skills": ["hs-dev-governance"]},
        )
        record_event(self.root, session_id, "phase_transition", data={"from": 0, "to": 3, "status": "entered"})
        record_event(self.root, session_id, "task_link", data={"task_id": "skill_trace_001"}, ref="hs_dev_docs/_06_dev_process/_01_plan_log/skill_trace_001_plan.md")
        record_event(self.root, session_id, "key_action", data={"kind": "test", "summary": "make test", "result": "ok"})
        record_event(self.root, session_id, "decision", data={"question": "验收?", "adopted": "ACCEPTED"}, ref="Q10")
        record_event(self.root, session_id, "deviation", data={"what_happened": "场景切断", "correction": "补约定"}, ref="e_000005")
        record_event(self.root, session_id, "error_retry", data={"error": "timeout", "action": "retry", "attempt": 1})
        record_event(self.root, session_id, "timing", data={"scope": "phase:3", "duration_ms": 1200})
        record_event(self.root, session_id, "session_end", data={"reason": "completed"})

        _, events = session_lines(self.root, session_id)
        self.assertEqual(events[0]["event"], "session_start")
        self.assertEqual(events[-1]["event"], "session_end")
        expected_ids = [f"e_{i:06d}" for i in range(1, len(events) + 1)]
        self.assertEqual([e["event_id"] for e in events], expected_ids)
        timestamps = [e["ts"] for e in events]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertTrue(all(e["session_id"] == session_id for e in events))

        report = validate_session(sessions_dir(self.root) / f"{session_id}.jsonl", root=self.root)
        self.assertTrue(report["ok"], report["errors"])

    # T4 依赖拒绝（不写入）
    def test_t4_rejections_without_write(self):
        session_id = start_session(self.root, host="codex")["session_id"]
        path, before = session_lines(self.root, session_id)

        missing = run_cli(
            "record", "--root", str(self.root), "--session", "s_20260101_000000_abcd", "--event", "timing",
            "--data", '{"scope":"x","duration_ms":1}',
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("session_not_found", missing.stderr)

        unknown = run_cli(
            "record", "--root", str(self.root), "--session", session_id, "--event", "made_up_event", "--data", "{}",
        )
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("unknown_event", unknown.stderr)

        bad_json = run_cli(
            "record", "--root", str(self.root), "--session", session_id, "--event", "timing", "--data", "{not json",
        )
        self.assertEqual(bad_json.returncode, 2)

        missing_ref = run_cli(
            "record", "--root", str(self.root), "--session", session_id, "--event", "decision",
            "--data", '{"question":"q","adopted":"a"}',
        )
        self.assertEqual(missing_ref.returncode, 2)
        self.assertIn("missing_ref", missing_ref.stderr)

        _, after = session_lines(self.root, session_id)
        self.assertEqual(len(before), len(after))

    # T5 关闭静默
    def test_t5_disabled_is_silent(self):
        fresh = Path(self._tmp.name) / "silent"
        fresh.mkdir()
        start = run_cli("start", "--root", str(fresh), "--host", "codex")
        self.assertEqual(start.returncode, 0)
        self.assertEqual(json.loads(start.stdout).get("skipped"), "trace_disabled")

        record = run_cli(
            "record", "--root", str(fresh), "--session", "s_20260101_000000_abcd", "--event", "timing",
            "--data", '{"scope":"x","duration_ms":1}',
        )
        self.assertEqual(record.returncode, 0)
        self.assertEqual(json.loads(record.stdout).get("skipped"), "trace_disabled")
        self.assertFalse((fresh / "hs_dev_docs").exists())
        self.assertFalse((fresh / "config").exists())

    # T6 截断保解析
    def test_t6_truncation_keeps_line_parseable(self):
        session_id = start_session(self.root, host="codex")["session_id"]
        record_event(
            self.root,
            session_id,
            "key_action",
            data={"kind": "output", "summary": "超大输出", "result": "ok", "detail": "汉" * 6000},
        )
        path = sessions_dir(self.root) / f"{session_id}.jsonl"
        last_line = path.read_text(encoding="utf-8").splitlines()[-1]
        self.assertLessEqual(len(last_line.encode("utf-8")), MAX_EVENT_BYTES)
        parsed = json.loads(last_line)
        self.assertTrue(parsed["truncated"])
        self.assertTrue(parsed["data"]["truncated"])
        self.assertGreater(parsed["data"]["original_bytes"], MAX_EVENT_BYTES)

        report = validate_session(path, root=self.root)
        self.assertTrue(report["ok"], report["errors"])
        self.assertTrue(any("payload_truncated" in w for w in report["warnings"]))

    # T7 查询复盘
    def test_t7_summary_and_query(self):
        s1 = start_session(self.root, host="codex")["session_id"]
        record_event(self.root, s1, "task_link", data={"task_id": "pay_001"}, ref="hs_dev_docs/plans/pay_001_plan.md")
        record_event(self.root, s1, "phase_transition", data={"from": 0, "to": 3, "status": "accepted"})
        record_event(self.root, s1, "deviation", data={"what_happened": "返工", "correction": "修复"}, ref="e_000002")
        record_event(self.root, s1, "error_retry", data={"error": "io", "action": "fallback", "attempt": 2})
        record_event(self.root, s1, "session_end", data={"reason": "completed"})
        s2 = seed_session(self.root, task_id="other_002")

        summary = run_cli("summary", "--root", str(self.root), "--task", "pay_001")
        self.assertEqual(summary.returncode, 0)
        payload = json.loads(summary.stdout)
        self.assertEqual(payload["sessions"], [s1])
        self.assertEqual(payload["counts"]["task_link"], 1)
        self.assertEqual(len(payload["phases"]), 1)
        self.assertEqual(len(payload["deviations"]), 1)
        self.assertEqual(len(payload["errors"]), 1)

        overall = json.loads(run_cli("summary", "--root", str(self.root)).stdout)
        self.assertEqual(len(overall["sessions"]), 2)
        self.assertIsNotNone(overall["first_ts"])
        self.assertIsNotNone(overall["last_ts"])

        query = run_cli("query", "--root", str(self.root), "--task", "pay_001", "--event", "deviation")
        self.assertEqual(query.returncode, 0)
        lines = [json.loads(line) for line in query.stdout.splitlines() if line.strip()]
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]["session_id"], s1)

        limited = run_cli("query", "--root", str(self.root), "--session", s2, "--limit", "2")
        self.assertEqual(len([line for line in limited.stdout.splitlines() if line.strip()]), 2)

    # T8 validate 规则
    def test_t8_validate_rules(self):
        path = sessions_dir(self.root) / "s_20260101_010101_aaaa.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        events = [
            {"v": 1, "event_id": "e_000002", "session_id": "s_20260101_010101_aaaa", "ts": "2026-01-01T01:01:01Z",
             "event": "key_action", "data": {"kind": "test", "summary": "s", "result": "ok"}},
            {"v": 1, "event_id": "e_000002", "session_id": "s_20260101_010101_aaaa", "ts": "2026-01-01T01:01:00Z",
             "event": "decision", "data": {"question": "q", "adopted": "a"}},
        ]
        path.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in events) + "\nnot-json\n", encoding="utf-8")

        report = validate_session(path, root=self.root)
        self.assertFalse(report["ok"])
        joined = " ".join(report["errors"])
        self.assertIn("first_event_not_session_start", joined)
        self.assertIn("event_id_out_of_sequence", joined)
        self.assertIn("ts_regression", joined)
        self.assertIn("invalid_json", joined)
        self.assertIn("missing_ref", joined)
        self.assertTrue(any("last_event_not_session_end" in w for w in report["warnings"]))

        cli = run_cli("validate", "--file", str(path))
        self.assertEqual(cli.returncode, 1)

        healthy = seed_session(self.root)
        ok = run_cli("validate", "--session", healthy, "--root", str(self.root))
        self.assertEqual(ok.returncode, 0)
        self.assertTrue(json.loads(ok.stdout)["ok"])

        both = run_cli("validate", "--session", healthy, "--file", str(path))
        self.assertEqual(both.returncode, 2)

    # T9 初始化集成
    def test_t9_init_creates_config_and_dir(self):
        target = Path(self._tmp.name) / "init_target"
        target.mkdir()
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "init_hs_dev_docs.py"), "--root", str(target)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        cfg_file = target / "config" / "skill_execution.yaml"
        self.assertTrue(cfg_file.is_file())
        self.assertFalse(load_skill_execution_config(target)["features"]["skill_trace"])
        self.assertTrue((target / "hs_dev_docs" / "_06_dev_process" / "_05_skill_trace" / "sessions").is_dir())

    # T10 门禁回归：路由注册与文档计数同步
    def test_t10_registry_and_doc_sync(self):
        check = subprocess.run(
            [sys.executable, str(SCRIPTS / "skill_router.py"), "check"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(check.returncode, 0, check.stderr)
        payload = json.loads(check.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["skills"], 16)
        self.assertEqual(payload["references"], 52)
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("52 份已登记详规", readme)

    # T11 失败降级路径
    def test_t11_degrade_on_write_failure(self):
        with self.assertRaises(TraceRuntimeError):
            _append_event_line(sessions_dir(self.root), "x")

        target = Path(self._tmp.name) / "binary.jsonl"
        target.write_bytes(b"\xff\xfe\x00binary")
        result = run_cli("validate", "--file", str(target))
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])

        with mock.patch.object(skill_trace, "record_event", side_effect=TraceRuntimeError("write_failed:simulated")):
            code = skill_trace.main(
                ["record", "--root", str(self.root), "--session", "s_20260101_000000_abcd", "--event", "timing",
                 "--data", '{"scope":"x","duration_ms":1}']
            )
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
