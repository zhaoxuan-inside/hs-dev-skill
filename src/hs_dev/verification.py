"""Actual command evidence, baseline consistency and traceability checks."""

from .contracts import OperationState

import json
import subprocess
from pathlib import Path
from .storage import CONTROL, identifier, local, now, read_json, sha, write_json

COMMAND_TIMEOUT = 120


def validate_commands(commands):
    if not isinstance(commands, list) or not commands or not all(
            isinstance(c, list) and c and all(isinstance(a, str) and a and "\0" not in a for a in c)
            for c in commands):
        raise ValueError("Checks require nonempty argv arrays, never shell strings")


def source_digest(root):
    from .indexing.engine import inventory
    return sha(json.dumps(inventory(root), sort_keys=True, ensure_ascii=False).encode())


def require_verified_sources(root, report):
    if not report["ok"] or report.get("source_digest") != source_digest(root):
        raise ValueError("Verified sources changed; run verification again before publishing")


def run_checks(root, commands, task_id):
    validate_commands(commands)
    baseline = source_digest(root)
    base = local(root, f"{CONTROL}/tasks/{task_id}/evidence/{identifier()}")
    base.mkdir(parents=True, exist_ok=False)
    results = []
    for number, command in enumerate(commands):
        output = base / f"check_{number}.log"
        with output.open("wb") as stream:
            try:
                process = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT,
                                         timeout=COMMAND_TIMEOUT, shell=False)
                code = process.returncode
            except subprocess.TimeoutExpired:
                code = 124
            except OSError as error:
                stream.write(str(error).encode())
                code = 127
        from .indexing.engine import fingerprint
        digest = fingerprint(output)
        results.append({"argv": command, "exit_code": code, "output": str(output.relative_to(root)), "sha256": digest})
    unchanged = source_digest(root) == baseline
    report = {"created_at": now(), "ok": unchanged and all(r["exit_code"] == 0 for r in results),
              "source_digest": baseline, "sources_unchanged": unchanged, "results": results}
    write_json(base / "result.json", report)
    return {**report, "evidence": str((base / "result.json").relative_to(root))}


def verify_workspace(root, require_clean=False, ignore_operation=None):
    from .indexing.engine import Index
    from .workspace import Workspace, CURRENT, BUSY
    workspace = Workspace(root)
    owner = CURRENT.get()
    state = workspace.inspect()
    if not owner and state["status"] in BUSY:
        result = {"ok": False, "errors": ["Workspace " + state["status"]],
                  "generation": state.get("revision"), "operation_id": state.get("operation_id")}
        if require_clean:
            raise ValueError(result["errors"][0])
        return result
    with Index(root) as index:
        status = index.verify()
    if not owner and state["status"] != "SAFE":
        status["errors"].append("Workspace " + state["status"])
    elif owner:
        workspace.assert_owner(owner)
    graph = read_json(Path(root) / "hs_dev_docs/foundation/object_graph.json")
    if graph is not None:
        result = coverage(graph["objects"], graph["relations"])
        status["errors"].extend(result["errors"])
    for path in (Path(root) / CONTROL / "recovery/operations").glob("*.json"):
        operation = read_json(path)
        if operation["operation_id"] != ignore_operation and operation["state"] in {OperationState.PREPARED, OperationState.VERIFIED, OperationState.INTERRUPTED}:
            status["errors"].append("Interrupted operation: " + operation["operation_id"])
    status["ok"] = not status["errors"]
    if not status["ok"] and not owner and state["status"] == "SAFE":
        def invalidate(value):
            if value["status"] == "SAFE":
                value.update(status="RECOVERY_REQUIRED", reason="Published workspace drift")
        workspace.update(invalidate)
    if require_clean and not status["ok"]:
        raise ValueError("Consistency gate blocked: " + "; ".join(status["errors"][:10]))
    return status


def coverage(nodes, edges):
    """Explicit object graph, not a claim that graph coverage proves behavior."""
    ids = [n["id"] for n in nodes]
    errors = []
    if len(ids) != len(set(ids)):
        errors.append("Duplicate object ID")
    lookup = {n["id"]: n for n in nodes}
    linked = set()
    for edge in edges:
        if edge["source"] not in lookup or edge["target"] not in lookup:
            errors.append("Dangling relationship: " + json.dumps(edge))
        linked.update((edge["source"], edge["target"]))
    for node in nodes:
        if node.get("required", True) and node["id"] not in linked and not node.get("not_applicable_reason"):
            errors.append("Uncovered object: " + node["id"])
        if node.get("kind") in {"method", "task"} and node.get("changed") and not any(
            e["source"] == node["id"] and lookup.get(e["target"], {}).get("kind") == "test" for e in edges
        ):
            errors.append("Changed object has no test mapping: " + node["id"])
    return {"ok": not errors, "errors": errors}
