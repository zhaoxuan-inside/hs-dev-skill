"""Behavior regressions from the October 17 audit, plus evolution boundaries."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from baseline_gate import digest, freeze, inspect_registry, invalidate, load_registry, register_artifact, validate_coverage
from execution_observer import emit, run_observed
from skill_trace import collect_events, save_skill_execution_config
from workflow_report import build_report


class TestBaselineGate(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scope.md").write_text("REQ-A: save once\nREQ-B: recover on retry\n", encoding="utf-8")
        (self.root / "design.md").write_text("Design contract", encoding="utf-8")
        (self.root / "pack.md").write_text("Executable context", encoding="utf-8")
        (self.root / "evidence.log").write_text("Both scenarios exercised", encoding="utf-8")
        baseline = freeze(self.root, "b1", "1", "scope.md", ["REQ-A", "REQ-B"],
                          {"source": "fixture conversation", "excerpt": "Accept both scenarios"},
                          {"task": ["REQ-A", "REQ-B"]})
        register_artifact(self.root, "design1", "design.md", ["b1"])
        register_artifact(self.root, "pack1", "pack.md", ["design1"])
        self.record = {"task_id": "task", "baseline": {"id": "b1", "version": "1", "sha256": baseline["sha256"]},
                       "requirements": [{"id": req, "result": "PASS", "evidence": "evidence.log"}
                                        for req in ["REQ-A", "REQ-B"]], "artifacts": ["pack1"]}

    def test_full_denominator_cannot_shrink_by_omitting_rows(self):
        self.assertEqual(validate_coverage(self.root, self.record, "task"), {"total": 2, "verified": 2})
        for rows in ([], self.record["requirements"][:1], self.record["requirements"] * 2):
            broken = dict(self.record, requirements=rows)
            with self.subTest(rows=rows), self.assertRaisesRegex(ValueError, "denominator"):
                validate_coverage(self.root, broken, "task")

    def test_source_change_invalidates_transitive_pack_and_acceptance(self):
        (self.root / "scope.md").write_text("REQ-A: changed\nREQ-B: recover", encoding="utf-8")
        before = (self.root / "hs_dev_docs/_06_dev_process/_07_baselines/registry.json").read_bytes()
        self.assertEqual(set(inspect_registry(self.root)["invalid"]), {"b1", "design1", "pack1"})
        self.assertEqual(before, (self.root / "hs_dev_docs/_06_dev_process/_07_baselines/registry.json").read_bytes())
        with self.assertRaisesRegex(ValueError, "invalid"):
            validate_coverage(self.root, self.record, "task")
        invalidate(self.root)
        self.assertEqual(load_registry(self.root)["artifacts"]["pack1"]["status"], "INVALIDATED")

    def test_drifted_artifact_and_missing_evidence_fail(self):
        (self.root / "pack.md").write_text("Unreviewed change", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "artifact"):
            validate_coverage(self.root, self.record, "task")
        (self.root / "evidence.log").unlink()
        with self.assertRaises(OSError):
            validate_coverage(self.root, self.record, "task")

    def test_scope_ownership_and_revision_are_not_agent_local_denominators(self):
        with self.assertRaisesRegex(ValueError, "denominator"):
            validate_coverage(self.root, dict(self.record, task_id="another"), "another")
        with self.assertRaisesRegex(ValueError, "revision"):
            validate_coverage(self.root, dict(self.record, baseline={"id": "b1", "version": "old"}), "task")
        with self.assertRaisesRegex(ValueError, "all REQ"):
            freeze(self.root, "b2", "2", "scope.md", ["REQ-A"], {"source": "fixture", "excerpt": "yes"}, {"task": ["REQ-A"]})
        with self.assertRaisesRegex(ValueError, "already exists"):
            freeze(self.root, "b1", "2", "scope.md", ["REQ-A", "REQ-B"], {"source": "fixture", "excerpt": "yes"}, {"task": ["REQ-A", "REQ-B"]})

    def test_paths_cannot_escape_project(self):
        with self.assertRaises(ValueError):
            digest(self.root, "../outside")
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            digest(self.root, "escape/outside")

    def test_cli_cannot_treat_missing_baseline_or_pack_as_ready(self):
        import contextlib
        import io
        from baseline_gate import main
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--root", str(self.root), "check", "--artifact", "missing-pack"]), 1)
            self.assertEqual(main(["--root", str(self.root), "check", "--artifact", "pack1"]), 0)
            with tempfile.TemporaryDirectory() as empty:
                self.assertEqual(main(["--root", empty, "check"]), 1)

    def test_completion_rejection_preserves_verifying_state(self):
        from idx_manager import IdxManager
        from task_manager import TaskManager
        manager = TaskManager(str(self.root))
        manager.create_task("task", "Require full denominator")
        manager.set_status("task", "IN_PROGRESS")
        manager.set_status("task", "VERIFYING")
        record = dict(self.record, schema_version=1, acceptance_status="ACCEPTED",
                      requirements=self.record["requirements"][:1])
        (self.root / "acceptance.md").write_text("<!-- HS_ACCEPTANCE_GATE_V1\n" + json.dumps(record) + "\nHS_ACCEPTANCE_GATE_V1 -->", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "denominator mismatch"):
            manager.set_status("task", "COMPLETED", acceptance_record="acceptance.md")
        self.assertEqual(IdxManager(str(manager.task_idx_path)).entries[0]["status"], "VERIFYING")

    def test_test_report_content_must_match_recorded_digest(self):
        from task_manager import TaskManager
        manager = TaskManager(str(self.root))
        record = dict(self.record, schema_version=1, acceptance_status="ACCEPTED",
                      verification={"tests": [{"command": "probe", "exit_code": 0,
                                                "evidence": "evidence.log", "sha256": "0" * 64}]})
        (self.root / "acceptance.md").write_text("<!-- HS_ACCEPTANCE_GATE_V1\n" + json.dumps(record) + "\nHS_ACCEPTANCE_GATE_V1 -->", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "evidence digest mismatch"):
            manager._validate_completion_gate("task", self.root / "pack.md", "acceptance.md")

    def test_revised_baseline_can_replace_invalid_history(self):
        from baseline_gate import supersede
        (self.root / "scope.md").write_text("REQ-A: new rule\nREQ-B: recover", encoding="utf-8")
        freeze(self.root, "b2", "2", "scope.md", ["REQ-A", "REQ-B"],
               {"source": "new fixture confirmation", "excerpt": "accept revised scope"},
               {"task": ["REQ-A", "REQ-B"]})
        register_artifact(self.root, "design2", "design.md", ["b2"])
        register_artifact(self.root, "pack2", "pack.md", ["design2"])
        supersede(self.root, "b1", "b2")
        supersede(self.root, "design1", "design2")
        self.assertTrue(supersede(self.root, "pack1", "pack2")["ok"])
        with self.assertRaisesRegex(ValueError, "revision"):
            validate_coverage(self.root, self.record, "task")
        current = dict(self.record, baseline={"id": "b2", "version": "2", "sha256": digest(self.root, "scope.md")}, artifacts=["pack2"])
        self.assertEqual(validate_coverage(self.root, current, "task")["verified"], 2)

    def test_parallel_smaller_scope_cannot_replace_current_task_denominator(self):
        (self.root / "smaller.md").write_text("REQ-A only", encoding="utf-8")
        freeze(self.root, "smaller", "2", "smaller.md", ["REQ-A"],
               {"source": "scope change fixture", "excerpt": "new proposed scope"}, {"task": ["REQ-A"]})
        with self.assertRaisesRegex(ValueError, "unique current baseline"):
            validate_coverage(self.root, self.record, "task")

    def test_missing_dependency_cycles_and_corrupt_registry_fail_closed(self):
        from baseline_gate import save_registry
        state = load_registry(self.root)
        state["artifacts"]["design1"]["dependencies"] = ["pack1"]
        save_registry(self.root, state)
        self.assertFalse(inspect_registry(self.root)["ok"])
        state["artifacts"]["design1"]["dependencies"] = ["missing"]
        save_registry(self.root, state)
        self.assertIn("design1", inspect_registry(self.root)["invalid"])
        state["artifacts"]["design1"] = None
        save_registry(self.root, state)
        with self.assertRaises(ValueError):
            inspect_registry(self.root)


class TestExecutionObservation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def enable(self):
        save_skill_execution_config(self.root, {"features": {"skill_trace": True}})

    def test_disabled_emission_is_noop(self):
        emit(self.root, "test", "action", task_id="t")
        self.assertEqual(list(self.root.iterdir()), [])
        report = build_report(self.root)
        self.assertEqual(report["observed_gate_attempts"], 0)
        self.assertIn("No trace events in selected scope", report["missing_data"])

    def test_actual_command_failure_and_hash_are_reported(self):
        self.enable()
        result = run_observed(self.root, "t", [sys.executable, "-c", "print('actual failure'); raise SystemExit(3)"], "runs/fail.log")
        self.assertEqual(result["exit_code"], 3)
        self.assertEqual(result["sha256"], digest(self.root, "runs/fail.log"))
        report = build_report(self.root, "t")
        self.assertEqual(report["observed_verification_failures"], 1)
        self.assertEqual(report["trace_problems"], [])
        self.assertEqual(build_report(self.root, "another")["observed_verification_runs"], 0)
        with self.assertRaises(ValueError):
            run_observed(self.root, "t", [sys.executable, "-V"], "runs/fail.log")

    def test_optional_trace_failure_does_not_break_work(self):
        self.enable()
        with patch("execution_observer.start_session", side_effect=OSError("unavailable")):
            self.assertIsNone(emit(self.root, "task_manager", "status", task_id="t"))

    def test_route_observation_uses_only_explicit_project_root(self):
        import subprocess
        self.enable()
        script = Path(__file__).resolve().parent.parent / "scripts/skill_router.py"
        result = subprocess.run([sys.executable, "-B", str(script), "route", "--intent", "FIX",
                                 "--project-root", str(self.root)], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["process_skill"]["id"], "hs-dev-debugging")
        _, events = collect_events(self.root)
        facts = [e["data"] for e in events if e["event"] == "tool_result"]
        self.assertEqual(facts[0]["producer"], "skill_router")
        self.assertEqual(facts[0]["facts"]["intent"], "FIX")

    def test_task_status_and_checkpoint_emit_facts(self):
        from task_manager import TaskManager
        from process_log import checkpoint
        self.enable()
        manager = TaskManager(str(self.root))
        manager.create_task("t", "Observed task", change_size="S")
        manager.set_status("t", "IN_PROGRESS")
        checkpoint(self.root, "t", "S1", "before change", ["new.py"])
        _, events = collect_events(self.root, task_id="t")
        actions = [e["data"]["action"] for e in events if e["event"] == "tool_result"]
        self.assertIn("task_created", actions)
        self.assertIn("task_transition", actions)
        self.assertIn("checkpoint", actions)


class TestEvolutionPolicy(unittest.TestCase):
    def test_fatal_habitual_and_advisory_have_different_update_strength(self):
        from skill_evolution import decide
        cases = [{"case_id": "audit-omitted-req", "session_id": "session1", "observed_at": "2026-10-01",
                  "before": {"failures": 1}, "after": {"failures": 0}, "regressions": 0}]
        self.assertEqual(decide("fatal", cases)["action"], "FIX_NOW")
        self.assertEqual(decide("habitual", cases)["action"], "ACCUMULATE")
        self.assertEqual(decide("advisory", cases)["action"], "HINT_ONLY")
        for i in range(2, 4):
            cases.append(dict(cases[0], case_id="case" + str(i), session_id="session" + str(i), observed_at="2026-10-10"))
        self.assertEqual(decide("habitual", cases)["action"], "GRADUAL_CANDIDATE")
        cases[0]["regressions"] = 1
        self.assertEqual(decide("fatal", cases)["action"], "REPAIR_REQUIRED")
        self.assertEqual(decide("habitual", cases)["action"], "ACCUMULATE")

    def test_same_session_and_no_gain_do_not_justify_habit_change(self):
        from skill_evolution import decide
        cases = [{"case_id": str(i), "session_id": "same", "observed_at": "2026-10-01",
                  "before": {"failures": 0}, "after": {"failures": 0}, "regressions": 0} for i in range(3)]
        self.assertEqual(decide("habitual", cases)["action"], "ACCUMULATE")
        with self.assertRaises(ValueError):
            decide("fatal", cases + [cases[0]])

    def test_evaluation_requires_unchanged_independent_paired_evidence(self):
        from skill_evolution import evaluate
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "source.md").write_text("Actual case observation", encoding="utf-8")
            case = {"case_id": "case1", "session_id": "actual-session", "observed_at": "2026-10-17",
                    "source": {"path": "source.md", "sha256": digest(root, "source.md")}, "regressions": 0}
            for stage, failures in (("before", 1), ("after", 0)):
                name = stage + ".json"
                (root / name).write_text(json.dumps({"case_id": "case1", "failures": failures}), encoding="utf-8")
                case[stage] = {"failures": failures, "evidence": name, "sha256": digest(root, name)}
            (root / "regressions.json").write_text(json.dumps({"regressions": 0, "command": "actual regression command"}), encoding="utf-8")
            case["regression_evidence"] = {"path": "regressions.json", "sha256": digest(root, "regressions.json")}
            document = {"schema_version": 1, "rule_id": "coverage", "severity": "fatal", "cases": [case]}
            self.assertEqual(evaluate(root, document)["action"], "FIX_NOW")
            (root / "after.json").write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed"):
                evaluate(root, document)


if __name__ == "__main__":
    unittest.main()
