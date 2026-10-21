"""Task persistence and typed check instances. No workflow or acceptance imports."""
import json
from pathlib import Path
from .models import CheckExecution, TaskRecord
from .storage import CONTROL, atomic, local, now, read_json, sha, write_json

DATA = Path(__file__).parent / "data" / "workflow.json"


def catalog():
    return read_json(DATA)


def task_path(root, task_id):
    return local(root, f"{CONTROL}/tasks/{task_id}")


def load_task(root, task_id) -> TaskRecord:
    value = read_json(task_path(root, task_id) / "task.json")
    if not value or value.get("task_id") != task_id or value.get("schema_version") != 2:
        raise ValueError("Unknown task")
    decisions = read_json(task_path(root, task_id) / "acceptance/decisions.json")
    if not decisions or decisions.get("schema_version") != 2:
        raise ValueError("Missing or unsupported acceptance decision format")
    value.update({key: decisions[key] for key in ("approvals", "material_reviews", "acceptance_history")})
    return value


def save_task(root, task: TaskRecord):
    task["updated_at"] = now()
    decision_keys = ("approvals", "material_reviews", "acceptance_history")
    decisions = {"schema_version": 2, **{key: task.get(key, [] if key == "acceptance_history" else {})
                                           for key in decision_keys}}
    write_json(task_path(root, task["task_id"]) / "acceptance/decisions.json", decisions)
    write_json(task_path(root, task["task_id"]) / "task.json", {k: v for k, v in task.items() if k not in decision_keys})
    summary = (f"# 当前任务\n\n目标：{task['title']}\n当前活动：{task['current_activity']}\n"
               f"状态：{task['status']}\n活动范围：{', '.join(task['activities'])}\n\n")
    summary += "依赖产物：\n" + "".join(f"- {r['producer']} → {r['consumer']}：{r['path']}\n"
                                     for r in task.get("dependencies", []))
    atomic(task_path(root, task["task_id"]) / "current.md", summary)
    refresh_task_index(root)
    from .support.trace import emit
    emit(root, "task_state", {"task_id": task["task_id"], "activity_id": task["current_activity"],
                              "outcome": task["status"]})
    from .contracts import TaskStatus
    if task["status"] in {TaskStatus.COMPLETED, TaskStatus.ROLLED_BACK}:
        from .support.trace_metrics import observe
        observe(root, task["task_id"], "finish", result=task["status"])


def tasks(root):
    return [read_json(p) for p in sorted((Path(root) / CONTROL / "tasks").glob("*/task.json"))]


def refresh_task_index(root):
    entries = [{"task_id": t["task_id"], "status": t["status"], "updated_at": t["updated_at"],
                "metadata_digest": sha((task_path(root, t["task_id"]) / "task.json").read_bytes())} for t in tasks(root)]
    atomic(Path(root) / CONTROL / "task_index.jsonl", "\n".join(json.dumps(row, ensure_ascii=False) for row in entries) + "\n")


def definition(activity):
    return next(a for s in catalog()["stages"] for a in s["activities"] if a["id"] == activity)


def rule_digest(check):
    return sha(json.dumps(check, sort_keys=True, ensure_ascii=False).encode())


def checks(root, task_id, activity):
    file = task_path(root, task_id) / "activities" / activity / "results.json"
    data = read_json(file)
    if not data or data.get("schema_version") != 2:
        raise ValueError("Unsupported or missing check execution format")
    return [CheckExecution(**record) for record in data["checks"]]


def write_checks(root, task_id, activity, rows):
    write_json(task_path(root, task_id) / "activities" / activity / "results.json",
               {"schema_version": 2, "checks": [r.to_dict() for r in rows]})


def approval_digest(root, task, activities):
    data = [[row.to_dict() for row in checks(root, task["task_id"], a)] for a in activities]
    for activity in activities:
        for relative in task.get("outputs", {}).get(activity, []):
            file = local(root, relative)
            data.append([relative, sha(file.read_bytes()) if file.is_file() else None])
    return sha(json.dumps(data, sort_keys=True, ensure_ascii=False).encode())


def validate_checks(root, task, activities):
    from .artifacts import evidence_path
    errors = []
    for activity in activities:
        rows = checks(root, task["task_id"], activity)
        expected = {c["id"]: c for c in definition(activity)["checks"]}
        if len(rows) != len(expected) or {r.check_id for r in rows} != set(expected):
            errors.append(activity + " checklist denominator changed")
        for row in rows:
            if row.check_id not in expected or row.rule_digest != rule_digest(expected[row.check_id]):
                errors.append(row.check_id + " checklist rule changed")
            if row.result not in {"PASS", "NA"}:
                errors.append(row.check_id + " is not passed")
            elif row.result == "NA" and not row.reason.strip():
                errors.append(row.check_id + " missing applicability reason")
            elif row.result == "PASS":
                file = evidence_path(root, row.evidence)
                if not file.is_file() or sha(file.read_bytes()) != row.evidence_digest:
                    errors.append(row.check_id + " evidence changed/missing")
    if errors:
        raise ValueError("; ".join(errors))
