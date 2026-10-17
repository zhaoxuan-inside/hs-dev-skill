#!/usr/bin/env python3
"""Read-only retrospective: explicit denominators, missing data, no invented rates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from baseline_gate import inspect_registry, load_registry
from skill_trace import collect_events, is_trace_enabled, list_session_files, validate_session


def build_report(root, task_id=None):
    root = Path(root).resolve()
    sessions, events = collect_events(root, task_id=task_id)
    tool_events = [e["data"] for e in events if e.get("event") == "tool_result"]
    counts = {}
    for event in events:
        name = event.get("event", "unknown")
        counts[name] = counts.get(name, 0) + 1
    checks = [e for e in tool_events if e.get("action") in ("completion_gate", "baseline_check")]
    runs = [e for e in tool_events if e.get("action") == "verification"]
    state = load_registry(root)
    validity = inspect_registry(root, state)
    denominators = {
        baseline_id: {key: ids for key, ids in baseline.get("assignments", {}).items()
                      if task_id is None or task_id == key}
        for baseline_id, baseline in state["baselines"].items()
        if baseline.get("status") != "SUPERSEDED"
    }
    problems = []
    for path in list_session_files(root):
        if path.stem in sessions:
            result = validate_session(path, root)
            if result["errors"] or result["warnings"]:
                problems.append({"session": path.stem, **result})
    return {
        "schema_version": 1, "scope": task_id or "project", "trace_enabled": is_trace_enabled(root),
        "sessions": len(sessions), "events": counts, "trace_problems": problems,
        "baseline_validity": validity, "requirement_denominators": denominators,
        "observed_gate_attempts": len(checks),
        "observed_gate_failures": sum(e.get("result") != "ok" for e in checks),
        "observed_verification_runs": len(runs),
        "observed_verification_failures": sum(e.get("result") != "ok" for e in runs),
        "observed_execution_ms": sum(e.get("facts", {}).get("duration_ms", 0) for e in runs),
        "deviations": [e["data"] for e in events if e.get("event") == "deviation"],
        "missing_data": [
            "Agent/hook omissions cannot be measured from self-reports alone",
            "First-pass acceptance and wait duration require complete stage acceptance events",
            "Requirement omission/rework rates require reviewed cause and effort records",
            "Registered requirement denominator is not proof of verified coverage",
        ] + (["No trace events in selected scope"] if not events else []),
    }


def render_markdown(report):
    lines = ["# Skill 执行复盘", "", "范围：" + report["scope"], "",
             "| 观测项 | 数值 |", "|---|---:|"]
    for label, key in (("会话", "sessions"), ("门禁尝试", "observed_gate_attempts"),
                       ("门禁失败", "observed_gate_failures"), ("验证运行", "observed_verification_runs"),
                       ("验证失败", "observed_verification_failures"), ("验证执行毫秒", "observed_execution_ms")):
        lines.append("| {} | {} |".format(label, report[key]))
    lines += ["", "基线检查：" + ("有效" if report["baseline_validity"]["ok"] else "存在失效项"),
              "", "```json", json.dumps(report, ensure_ascii=False, indent=2), "```", ""]
    return "\n".join(lines)


def main(argv=None):
    from hs_paths import ensure_utf8_stdout
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--task")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.root, args.task)
        print(render_markdown(report) if args.format == "markdown" else json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
