"""Snapshots and changelog form one conflict-aware, verifiable recovery system."""

from ..contracts import OperationState

import os
import ast
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from ..storage import CONTROL, append_event, atomic, identifier, local, managed_files, managed_directories, now, read_json, sha, write_json
from ..contracts import TaskStatus

RECOVERY = f"{CONTROL}/recovery"


def capture(root, task_id, kind="task"):
    root = Path(root).resolve()
    snapshot_id = identifier()
    folder = root / RECOVERY / "snapshots" / snapshot_id
    objects = root / RECOVERY / "objects"
    files = {}
    for path in managed_files(root, runtime=True):
        data = path.read_bytes()
        digest = sha(data)
        object_path = objects / digest
        if not object_path.exists():
            atomic(object_path, data)
        if sha(object_path.read_bytes()) != digest:
            raise ValueError("Corrupt recovery object: " + digest)
        stat = path.stat()
        files[str(path.relative_to(root))] = {"sha256": digest, "mode": stat.st_mode & 0o777,
                                               "mtime_ns": stat.st_mtime_ns, "atime_ns": stat.st_atime_ns}
    directories = set()
    for relative in files:
        parent = Path(relative).parent
        while parent != Path("."):
            directories.add(str(parent))
            parent = parent.parent
    directories.update(str(p.relative_to(root)) for p in managed_directories(root))
    manifest = {"schema_version": 1, "snapshot_id": snapshot_id, "task_id": task_id,
                "kind": kind, "created_at": now(), "files": files, "directories": sorted(directories)}
    write_json(folder / "manifest.json", manifest)
    append_event(root / RECOVERY / "audit.jsonl", {"event": "snapshot", "snapshot_id": snapshot_id, "task_id": task_id})
    from ..config import resolve
    settings = resolve(root, task_id)["values"]["retention"]
    protected = {snapshot_id}
    for task_file in (root / CONTROL / "tasks").glob("*/task.json"):
        task = read_json(task_file)
        if task.get("status") == TaskStatus.ACTIVE and task.get("snapshot_id"):
            protected.add(task["snapshot_id"])
    retain(root, settings["hours"], settings["snapshots"], protected)
    return snapshot_id


def manifest(root, snapshot_id):
    value = read_json(local(root, f"{RECOVERY}/snapshots/{snapshot_id}/manifest.json"))
    if value is None or value.get("snapshot_id") != snapshot_id:
        raise ValueError("Recovery point unavailable")
    for relative, entry in value["files"].items():
        local(root, relative)
        digest = entry["sha256"]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid recovery object key")
        path = Path(root) / RECOVERY / "objects" / digest
        if not path.exists() or sha(path.read_bytes()) != digest:
            raise ValueError("Missing or corrupt recovery data")
    return value


def restore(root, snapshot_id, expected=None):
    """expected is the complete postimage for conflict detection; explicit recovery only."""
    root = Path(root).resolve()
    saved = manifest(root, snapshot_id)
    if expected is not None:
        conflicts = []
        for relative, digest in expected.items():
            path = local(root, relative)
            actual = sha(path.read_bytes()) if path.is_file() else None
            if actual != digest:
                conflicts.append(relative)
        if conflicts:
            raise ValueError("Later edits conflict with restore: " + ", ".join(conflicts))
    current = {str(p.relative_to(root)) for p in managed_files(root, runtime=True)}
    selected = set(expected) if expected is not None else current | set(saved["files"])
    for relative in sorted(selected):
        path = local(root, relative)
        entry = saved["files"].get(relative)
        if entry is None:
            if path.exists():
                path.unlink()
        else:
            atomic(path, (root / RECOVERY / "objects" / entry["sha256"]).read_bytes())
            path.chmod(entry["mode"])
            os.utime(path, ns=(entry["atime_ns"], entry["mtime_ns"]))
    for relative in saved["directories"]:
        if expected is None:
            local(root, relative).mkdir(parents=True, exist_ok=True)
    if expected is None:
        for directory in sorted(managed_directories(root), key=lambda p: len(p.parts), reverse=True):
            if str(directory.relative_to(root)) not in saved["directories"]:
                directory.rmdir()
    parents = {str(Path(relative).parent) for relative in selected}
    for relative in sorted(parents, key=lambda p: len(Path(p).parts), reverse=True):
        parent = local(root, relative) if relative != "." else root
        while parent != root and str(parent.relative_to(root)) not in saved["directories"]:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    for relative in selected:
        path = local(root, relative)
        entry = saved["files"].get(relative)
        if (entry and (not path.is_file() or sha(path.read_bytes()) != entry["sha256"])) or (entry is None and path.exists()):
            raise ValueError("Restore verification failed: " + relative)
    append_event(root / RECOVERY / "audit.jsonl", {"event": "restore", "snapshot_id": snapshot_id})
    return saved


