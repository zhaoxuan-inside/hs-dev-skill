"""Deterministic signals, lightweight lexical NLP, then explicit model assessment."""

import re
from .workflow import gate, load_task

PATTERNS = {
    "RESUME": r"继续|接着|恢复任务|\bresume\b",
    "ROLLBACK": r"回滚|回退|\brollback\b",
    "REFACTOR": r"重构|解耦|\brefactor\b",
    "FIX": r"修复|报错|故障|缺陷|\bfix\b|\bbug\b",
    "BUILD": r"开发|实现|新增|搭建|重写|\bimplement\b|\bbuild\b",
    "DESIGN": r"需求|设计|架构|方案|\bdesign\b",
    "EXPLORE": r"分析|解释|查看|阅读|为什么|\bexplain\b|\breview\b",
}
ENTRIES = {"RESUME": "continuity", "ROLLBACK": "continuity", "REFACTOR": "H1",
           "FIX": "H1", "BUILD": "A1", "DESIGN": "A1", "EXPLORE": "exploration"}


def classify(root, text, signals=None, model=None):
    signals = signals or {}
    current = signals.get("task_id")
    if current:
        load_task(root, current)
    continuity = gate(root, current=current)
    if continuity["decision_required"]:
        return {"route": "BLOCKED", "reason": "continuity", "gate": continuity}
    explicit = signals.get("intent")
    if explicit and explicit not in PATTERNS:
        raise ValueError("Unknown explicit intent")
    # Quoted and negated verbs must not independently authorize mutation.
    cleaned = re.sub(r"`[^`]*`|“[^”]*”|\"[^\"]*\"", "", text)
    negated = bool(re.search(r"不要|不需要|仅分析|只分析|先讨论|do not|don't|only explain", cleaned, re.I))
    hits = [intent for intent, pattern in PATTERNS.items() if re.search(pattern, cleaned, re.I)]
    reasons = ["lexical:" + intent for intent in hits]
    if signals.get("test_failed"):
        hits.insert(0, "FIX")
        reasons.append("signal:test_failed")
    if negated:
        route = "EXPLORE"
        reasons.append("negation_or_discussion")
    elif explicit:
        route = explicit
        reasons.append("explicit_intent")
    elif model:
        if model.get("intent") not in PATTERNS or not model.get("reason"):
            raise ValueError("Model assessment requires known intent and reasoning")
        route = model["intent"]
        reasons.append("model:" + model["reason"])
    elif hits:
        route = hits[0]
    else:
        route = "UNCLASSIFIED"
    needs_model = not explicit and model is None and not negated and len(set(hits)) != 1
    new_task = route in {"BUILD", "FIX", "REFACTOR"} and not current and not needs_model
    if route == "RESUME" and not current:
        return {"route": "NEEDS_TASK", "reason": "Resume requires an existing task ID"}
    return {"route": "NEEDS_MODEL" if needs_model else route, "entry": ENTRIES.get(route), "new_task": new_task,
            "requires_model": needs_model, "candidates": list(dict.fromkeys(hits)),
            "signals": reasons, "objects": re.findall(r"\b(?:REQ|API|METHOD|TASK)-[\w-]+", text)}
