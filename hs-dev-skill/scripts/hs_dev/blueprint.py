"""Feature × scenario × case reconciliation for the behavior blueprint.

The registry is the machine-checkable core of the document system: a rewrite
consumes features and scenarios, and cases are the executable equivalence
criterion. Missing mappings block E9 readiness and task completion instead of
relying on review discipline; explicit deferral with a reason stays visible
instead of silently shrinking the denominator. Every current feature must
design a normal and an error scenario (B2.3 made mechanical), and UI features
must register authoritative copy so a rewrite reproduces the exact strings.
"""

from pathlib import Path

from .storage import local, read_json

REGISTRY = "hs_dev_docs/foundation/blueprint.json"
SCHEMA_VERSION = 1
SECTIONS = ("features", "scenarios", "cases")
OPTIONAL_SECTIONS = ("copy",)
KINDS = {"normal", "boundary", "error", "recovery"}
SURFACES = {"ui", "api", "cli", "service"}
REQUIRED_KINDS = ("normal", "error")


def load(root):
    return read_json(Path(root) / REGISTRY)


def _deferred_problems(row, label, errors):
    deferred = row.get("deferred")
    if deferred is None:
        return
    if not isinstance(deferred, dict) or not isinstance(deferred.get("reason"), str) or not deferred["reason"].strip():
        errors.append("Deferred requires a reason: " + label)


