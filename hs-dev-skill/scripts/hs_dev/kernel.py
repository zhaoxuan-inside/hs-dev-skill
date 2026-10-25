"""Structured contract kernels and the ID chain plus documentation-debt engine.

A kernel is the machine authority embedded in a Markdown :::contract block. The
chain feature -> behavior -> case -> contract -> symbol must resolve end to end:
dangling links fail the consistency gate the same way drift does. Documentation
debt is the reverse direction — code that moved after the decision that
documented it. Debt blocks release unless explicitly waived by a human with the
debt's own digest, so an old waiver never covers new drift.
"""

import json
from pathlib import Path

from .storage import append_event, sha

WAIVERS = "hs_dev_docs/foundation/doc_debt_waivers.jsonl"
KERNEL_KINDS = ("feature", "behavior", "interface", "data", "method")


def _index_tables(root):
    """Current unit revisions from the published index; None when not initialized."""
    from .indexing.engine import PUBLICATION, Index
    if not (Path(root) / PUBLICATION).is_file():
        return None
    revisions = {}
    with Index(root) as index:
        for row in index.connect().execute("SELECT key, properties FROM items"):
            revisions[row["key"]] = json.loads(row["properties"]).get("unit_revision")
    return revisions


def load(root):
    """Kernels with payloads straight from published sources; None when not initialized."""
    from .indexing.engine import PUBLICATION
    if not (Path(root) / PUBLICATION).is_file():
        return None
    from .indexing.engine import Index
    from .indexing.semantic import contract_kernel
    result = {}
    with Index(root) as index:
        rows = list(index.connect().execute(
            "SELECT i.key, i.path FROM items i "
            "JOIN attributes a ON a.item = i.key WHERE a.name='unit_kind' AND a.value='kernel'"))
    for row in rows:
        text = (Path(root) / row["path"]).read_text(encoding="utf-8")
        for entry in contract_kernel(text, row["path"]):
            entry["unit_id"] = row["key"]
            result[entry["id"]] = entry
    return result


def validate(root):
    """ID-chain reconciliation across kernels, blueprint, contracts and code units."""
    kernels = load(root)
    if kernels is None:
        return {"ok": True, "errors": [], "counts": {"kernels": 0}, "initialized": False}
    errors = []
    from . import blueprint as blueprint_module
    from . import contract_registry
    registry = blueprint_module.load(root) or {}
    features = {row.get("id"): row for row in registry.get("features") or [] if isinstance(row, dict)}
    scenarios = {row.get("id"): row for row in registry.get("scenarios") or [] if isinstance(row, dict)}
    cases = {row.get("id"): row for row in registry.get("cases") or [] if isinstance(row, dict)}
    contracts_doc = contract_registry.load(root) or {}
    contracts = {row.get("id"): row for row in contracts_doc.get("contracts") or [] if isinstance(row, dict)}
    revisions = _index_tables(root) or {}

    def require_links(kernel, field, universe, label, required):
        values = kernel["payload"].get(field) or []
        if isinstance(values, str):
            values = [values]
        if not values and required:
            if field == "implemented_by" and kernel["payload"].get("unimplemented_reason"):
                return
            errors.append("Kernel " + kernel["id"] + " requires " + field + " links")
            return
        for target in values:
            if target not in universe:
                errors.append("Kernel " + kernel["id"] + " references unknown " + label + ": " + target)

    for kernel in kernels.values():
        kind = kernel["kind"]
        if kind == "feature":
            require_links(kernel, "scenarios", scenarios, "scenario", required=False)
        elif kind == "behavior":
            require_links(kernel, "feature", {**features, **{k: None for k in kernels if kernels[k]["kind"] == "feature"}}, "feature", required=True)
            require_links(kernel, "covered_by", {cid: row for cid, row in cases.items()
                                                 if row.get("status", "current") == "current"}, "case", required=True)
            require_links(kernel, "implemented_by", revisions, "code unit", required=True)
        elif kind in ("interface", "data"):
            require_links(kernel, "contract", {cid for cid, row in contracts.items()
                                               if row.get("status", "current") == "current"}, "registered contract", required=True)
        elif kind == "method":
            require_links(kernel, "implemented_by", revisions, "code unit", required=True)
    return {"ok": not errors, "errors": errors,
            "counts": {"kernels": len(kernels), "by_kind": {kind: sum(1 for k in kernels.values() if k["kind"] == kind)
                                                            for kind in KERNEL_KINDS if any(k["kind"] == kind for k in kernels.values())}},
            "initialized": True}


