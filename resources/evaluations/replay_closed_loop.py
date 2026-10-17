#!/usr/bin/env python3
"""Replay observed audit gaps against an explicitly selected local Skill bundle.

Run each bundle/case in a fresh process. All project mutations use a temporary
workspace; stdout is JSON evidence. These are audit reproductions, not incidents.
"""

import argparse
import contextlib
import io
import json
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path


def replay(bundle, case_id):
    sys.path.insert(0, str(Path(bundle).resolve() / "scripts"))
    # Old packages lack the registry fixture builder. It only prepares input;
    # the gate and verifier under evaluation always come from the chosen bundle.
    sys.path.append(str(Path(__file__).resolve().parents[2] / "scripts"))
    from baseline_gate import digest, freeze, register_artifact
    from init_hs_dev_docs import init_full_workspace
    from skill_trace import collect_events, save_skill_execution_config
    from task_manager import TaskManager

    capture = io.StringIO()
    error = ""
    rejected = False
    observed_actions = []
    with tempfile.TemporaryDirectory(prefix="hs-skill-replay-") as temporary, contextlib.redirect_stdout(capture):
        root = Path(temporary)
        init_full_workspace(str(root))
        manager = TaskManager(str(root))
        save_skill_execution_config(root, {"features": {"skill_trace": True}})
        manager.create_task("audit", "Replay audit gap", change_size="S")
        manager.set_status("audit", "IN_PROGRESS")
        if case_id == "tool-linkage":
            from process_log import checkpoint
            checkpoint(root, "audit", "S1", "before changing", ["new.py"])
            _, events = collect_events(root, task_id="audit")
            observed_actions = [e["data"]["action"] for e in events if e["event"] == "tool_result"]
            failures = int(not {"task_created", "task_transition", "checkpoint"}.issubset(observed_actions))
        else:
            (root / "scope.md").write_text("REQ-A save once\nREQ-B recover on retry\n", encoding="utf-8")
            (root / "result.md").write_text("Isolated replay implementation artifact", encoding="utf-8")
            with (root / "run.log").open("wb") as stream:
                subprocess.run([sys.executable, "-c", "print('isolated replay probe passed')"], stdout=stream, check=True)
            baseline = freeze(root, "scope1", "1", "scope.md", ["REQ-A", "REQ-B"],
                              {"source": "isolated replay fixture", "excerpt": "Both requirements accepted in fixture"},
                              {"audit": ["REQ-A", "REQ-B"]})
            register_artifact(root, "result1", "result.md", ["scope1"])
            record = {
                "schema_version": 1, "task_id": "audit", "acceptance_status": "ACCEPTED",
                "baseline": {"id": "scope1", "version": "1", "sha256": baseline["sha256"]},
                "artifacts": ["result1"],
                "requirements": [{"id": req, "result": "PASS", "evidence": "run.log"} for req in ("REQ-A", "REQ-B")],
                "verification": {"tests": [{"command": "python -c replay-probe", "exit_code": 0,
                                             "evidence": "run.log", "sha256": digest(root, "run.log")}]},
                "developer_confirmation": {"decision": "ACCEPTED", "reviewer": "test fixture",
                                           "confirmed_at": "2026-10-17T00:00:00Z", "source": "fixture",
                                           "excerpt": "Fixture only; not a real developer sign-off"},
                "checks": [{"rule_id": "DELIV-01", "result": "PASS", "evidence": "run.log"}],
                "dod": [{"criterion": "Both scenarios verified", "result": "PASS", "evidence": "run.log"}],
                "unimplemented": [],
            }
            if case_id == "omitted-requirement":
                record["requirements"].pop()
                expected_error = "denominator mismatch"
            elif case_id == "stale-source":
                (root / "scope.md").write_text("REQ-A changed\nREQ-B recover\n", encoding="utf-8")
                expected_error = "baseline is invalid"
            else:
                (root / "run.log").unlink()
                expected_error = "run.log"
            (root / "acceptance.md").write_text("<!-- HS_ACCEPTANCE_GATE_V1\n" + json.dumps(record)
                                                + "\nHS_ACCEPTANCE_GATE_V1 -->", encoding="utf-8")
            manager.set_status("audit", "VERIFYING")
            try:
                manager.set_status("audit", "COMPLETED", acceptance_record="acceptance.md")
            except (ValueError, OSError) as exc:
                rejected, error = True, str(exc)
            failures = int(not rejected or expected_error not in error)
    return {"case_id": case_id, "failures": failures, "rejected": rejected, "error": error,
            "bundle": str(Path(bundle).resolve()), "observed_actions": observed_actions,
            "subject_sha256": {name: hashlib.sha256((Path(bundle) / "scripts" / name).read_bytes()).hexdigest()
                               for name in ("task_manager.py", "verify_consistency.py", "process_log.py")},
            "gate_log": capture.getvalue(), "origin": "2026-10-17 audit reproduction"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--case", required=True, choices=("omitted-requirement", "stale-source", "missing-evidence", "tool-linkage"))
    args = parser.parse_args()
    result = replay(args.bundle, args.case)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
