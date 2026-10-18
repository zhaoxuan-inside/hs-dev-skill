"""Bounded, source-verified context assembly; histories are referenced, never bulk injected."""

from .indexing.engine import Index
from .storage import now

DEFAULT_CONTEXT_BYTES = 48_000


def assemble(root, paths, task_id=None, maximum=DEFAULT_CONTEXT_BYTES):
    if maximum <= 0 or maximum > DEFAULT_CONTEXT_BYTES:
        raise ValueError("Context budget must be between 1 and 48000 UTF-8 bytes")
    used, included, references = 0, [], []
    with Index(root) as index:
        for path in dict.fromkeys(paths):
            if "history" in path.split("/"):
                references.append(path)
                continue
            content = index.exact(path)
            size = len(content["text"].encode("utf-8"))
            if used + size > maximum:
                references.append(path)
                continue
            used += size
            included.append(content)
    return {"task_id": task_id, "assembled_at": now(), "bytes": used,
            "active": included, "on_demand": references}
