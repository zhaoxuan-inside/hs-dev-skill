"""One acceptance service for material decisions, progress and human-readable cards."""

import json
from pathlib import Path
from urllib.parse import quote

from . import task_store as workflow
from .dependencies import dependency_digest
from .artifacts import evidence_path
from .contracts import CheckResult, ExecutionMode, TaskStatus
from .storage import atomic, local, now, sha
from .verification import verify_workspace

LABELS = {"PENDING": "待审阅", "PASS": "已通过", "FAIL": "需修改", "STALE": "待复验", "MISSING": "材料缺失"}
DECISIONS = {"pass", "reject", "defer", "repair"}


def scope_activities(task, scope):
    if task["mode"] == ExecutionMode.ACTIVITY:
        selected = [scope] if scope in task["activities"] else []
    else:
        scope = scope.upper()
        selected = [a for a in task["activities"] if a[0] == scope]
    if not selected:
        raise ValueError("Acceptance scope does not match execution mode")
    return selected


def material_id(activity, path):
    return activity + "-" + sha(path.encode())[:12]


def materials(root, task, activities):
    """Derive evidence cards, enriched by explicitly registered deliverables."""
    definitions = {m["id"]: dict(m) for m in task.get("materials", []) if m["activity"] in activities}
    reviews = task.get("material_reviews", {})
    result = []
    for key, item in definitions.items():
        path = evidence_path(root, item["path"])
        source = sha(path.read_bytes()) if path.is_file() else None
        checklist = workflow.approval_digest(root, task, [item["activity"]])
        binding = sha(json.dumps([source, checklist, item["title"], item["focus"]], ensure_ascii=False).encode())
        review = reviews.get(key)
        status = CheckResult.PENDING
        if source is None:
            status = "MISSING"
        elif review:
            status = review["result"] if review["binding"] == binding else "STALE"
        result.append({**item, "source_digest": source, "binding": binding, "status": status,
                       "review": review, "number": len(result) + 1})
    return result


def digest(root, task, activities):
    return sha(json.dumps(materials(root, task, activities), sort_keys=True, ensure_ascii=False).encode())


def mutable_task(root, task_id):
    task = workflow.load_task(root, task_id)
    if task["status"] != TaskStatus.ACTIVE:
        raise ValueError("Acceptance changes require an active task")
    verify_workspace(root, require_clean=True)
    return task


def invalidate(task, activity):
    scope = activity if task["mode"] == ExecutionMode.ACTIVITY else activity[0]
    task["approvals"].pop(scope, None)
    task["verification"] = None


def register(root, task_id, activity, path, title, focus):
    task = mutable_task(root, task_id)
    if activity not in task["activities"]:
        raise ValueError("Material activity is outside task scope")
    if not title.strip() or not focus.strip():
        raise ValueError("Material title and review focus are required")
    file = local(root, path)
    if not file.is_file():
        raise ValueError("Material must be an existing workspace file")
    path = str(file.relative_to(Path(root).resolve()))
    item = {"id": material_id(activity, path), "activity": activity, "path": path, "title": title, "focus": focus}
    registered = task.setdefault("materials", [])
    previous = next((m for m in registered if m["id"] == item["id"]), None)
    if previous == item:
        return item
    if previous:
        registered[registered.index(previous)] = item
    else:
        registered.append(item)
    invalidate(task, activity)
    workflow.save_task(root, task)
    refresh(root, task)
    return item


def actor_valid(task, actor, confirmation):
    expected = "model" if task["mode"] == ExecutionMode.MUTE else "human"
    if actor != expected or not confirmation.strip():
        raise ValueError("Acceptance requires " + expected + " attribution and actual confirmation excerpt")


def record(root, task, item, decision, actor, confirmation, reason="", next_action=""):
    result = CheckResult.PASS if decision == "pass" else CheckResult.FAIL
    event = {"material_id": item["id"], "result": result, "decision": decision, "actor": actor,
             "confirmation": confirmation, "reason": reason, "next_action": next_action,
             "binding": item["binding"], "source_digest": item["source_digest"], "recorded_at": now()}
    task.setdefault("material_reviews", {})[item["id"]] = event
    task.setdefault("acceptance_history", []).append(event)
    invalidate(task, item["activity"])


