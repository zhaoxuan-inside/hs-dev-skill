#!/usr/bin/env python3
"""Evidence-based update recommendations; never rewrite or publish Skill rules."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from baseline_gate import digest, local_path


def decide(severity, cases):
    if severity not in ("fatal", "habitual", "advisory"):
        raise ValueError("Unknown optimization severity")
    if not isinstance(cases, list) or not cases:
        raise ValueError("At least one paired case is required")
    ids, sessions, days = set(), set(), []
    before, after, regressions = 0, 0, 0
    for case in cases:
        key = case.get("case_id")
        if not isinstance(key, str) or not key or key in ids or not case.get("session_id"):
            raise ValueError("Unique cases and original session IDs are required")
        ids.add(key)
        sessions.add(case["session_id"])
        days.append(date.fromisoformat(case["observed_at"]))
        for stage in ("before", "after"):
            failures = case[stage]["failures"]
            if type(failures) is not int or failures < 0:
                raise ValueError("Failure counts must be nonnegative integers")
        regression = case.get("regressions")
        if type(regression) is not int or regression < 0:
            raise ValueError("Explicit nonnegative regression count is required")
        before += case["before"]["failures"]
        after += case["after"]["failures"]
        # Aggregate improvement cannot hide a newly failing case.
        regressions += regression + max(0, case["after"]["failures"] - case["before"]["failures"])
    elapsed = (max(days) - min(days)).days
    improved = after < before and regressions == 0
    if severity == "fatal":
        action = "FIX_NOW" if after == 0 and improved else "REPAIR_REQUIRED"
    elif severity == "habitual":
        action = "GRADUAL_CANDIDATE" if improved and len(ids) >= 3 and len(sessions) >= 3 and elapsed >= 7 else "ACCUMULATE"
    else:
        action = "HINT_ONLY"
    return {"severity": severity, "action": action, "cases": len(ids),
            "independent_sessions": len(sessions), "observation_days": elapsed,
            "before_failures": before, "after_failures": after, "regressions": regressions,
            "automatic_rule_change": False,
            "next": "Verify, review scope, version and rollback before adoption"}


def evaluate(root, document):
    """Check paired run evidence against immutable digests, including zero regressions."""
    if document.get("schema_version") != 1 or not document.get("rule_id"):
        raise ValueError("Evaluation needs schema_version=1 and rule_id")
    cases = document.get("cases")
    if not isinstance(cases, list):
        raise ValueError("Evaluation cases must be a list")
    evidence_paths = set()
    for case in cases:
        source = case["source"]
        if source.get("sha256") != digest(root, source["path"]):
            raise ValueError("Case source evidence changed")
        for stage in ("before", "after"):
            run = case[stage]
            path = local_path(root, run["evidence"])
            if path in evidence_paths:
                raise ValueError("Paired evidence must use distinct run files")
            evidence_paths.add(path)
            if run.get("sha256") != digest(root, run["evidence"]):
                raise ValueError("Run evidence changed")
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("case_id") != case["case_id"] or payload.get("failures") != run.get("failures"):
                raise ValueError("Run result does not match paired evaluation")
        regression = case["regression_evidence"]
        if regression.get("sha256") != digest(root, regression["path"]):
            raise ValueError("Regression evidence changed")
        result = json.loads(local_path(root, regression["path"]).read_text(encoding="utf-8"))
        if result.get("regressions") != case.get("regressions") or not result.get("command"):
            raise ValueError("Regression report must match case and contain executed command")
    return dict(decide(document["severity"], cases), rule_id=document["rule_id"])


def main(argv=None):
    from hs_paths import ensure_utf8_stdout
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", required=True, help="Workspace-relative paired evaluation JSON")
    args = parser.parse_args(argv)
    try:
        path = local_path(args.root, args.input)
        result = evaluate(args.root, json.loads(path.read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["action"] == "REPAIR_REQUIRED" else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
