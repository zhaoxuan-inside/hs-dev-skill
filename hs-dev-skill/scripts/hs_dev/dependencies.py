"""Content-bound upstream baselines. Index publication is not business approval."""
import json
from pathlib import Path
from .storage import local, sha, now
from . import task_store as store
from .indexing.units import resolve_units


def bind(root, task_id, consumer, producer, unit_id, actor, confirmation):
    task = store.load_task(root, task_id)
    if consumer not in task["activities"] or producer not in store.definition(consumer)["upstream"]:
        raise ValueError("Dependency is not an upstream edge of this task activity")
    expected = "model" if task["mode"] == "mute" else "human"
    if actor != expected or not confirmation.strip():
        raise ValueError("Baseline requires configured actor and actual confirmation excerpt")
    unit = resolve_units(root, [unit_id])[unit_id]
    path = unit["path"]
    if path.startswith("hs-dev-skill/"):
        raise ValueError("Baseline must reference a current project artifact")
    file = local(root, path)
    digest = sha(file.read_bytes())
    item = {"consumer": consumer, "producer": producer, "path": path,
            "unit_id": unit_id, "unit_revision": unit["unit_revision"],
            "digest": digest, "actor": actor, "confirmation": confirmation, "bound_at": now()}
    records = task.setdefault("dependencies", [])
    records[:] = [r for r in records if (r["consumer"], r["producer"]) != (consumer, producer)]
    records.append(item)
    store.save_task(root, task)
    return item


def dependency_digest(root, task, activities):
    data, visited = [], set()
    bound_ids = [r["unit_id"] for r in task.get("dependencies", []) if r.get("unit_id")]
    try:
        bound_units = resolve_units(root, bound_ids)
    except (ValueError, OSError):
        bound_units = {}
    def visit(activity):
        if activity in visited:
            return
        visited.add(activity)
        for producer in store.definition(activity)["upstream"]:
            bound = next((r for r in task.get("dependencies", [])
                          if r["consumer"] == activity and r["producer"] == producer), None)
            if bound:
                current = bound_units.get(bound["unit_id"], {}).get("unit_revision")
                data.append([activity, producer, bound, current])
            elif producer in task["activities"]:
                data.append([activity, producer, store.approval_digest(root, task, [producer])])
                for check in store.checks(root, task["task_id"], producer):
                    if check.evidence:
                        file = local(root, check.evidence)
                        data.append([check.evidence, sha(file.read_bytes()) if file.is_file() else None])
                for item in task.get("materials", []):
                    if item["activity"] == producer:
                        file = local(root, item["path"])
                        data.append([item["path"], sha(file.read_bytes()) if file.is_file() else None])
                visit(producer)
            else:
                data.append([activity, producer, "UNBOUND"])
    for activity in activities:
        visit(activity)
    return sha(json.dumps(data, sort_keys=True, ensure_ascii=False).encode())


def require_upstream(root, task, activity):
    for producer in store.definition(activity)["upstream"]:
        bound = next((r for r in task.get("dependencies", [])
                      if r["consumer"] == activity and r["producer"] == producer), None)
        if bound:
            try:
                current = resolve_units(root, [bound["unit_id"]])[bound["unit_id"]]["unit_revision"]
            except (ValueError, OSError):
                current = None
            if current is None or current != bound["unit_revision"]:
                raise ValueError("Upstream baseline changed: " + producer)
        elif producer in task["activities"]:
            store.validate_checks(root, task, [producer])
            require_upstream(root, task, producer)
            if task["mode"] != "mute" and (task["mode"] == "activity" or producer[0] != activity[0]):
                from .acceptance import approval_valid
                scope = producer if task["mode"] == "activity" else producer[0]
                if not approval_valid(root, task, scope):
                    raise ValueError("Upstream confirmation required: " + scope)
        else:
            raise ValueError(f"Bind an accepted baseline for {producer} -> {activity}")
