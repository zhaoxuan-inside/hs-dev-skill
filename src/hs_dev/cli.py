"""One current CLI; argv-based verification, explicit repair and structured responses."""

import argparse
import json
import sys
from pathlib import Path
from . import __version__
from . import workflow
from .config import environment, resolve
from .contracts import TaskStatus, OperationState
from .context import assemble
from .indexing.engine import Index
from .intake import classify
from .storage import CONTROL, append_event, atomic, identifier, local, now, read_json, workspace_lock, write_json
from .support import recovery
from .verification import run_checks, verify_workspace


def json_value(value):
    if value is None:
        return None
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("init", "status", "verify", "retention", "serve", "coverage"):
        sub.add_parser(name)
    q = sub.add_parser("classify")
    q.add_argument("text")
    q.add_argument("--signals", default="{}")
    q.add_argument("--model")
    q = sub.add_parser("config")
    q.add_argument("--task")
    q.add_argument("--direct", default="{}")
    q = sub.add_parser("env")
    q.add_argument("name")
    q = sub.add_parser("task-start")
    q.add_argument("title")
    q.add_argument("--activities", help="Comma-separated reviewed impact scope")
    q.add_argument("--mode", choices=["mute", "stage", "activity"])
    q = sub.add_parser("task-continue")
    q.add_argument("task")
    q = sub.add_parser("check")
    q.add_argument("task")
    q.add_argument("activity")
    q.add_argument("item")
    q.add_argument("result", choices=["PASS", "FAIL", "NA"])
    q.add_argument("--evidence")
    q.add_argument("--reason", default="")
    q = sub.add_parser("approve")
    q.add_argument("task")
    q.add_argument("scope")
    q.add_argument("--actor", choices=["model", "human"], required=True)
    q.add_argument("--confirmation", required=True)
    q = sub.add_parser("acceptance", help="Unified progress, material cards and decisions")
    q.add_argument("task")
    q.add_argument("--scope")
    q.add_argument("--format", choices=["json", "markdown"], default="json")
    q = sub.add_parser("acceptance-material")
    q.add_argument("task")
    q.add_argument("activity")
    q.add_argument("path")
    q.add_argument("--title", required=True)
    q.add_argument("--focus", required=True)
    q = sub.add_parser("acceptance-decide")
    q.add_argument("task")
    q.add_argument("scope")
    q.add_argument("--materials", required=True, help="Comma-separated stable material IDs from acceptance")
    q.add_argument("--decision", choices=["pass", "reject", "defer", "repair"], required=True)
    q.add_argument("--actor", choices=["human", "model"], required=True)
    q.add_argument("--confirmation", required=True)
    q.add_argument("--reason", default="")
    q.add_argument("--next-action", default="")
    q.add_argument("--view-digest", required=True, help="Bind decisions to the reviewed acceptance view")
    q = sub.add_parser("complete")
    q.add_argument("task")
    q.add_argument("--checks", required=True, help="JSON argv arrays, or @JSON-file")
    q = sub.add_parser("commit")
    q.add_argument("task")
    q.add_argument("--activity", required=True)
    q.add_argument("--changes", required=True, help="JSON path -> UTF-8 text/null, or @JSON-file")
    q.add_argument("--checks", required=True)
    q = sub.add_parser("reconcile")
    q.add_argument("--task", required=True)
    q.add_argument("--decision", choices=["continue"], required=True)
    q.add_argument("--checks", required=True)
    q = sub.add_parser("rollback")
    q.add_argument("operation")
    q.add_argument("--decision", choices=["rollback"], required=True)
    q = sub.add_parser("recover-lock")
    q.add_argument("--decision", choices=["continue", "rollback"], required=True)
    q = sub.add_parser("task-rollback")
    q.add_argument("task")
    q.add_argument("--decision", choices=["rollback"], required=True)
    q = sub.add_parser("snapshot")
    q.add_argument("--task", required=True)
    q = sub.add_parser("search")
    q.add_argument("--query", default="")
    q.add_argument("--filters", default="{}")
    q.add_argument("--limit", type=int, default=10)
    q.add_argument("--match", choices=["terms", "phrase", "prefix"], default="terms")
    q = sub.add_parser("read")
    q.add_argument("path")
    q.add_argument("--start", type=int, default=1)
    q.add_argument("--end", type=int)
    q = sub.add_parser("relations")
    q.add_argument("object")
    q = sub.add_parser("context")
    q.add_argument("paths", nargs="+")
    q.add_argument("--task")
    q = sub.add_parser("service-query")
    q.add_argument("payload")
    q = sub.add_parser("connect")
    q.add_argument("--target", default="AGENTS.md")
    q.add_argument("--skill-root")
    q = sub.add_parser("install")
    q.add_argument("--source", required=True)
    q.add_argument("--target", required=True)
    return p