def retain(root, hours=48, maximum=5, protected=()):
    """Expire dependent journals explicitly and GC only objects with no live references."""
    root = Path(root)
    protected = set(protected)
    for path in (root / RECOVERY / "operations").glob("*.json"):
        operation = read_json(path)
        if operation.get("state") in {OperationState.PREPARED, OperationState.VERIFIED, OperationState.INTERRUPTED}:
            protected.add(operation["snapshot_id"])
    directory = root / RECOVERY / "snapshots"
    snapshots = sorted(directory.glob("*/manifest.json"), reverse=True)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    removed = []
    protected_count = sum(path.parent.name in protected for path in snapshots)
    remaining_slots = max(0, maximum - protected_count)
    retained = 0
    for path in snapshots:
        saved = read_json(path)
        if saved["snapshot_id"] in protected:
            continue
        age = datetime.fromisoformat(saved["created_at"].replace("Z", "+00:00"))
        if retained >= remaining_slots or age < cutoff:
            removed.append(saved["snapshot_id"])
            shutil.rmtree(path.parent)
        else:
            retained += 1
    for path in (root / RECOVERY / "operations").glob("*.json"):
        operation = read_json(path)
        if operation.get("snapshot_id") in removed:
            operation["recovery_available"] = False
            write_json(path, operation)
    live = set()
    for path in directory.glob("*/manifest.json"):
        live.update(e["sha256"] for e in read_json(path)["files"].values())
    for path in (root / RECOVERY / "objects").glob("*"):
        if path.name not in live:
            path.unlink()
    if removed:
        append_event(root / RECOVERY / "audit.jsonl", {"event": "expire", "snapshot_ids": removed})
    return removed


