#!/usr/bin/env python3
"""Versioned requirement baselines and transitive artifact validity (stdlib only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

STATE_PATH = "hs_dev_docs/_06_dev_process/_07_baselines/registry.json"
REQ_PATTERN = re.compile(r"\bREQ-[A-Za-z0-9_-]+\b")


def local_path(root, relative):
    root = Path(root).resolve()
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Expected a workspace-relative path")
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError("Path escapes workspace: " + relative)
    return path


def digest(root, relative):
    return hashlib.sha256(local_path(root, relative).read_bytes()).hexdigest()


def load_registry(root):
    path = local_path(root, STATE_PATH)
    if not path.exists():
        return {"schema_version": 1, "baselines": {}, "artifacts": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("schema_version") != 1 or not all(isinstance(state.get(k), dict) for k in ("baselines", "artifacts")):
        raise ValueError("Invalid baseline registry")
    if set(state["baselines"]) & set(state["artifacts"]):
        raise ValueError("Baseline and artifact IDs must be globally unique")
    for group in ("baselines", "artifacts"):
        for key, node in state[group].items():
            if not key or not isinstance(node, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(node.get("sha256", ""))):
                raise ValueError("Invalid baseline node: " + key)
            if node.get("status", "VALID") not in ("VALID", "INVALIDATED", "SUPERSEDED"):
                raise ValueError("Unknown baseline node status: " + key)
            if group == "baselines":
                requirements, assignments = node.get("requirements"), node.get("assignments")
                if not isinstance(requirements, list) or not requirements or not all(isinstance(r, str) and REQ_PATTERN.fullmatch(r) for r in requirements) or len(set(requirements)) != len(requirements):
                    raise ValueError("Invalid requirement denominator")
                if not isinstance(assignments, dict) or not assignments or not all(isinstance(ids, list) and ids for ids in assignments.values()):
                    raise ValueError("Invalid task assignments")
                owned = [r for ids in assignments.values() for r in ids]
                if not all(isinstance(r, str) for r in owned) or len(owned) != len(set(owned)) or set(owned) != set(requirements):
                    raise ValueError("Invalid task ownership coverage")
            elif not isinstance(node.get("dependencies"), list) or not node["dependencies"] or not all(isinstance(d, str) for d in node["dependencies"]):
                raise ValueError("Invalid artifact dependencies")
    return state


def save_registry(root, state):
    path = local_path(root, STATE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def freeze(root, baseline_id, version, source, requirements, confirmation, assignments):
    """Store an immutable reviewed denominator; never infer developer confirmation."""
    state = load_registry(root)
    if baseline_id in state["baselines"] or baseline_id in state["artifacts"]:
        raise ValueError("Baseline ID already exists; create a new revision")
    if not baseline_id or not version or not isinstance(confirmation, dict) or not all(
        isinstance(confirmation.get(k), str) and confirmation[k].strip()
        for k in ("source", "excerpt")
    ):
        raise ValueError("Version and actual confirmation source/excerpt are required")
    if not isinstance(requirements, list) or not requirements or any(
        not isinstance(r, str) or not REQ_PATTERN.fullmatch(r) for r in requirements
    ) or len(set(requirements)) != len(requirements):
        raise ValueError("Requirements must be nonempty unique REQ IDs")
    text = local_path(root, source).read_text(encoding="utf-8")
    if set(requirements) != set(REQ_PATTERN.findall(text)):
        raise ValueError("Denominator must match all REQ IDs in the dedicated scope source")
    if not isinstance(assignments, dict) or not assignments or any(
        not task or not isinstance(ids, list) or not ids for task, ids in assignments.items()
    ):
        raise ValueError("Explicit task ownership is required for every requirement")
    owned = [req for ids in assignments.values() for req in ids]
    if len(owned) != len(set(owned)) or set(owned) != set(requirements):
        raise ValueError("Task assignments must cover the full denominator exactly once")
    state["baselines"][baseline_id] = {
        "version": version, "source": source, "sha256": digest(root, source),
        "requirements": sorted(requirements), "confirmation": confirmation, "assignments": assignments,
    }
    save_registry(root, state)
    return state["baselines"][baseline_id]


def register_artifact(root, artifact_id, path, dependencies):
    state = load_registry(root)
    nodes = dict(state["baselines"], **state["artifacts"])
    if artifact_id in nodes or not artifact_id or not dependencies or len(set(dependencies)) != len(dependencies):
        raise ValueError("New artifact ID and unique dependencies are required")
    if any(dep not in nodes for dep in dependencies):
        raise ValueError("Unknown dependency")
    invalid = inspect_registry(root, state)["invalid"]
    if any(dep in invalid or nodes[dep].get("status") == "SUPERSEDED" for dep in dependencies):
        raise ValueError("Cannot derive from an invalid dependency")
    state["artifacts"][artifact_id] = {
        "path": path, "sha256": digest(root, path), "dependencies": list(dependencies),
        "status": "VALID",
    }
    save_registry(root, state)
    return state["artifacts"][artifact_id]


def inspect_registry(root, state=None):
    """Read-only, fail-closed check; no semantic-equivalence guesses."""
    state = load_registry(root) if state is None else state
    invalid = {}
    nodes = dict(state["baselines"], **state["artifacts"])
    for key, node in nodes.items():
        if node.get("status") == "SUPERSEDED":
            continue
        try:
            relative = node.get("source", node.get("path"))
            if digest(root, relative) != node["sha256"]:
                invalid[key] = "source_digest_changed"
        except (OSError, ValueError, KeyError, TypeError):
            invalid[key] = "missing_or_invalid_source"
        if node.get("status") == "INVALIDATED":
            invalid[key] = "explicitly_invalidated"
    visiting, visited = set(), set()

    def visit(key):
        if key in visiting:
            invalid[key] = "dependency_cycle"
            return
        if key in visited:
            return
        visiting.add(key)
        for dep in nodes[key].get("dependencies", []):
            if dep not in nodes:
                invalid[key] = "missing_dependency"
                continue
            visit(dep)
            if dep in invalid or nodes[dep].get("status") == "SUPERSEDED":
                invalid[key] = "invalid_dependency:" + dep
        visiting.remove(key)
        visited.add(key)

    for key in nodes:
        if nodes[key].get("status") != "SUPERSEDED":
            visit(key)
    return {"ok": not invalid, "invalid": invalid, "baselines": len(state["baselines"]), "artifacts": len(state["artifacts"])}


def invalidate(root):
    state = load_registry(root)
    report = inspect_registry(root, state)
    for key in report["invalid"]:
        if key in state["artifacts"]:
            state["artifacts"][key]["status"] = "INVALIDATED"
    save_registry(root, state)
    return report


def supersede(root, old_id, replacement_id):
    """Retire historical nodes only after a separately registered replacement exists."""
    state = load_registry(root)
    group = "baselines" if old_id in state["baselines"] else "artifacts"
    if old_id == replacement_id or old_id not in state[group] or replacement_id not in state[group]:
        raise ValueError("Supersession requires distinct existing nodes of the same type")
    report = inspect_registry(root, state)
    if replacement_id in report["invalid"] or state[group][replacement_id].get("status") == "SUPERSEDED":
        raise ValueError("Replacement must be current and valid")
    state[group][old_id]["status"] = "SUPERSEDED"
    state[group][old_id]["superseded_by"] = replacement_id
    save_registry(root, state)
    return inspect_registry(root, state)


def validate_coverage(root, record, task_id):
    """Check an acceptance against the externally stored full task denominator."""
    state = load_registry(root)
    if not state["baselines"]:
        raise ValueError("Missing requirement baseline; freeze the reviewed task scope first")
    binding = record.get("baseline")
    if not isinstance(binding, dict):
        raise ValueError("Acceptance must bind a baseline id/version/sha256")
    key = binding.get("id")
    baseline = state["baselines"].get(key)
    if not baseline or baseline.get("status") == "SUPERSEDED" or any(binding.get(k) != baseline[k] for k in ("version", "sha256")):
        raise ValueError("Acceptance baseline revision mismatch")
    report = inspect_registry(root, state)
    if key in report["invalid"]:
        raise ValueError("Acceptance baseline is invalid: " + key)
    if record.get("task_id") != task_id:
        raise ValueError("Task mismatch")
    current = [node_id for node_id, node in state["baselines"].items()
               if node.get("status") != "SUPERSEDED" and task_id in node.get("assignments", {})]
    if current != [key]:
        raise ValueError("Requirement denominator needs a unique current baseline; explicitly supersede older scope revisions")
    rows = record.get("requirements")
    if not isinstance(rows, list):
        raise ValueError("Acceptance needs complete requirements evidence")
    ids = []
    for row in rows:
        if not isinstance(row, dict) or row.get("result") != "PASS" or not row.get("evidence"):
            raise ValueError("Each requirement needs PASS and evidence")
        if not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError("Requirement id must be a string")
        local_path(root, row["evidence"]).read_bytes()
        ids.append(row.get("id"))
    expected = baseline.get("assignments", {}).get(task_id)
    if not expected or len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise ValueError("Requirement denominator mismatch: missing, extra or duplicate IDs")
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("Acceptance must bind registered derived artifacts")
    def ancestors(node_id):
        result = set()
        for dep in state["artifacts"].get(node_id, {}).get("dependencies", []):
            result.add(dep)
            result.update(ancestors(dep))
        return result
    for artifact in artifacts:
        if not isinstance(artifact, str) or artifact not in state["artifacts"] or artifact in report["invalid"] or state["artifacts"][artifact].get("status") == "SUPERSEDED":
            raise ValueError("Missing or invalid derived artifact: " + str(artifact))
        if key not in ancestors(artifact):
            raise ValueError("Artifact does not derive from acceptance baseline")
    return {"total": len(ids), "verified": len(ids)}


def validate_record_file(root, path, task_id, allow_historical=False):
    content = local_path(root, path).read_text(encoding="utf-8")
    match = re.search(r"<!--\s*HS_ACCEPTANCE_GATE_V1\s*(.*?)\s*HS_ACCEPTANCE_GATE_V1\s*-->", content, re.DOTALL)
    if not match:
        raise ValueError("Missing structured acceptance record")
    record = json.loads(match.group(1))
    if allow_historical:
        key = record.get("baseline", {}).get("id")
        node = load_registry(root)["baselines"].get(key, {})
        if node.get("status") == "SUPERSEDED":
            return {"historical": True, "current_acceptance": False}
    return validate_coverage(root, record, task_id)


def main(argv=None):
    from hs_paths import ensure_utf8_stdout
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("freeze")
    for name in ("id", "version", "source", "requirements", "confirmation", "assignments"):
        p.add_argument("--" + name, required=True)
    p = commands.add_parser("derive")
    for name in ("id", "path"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--depends-on", nargs="+", required=True)
    p = commands.add_parser("check")
    p.add_argument("--artifact", nargs="+", help="Require these current Pack/design IDs")
    commands.add_parser("invalidate")
    p = commands.add_parser("supersede")
    p.add_argument("--id", required=True)
    p.add_argument("--by", required=True)
    args = parser.parse_args(argv)
    root = Path(args.root)
    try:
        if args.command == "freeze":
            result = freeze(root, args.id, args.version, args.source, json.loads(args.requirements), json.loads(args.confirmation), json.loads(args.assignments))
        elif args.command == "derive":
            result = register_artifact(root, args.id, args.path, args.depends_on)
        elif args.command == "invalidate":
            result = invalidate(root)
        elif args.command == "supersede":
            result = supersede(root, args.id, args.by)
        else:
            result = inspect_registry(root)
            state = load_registry(root)
            if not state["baselines"]:
                result["invalid"]["__baseline__"] = "missing_requirement_baseline"
            for key in args.artifact or []:
                if key not in state["artifacts"] or state["artifacts"][key].get("status") == "SUPERSEDED":
                    result["invalid"][key] = "missing_or_superseded_artifact"
            result["ok"] = not result["invalid"]
        if args.command in ("check", "invalidate"):
            from execution_observer import emit
            emit(root, "baseline_gate", "baseline_check", "ok" if result["ok"] else "fail",
                 facts={"invalid_count": len(result["invalid"])})
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok", True) else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
