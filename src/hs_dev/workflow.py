"""Task lifecycle and Markdown-authoritative checks with mode-specific approval."""

from .contracts import TaskStatus, CheckResult, ExecutionMode

import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .config import resolve
from .storage import CONTROL, atomic, identifier, local, now, read_json, sha, write_json
from .support import recovery
from .verification import run_checks, verify_workspace

from .models import CheckExecution
from .task_store import (catalog, task_path, load_task, save_task, tasks, refresh_task_index,
                         checks, write_checks, approval_digest, validate_checks, rule_digest)
from .dependencies import require_upstream, dependency_digest

TERMINAL = {TaskStatus.COMPLETED, TaskStatus.ROLLED_BACK}

def gate(root, current=None):
    status = verify_workspace(root)
    pending = [t["task_id"] for t in tasks(root) if t["status"] not in TERMINAL and t["task_id"] != current]
    # Eviction preserves unresolved blockers outside the evicted task directory.
    pending.extend(e["task_id"] for e in read_json(Path(root) / CONTROL / "state/expired_tasks.json", [])
                   if e["status"] not in TERMINAL and e["task_id"] != current and not e.get("resolved"))
    return {**status, "ok": status["ok"] and not pending, "pending_tasks": sorted(set(pending)),
            "decision_required": not status["ok"] or bool(pending), "choices": ["continue", "rollback"]}


def start(root, title, activities=None, direct=None, home=None):
    status = gate(root)
    if not status["ok"]:
        raise ValueError("New task blocked; user must choose continue/rollback: " + json.dumps(status, ensure_ascii=False))
    if not activities:
        raise ValueError("Explicit activity scope required; classify the request before task-start")
    selected = activities
    definitions = {a["id"]: a for s in catalog()["stages"] for a in s["activities"]}
    if not selected or len(selected) != len(set(selected)) or any(a not in definitions for a in selected):
        raise ValueError("Unknown or duplicate activities")
    task_id = identifier()
    directory = task_path(root, task_id)
    directory.mkdir(parents=True, exist_ok=False)
    task = {"schema_version": 2, "task_id": task_id, "title": title, "created_at": now(),
            "status": TaskStatus.ACTIVE, "activities": selected, "current_activity": selected[0], "approvals": {}, "verification": None}
    config = resolve(root, task_id, direct, home)
    task["mode"] = config["values"]["execution"]["mode"]
    write_json(directory / "config/config.json", direct or {})
    write_json(directory / "resolved_config.json", config)
    atomic(directory / "README.md", f"# {title}\n\n任务 {task_id}。本目录仅含任务绑定状态；全局设计通过引用读取。\n")
    atomic(directory / "plan.md", f"# 执行计划\n\n目标：{title}\n\n活动：{', '.join(selected)}\n\n按实际影响选择活动；未选择的上游结论须在上下文中核验有效性。\n")
    atomic(directory / "current.md", f"# 当前任务\n\n目标：{title}\n当前活动：{selected[0]}\n状态：执行中\n")
    for activity in selected:
        rows = [CheckExecution(c["id"], rule_digest(c)) for c in definitions[activity]["checks"]]
        write_checks(root, task_id, activity, rows)
    save_task(root, task)
    task["snapshot_id"] = recovery.capture(root, task_id)
    save_task(root, task)
    from .acceptance import refresh
    refresh(root, task)
    retention = config["values"]["retention"]
    recovery.retain(root, retention["hours"], retention["snapshots"], protected=[task["snapshot_id"]])
    expire(root, retention["hours"], retention["tasks"], active=task_id)
    return task


def record_check(root, task_id, activity, item, result, evidence=None, reason=""):
    task = load_task(root, task_id)
    if task["status"] != TaskStatus.ACTIVE or activity not in task["activities"]:
        raise ValueError("Activity is not active in this task")
    verify_workspace(root, require_clean=True)
    enter_activity(root, task, activity)
    if result not in {CheckResult.PASS, CheckResult.FAIL, CheckResult.NA}:
        raise ValueError("Unknown check result")
    if any("|" in str(v) or "\n" in str(v) for v in (evidence or "", reason)):
        raise ValueError("Checklist fields cannot contain table delimiters")
    if result == CheckResult.NA and not reason.strip():
        raise ValueError("NA requires applicability reasoning")
    digest = ""
    if result != CheckResult.NA:
        if not evidence:
            raise ValueError("PASS/FAIL require concrete evidence")
        file = local(root, evidence)
        digest = sha(file.read_bytes())
    rows = checks(root, task_id, activity)
    row = next((r for r in rows if r.check_id == item), None)
    if row is None:
        raise ValueError("Unknown check item")
    row.result, row.evidence, row.evidence_digest, row.reason = result, evidence or "", digest, reason
    write_checks(root, task_id, activity, rows)
    task["approvals"].pop(activity if task["mode"] == ExecutionMode.ACTIVITY else activity[0], None)
    task["verification"] = None
    task["current_activity"] = activity
    save_task(root, task)
    from .acceptance import refresh
    refresh(root, task)
    from .support.trace import emit
    emit(root, "check", {"task_id": task_id, "activity_id": activity, "outcome": result})
    return {"task_id": task_id, "item": item, "result": result}