def decide(root, task_id, scope, ids, decision, actor, confirmation, reason="", next_action="", expected_digest=None):
    """Host maps explicit checkboxes/text to IDs; ambiguity is never guessed here."""
    task = mutable_task(root, task_id)
    selected = scope_activities(task, scope)
    actor_valid(task, actor, confirmation)
    if expected_digest is None or expected_digest != digest(root, task, selected):
        raise ValueError("Acceptance view changed; refresh and confirm the current materials")
    if decision not in DECISIONS or not ids or len(ids) != len(set(ids)):
        raise ValueError("Explicit unique material IDs and a valid decision are required")
    if decision != "pass" and not reason.strip():
        raise ValueError("Unpassed material requires an issue/reason")
    if decision in {"defer", "repair"} and not next_action.strip():
        raise ValueError("Deferred/repair material requires a next action")
    available = {m["id"]: m for m in materials(root, task, selected)}
    if any(key not in available for key in ids):
        raise ValueError("Unknown material in this acceptance scope")
    if decision == "pass" and any(available[key]["source_digest"] is None for key in ids):
        raise ValueError("Missing material cannot pass")
    for key in ids:
        record(root, task, available[key], decision, actor, confirmation, reason, next_action)
    workflow.save_task(root, task)
    refresh(root, task)
    return view(root, task_id, scope)


def prepare_approval(root, task, activities, actor, confirmation):
    """Explicit scope approval confirms pending materials; failures require item-level resolution."""
    items = materials(root, task, activities)
    blocked = [m["id"] for m in items if m["status"] not in {CheckResult.PASS, CheckResult.PENDING}]
    if blocked:
        raise ValueError("Unresolved acceptance materials: " + ", ".join(blocked))
    for item in items:
        if item["status"] == CheckResult.PENDING:
            record(root, task, item, "pass", actor, confirmation)


def approval_valid(root, task, scope):
    activities = scope_activities(task, scope)
    approval = task["approvals"].get(scope)
    if not approval:
        return False
    try:
        workflow.validate_checks(root, task, activities)
    except ValueError:
        return False
    return (approval.get("dependency_digest") == dependency_digest(root, task, activities)
            and approval["checklist_digest"] == workflow.approval_digest(root, task, activities)
            and approval.get("material_digest") == digest(root, task, activities)
            and all(m["status"] == CheckResult.PASS for m in materials(root, task, activities)))


def view(root, task_id, scope=None):
    task = workflow.load_task(root, task_id)
    current = task["current_activity"]
    scope = scope or (current if task["mode"] == ExecutionMode.ACTIVITY else current[0])
    if task["mode"] != ExecutionMode.ACTIVITY:
        scope = scope.upper()
    selected = scope_activities(task, scope)
    items = materials(root, task, selected)
    scopes = task["activities"] if task["mode"] == ExecutionMode.ACTIVITY else list(dict.fromkeys(a[0] for a in task["activities"]))
    completed = [s for s in scopes if approval_valid(root, task, s)]
    stages = [{"id": s["id"], "title": s["title"],
               "activities": [a["id"] for a in s["activities"] if a["id"] in task["activities"]]}
              for s in workflow.catalog()["stages"] if any(a["id"] in task["activities"] for a in s["activities"])]
    summary = {key: sum(m["status"] == key for m in items) for key in LABELS}
    try:
        workflow.validate_checks(root, task, selected)
        errors = []
    except ValueError as error:
        errors = [str(error)]
    consistent = verify_workspace(root)
    current_definition = next(a for s in workflow.catalog()["stages"] for a in s["activities"] if a["id"] == current)
    return {"task_id": task_id, "title": task["title"], "mode": task["mode"], "scope": scope,
            "current_activity": current, "current_activity_title": current_definition["title"],
            "activity_position": {"current": task["activities"].index(current) + 1, "total": len(task["activities"])},
            "activities": selected, "stages": stages,
            "progress": {"approved": len(completed), "total": len(scopes), "approved_scopes": completed},
            "materials": items, "summary": summary, "view_digest": digest(root, task, selected),
            "check_errors": errors, "workspace_errors": consistent["errors"],
            "approved": scope in completed,
            "ready": all(m["status"] == CheckResult.PASS for m in items) and not errors and consistent["ok"]}


