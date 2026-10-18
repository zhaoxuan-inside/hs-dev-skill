"""Task lifecycle and Markdown-authoritative checks with mode-specific approval."""

from .contracts import TaskStatus, CheckResult, ExecutionMode

import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .config import resolve
from .artifacts import evidence_path
from .storage import CONTROL, atomic, identifier, local, now, read_json, sha, write_json
from .support import recovery
from .verification import run_checks, verify_workspace

DATA = Path(__file__).parent / "data" / "workflow.json"
TERMINAL = {TaskStatus.COMPLETED, TaskStatus.ROLLED_BACK}
CHECK_COLUMNS = "| ID | 检查项及通过标准 | 方法 | 结果 | 证据 | 摘要 | 理由 |\n|---|---|---|---|---|---|---|\n"


def catalog():
    return read_json(DATA)


def task_path(root, task_id):
    return local(root, f"{CONTROL}/task/{task_id}")


def load_task(root, task_id):
    value = read_json(task_path(root, task_id) / "task.json")
    if not value or value.get("task_id") != task_id:
        raise ValueError("Unknown task")
    return value


def save_task(root, task):
    task["updated_at"] = now()
    write_json(task_path(root, task["task_id"]) / "task.json", task)
    refresh_task_index(root)


def tasks(root):
    return [read_json(p) for p in sorted((Path(root) / CONTROL / "task").glob("*/task.json"))]


def refresh_task_index(root):
    entries = [{"task_id": t["task_id"], "status": t["status"], "updated_at": t["updated_at"],
                "metadata_digest": sha((task_path(root, t["task_id"]) / "task.json").read_bytes())} for t in tasks(root)]
    atomic(Path(root) / CONTROL / "task_index.jsonl", "\n".join(json.dumps(row, ensure_ascii=False) for row in entries) + "\n")


def gate(root, current=None):
    status = verify_workspace(root)
    pending = [t["task_id"] for t in tasks(root) if t["status"] not in TERMINAL and t["task_id"] != current]
    # Eviction preserves unresolved blockers outside the evicted task directory.
    pending.extend(e["task_id"] for e in read_json(Path(root) / CONTROL / "state/expired_tasks.json", [])
                   if e["status"] not in TERMINAL and e["task_id"] != current and not e.get("resolved"))
    return {**status, "ok": status["ok"] and not pending, "pending_tasks": sorted(set(pending)),
            "decision_required": not status["ok"] or bool(pending), "choices": ["continue", "rollback"]}


def checks(root, task_id, activity):
    file = local(root, f"{CONTROL}/task/{task_id}/activities/{activity}/checklist.md")
    rows = []
    for line in file.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ") and not line.startswith("| ID "):
            fields = [part.strip() for part in line.strip("|").split("|")]
            if len(fields) == 7:
                rows.append(fields)
    return rows


def write_checks(root, task_id, activity, rows):
    text = "# " + activity + " 验收清单\n\n" + CHECK_COLUMNS
    text += "".join("| " + " | ".join(row) + " |\n" for row in rows)
    atomic(task_path(root, task_id) / "activities" / activity / "checklist.md", text)


