"""One completion policy for mute, activity and stage; no second material ceremony."""

from . import task_store as store


def on_ready(root, task_id, approve, actor=None, confirmation="", scope=None):
    task = store.load_task(root, task_id)
    current = task["current_activity"]
    scope = scope or (current if task["mode"] == "activity" else current[0])
    selected = [a for a in task["activities"] if a == scope or a[0] == scope]
    try:
        store.validate_checks(root, task, selected)
    except ValueError:
        return {"action": "continue", "scope": scope}
    from .acceptance import materials, approval_valid
    if approval_valid(root, task, scope):
        return {"action": "already_confirmed", "scope": scope}
    items = materials(root, task, selected)
    if task["mode"] == "mute":
        approve(root, task_id, scope, "model", "模型：适用检查项及证据核验通过")
        return {"action": "confirmed", "scope": scope, "actor": "model"}
    if actor and items and all(m["status"] == "PASS" for m in items):
        approve(root, task_id, scope, actor, confirmation)
        return {"action": "confirmed", "scope": scope, "actor": actor}
    return {"action": "request_confirmation", "scope": scope}