def execute(args):
    root = Path(args.root).resolve()
    name = args.command
    if name == "init":
        from .project import initialize
        return initialize(root)
    if name in {"status", "verify"}:
        return workflow.gate(root) if name == "status" else verify_workspace(root)
    if name == "coverage":
        from .verification import coverage
        graph = read_json(root / "hs_dev_docs/_00_foundation/object_graph.json")
        if graph is None:
            raise ValueError("Register objects and relationships in the foundation object_graph.json")
        return coverage(graph["objects"], graph["relations"])
    if name == "config":
        return resolve(root, args.task, json_value(args.direct))
    if name == "env":
        return environment(root, args.name)
    if name == "classify":
        return classify(root, args.text, json_value(args.signals), json_value(args.model))
    if name == "task-start":
        direct = {"execution": {"mode": args.mode}} if args.mode else None
        return workflow.start(root, args.title, args.activities.split(",") if args.activities else None, direct)
    if name == "task-continue":
        return workflow.continue_task(root, args.task)
    if name == "check":
        return workflow.record_check(root, args.task, args.activity, args.item, args.result, args.evidence, args.reason)
    if name == "approve":
        return workflow.approve(root, args.task, args.scope, args.actor, args.confirmation)
    if name in {"acceptance", "acceptance-material", "acceptance-decide"}:
        from . import acceptance
        if name == "acceptance-material":
            return acceptance.register(root, args.task, args.activity, args.path, args.title, args.focus)
        if name == "acceptance-decide":
            return acceptance.decide(root, args.task, args.scope, args.materials.split(","), args.decision,
                                     args.actor, args.confirmation, args.reason, args.next_action, args.view_digest)
        value = acceptance.view(root, args.task, args.scope)
        return acceptance.render(value, root) if args.format == "markdown" else value
    if name == "complete":
        return workflow.finish(root, args.task, json_value(args.checks))
    if name == "commit":
        task = workflow.load_task(root, args.task)
        if task["status"] != TaskStatus.ACTIVE:
            raise ValueError("Commit requires an active task")
        if args.activity not in task["activities"]:
            raise ValueError("Commit activity is outside task scope")
        workflow.enter_activity(root, task, args.activity)
        return recovery.commit(root, args.task, json_value(args.changes), json_value(args.checks))
    if name == "rollback":
        return recovery.rollback_operation(root, args.operation)
    if name == "recover-lock":
        import os
        lock = root / CONTROL / "mutation.lock"
        owner = read_json(lock)
        if not owner:
            return {"ok": True, "lock": "absent"}
        try:
            os.kill(owner["pid"], 0)
        except ProcessLookupError:
            lock.unlink()
            return {"ok": True, "lock": "released", "decision": args.decision,
                    "next": "Inspect interrupted operations; release alone does not resolve task blocking"}
        raise ValueError("Lock owner is alive or cannot be proven dead")
    if name == "task-rollback":
        task = workflow.load_task(root, args.task)
        if any(t["task_id"] > args.task for t in workflow.tasks(root)):
            raise ValueError("Later tasks exist; use scoped operation rollback to protect their work")
        saved = recovery.manifest(root, task["snapshot_id"])
        # Explicit task rollback restores the entire task baseline, not only document text.
        recovery.restore(root, task["snapshot_id"])
        task["status"] = TaskStatus.ROLLED_BACK
        task["restored_at"] = now()
        workflow.save_task(root, task)
        with Index(root) as index:
            index.publish()
        return {"ok": verify_workspace(root)["ok"], "task": task, "snapshot": saved["snapshot_id"]}
    if name == "snapshot":
        workflow.load_task(root, args.task)
        return {"snapshot_id": recovery.capture(root, args.task)}
    if name == "reconcile":
        # User's explicit continue is required; verification must precede any new baseline.
        workflow.load_task(root, args.task)
        result = run_checks(root, json_value(args.checks), args.task)
        if not result["ok"]:
            raise ValueError("Repair checks failed; indices were not published")
        pending = []
        from .indexing.engine import inventory
        current = inventory(root)
        for file in (root / CONTROL / "recovery/operations").glob("*.json"):
            operation = read_json(file)
            if operation.get("state") not in {OperationState.PREPARED, OperationState.VERIFIED, OperationState.INTERRUPTED}:
                continue
            if operation["task_id"] != args.task:
                raise ValueError("Another task has an interrupted operation")
            before = recovery.manifest(root, operation["snapshot_id"])["files"]
            altered = {p for p in set(current) | set(before) if not p.startswith(CONTROL + "/")
                       and Path(p).name not in {"file_index.jsonl", "content_index.jsonl"}
                       and current.get(p) != (before[p]["sha256"] if p in before else None)}
            operation["paths"] = sorted(set(operation["paths"]) | altered)
            operation["postimage"] = {p: current.get(p) for p in operation["paths"]}
            operation["state"] = OperationState.VERIFIED
            write_json(file, operation)
            pending.append((file, operation))
        if not pending:
            previous = read_json(root / CONTROL / "state/publication.json")["sources"]
            altered = {p for p in set(current) | set(previous) if current.get(p) != previous.get(p)}
            if altered:
                selected = None
                for snapshot_file in sorted((root / CONTROL / "recovery/snapshots").glob("*/manifest.json"), reverse=True):
                    saved = read_json(snapshot_file)
                    if saved["task_id"] != args.task:
                        continue
                    source_before = {p: value["sha256"] for p, value in saved["files"].items()
                                     if not p.startswith(CONTROL + "/") and Path(p).name not in {"file_index.jsonl", "content_index.jsonl"}}
                    if source_before == previous:
                        selected = recovery.manifest(root, saved["snapshot_id"])
                        break
                if selected is None:
                    raise ValueError("No exact prechange snapshot; restore or establish a reviewed recovery plan before rebasing")
                operation_id = identifier()
                operation = {"operation_id": operation_id, "task_id": args.task, "snapshot_id": selected["snapshot_id"],
                             "created_at": now(), "state": OperationState.VERIFIED, "recovery_available": True,
                             "paths": sorted(altered), "postimage": {p: current.get(p) for p in altered}, "origin": "external_edit"}
                file = root / CONTROL / "recovery/operations" / (operation_id + ".json")
                write_json(file, operation)
                pending.append((file, operation))
        with Index(root) as index:
            publication = index.publish()
        for file, operation in pending:
            operation.update(state=OperationState.COMMITTED, committed_at=now(), evidence=result["evidence"], resolution="explicit_continue")
            write_json(file, operation)
            append_event(root / CONTROL / "recovery/changelog" / (args.task + ".jsonl"), operation)
        verify_workspace(root, require_clean=True)
        return {"publication": publication, "verification": result}
    if name == "retention":
        settings = resolve(root)["values"]["retention"]
        active = [t for t in workflow.tasks(root) if t["status"] not in workflow.TERMINAL]
        removed = recovery.retain(root, settings["hours"], settings["snapshots"], [t["snapshot_id"] for t in active])
        return {"snapshots": removed, "tasks": workflow.expire(root, settings["hours"], settings["tasks"])}
    if name == "serve":
        from .indexing.service import serve
        serve(root)
        return {}
    if name == "service-query":
        from .indexing.service import request
        return request(root / CONTROL / "cache/index.sock", json_value(args.payload))
    if name == "relations":
        with Index(root) as index:
            return index.relationships(args.object)
    if name in {"search", "read"}:
        with Index(root) as index:
            return index.search(args.query, json_value(args.filters), args.limit, args.match) if name == "search" else index.exact(args.path, args.start, args.end)
    if name == "context":
        return assemble(root, args.paths, args.task)
    if name == "connect":
        package = Path(args.skill_root).resolve() if args.skill_root else Path(__file__).resolve().parents[2]
        if not (package / "SKILL.md").is_file():
            raise ValueError("connect requires the complete bundle via --skill-root")
        target = local(root, args.target)
        text = target.read_text(encoding="utf-8") if target.exists() else ""
        marker = "<!-- hs-dev-skill:5 -->"
        if marker not in text:
            text += ("\n" + marker + "\n## Development entry\n\nBefore project investigation or mutation, read `" + str(package / "SKILL.md") + "`. "
                     "Run `python " + str(package / "scripts/hs_dev.py") + " --root " + str(root) + " status`. "
                     "Run its status gate; unresolved work or code/document/index drift blocks new tasks. "
                     "Classify with deterministic signals, lexical NLP and model reasoning. "
                     "Use current activity contracts, recovery and consistency checks. Pure consultation creates no task.\n")
            atomic(target, text)
        return {"ok": True, "path": str(target), "note": "Validate host triggering in a new session; this file cannot enforce an unloaded host"}
    if name == "install":
        from .support.update import install
        return install(args.source, args.target)
    raise ValueError("Unsupported command")


MUTATIONS = {"init", "task-start", "task-continue", "check", "approve", "complete", "commit", "rollback", "task-rollback", "snapshot", "reconcile", "retention", "connect", "acceptance-material", "acceptance-decide"}


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command in MUTATIONS:
            with workspace_lock(args.root):
                result = execute(args)
        else:
            result = execute(args)
        from .support.trace import emit
        emit(args.root, "command", {"name": args.command, "ok": not isinstance(result, dict) or result.get("ok") is not False})
        if args.command == "acceptance" and args.format == "markdown":
            print(result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and result.get("ok") is False else 0
    except (ValueError, OSError, KeyError, SyntaxError, json.JSONDecodeError) as error:
        from .support.trace import emit
        emit(args.root, "command", {"name": args.command, "ok": False})
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