def start(root, title, activities=None, direct=None, home=None):
    status = gate(root)
    if not status["ok"]:
        raise ValueError("New task blocked; user must choose continue/rollback: " + json.dumps(status, ensure_ascii=False))
    selected = activities or [a["id"] for s in catalog()["stages"] for a in s["activities"]]
    definitions = {a["id"]: a for s in catalog()["stages"] for a in s["activities"]}
    if not selected or len(selected) != len(set(selected)) or any(a not in definitions for a in selected):
        raise ValueError("Unknown or duplicate activities")
    task_id = identifier()
    directory = task_path(root, task_id)
    directory.mkdir(parents=True, exist_ok=False)
    task = {"schema_version": 1, "task_id": task_id, "title": title, "created_at": now(),
            "status": TaskStatus.ACTIVE, "activities": selected, "current_activity": selected[0], "approvals": {}, "verification": None}
    config = resolve(root, task_id, direct, home)
    task["mode"] = config["values"]["execution"]["mode"]
    write_json(directory / "config/config.json", direct or {})
    write_json(directory / "resolved_config.json", config)
    atomic(directory / "README.md", f"# {title}\n\n任务 {task_id}。本目录仅含任务绑定状态；全局设计通过引用读取。\n")
    atomic(directory / "plan.md", f"# 执行计划\n\n目标：{title}\n\n活动：{', '.join(selected)}\n\n按实际影响选择活动；未选择的上游结论须在上下文中核验有效性。\n")
    atomic(directory / "handoff.md", "# 交接\n\n当前目标见计划；未通过清单项即剩余工作。\n")
    atomic(directory / "context/current.md", "# 活跃工作集\n\n只装配当前活动的有效目标、约束、契约、未决项和证据引用。\n")
    for activity in selected:
        rows = [[c["id"], c["criterion"], c["method"], CheckResult.PENDING, "", "", ""] for c in definitions[activity]["checks"]]
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
    row = next((r for r in rows if r[0] == item), None)
    if row is None:
        raise ValueError("Unknown check item")
    row[3:] = [result, evidence or "", digest, reason]
    write_checks(root, task_id, activity, rows)
    task["approvals"].pop(activity if task["mode"] == ExecutionMode.ACTIVITY else activity[0], None)
    task["verification"] = None
    task["current_activity"] = activity
    save_task(root, task)
    from .acceptance import refresh
    refresh(root, task)
    return {"task_id": task_id, "item": item, "result": result}


def validate_checks(root, task, activities):
    errors = []
    definitions = {a["id"]: a for stage in catalog()["stages"] for a in stage["activities"]}
    for activity in activities:
        rows = checks(root, task["task_id"], activity)
        expected = {c["id"]: c for c in definitions[activity]["checks"]}
        if len(rows) != len(expected) or {r[0] for r in rows} != set(expected):
            errors.append(activity + " checklist denominator changed")
        for row in rows:
            if row[0] not in expected or row[1] != expected[row[0]]["criterion"]:
                errors.append(activity + " checklist rule changed")
            if row[3] not in {CheckResult.PASS, CheckResult.NA}:
                errors.append(row[0] + " is not passed")
            elif row[3] == CheckResult.NA and not row[6]:
                errors.append(row[0] + " missing applicability reason")
            elif row[3] == CheckResult.PASS:
                file = evidence_path(root, row[4])
                if not file.is_file() or sha(file.read_bytes()) != row[5]:
                    errors.append(row[0] + " evidence changed/missing")
    if errors:
        raise ValueError("; ".join(errors))


def approval_digest(root, task, activities):
    return sha("".join((task_path(root, task["task_id"]) / "activities" / a / "checklist.md").read_text() for a in activities).encode())


def enter_activity(root, task, activity):
    prior = task["activities"][:task["activities"].index(activity)]
    if task["mode"] == ExecutionMode.MUTE:
        return
    scopes = prior if task["mode"] == ExecutionMode.ACTIVITY else list(dict.fromkeys(a[0] for a in prior if a[0] != activity[0]))
    for scope in scopes:
        from .acceptance import approval_valid
        if not approval_valid(root, task, scope):
            raise ValueError("Previous confirmation required: " + scope)


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
    acceptance.actor_valid(task, actor, confirmation)
    acceptance.prepare_approval(root, task, selected, actor, confirmation)
    task["approvals"][scope] = {"actor": actor, "confirmation": confirmation, "confirmed_at": now(),
        "checklist_digest": approval_digest(root, task, selected), "material_digest": acceptance.digest(root, task, selected),
        "source_generation": read_json(Path(root) / "hs-dev-skill/state/publication.json")["generation"]}
    save_task(root, task)
    acceptance.refresh(root, task)
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