def reconcile(registry, root=None):
    """Structural and mapping integrity. Deferred entries keep counting, never vanish."""
    if not isinstance(registry, dict) or registry.get("schema_version") != SCHEMA_VERSION:
        return {"ok": False, "errors": ["Unsupported blueprint registry format"], "counts": {}}
    errors = []
    if set(registry) - {"schema_version", *SECTIONS, *OPTIONAL_SECTIONS}:
        errors.append("Unknown blueprint registry fields")
    for section in SECTIONS:
        if section not in registry:
            errors.append("Missing blueprint section: " + section)
    features, scenarios, cases = registry.get("features") or [], registry.get("scenarios") or [], registry.get("cases") or []
    copy_rows = registry.get("copy") or []
    if "copy" in registry and not isinstance(registry["copy"], list):
        errors.append("Invalid blueprint section: copy")
        copy_rows = []
    feature_ids, scenario_ids = {}, {}
    scenario_counts, case_counts, feature_kinds = {}, {}, {}
    deferred, waived = 0, 0
    for row in features:
        if not isinstance(row, dict):
            errors.append("Invalid feature row")
            continue
        fid = row.get("id")
        if not isinstance(fid, str) or not fid.strip():
            errors.append("Feature missing id")
            continue
        if fid in feature_ids:
            errors.append("Duplicate feature id: " + fid)
        feature_ids[fid] = row
        if not isinstance(row.get("title"), str) or not row["title"].strip():
            errors.append("Feature missing title: " + fid)
        if row.get("status", "current") not in {"current", "superseded"}:
            errors.append("Unknown feature status: " + fid)
        if row.get("surface") is not None and row.get("surface") not in SURFACES:
            errors.append("Unknown feature surface: " + fid)
        if row.get("not_applicable_reason") is not None and (
                not isinstance(row.get("not_applicable_reason"), str) or not row["not_applicable_reason"].strip()):
            errors.append("Feature waiver requires a reason: " + fid)
        if row.get("deferred") is not None:
            deferred += 1
        if row.get("not_applicable_reason"):
            waived += 1
        _deferred_problems(row, "feature " + fid, errors)
    for row in scenarios:
        if not isinstance(row, dict):
            errors.append("Invalid scenario row")
            continue
        sid = row.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append("Scenario missing id")
            continue
        if sid in scenario_ids:
            errors.append("Duplicate scenario id: " + sid)
        scenario_ids[sid] = row
        feature = feature_ids.get(row.get("feature"))
        if feature is None:
            errors.append("Scenario references unknown feature: " + str(row.get("feature")))
        elif feature.get("status", "current") == "current" and feature.get("deferred") is None:
            scenario_counts[feature["id"]] = scenario_counts.get(feature["id"], 0) + 1
            feature_kinds.setdefault(feature["id"], set()).add(row.get("kind", "normal"))
        if not isinstance(row.get("title"), str) or not row["title"].strip():
            errors.append("Scenario missing title: " + sid)
        if row.get("kind", "normal") not in KINDS:
            errors.append("Unknown scenario kind: " + sid)
        if row.get("deferred") is not None:
            deferred += 1
        _deferred_problems(row, "scenario " + sid, errors)
    planned = 0
    for row in cases:
        if not isinstance(row, dict):
            errors.append("Invalid case row")
            continue
        cid = row.get("id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append("Case missing id")
            continue
        scenario = scenario_ids.get(row.get("scenario"))
        if scenario is None:
            errors.append("Case references unknown scenario: " + str(row.get("scenario")))
        status = row.get("status", "current")
        if status not in {"current", "planned"}:
            errors.append("Unknown case status: " + cid)
        elif status == "planned":
            planned += 1
        evidence = row.get("evidence")
        if not isinstance(evidence, str) or not evidence.split("::")[0].strip():
            errors.append("Case missing evidence: " + cid)
        elif root is not None:
            path = evidence.split("::")[0].strip()
            try:
                file = local(root, path)
            except ValueError:
                errors.append("Invalid case evidence path: " + cid)
            else:
                if not file.is_file():
                    errors.append("Case evidence file missing: " + cid)
        if status == "current" and scenario is not None:
            case_counts[scenario["id"]] = case_counts.get(scenario["id"], 0) + 1
    copy_by_feature, copy_keys = {}, set()
    for row in copy_rows:
        if not isinstance(row, dict):
            errors.append("Invalid copy row")
            continue
        tid = row.get("id")
        if not isinstance(tid, str) or not tid.strip():
            errors.append("Copy missing id")
            continue
        feature = feature_ids.get(row.get("feature"))
        if feature is None:
            errors.append("Copy references unknown feature: " + str(row.get("feature")))
        else:
            copy_by_feature[feature["id"]] = copy_by_feature.get(feature["id"], 0) + 1
            key = (feature["id"], row.get("key"))
            if key in copy_keys:
                errors.append("Duplicate copy key: " + str(row.get("key")) + " (" + feature["id"] + ")")
            copy_keys.add(key)
        scenario = row.get("scenario")
        if scenario is not None:
            referred = scenario_ids.get(scenario)
            if referred is None:
                errors.append("Copy references unknown scenario: " + str(scenario))
            elif feature is not None and referred.get("feature") != row.get("feature"):
                errors.append("Copy scenario belongs to another feature: " + tid)
        if not isinstance(row.get("key"), str) or not row["key"].strip():
            errors.append("Copy missing key: " + tid)
        if not isinstance(row.get("text"), str) or not row["text"].strip():
            errors.append("Copy missing text: " + tid)
        if row.get("status", "current") not in {"current", "superseded"}:
            errors.append("Unknown copy status: " + tid)
    for fid, row in feature_ids.items():
        if row.get("status", "current") == "superseded" or row.get("deferred") is not None:
            continue
        if row.get("not_applicable_reason"):
            continue
        if not scenario_counts.get(fid):
            errors.append("Feature has no behavior scenarios: " + fid)
            continue
        kinds = feature_kinds.get(fid, set())
        for required in REQUIRED_KINDS:
            if required not in kinds:
                errors.append("Feature lacks a " + required + " scenario: " + fid)
        if row.get("surface") == "ui" and not copy_by_feature.get(fid):
            errors.append("UI feature has no authoritative copy: " + fid)
    for sid, row in scenario_ids.items():
        feature = feature_ids.get(row.get("feature"))
        if row.get("deferred") is not None or feature is None or feature.get("status", "current") == "superseded" \
                or feature.get("deferred") is not None or feature.get("not_applicable_reason"):
            continue
        if not case_counts.get(sid):
            errors.append("Scenario has no current test case: " + sid)
    counts = {"features": len(features), "scenarios": len(scenarios), "cases": len(cases), "copy": len(copy_rows),
              "deferred": deferred, "planned_cases": planned, "waived": waived}
    return {"ok": not errors, "errors": errors, "counts": counts}


def report(root):
    registry = load(root)
    if registry is None:
        return {"ok": True, "registry": False, "errors": [], "counts": {}}
    result = reconcile(registry, root=Path(root).resolve())
    result["registry"] = True
    return result


def require_ready(root):
    """Readiness gate: registries must exist, be populated and reconcile clean."""
    registry = load(root)
    if registry is None:
        raise ValueError("Blueprint registry missing: register features, scenarios and cases in " + REGISTRY)
    if not registry.get("features"):
        raise ValueError("Blueprint registry has no registered features")
    result = reconcile(registry, root=Path(root).resolve())
    if not result["ok"]:
        raise ValueError("Blueprint reconciliation failed: " + "; ".join(result["errors"][:8]))
    from . import contract_registry
    contract_registry.require_consistent(root)