def commit(root, task_id, changes, verification):
    """A recoverable publish protocol, not a claim of filesystem-wide atomicity."""
    from ..indexing.engine import Index
    from ..verification import run_checks, verify_workspace
    root = Path(root).resolve()
    if not changes or not verification:
        raise ValueError("Commit requires changes and real verification commands")
    verify_workspace(root, require_clean=True)
    normalized = {}
    for relative, content in changes.items():
        path = local(root, relative)
        rel = path.relative_to(root)
        from ..workspace import CURRENT
        permit = CURRENT.get()
        if permit and permit.scope and not any(str(rel) == p or str(rel).startswith(p.rstrip("/") + "/") for p in permit.scope):
            raise ValueError("Change is outside the UUID scope: " + str(rel))
        if rel.parts[0] in {CONTROL, ".git"} or path.name in {"file_index.jsonl", "content_index.jsonl"}:
            raise ValueError("Cannot directly mutate runtime state or derived indices")
        if not isinstance(content, (str, type(None))):
            raise ValueError("Changes must contain UTF-8 strings or null (delete)")
        normalized[str(rel)] = content
    snapshot_id = capture(root, task_id, "operation")
    operation_id = identifier()
    operation_path = root / RECOVERY / "operations" / (operation_id + ".json")
    operation = {"operation_id": operation_id, "task_id": task_id, "snapshot_id": snapshot_id,
                 "created_at": now(), "state": OperationState.PREPARED, "recovery_available": True,
                 "paths": list(normalized), "postimage": {}}
    write_json(operation_path, operation)
    try:
        for relative, content in normalized.items():
            path = local(root, relative)
            if content is None:
                path.unlink(missing_ok=True)
            else:
                atomic(path, content)
            operation["postimage"][relative] = sha(path.read_bytes()) if path.exists() else None
            write_json(operation_path, operation)
        objects = []
        before = manifest(root, snapshot_id)["files"]
        for relative in normalized:
            symbols = set()
            versions = []
            if relative.endswith(".py"):
                if relative in before:
                    versions.append((root / RECOVERY / "objects" / before[relative]["sha256"]).read_text(encoding="utf-8"))
                if normalized[relative] is not None:
                    versions.append(normalized[relative])
                for text in versions:
                    try:
                        symbols.update(node.name for node in ast.walk(ast.parse(text)) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
                    except SyntaxError:
                        symbols.add("PARSE_ERROR")
            objects.extend({"path": relative, "symbol": symbol} for symbol in sorted(symbols))
            if not symbols:
                objects.append({"path": relative, "symbol": "file"})
        operation["affected_objects"] = objects
        write_json(operation_path, operation)
        affected = root / CONTROL / "tasks" / task_id / "affected_objects.md"
        previous_text = affected.read_text(encoding="utf-8") if affected.exists() else "# 实际修改对象\n\n| 操作 | 文件 | 符号 |\n|---|---|---|\n"
        atomic(affected, previous_text + "".join(f"| {operation_id} | {obj['path']} | {obj['symbol']} |\n" for obj in objects))
        from ..indexing.engine import inventory
        before_checks = inventory(root)
        from ..workspace import Workspace, CURRENT
        workspace, permit = Workspace(root), CURRENT.get()
        workspace.transition(permit, "VERIFYING")
        checks = run_checks(root, verification, task_id)
        if not checks["ok"] or inventory(root) != before_checks:
            raise ValueError("Behavior verification failed; operation remains recoverable")
        operation["state"] = OperationState.VERIFIED
        write_json(operation_path, operation)
        workspace.transition(permit, "PUBLISHING")
        with Index(root) as index:
            index.publish()
        verify_workspace(root, require_clean=True, ignore_operation=operation_id)
        operation["state"] = OperationState.COMMITTED
        operation["committed_at"] = now()
        operation["evidence"] = checks["evidence"]
        write_json(operation_path, operation)
        append_event(root / RECOVERY / "changelog" / (task_id + ".jsonl"), operation)
        return operation
    except Exception:
        # Include verification side effects in the actual recovery set.
        from ..indexing.engine import inventory
        current = inventory(root)
        saved = manifest(root, snapshot_id)["files"]
        altered = {p for p in set(current) | set(saved) if not p.startswith(CONTROL + "/")
                   and Path(p).name not in {"content_index.jsonl", "file_index.jsonl"}
                   and current.get(p) != (saved[p]["sha256"] if p in saved else None)}
        operation["paths"] = sorted(set(operation["paths"]) | altered)
        operation["postimage"].update({p: current.get(p) for p in altered})
        operation["state"] = OperationState.INTERRUPTED
        write_json(operation_path, operation)
        raise


def rollback_operation(root, operation_id):
    from ..indexing.engine import Index
    path = local(root, f"{RECOVERY}/operations/{operation_id}.json")
    operation = read_json(path)
    if not operation or not operation.get("recovery_available"):
        raise ValueError("Operation recovery data unavailable")
    from ..workspace import Workspace, CURRENT
    Workspace(root).transition(CURRENT.get(), "ROLLING_BACK")
    snapshot = manifest(root, operation["snapshot_id"])
    expected = {}
    for relative in operation["paths"]:
        # A crash between a write and its journal update is detected, never guessed away.
        if relative not in operation["postimage"]:
            before = snapshot["files"].get(relative)
            expected[relative] = before["sha256"] if before else None
        else:
            expected[relative] = operation["postimage"][relative]
    restore(root, operation["snapshot_id"], expected)
    with Index(root) as index:
        index.publish()
    operation["state"] = OperationState.ROLLED_BACK
    operation["restored_at"] = now()
    write_json(path, operation)
    from ..verification import verify_workspace
    verify_workspace(root, require_clean=True)
    return operation
