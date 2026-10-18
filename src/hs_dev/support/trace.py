"""Best-effort project-local telemetry with no authority over workflow state."""

import warnings
from pathlib import Path
from ..config import resolve
from ..storage import CONTROL, append_event


def emit(root, event, facts):
    try:
        if resolve(root)["values"]["trace"]["enabled"]:
            append_event(Path(root) / CONTROL / "trace/events.jsonl", {"event": event, "facts": facts})
    except (OSError, ValueError):
        warnings.warn("Optional trace write failed", RuntimeWarning)
