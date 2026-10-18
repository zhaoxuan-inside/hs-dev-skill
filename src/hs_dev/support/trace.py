"""Optional bounded project-local trace; never evidence or recovery authority."""
from contextvars import ContextVar
import json
import os
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from ..config import resolve
from ..storage import CONTROL, now

RUN = ContextVar("hs_trace_run", default=None)
ENABLED = ContextVar("hs_trace_enabled", default=None)
DROPPED = 0
FIELDS = {"name", "outcome", "reason_code", "duration_ms", "fragment_count", "bytes",
          "cache_hit", "score", "requires_model", "route", "task_id", "activity_id", "operation_id", "ok",
          "scope", "actor"}


def emit(root, event, facts):
    global DROPPED
    try:
        settings = resolve(root)["values"]["trace"]
        if not (settings["enabled"] if ENABLED.get() is None else ENABLED.get()):
            return
        attributes = {k: v for k, v in facts.items() if k in FIELDS and isinstance(v, (str, int, float, bool, type(None)))}
        attributes = {k: v[:160] if isinstance(v, str) else v for k, v in attributes.items()}
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
    allowed = {"run_id", "task_id", "activity_id", "operation_id", "event", "outcome"}
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
