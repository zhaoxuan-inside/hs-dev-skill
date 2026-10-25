"""Actual command evidence, baseline consistency and traceability checks."""

from .contracts import OperationState

import json
import subprocess
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from .storage import CONTROL, identifier, local, now, read_json, sha, write_json

COMMAND_TIMEOUT = 120
GATES = "hs_dev_docs/foundation/gates.json"
GATE_ENTRY_FIELDS = {"id", "title", "argv", "report"}
REPORT_FORMATS = {"junit"}


def validate_commands(commands):
    if not isinstance(commands, list) or not commands or not all(
            isinstance(c, list) and c and all(isinstance(a, str) and a and "\0" not in a for a in c)
            for c in commands):
        raise ValueError("Checks require nonempty argv arrays, never shell strings")


def load_gates(root):
    """Declared verification entries; absent or empty entries keep bootstrap free-form."""
    doc = read_json(Path(root) / GATES)
    if doc is None:
        return {"schema_version": 1, "entries": []}
    problems = []
    if not isinstance(doc, dict) or doc.get("schema_version") != 1:
        raise ValueError("Unsupported gates registry format in " + GATES)
    if set(doc) - {"schema_version", "entries"}:
        problems.append("Unknown gates registry fields")
    entries = doc.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Gates registry requires an entries array")
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) - GATE_ENTRY_FIELDS:
            problems.append("Invalid gate entry")
            continue
        gid = entry.get("id")
        if not isinstance(gid, str) or not gid.strip():
            problems.append("Gate missing id")
        elif gid in seen:
            problems.append("Duplicate gate id: " + gid)
        seen.add(gid)
        try:
            validate_commands([entry.get("argv")])
        except (ValueError, TypeError):
            problems.append("Gate argv must be one nonempty argv array: " + str(gid))
        report = entry.get("report")
        if report is not None:
            if not isinstance(report, dict) or set(report) - {"format", "path"} \
                    or report.get("format") not in REPORT_FORMATS \
                    or not isinstance(report.get("path"), str) or not report["path"].strip():
                problems.append("Gate report requires format junit and a path: " + str(gid))
            elif not report["path"].startswith(CONTROL + "/"):
                problems.append("Gate report paths must stay inside the runtime directory ("
                                + CONTROL + "/...): " + str(gid))
            else:
                local(root, report["path"])
    if problems:
        raise ValueError("Invalid gates registry: " + "; ".join(problems))
    return doc


def _junit_summary(root, report):
    """Parse a junit XML report: case names plus failure/error/skip counts."""
    file = local(root, report["path"])
    if not file.is_file():
        return {"ok": False, "error": "Report file missing: " + report["path"]}
    try:
        tree = ElementTree.parse(file)
    except ElementTree.ParseError as error:
        return {"ok": False, "error": "Report is not valid XML: " + str(error)}
    names, failed, skipped = [], [], 0
    for case in tree.iter("testcase"):
        name = ((case.get("classname") + "." if case.get("classname") else "") + (case.get("name") or "")).strip()
        if name:
            names.append(name)
        verdict = "passed"
        for child in case:
            tag = child.tag.split("}")[-1]
            if tag in {"failure", "error"}:
                verdict = tag
                failed.append(name or "<unnamed>")
            elif tag == "skipped":
                verdict = "skipped"
        if verdict == "skipped":
            skipped += 1
    return {"ok": not failed, "report_path": report["path"], "sha256": sha(file.read_bytes()),
            "cases": len(names), "failures": failed, "skipped": skipped, "names": names[:500]}


def resolve_gate_commands(root, commands):
    """Declared gates accept only gate:<id> selectors; bootstrap accepts free-form argv."""
    validate_commands(commands)
    gates = load_gates(root)
    entries = {entry["id"]: entry for entry in gates["entries"]}
    resolved = []
    if entries:
        for command in commands:
            if len(command) == 1 and command[0].startswith("gate:"):
                gid = command[0][5:]
                if gid not in entries:
                    raise ValueError("Unknown verification gate: " + gid)
                resolved.append(entries[gid])
            else:
                raise ValueError("Gates are declared; verification must select gate:<id> entries from " + GATES)
    else:
        resolved = [{"id": None, "argv": command, "report": None} for command in commands]
    return gates, resolved


def source_digest(root):
    from .indexing.engine import inventory
    return sha(json.dumps(inventory(root), sort_keys=True, ensure_ascii=False).encode())


def require_verified_sources(root, report):
    if not report["ok"] or report.get("source_digest") != source_digest(root):
        raise ValueError("Verified sources changed; run verification again before publishing")


def run_checks(root, commands, task_id):
    gates, resolved = resolve_gate_commands(root, commands)
    baseline = source_digest(root)
    base = local(root, f"{CONTROL}/tasks/{task_id}/evidence/{identifier()}")
    base.mkdir(parents=True, exist_ok=False)
    results, reports = [], []
    for number, entry in enumerate(resolved):
        command = entry["argv"]
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
        row = {"gate": entry["id"], "argv": command, "exit_code": code,
               "output": str(output.relative_to(root)), "sha256": digest}
        if entry.get("report"):
            summary = _junit_summary(root, entry["report"])
            row["report"] = summary
            reports.append(summary)
        results.append(row)
    unchanged = source_digest(root) == baseline
    clean = all(r["exit_code"] == 0 for r in results) and all(
        r.get("report") is None or r["report"].get("ok") for r in results)
    report = {"created_at": now(), "ok": unchanged and clean,
              "source_digest": baseline, "sources_unchanged": unchanged,
              "gates": "declared" if gates["entries"] else "undeclared", "reports": reports, "results": results}
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
    index_clean = not status["errors"]
    if index_clean:
        from . import kernel
        status["errors"].extend(kernel.validate(root)["errors"])
    if not owner and state["status"] != "SAFE":
        status["errors"].append("Workspace " + state["status"])
    elif owner:
        workspace.assert_owner(owner)
    graph = read_json(Path(root) / "hs_dev_docs/foundation/object_graph.json")
    if graph is None:
        status["errors"].append("Object registry missing: hs_dev_docs/foundation/object_graph.json")
    elif not isinstance(graph, dict):
        status["errors"].append("Invalid object registry structure")
    else:
        status["errors"].extend(coverage(graph.get("objects"), graph.get("relations"))["errors"])
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
    """Explicit object graph: every object stays linked or explicitly waived with a reason."""
    if not isinstance(nodes, list) or not isinstance(edges, list):
        return {"ok": False, "errors": ["Invalid object registry structure"]}
    errors, lookup, ids = [], {}, []
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"].strip():
            errors.append("Object missing id")
            continue
        ids.append(node["id"])
        lookup[node["id"]] = node
    if len(ids) != len(set(ids)):
        errors.append("Duplicate object ID")
    linked = set()
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("source") not in lookup or edge.get("target") not in lookup:
            errors.append("Dangling relationship: " + json.dumps(edge, sort_keys=True, default=str))
            continue
        linked.update((edge["source"], edge["target"]))
    for node in lookup.values():
        if node["id"] not in linked and not node.get("not_applicable_reason"):
            errors.append("Uncovered object: " + node["id"])
        if node.get("kind") in {"method", "task"} and node.get("changed") and not any(
            isinstance(e, dict) and e.get("source") == node["id"] and lookup.get(e.get("target"), {}).get("kind") == "test" for e in edges
        ):
            errors.append("Changed object has no test mapping: " + node["id"])
    return {"ok": not errors, "errors": errors}
