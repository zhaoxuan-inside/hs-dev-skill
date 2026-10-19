"""Workspace-contained paths, atomic publication and exclusive mutation locks."""

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

CONTROL = "hs-dev-skill"
IGNORED = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".hs_cache", "dist", "build", "logs", "output", "htmlcov"}
GENERATED_NAMES = {"file_index.jsonl", "content_index.jsonl"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def identifier():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def local(root, relative):
    root = Path(root).resolve()
    value = Path(relative)
    if value.is_absolute() or ".." in value.parts or not value.parts:
        raise ValueError("Expected a nonempty workspace-relative path")
    candidate = root / value
    for part in [candidate, *candidate.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("Symlink paths are not managed")
    candidate.resolve().relative_to(root)
    return candidate


def atomic(path, data):
    from .workspace import CURRENT, Workspace
    permit = CURRENT.get()
    if permit:
        Workspace(permit.root).assert_owner(permit)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=".hs-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if permit:
            Workspace(permit.root).assert_owner(permit)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def write_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def append_event(path, event):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(dict(event, recorded_at=now()), ensure_ascii=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def managed_files(root, runtime=False):
    """Stream paths; recovery includes task/config state but excludes its own data."""
    root = Path(root).resolve()
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        rel = base.relative_to(root)
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and not d.endswith(".egg-info") and not (base / d).is_symlink())
        if not runtime:
            dirs[:] = [d for d in dirs if d != "history"]
        if not runtime and rel == Path("."):
            dirs[:] = [d for d in dirs if d != CONTROL]
        if runtime and rel == Path(CONTROL):
            dirs[:] = [d for d in dirs if d in {"tasks", "config"}]
        for name in sorted(files):
            path = base / name
            if path.is_symlink() or name.startswith(".hs-write-") or name == ".coverage":
                continue
            if not runtime and name in GENERATED_NAMES:
                continue
            if rel == Path(CONTROL) and name not in {"task_index.jsonl"}:
                continue
            yield path


def managed_directories(root):
    root = Path(root).resolve()
    for directory, dirs, _ in os.walk(root, followlinks=False):
        base = Path(directory)
        rel = base.relative_to(root)
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and not d.endswith(".egg-info") and not (base / d).is_symlink())
        if rel == Path(CONTROL):
            dirs[:] = [d for d in dirs if d in {"tasks", "config"}]
        if rel != Path("."):
            yield base


@contextmanager
def workspace_lock(root, recovery=False, initialize=False, operation_id=None, fence=None, task_id=None):
    from .workspace import operation
    with operation(root, recovery=recovery, initialize=initialize, operation_id=operation_id, fence=fence, task_id=task_id) as permit:
        yield permit