def enter_activity(root, task, activity):
    require_upstream(root, task, activity)


def approve(root, task_id, scope, actor, confirmation):
    from . import acceptance
    task = load_task(root, task_id)
    if task["status"] != TaskStatus.ACTIVE:
        raise ValueError("Only an active task can be approved")
    mode = task["mode"]
    if mode == ExecutionMode.MUTE and actor != "model":
        raise ValueError("mute records model confirmation explicitly")
    if mode != ExecutionMode.MUTE and (actor != "human" or not confirmation.strip()):
        raise ValueError("Human confirmation source/excerpt is required")
    if mode == ExecutionMode.ACTIVITY:
        selected = [scope] if scope in task["activities"] else []
    else:
        selected = [a for a in task["activities"] if a[0] == scope.upper()]
    if not selected:
        raise ValueError("Approval scope does not match execution mode")
    if mode != ExecutionMode.ACTIVITY:
        scope = scope.upper()
    verify_workspace(root, require_clean=True)
    validate_checks(root, task, selected)
    for activity in selected:
        require_upstream(root, task, activity)
    acceptance.actor_valid(task, actor, confirmation)
    acceptance.prepare_approval(root, task, selected, actor, confirmation)
    task["approvals"][scope] = {"actor": actor, "confirmation": confirmation, "confirmed_at": now(),
        "checklist_digest": approval_digest(root, task, selected), "material_digest": acceptance.digest(root, task, selected),
        "dependency_digest": dependency_digest(root, task, selected)}
    save_task(root, task)
    acceptance.refresh(root, task)
    from .support.trace import emit
    emit(root, "confirmation", {"task_id": task_id, "scope": scope, "actor": actor, "outcome": "PASS"})
    return task["approvals"][scope]


def finish(root, task_id, commands):
    task = load_task(root, task_id)
    if task["status"] != TaskStatus.ACTIVE:
        raise ValueError("Only an active task can be completed")
    verify_workspace(root, require_clean=True)
    validate_checks(root, task, task["activities"])
    scopes = task["activities"] if task["mode"] == ExecutionMode.ACTIVITY else sorted({a[0] for a in task["activities"]})
    for scope in scopes:
        from .acceptance import approval_valid
        if not approval_valid(root, task, scope):
            raise ValueError("Missing/stale approval: " + scope)
    result = run_checks(root, commands, task_id)
    if not result["ok"]:
        raise ValueError("Final verification failed")
    # Verification commands may themselves mutate the workspace.
    verify_workspace(root, require_clean=True)
    task.update(status=TaskStatus.COMPLETED, completed_at=now(), verification=result["evidence"])
    save_task(root, task)
    return task


def expire(root, hours=48, maximum=5, active=None):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    tombstone = Path(root) / CONTROL / "state/expired_tasks.json"
    records = read_json(tombstone, [])
    removed = []
    for rank, task in enumerate(sorted(tasks(root), key=lambda t: t["task_id"], reverse=True)):
        if task["task_id"] == active:
            continue
        age = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
        if rank >= maximum or age < cutoff:
            directory = task_path(root, task["task_id"])
            # Move complete evidence before deletion; global references remain valid via relocation map.
            destination = Path(root) / CONTROL / "evidence_archive" / task["task_id"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise ValueError("Task archive already exists")
            shutil.move(str(directory), str(destination))
            records.append({"task_id": task["task_id"], "status": task["status"], "expired_at": now(),
                            "archive": str(destination.relative_to(root))})
            removed.append(task["task_id"])
    write_json(tombstone, records)
    refresh_task_index(root)
    return removed


def continue_task(root, task_id):
    """Explicit continuation can reactivate an expired task without allocating a new ID."""
    directory = task_path(root, task_id)
    registry = Path(root) / CONTROL / "state/expired_tasks.json"
    records = read_json(registry, [])
    if not directory.exists():
        archived = local(root, f"{CONTROL}/evidence_archive/{task_id}")
        if not archived.is_dir():
            raise ValueError("Task unavailable")
        shutil.move(str(archived), str(directory))
        for entry in records:
            if entry["task_id"] == task_id:
                entry["resolved"] = True
                entry["reactivated_at"] = now()
        write_json(registry, records)
        refresh_task_index(root)
    task = load_task(root, task_id)
    if task["status"] in TERMINAL:
        raise ValueError("Completed task is not a continuation target")
    return {"task": task, "gate": gate(root, current=task_id), "decision": "continue"}
