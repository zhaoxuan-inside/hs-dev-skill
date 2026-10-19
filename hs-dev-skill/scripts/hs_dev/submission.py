"""Shared constraints for managed code submissions and external edits."""
from pathlib import Path

from .storage import CONTROL, GENERATED_NAMES, IGNORED, local
from .workspace import CURRENT


def validate_paths(root, paths):
    for relative in paths:
        path = local(root, relative)
        rel = path.relative_to(Path(root).resolve())
        if not rel.parts or path.is_dir():
            raise ValueError("Submission requires a file path: " + str(rel))
        if (rel.parts[0] == CONTROL or any(p in IGNORED or p.endswith(".egg-info") for p in rel.parts[:-1])
                or "history" in rel.parts[:-1] or path.name in GENERATED_NAMES
                or path.name == ".coverage" or path.name.startswith(".hs-write-")):
            raise ValueError("Submission path is outside recoverable sources: " + str(rel))
        permit = CURRENT.get()
        if permit and permit.scope and not any(
                str(rel) == p or str(rel).startswith(p.rstrip("/") + "/") for p in permit.scope):
            raise ValueError("Change is outside the UUID scope: " + str(rel))


def register(root, task, activity, paths):
    from . import task_store
    outputs = task.setdefault("outputs", {})
    outputs[activity] = sorted(set(outputs.get(activity, [])) | set(paths))
    task["approvals"].pop(activity if task["mode"] == "activity" else activity[0], None)
    task["verification"] = None
    task_store.save_task(root, task)
