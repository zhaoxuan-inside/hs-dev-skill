"""Goal-directed, version-checked filesystem context with mandatory budgets."""
from contextlib import nullcontext
from pathlib import Path
from .indexing.engine import Index, fingerprint
from .storage import CONTROL, local, now, sha
from .workspace import Workspace

DEFAULT_CONTEXT_BYTES = 48_000


class ContextProvider:
    def __init__(self, root, index=None, resident=None):
        self.root = Path(root).resolve()
        self.index = index
        self.resident = resident

    def obtain(self, paths=(), task_id=None, maximum=DEFAULT_CONTEXT_BYTES, query=None, required=()):
        if maximum <= 0 or maximum > DEFAULT_CONTEXT_BYTES:
            raise ValueError("Context byte budget must be between 1 and 48000")
        workspace = Workspace(self.root)
        ticket = workspace.ticket(timeout=1)
        required_set = set(required)
        requests = [(path, 1, None if path in required_set else 80, "explicit") for path in dict.fromkeys([*required, *paths])]
        used, included, references, missing, observed = 0, [], [], [], {}
        if task_id:
            from .task_store import load_task
            task = load_task(self.root, task_id)
            path = f"{CONTROL}/tasks/{task_id}/current.md"
            requests.insert(0, (path, 1, None, "current_task"))
            required_set.add(path)
            for dep in task.get("dependencies", []):
                if dep["consumer"] == task["current_activity"]:
                    requests.append((dep["path"], 1, None, "upstream"))
                    required_set.add(dep["path"])
        manager = nullcontext(self.index) if self.index else Index(self.root)
        with manager as index:
            with index.read_session():
                index.ensure()
                if query:
                    requests.extend((row["path"], row["start"] or 1, row["end"], "query") for row in index.search(query))
                if self.resident:
                    self.resident.refresh()
                seen = set()
                # Mandatory contracts precede optional source slices.
                requests.sort(key=lambda r: r[0] not in required_set)
                for path, start, end, reason in requests:
                    key = (path, start, end)
                    if key in seen or any(item["path"] == path and item.get("end") is None for item in included):
                        continue
                    seen.add(key)
                    parts = Path(path).parts
                    runtime = bool(parts and parts[0] == CONTROL)
                    allowed_runtime = (task_id and parts[:3] == (CONTROL, "tasks", task_id)
                                   and (parts[3:] in {("current.md",), ("plan.md",)}
                                        or (len(parts) > 4 and parts[3] == "evidence")))
                    if "history" in parts or (runtime and not allowed_runtime):
                        raise ValueError("Private recovery/runtime data is excluded from model context")
                    file = local(self.root, path)
                    if not file.is_file():
                        missing.append(path)
                        continue
                    if (end is None or runtime) and file.stat().st_size > maximum - used:
                        (missing if path in required_set else references).append(path)
                        continue
                    if runtime:
                        pinned = self.resident.items.get(path) if self.resident else None
                        data = pinned["text"].encode() if pinned else file.read_bytes()
                        content = {"path": path, "text": data.decode(), "source_digest": sha(data),
                                   "source": "hot" if pinned else "task_filesystem", "start": 1, "end": None}
                    else:
                        content = index.exact(path, start=start, end=end)
                        content.update(source="filesystem", start=start, end=end)
                    size = len(content["text"].encode())
                    if used + size > maximum:
                        (missing if path in required_set else references).append(path)
                        continue
                    content["selection_reason"] = reason
                    observed[path] = content["source_digest"]
                    used += size
                    included.append(content)
                for path, digest in observed.items():
                    if fingerprint(local(self.root, path)) != digest:
                        raise ValueError("Context source changed; discard and retry")
                if not index.verify()["ok"]:
                    raise ValueError("Workspace changed during context assembly")
        workspace.validate_ticket(ticket)
        from .support.trace import emit
        emit(self.root, "context", {"fragment_count": len(included), "bytes": used,
                                   "outcome": "missing" if missing else "ok", "task_id": task_id})
        return {"ok": not missing, "task_id": task_id, "revision": ticket.revision, "assembled_at": now(),
                "bytes": used, "estimated_tokens": used, "token_count_kind": "utf8_byte_upper_estimate",
                "active": included, "on_demand": list(dict.fromkeys(references)),
                "missing_requirements": list(dict.fromkeys(missing))}


def assemble(root, paths=(), task_id=None, maximum=DEFAULT_CONTEXT_BYTES, query=None, required=()):
    return ContextProvider(root).obtain(paths, task_id, maximum, query, required)
