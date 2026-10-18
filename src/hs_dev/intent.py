"""Clause-scoped signals and conservative decisions with host-model fallback."""
from dataclasses import asdict, dataclass
import re

PATTERNS = {
    "RESUME": r"继续|接着|恢复任务|\bresume\b", "ROLLBACK": r"回滚|回退|\brollback\b",
    "REFACTOR": r"重构|解耦|\brefactor\b", "FIX": r"修复|报错|故障|缺陷|\bfix\b|\bbug\b",
    "BUILD": r"开发|实现|新增|搭建|重写|\bimplement\b|\bbuild\b",
    "DESIGN": r"需求|设计|架构|方案|\bdesign\b",
    "EXPLORE": r"分析|解释|查看|阅读|为什么|\bexplain\b|\breview\b"}
ENTRIES = {"RESUME": "continuity", "ROLLBACK": "continuity", "REFACTOR": "H1",
           "FIX": "H1", "BUILD": "A1", "DESIGN": "A1", "EXPLORE": "exploration"}


@dataclass(frozen=True)
class Signal:
    intent: str
    text: str
    start: int
    end: int
    polarity: str
    score: float
    source: str = "lexical"


def extract(text):
    cleaned = re.sub(r'`[^`]*`|“[^”]*”|"[^"\n]*"', lambda m: " " * len(m[0]), text)
    result = []
    for clause in re.finditer(r"[^，,。；;\n]+", cleaned):
        for intent, pattern in PATTERNS.items():
            for match in re.finditer(pattern, clause[0], re.I):
                prefix = clause[0][:match.start()]
                negative = bool(re.search(r"(?:不要|不需要|禁止|别|do not|don't)\s*(?:再|去|进行|执行|直接|立即|马上)*\s*$", prefix, re.I))
                result.append(Signal(intent, match[0], clause.start()+match.start(), clause.start()+match.end(),
                                     "negative" if negative else "positive", 0.72))
    for match in re.finditer(r"仅分析|只分析|只读|先讨论|only explain", cleaned, re.I):
        if not re.search(r"不要\s*$|不需要\s*$", cleaned[:match.start()]):
            result.append(Signal("EXPLORE", "readonly", match.start(), match.end(), "positive", 0.99, "constraint"))
    return result


def decide(text, signals=None, model=None, threshold=0.85, margin=0.15):
    explicit = signals or {}
    found = extract(text)
    if explicit.get("test_failed"):
        found.append(Signal("FIX", "test_failed", 0, 0, "positive", 0.95, "environment"))
    candidates = {}
    for signal in found:
        if signal.polarity == "positive":
            candidates[signal.intent] = max(candidates.get(signal.intent, 0), signal.score)
    target_pattern = r"(?:REQ|API|METHOD|TASK)-[\w-]+|[\w./-]+\.(?:py|ts|js|md|json)\b|接口|模块|文件|函数|页面|测试|代码|任务|Skill"
    objects = [{"value": m[0], "start": m.start(), "end": m.end()} for m in re.finditer(target_pattern, text, re.I)]
    targeted = bool(objects)
    for intent in candidates:
        if targeted and candidates[intent] < threshold:
            candidates[intent] += 0.15
    ordered = sorted(candidates, key=lambda k: -candidates[k])
    route = ordered[0] if ordered else None
    score = candidates.get(route, 0)
    gap = score - (candidates[ordered[1]] if len(ordered)>1 else 0)
    reasons = []
    readonly = any(s.source == "constraint" for s in found)
    if explicit.get("intent"):
        route = explicit["intent"]
        if route not in PATTERNS:
            raise ValueError("Unknown explicit intent")
        score, gap = 1.0, 1.0
    if readonly:
        route, score, gap = "EXPLORE", 1.0, 1.0
    needs_model = score < threshold or gap < margin
    if needs_model:
        reasons.append("insufficient_signals" if not ordered else "low_confidence_or_conflicting_signals")
    if model and not readonly and not explicit.get("intent"):
        if model.get("intent") not in PATTERNS or not str(model.get("reason", "")).strip():
            raise ValueError("Model decision requires a known intent and reason")
        route, needs_model = model["intent"], False
        reasons.append("host_model:" + model["reason"])
    return {"route": "NEEDS_MODEL" if needs_model else route, "entry": ENTRIES.get(route),
            "requires_model": needs_model, "score": score, "score_kind": "heuristic_uncalibrated",
            "candidates": [{"intent": i, "score": candidates[i]} for i in ordered],
            "signals": [asdict(s) for s in found], "reasons": reasons,
            "objects": objects,
            "new_task": not needs_model and route in {"BUILD", "FIX", "REFACTOR"} and not explicit.get("task_id")}
