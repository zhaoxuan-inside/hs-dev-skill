"""Routing boundary: safety and continuity precede signal decisions."""
from .intent import decide
from .workflow import gate, load_task


def classify(root, text, signals=None, model=None):
    signals = signals or {}
    current = signals.get("task_id")
    if current:
        load_task(root, current)
    continuity = gate(root, current=current)
    if continuity["decision_required"]:
        return {"route": "BLOCKED", "reason": "continuity", "gate": continuity}
    from .config import resolve
    settings = resolve(root)["values"]["intent"]
    result = decide(text, signals, model, **settings)
    if result["route"] == "RESUME" and not current:
        result.update(route="NEEDS_TASK", new_task=False)
    return result