def plain(value):
    return str(value).replace("\n", " ").replace("\r", " ").replace("<", "&lt;").replace(">", "&gt;").replace("[", "\\[").replace("]", "\\]").replace("*", "\\*").replace("`", "\\`")


def render(value, root):
    navigation = " › ".join(("**" if s["id"] == value["current_activity"][0] else "")
                            + plain(s["id"] + " " + s["title"])
                            + ("**" if s["id"] == value["current_activity"][0] else "") for s in value["stages"])
    summary = value["summary"]
    lines = [navigation, "", "**" + plain(value["title"]) + "**", "",
             f"当前位置：{value['current_activity']} {plain(value['current_activity_title'])}（任务路径 {value['activity_position']['current']}/{value['activity_position']['total']}） · 本次验收：{value['scope']} · 确认来源：{'模型' if value['mode'] == ExecutionMode.MUTE else '人工'}",
             "", f"阶段／活动已验收 {value['progress']['approved']}/{value['progress']['total']}（按任务实际范围）",
             "", f"共 {len(value['materials'])} 份材料：✓ {summary['PASS']} 份通过 · ◷ {summary['PENDING']} 份待审 · ✎ {summary['FAIL']} 份需修改 · ↻ {summary['STALE']} 份待复验 · ! {summary['MISSING']} 份缺失", ""]
    for item in value["materials"]:
        mark = "x" if item["status"] == CheckResult.PASS else " "
        path = quote(str(evidence_path(root, item["path"])), safe="/")
        lines.extend([f"- [{mark}] **{item['number']}. {plain(item['title'])}** · {LABELS[item['status']]} · [查看文档]({path})",
                      f"  审阅重点：{plain(item['focus'])}"])
        review = item["review"]
        if review and item["status"] != CheckResult.PASS:
            lines.append("  问题：" + plain(review["reason"] or "材料或清单已变化，请重新审阅"))
            action = {"reject": "待决定：暂不处理 / 继续沟通修复", "defer": "暂不处理", "repair": "继续沟通修复", "pass": "需重新验收"}[review["decision"]]
            lines.append("  处理：" + action + ("；下一步：" + plain(review["next_action"]) if review["next_action"] else ""))
        if item["status"] == "MISSING":
            lines.append("  请恢复材料；缺失材料不能验收通过。")
        lines.append("")
    if not value["materials"]:
        lines.extend(["无单独交付材料；依据检查项结果及证据验收。", ""])
    if value["approved"]:
        lines.append("本范围已验收通过。")
    elif value["ready"]:
        lines.append("检查结果已就绪，可确认本范围。")
    else:
        lines.append("本范围尚未通过；暂不处理仍保留未通过状态。")
    lines.extend(["", "可勾选后确认，也可回复：‘1、3通过；2不通过，原因……，继续沟通修复’。未提及材料保留原结果。",
                  "宿主将明确回答转换为稳定材料ID并绑定本次视图版本；含糊回答先澄清。"])
    details = [*value["check_errors"], *value["workspace_errors"]]
    lines.extend(["", "<details>", "<summary>检查、版本与记录</summary>", "",
                  "视图版本：" + value["view_digest"], ""])
    lines.extend("- " + plain(error) for error in details)
    lines.extend(f"- {m['number']} → {m['id']} · 源摘要：{m['source_digest'] or '缺失'}" for m in value["materials"])
    for item in value["materials"]:
        if item["review"]:
            review = item["review"]
            lines.append(f"- {item['number']} 最近决定：{review['actor']} · {review['recorded_at']} · {plain(review['confirmation'])}")
    lines.extend(["", "</details>", ""])
    return "\n".join(lines)


def refresh(root, task):
    """Persist one derived overview after every check, material or scope decision."""
    value = view(root, task["task_id"])
    atomic(workflow.task_path(root, task["task_id"]) / "acceptance/overview.md", render(value, root))
