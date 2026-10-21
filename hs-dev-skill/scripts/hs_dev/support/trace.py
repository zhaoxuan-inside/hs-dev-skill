"""Optional bounded project-local trace; never evidence or recovery authority."""
from contextvars import ContextVar
import json
import os
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from ..config import resolve
from ..storage import CONTROL, now, write_json

RUN = ContextVar("hs_trace_run", default=None)
ENABLED = ContextVar("hs_trace_enabled", default=None)
DROPPED = 0
FIELDS = {"name", "outcome", "reason_code", "duration_ms", "fragment_count", "bytes",
          "cache_hit", "score", "requires_model", "route", "task_id", "activity_id", "operation_id", "ok",
          "scope", "actor", "stage_id", "retry_count", "context_chars", "context_id",
          "source_path", "start_line", "end_line", "source_count", "check_id", "parent_event_id"}


def emit(root, event, facts):
    global DROPPED
    try:
        settings = resolve(root)["values"]["trace"]
        if not (settings["enabled"] if ENABLED.get() is None else ENABLED.get()):
            return
        attributes = {k: v for k, v in facts.items() if k in FIELDS and isinstance(v, (str, int, float, bool, type(None)))}
        # Source paths must remain exact; oversized events are dropped, never
        # silently attributed to a truncated (and potentially different) path.
        attributes = {k: v[:160] if isinstance(v, str) and k != "source_path" else v for k, v in attributes.items()}
        from ..workspace import CURRENT
        permit = CURRENT.get()
        event_data = {"event_id": str(uuid4()), "run_id": RUN.get() or str(uuid4()), "timestamp": now(),
                      "event": event[:64], "operation_id": permit.operation_id if permit else None,
                      "dropped_events": DROPPED, "attributes": attributes}
        encoded = (json.dumps(event_data, ensure_ascii=False) + "\n").encode()
        if len(encoded) > settings["max_event_bytes"]:
            DROPPED += 1
            return
        folder = Path(root) / CONTROL / "trace"
        folder.mkdir(parents=True, exist_ok=True)
        lock = folder / ".write.lock"
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            DROPPED += 1
            return
        try:
            cutoff = time.time() - settings["max_age_hours"] * 3600
            for expired in folder.glob("events*.jsonl"):
                if expired.stat().st_mtime < cutoff:
                    expired.unlink()
            links_path = folder / "links.json"
            links = json.loads(links_path.read_text()) if links_path.exists() else {}
            links = {k: v for k, v in links.items() if v["updated"] >= cutoff}
            task_id = attributes.get("task_id")
            cursor = links.get(task_id, {}) if task_id else {}
            if task_id:
                activity = attributes.get("activity_id")
                stage = attributes.get("stage_id") or (activity[0] if activity else None)
                if stage:
                    attributes["stage_id"] = stage
                event_data["previous_event_id"] = cursor.get("last")
                scopes = cursor.setdefault("scopes", {})
                parent = attributes.pop("parent_event_id", None)
                if not parent:
                    parent = (scopes.get(activity) if activity and event != "activity" else None)
                    parent = parent or (scopes.get(stage) if stage and event != "stage" else None)
                    parent = parent or cursor.get("root")
                event_data["parent_event_id"] = parent
                check = attributes.get("check_id")
                if event == "check" and check:
                    prior = cursor.setdefault("checks", {}).get(f"{activity}:{check}")
                    if prior and prior["outcome"] == "FAIL":
                        event_data["retry_of_event_id"] = prior["event_id"]
                    cursor["checks"][f"{activity}:{check}"] = {
                        "event_id": event_data["event_id"], "outcome": attributes.get("outcome")}
                if event in {"stage", "activity"} and attributes.get("outcome") == "entered":
                    scopes[activity if event == "activity" else stage] = event_data["event_id"]
                cursor.update(last=event_data["event_id"], root=cursor.get("root") or event_data["event_id"], updated=time.time())
                links[task_id] = cursor
            elif attributes.get("parent_event_id"):
                event_data["parent_event_id"] = attributes.pop("parent_event_id")
            encoded = (json.dumps(event_data, ensure_ascii=False) + "\n").encode()
            if len(encoded) > settings["max_event_bytes"]:
                DROPPED += 1
                return
            path = folder / "events.jsonl"
            if path.exists() and path.stat().st_size + len(encoded) > settings["max_file_bytes"]:
                for number in range(settings["max_files"] - 1, 0, -1):
                    source = folder / ("events.jsonl" if number == 1 else f"events.{number-1}.jsonl")
                    target = folder / f"events.{number}.jsonl"
                    if source.exists():
                        source.replace(target)
                if settings["max_files"] == 1:
                    path.unlink(missing_ok=True)
            with path.open("ab") as stream:
                stream.write(encoded)
            if task_id:
                retained = sorted(links, key=lambda k: links[k]["updated"], reverse=True)[:settings["max_files"]]
                write_json(links_path, {k: links[k] for k in retained})
            return event_data["event_id"]
        finally:
            os.close(fd)
            lock.unlink(missing_ok=True)
    except (OSError, ValueError, TypeError, KeyError):
        DROPPED += 1


def query(root, limit=20, **filters):
    if not 1 <= limit <= 100:
        raise ValueError("Trace limit must be between 1 and 100")
    since, until = filters.pop("since", None), filters.pop("until", None)
    def timestamp(value):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() if value else None
    lower, upper = timestamp(since), timestamp(until)
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("Trace time range is reversed")
    allowed = {"run_id", "task_id", "stage_id", "activity_id", "operation_id", "event", "outcome", "context_id"}
    if set(filters) - allowed:
        raise ValueError("Unknown trace filter")
    result = []
    folder = Path(root) / CONTROL / "trace"
    for path in sorted(folder.glob("events*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                observed = timestamp(row["timestamp"])
                if (lower is not None and observed < lower) or (upper is not None and observed > upper):
                    continue
                if all(row.get(k, row.get("attributes", {}).get(k)) == v for k, v in filters.items() if v is not None):
                    result.append(row)
                    if len(result) >= limit:
                        return {"events": result, "dropped_events": DROPPED}
    return {"events": result, "dropped_events": DROPPED}
