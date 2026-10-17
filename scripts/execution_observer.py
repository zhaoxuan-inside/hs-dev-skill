#!/usr/bin/env python3
"""Best-effort tool facts, recorded in isolated sessions without shared writers."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from skill_trace import is_trace_enabled, record_event, start_session


def emit(root, tool, action, result="ok", task_id=None, facts=None):
    """Never change tool success/failure because optional telemetry failed."""
    try:
        root = Path(root).resolve()
        if not is_trace_enabled(root):
            return
        session = start_session(root, host="tool:" + tool)["session_id"]
        if task_id:
            record_event(root, session, "task_link", {"task_id": task_id}, ref=task_id)
        record_event(root, session, "tool_result", {
            "producer": tool, "action": action, "result": result,
            "facts": facts or {}, "source": "tool",
        })
        record_event(root, session, "session_end", {"reason": "completed" if result == "ok" else "aborted"})
    except Exception as exc:
        print("[TRACE WARNING] Tool fact could not be recorded: " + str(exc), file=sys.stderr)


def run_observed(root, task_id, command, evidence):
    """Run an argv array without a shell and persist actual output plus exit code."""
    import subprocess
    from baseline_gate import digest, local_path

    if not command or not isinstance(command, list) or not all(isinstance(c, str) and c for c in command):
        raise ValueError("Command must be a nonempty argv array")
    destination = local_path(root, evidence)
    if destination.exists():
        raise ValueError("Evidence path already exists; choose a new run path")
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with destination.open("xb") as stream:
        try:
            process = subprocess.run(command, cwd=Path(root), stdout=stream, stderr=subprocess.STDOUT)
            code = process.returncode
        except OSError as exc:
            stream.write(str(exc).encode("utf-8"))
            code = 127
    facts = {"exit_code": code, "evidence": evidence,
             "sha256": digest(root, evidence), "duration_ms": round((time.monotonic() - started) * 1000)}
    # Commands/arguments may contain credentials; never duplicate them in telemetry.
    emit(root, "execution_observer", "verification", "ok" if code == 0 else "fail", task_id, facts)
    return dict(facts, command=command)


def main(argv=None):
    import argparse
    import json
    from hs_paths import ensure_utf8_stdout

    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--task", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    try:
        result = run_observed(Path(args.root), args.task, command, args.evidence)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result["exit_code"] if result["exit_code"] >= 0 else 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