def report(root):
    return validate(root)


def require_consistent(root):
    result = validate(root)
    if not result["ok"]:
        raise ValueError("Contract kernel chain broken: " + "; ".join(result["errors"][:8]))


def _row_digest(row):
    return sha(json.dumps({k: row[k] for k in sorted(row) if k != "waived"}, ensure_ascii=False).encode())


def doc_debt(root):
    """Stale decisions plus behaviors whose code drifted past the latest decision anchor."""
    rows = []
    from . import decisions
    try:
        entries = decisions.read_entries(root)
        state = decisions.statuses(root, entries)
    except ValueError as error:
        return [{"key": "ledger", "source": "decision", "reason": str(error)}]
    for entry in entries:
        if entry["event"] == "accepted" and state.get(entry["decision_id"]) == "stale":
            rows.append({"key": "decision:" + entry["decision_id"], "source": "decision",
                         "id": entry["decision_id"], "reason": "决策绑定的文档或代码内容已变化，需复核或推翻"})
    anchor = {}
    for entry in entries:
        for binding in [*entry.get("units", []), *entry.get("describes", [])]:
            anchor[binding["unit_id"]] = binding["unit_revision"]
    kernels = load(root) or {}
    revisions = _index_tables(root) or {}
    for kernel in kernels.values():
        if kernel["kind"] not in ("behavior", "method"):
            continue
        drifted, missing = [], []
        implemented = kernel["payload"].get("implemented_by") or []
        if isinstance(implemented, str):
            implemented = [implemented]
        for unit_id in implemented:
            current = revisions.get(unit_id)
            if current is None:
                missing.append(unit_id)
            elif unit_id in anchor and anchor[unit_id] != current:
                drifted.append({"unit_id": unit_id, "anchored": anchor[unit_id][:12], "current": current[:12]})
        if drifted or missing:
            detail = []
            if missing:
                detail.append("缺失实现单元: " + ", ".join(missing))
            if drifted:
                detail.append("代码已变化: " + ", ".join(
                    item["unit_id"] + f" ({item['anchored']}->{item['current']})" for item in drifted))
            rows.append({"key": "kernel:" + kernel["id"], "source": kernel["kind"], "id": kernel["id"],
                         "reason": "；".join(detail)})
    for row in rows:
        row["digest"] = _row_digest(row)
    return rows


def waivers(root):
    path = Path(root) / WAIVERS
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def debt_report(root):
    rows = doc_debt(root)
    active = {row["key"]: row["digest"] for row in rows}
    covered = {row["key"] for row in waivers(root) if row.get("debt_digest") == active.get(row["key"])}
    return {"ok": not [row for row in rows if row["key"] not in covered], "rows": rows, "waived": sorted(covered),
            "counts": {"debt": len(rows), "waived": len(covered), "blocking": len(rows) - len(covered)}}


def require_no_debt(root):
    report = debt_report(root)
    blocking = [row for row in report["rows"] if row["key"] not in report["waived"]]
    if blocking:
        raise ValueError("Documentation debt blocks release (fix or waive via doc-debt-waive): "
                         + "; ".join(row["key"] + " " + row["reason"] for row in blocking[:8]))


def waive(root, key, reason, actor):
    if actor != "human":
        raise ValueError("Debt waivers require a human actor; fix the documentation instead")
    if not reason.strip():
        raise ValueError("Debt waiver requires a reason")
    row = next((row for row in doc_debt(root) if row["key"] == key), None)
    if row is None:
        raise ValueError("No current documentation debt for key: " + key)
    event = {"key": key, "reason": reason, "actor": actor, "debt_digest": row["digest"]}
    path = Path(root) / WAIVERS
    path.parent.mkdir(parents=True, exist_ok=True)
    append_event(path, event)
    from .indexing.engine import Index
    with Index(root) as index:
        index.publish()
    return {"ok": True, **event}
