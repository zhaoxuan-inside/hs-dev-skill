"""Catalog-backed output contracts: evidence and decisions, not invented prose."""
import json
import re
from pathlib import Path
from .store import digest

CATALOG = Path(__file__).resolve().parents[2] / "references" / "catalog.json"
PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}|\b(?:TODO|TBD|FIXME)\b|待填写|待补充|按需填写", re.I)
EMPTY_CLAIMS = {"完成", "已完成", "正常", "通过", "无", "符合要求", "已按要求完成", "不适用", "同上", "见上文"}


def concrete(value, label):
    if not isinstance(value, str) or not value.strip() or PLACEHOLDER.search(value) or value.strip().rstrip("。.") in EMPTY_CLAIMS:
        raise ValueError(label + " requires a concrete, non-placeholder statement")
    return value.strip()


def catalog():
    value = json.loads(CATALOG.read_text())
    if value.get("version") != "0.0.2":
        raise ValueError("Catalog/runtime version mismatch")
    return value


def activity(activity_id):
    for stage in catalog()["stages"]:
        for item in stage["activities"]:
            if item["id"] == activity_id:
                return {**item, "stage": stage["id"], "questioning": stage["questioning"]}
    raise ValueError("Unknown activity: " + activity_id)


def contract(activity_id, output_id=None):
    item = activity(activity_id)
    selected = [o for o in item["outputs"] if not output_id or o["id"] == output_id]
    if not selected:
        raise ValueError("Unknown activity output")
    return {"version": "0.0.2", "activity": activity_id, "goal": item["goal"], "inputs": item["inputs"],
            "minimum": [{"id": f"{activity_id}.M{i}", "criterion": text} for i, text in enumerate(item["entry"], 1)],
            "outputs": [{**o, "questions": [{"id": f"{o['id']}.Q{i}", "question": q}
                          for i, q in enumerate(o["questions"], 1)],
                         "acceptance_checks": [{"id": f"{o['id']}.A{i}", "criterion": criterion}
                                               for i, criterion in enumerate(o["acceptance"], 1)]} for o in selected],
            "risks": item["risks"]}


def validate_output(activity_id, record, validate_sources):
    if not isinstance(record, dict):
        raise ValueError("Output judgment must be an object")
    spec = contract(activity_id, record.get("id"))["outputs"][0]
    if record.get("id") != spec["id"]:
        raise ValueError("Output id is required")
    concrete(record.get("scope"), "Output scope")
    expected = {q["id"] for q in spec["questions"]}
    answers = record.get("answers")
    if not isinstance(answers, list) or len(answers) != len(expected) or {a.get("id") for a in answers if isinstance(a, dict)} != expected:
        raise ValueError("Answer every template question exactly once")
    texts = []
    for answer in answers:
        texts.append(concrete(answer.get("answer"), answer["id"]))
        if answer.get("status") not in {"supported", "unknown", "conflict", "not-applicable"}:
            raise ValueError("Each answer needs a supported/unknown/conflict/not-applicable status")
        if answer["status"] != "supported":
            concrete(answer.get("reason"), "Unresolved or inapplicable reason")
            concrete(answer.get("next_action"), "Follow-up action")
        if answer["status"] in {"supported", "not-applicable"}:
            validate_sources(answer.get("source_ids"))
    if len(answers) > 1 and len(set(texts)) == 1:
        raise ValueError("Repeating one answer does not address different template questions")
    concrete(record.get("limitations"), "Evidence limits")
    acceptance = record.get("acceptance")
    expected_checks = {row["id"] for row in spec["acceptance_checks"]}
    if not isinstance(acceptance, list) or len(acceptance) != len(expected_checks) or {row.get("id") for row in acceptance if isinstance(row, dict)} != expected_checks:
        raise ValueError("Judge every output acceptance criterion exactly once")
    for row in acceptance:
        concrete(row.get("judgment"), row["id"] + " acceptance judgment")
        if row.get("status") not in {"supported", "unknown", "conflict", "not-applicable"}:
            raise ValueError("Acceptance judgment needs an explicit supported/unknown/conflict/not-applicable status")
        if row["status"] in {"supported", "not-applicable"}:
            validate_sources(row.get("source_ids"))
        if row["status"] != "supported":
            concrete(row.get("reason"), row["id"] + " reason")
            concrete(row.get("next_action"), row["id"] + " follow-up")
    return spec, all(a["status"] in {"supported", "not-applicable"} for a in answers + acceptance)


def render(spec, record):
    by_id = {a["id"]: a for a in record["answers"]}
    lines = [f"<!-- hs-output:{spec['id']}:start -->", "## " + spec["title"], "", "适用范围：" + record["scope"], ""]
    for question in spec["questions"]:
        answer = by_id[question["id"]]
        lines += ["### " + question["question"], "", answer["answer"], "",
                  "状态：" + answer["status"] + "；依据时点：" + answer.get("basis", "current") + "；依据：" + ", ".join(answer.get("source_ids", [])), ""]
        if answer.get("reason"):
            lines += ["原因：" + answer["reason"], "下一动作：" + answer["next_action"], ""]
    checks = {row["id"]: row for row in record["acceptance"]}
    lines += ["### 达成判据", ""]
    for criterion in spec["acceptance_checks"]:
        row = checks[criterion["id"]]
        lines += ["- " + criterion["criterion"] + "：" + row["status"] + "；" + row["judgment"] + "；依据时点：" + row.get("basis", "current") + "；依据：" + ", ".join(row.get("source_ids", []))]
        if row.get("reason"):
            lines += ["  原因：" + row["reason"] + "；下一动作：" + row["next_action"]]
    lines += ["", "证据与结论边界：" + record["limitations"], "", f"<!-- hs-output:{spec['id']}:end -->"]
    return "\n".join(lines)


def section(text, output_id):
    start, end = f"<!-- hs-output:{output_id}:start -->", f"<!-- hs-output:{output_id}:end -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) >= text.index(end):
        raise ValueError("Output section missing/duplicated: " + output_id)
    return text[text.index(start):text.index(end) + len(end)]


def insert(text, spec, record):
    marker = f"<!-- hs-output:{spec['id']}:start -->"
    rendered = render(spec, record)
    end = f"<!-- hs-output:{spec['id']}:end -->"
    if marker in text or end in text:
        return text.replace(section(text, spec["id"]), rendered)
    return text.rstrip() + "\n\n" + rendered + "\n"


def verify_catalog():
    data, ids, outputs, errors = catalog(), set(), set(), []
    for stage in data["stages"]:
        for item in stage["activities"]:
            if item["id"] in ids:
                errors.append("Duplicate activity " + item["id"])
            ids.add(item["id"])
            for field in ("goal", "inputs", "entry", "outputs", "risks"):
                if not item.get(field):
                    errors.append(item["id"] + " missing " + field)
            for output in item["outputs"]:
                if output["id"] in outputs or output["layer"] not in {"project", "delivery", "execution"}:
                    errors.append("Invalid output " + output["id"])
                outputs.add(output["id"])
                for field in ("questions", "evidence", "acceptance"):
                    if not output.get(field) or not all(isinstance(s, str) and s.strip() for s in output[field]):
                        errors.append(output["id"] + " missing " + field)
    return {"ok": not errors, "errors": errors, "stages": len(data["stages"]), "activities": len(ids), "outputs": len(outputs), "digest": digest(data)}
