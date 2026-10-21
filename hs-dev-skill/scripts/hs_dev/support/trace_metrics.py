"""Best-effort observed workflow spans; independent of business task state."""
import json
import os
import time
from pathlib import Path
from uuid import uuid4

from ..config import resolve
from ..storage import CONTROL, local, write_json
from . import trace


def observe(root, task_id, action, activity=None, selected=(), item=None, result=None, context=None):
    """Persist bounded per-task counters across CLI processes when trace is on.

    Duration is wall time in observed active spans, including human waiting.
    Retries count a check submission whose previous recorded result was FAIL.
    """
    try:
        settings = resolve(root)["values"]["trace"]
        if not (settings["enabled"] if trace.ENABLED.get() is None else trace.ENABLED.get()):
            return
        # Validate identities before using them in a filename or scope table.
        from ..task_store import catalog
        stages = {a["id"]: s["id"] for s in catalog()["stages"] for a in s["activities"]}
        if activity is not None and activity not in stages:
            return
        folder = Path(root) / CONTROL / "trace"
        path = local(root, f"{CONTROL}/trace/metrics/{task_id}.json")
        if path.parent != folder.resolve() / "metrics":
            return
        folder.mkdir(parents=True, exist_ok=True)
        lock = folder / ".metrics.lock"
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            trace.DROPPED += 1
            return
        try:
            cutoff = time.time() - settings["max_age_hours"] * 3600
            for expired in (folder / "metrics").glob("*.json"):
                if expired.stat().st_mtime < cutoff:
                    expired.unlink()
            retained = sorted((p for p in (folder / "metrics").glob("*.json") if p != path),
                              key=lambda p: p.stat().st_mtime, reverse=True)
            for expired in retained[max(0, settings["max_files"] - 1):]:
                expired.unlink()
            state = json.loads(path.read_text()) if path.exists() else {"scopes": {}, "checks": {}}
            instant = time.time()

            def scope(key, kind):
                return state["scopes"].setdefault(key, {"kind": kind, "duration_ms": 0,
                    "retry_count": 0, "context_chars": 0, "source_count": 0, "started": None})

            def report(key, outcome):
                row = state["scopes"][key]
                elapsed = max(0, instant - row["started"]) * 1000 if row["started"] is not None else 0
                trace.emit(root, row["kind"], {"task_id": task_id, "stage_id": stages.get(key, key),
                    **({"activity_id": key} if row["kind"] == "activity" else {}),
                    "outcome": outcome, "duration_ms": round(row["duration_ms"] + elapsed, 3),
                    "retry_count": row["retry_count"], "context_chars": row["context_chars"],
                    "source_count": row["source_count"]})

            def close(key, outcome):
                row = state["scopes"].get(key)
                if row:
                    report(key, outcome)
                    if row["started"] is not None:
                        row["duration_ms"] += max(0, instant - row["started"]) * 1000
                    row["started"] = None

            if action == "enter":
                previous = state.get("activity")
                if previous and previous != activity:
                    close(previous, "left")
                    if stages[previous] != stages[activity]:
                        close(stages[previous], "left")
                for key, kind in ((stages[activity], "stage"), (activity, "activity")):
                    row = scope(key, kind)
                    if row["started"] is None:
                        row["started"] = instant
                        report(key, "entered")
                state["activity"] = activity
            elif action == "check":
                state["approved"] = [a for a in state.get("approved", []) if a != activity]
                key = f"{activity}:{item}"
                retry = state["checks"].get(key) == "FAIL"
                state["checks"][key] = result
                for key, kind in ((stages[activity], "stage"), (activity, "activity")):
                    row = scope(key, kind)
                    row["retry_count"] += int(retry)
                    report(key, "check")
            elif action == "context":
                chars = sum(len(b["text"]) for b in context["body"])
                for key, kind in ((stages[activity], "stage"), (activity, "activity")):
                    row = scope(key, kind)
                    row["context_chars"] += chars
                    row["source_count"] += len(context["body"])
                    report(key, "context")
            elif action == "approve":
                for key in selected:
                    close(key, "completed")
                for stage in {stages[a] for a in selected}:
                    if all(a in state.get("approved", []) or a in selected for a in state.get("activities", selected) if stages[a] == stage):
                        close(stage, "completed")
                state["approved"] = sorted(set(state.get("approved", [])) | set(selected))
            elif action == "finish":
                for key in state["scopes"]:
                    close(key, result)
            if selected and action == "enter":
                state["activities"] = list(selected)
            write_json(path, state)
        finally:
            os.close(fd)
            lock.unlink(missing_ok=True)
    except (OSError, ValueError, TypeError, KeyError):
        trace.DROPPED += 1


def record_context(root, task_id, activity, context, duration_ms):
    context_id = str(uuid4())
    identity = {"task_id": task_id, "activity_id": activity,
                "stage_id": activity[0] if activity else None, "context_id": context_id}
    parent = trace.emit(root, "context", {**identity, "fragment_count": len(context["body"]),
        "bytes": context["usage"]["output_bytes"], "context_chars": sum(len(b["text"]) for b in context["body"]),
        "outcome": context["status"], "duration_ms": duration_ms})
    for body in context["body"]:
        trace.emit(root, "context_source", {**identity, "parent_event_id": parent, "source_path": body["path"],
            "start_line": body["start"], "end_line": body["end"], "context_chars": len(body["text"])})
    if task_id and activity:
        observe(root, task_id, "context", activity, context=context)
