"""Application orchestration; CLI parsing lives outside this module."""

from pathlib import Path
from . import workflow
from .config import environment, resolve
from .contracts import TaskStatus, OperationState
from .context import assemble
from .indexing.engine import Index
from .intake import classify
from .storage import CONTROL, append_event, atomic, identifier, local, now, read_json, write_json
from .support import recovery
from .verification import run_checks, verify_workspace, require_verified_sources



from .cli_values import json_value

def execute(args):
    root = Path(args.root).resolve()
    name = args.command
    if name.startswith("operation-"):
        from dataclasses import asdict
        from .workspace import Workspace, operation
        workspace = Workspace(root)
        if name == "operation-status":
            return workspace.inspect()
        if name == "operation-start":
            verify_workspace(root, require_clean=True)
            if args.task:
                workflow.load_task(root, args.task)
            for relative in args.scope:
                local(root, relative)
            scope = [str(local(root, relative).relative_to(root)) for relative in args.scope]
            return asdict(workspace.acquire(task_id=args.task, scope=scope))
        if name == "operation-revoke":
            return workspace.revoke(args.reason)
        if name in {"operation-finish", "operation-cancel"}:
            if not args.operation or args.fence is None:
                raise ValueError("Finish requires --operation and --fence")
            with operation(root, operation_id=args.operation, fence=args.fence) as permit:
                result = verify_workspace(root, require_clean=True)
                if name == "operation-cancel" and result["generation"] != workspace.inspect().get("base_revision"):
                    raise ValueError("Published changes cannot be cancelled; finish or rollback")
                return workspace.transition(permit, "SAFE", result["generation"])
    if name == "repair-index":
        from .indexing.engine import inventory, PUBLICATION
        publication = read_json(root / PUBLICATION)
        if not publication or publication["sources"] != inventory(root):
            raise ValueError("Repair only accepts unchanged sources; reconcile or rollback external edits")
        with Index(root) as index:
            return index.publish()
    if name == "dependency-bind":
        from .dependencies import bind
        return bind(root, args.task, args.consumer, args.producer, args.unit_id, args.actor, args.confirmation)
    if name == "trace-graph":
        from .support.trace_graph import graph, mermaid
        result = graph(root, args.task_id, args.limit)
        return mermaid(result) if args.format == "mermaid" else result
    if name == "trace-query":
        from .support.trace import query
        return query(root, args.limit, run_id=args.run_id, task_id=args.task_id, operation_id=args.operation_id,
                     activity_id=args.activity_id, stage_id=args.stage_id, context_id=args.context_id, event=args.event, outcome=args.outcome,
                     since=args.since, until=args.until)
    if name == "init":
        from .project import initialize
        return initialize(root)
    if name in {"status", "verify"}:
        return workflow.gate(root) if name == "status" else verify_workspace(root)
    if name == "coverage":
        from .verification import coverage
        graph = read_json(root / "hs_dev_docs/foundation/object_graph.json")
        if graph is None:
            raise ValueError("Register objects and relationships in the foundation object_graph.json")
        return coverage(graph["objects"], graph["relations"])
    if name == "config":
        return resolve(root, args.task, json_value(args.direct))
    if name == "env":
        return environment(root, args.name)
    if name == "classify":
        result = classify(root, args.text, json_value(args.signals), json_value(args.model))
        from .support.trace import emit
        emit(root, "intent", {"route": result["route"], "requires_model": result.get("requires_model", False),
                              "score": result.get("score", 0)})
        return result
    if name == "task-start":
        direct = {"execution": {"mode": args.mode}} if args.mode else None
        return workflow.start(root, args.title, args.activities.split(",") if args.activities else None, direct)
    if name == "task-continue":
        return workflow.continue_task(root, args.task)
    if name == "check":
        result = workflow.record_check(root, args.task, args.activity, args.item, args.result, args.evidence, args.reason)
        from .confirmation import on_ready
        result["confirmation"] = on_ready(root, args.task, workflow.approve)
        return result
    if name == "approve":
        return workflow.approve(root, args.task, args.scope, args.actor, args.confirmation)
    if name in {"acceptance", "acceptance-material", "acceptance-decide"}:
        from . import acceptance
        if name == "acceptance-material":
            return acceptance.register(root, args.task, args.activity, args.path, args.title, args.focus, args.unit_id)
        if name == "acceptance-decide":
            result = acceptance.decide(root, args.task, args.scope, args.materials.split(","), args.decision,
                                       args.actor, args.confirmation, args.reason, args.next_action, args.view_digest)
            from .confirmation import on_ready
            action = on_ready(root, args.task, workflow.approve, args.actor, args.confirmation, args.scope)
            result = acceptance.view(root, args.task, args.scope)
            return {**result, "confirmation": action}
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
        changes = json_value(args.changes)
        return recovery.commit(root, args.task, args.activity, changes, json_value(args.checks))
    if name == "rollback":
        return recovery.rollback_operation(root, args.recovery_operation)
    if name == "recover-lock":
        from .workspace import Workspace
        return Workspace(root).revoke("Explicit recovery decision: " + args.decision)
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
        task = workflow.load_task(root, args.task)
        if task["status"] != TaskStatus.ACTIVE or args.activity not in task["activities"]:
            raise ValueError("Reconcile requires an active task activity")
        workflow.enter_activity(root, task, args.activity)
        from .indexing.engine import inventory, PUBLICATION
        from .submission import validate_paths, register
        before_checks = inventory(root)
        previous = read_json(root / PUBLICATION)["sources"]
        changed = {p for p in set(before_checks) | set(previous) if before_checks.get(p) != previous.get(p)}
        validate_paths(root, changed)
        result = run_checks(root, json_value(args.checks), args.task)
        if not result["ok"] or inventory(root) != before_checks:
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
            if operation.get("activity", args.activity) != args.activity:
                raise ValueError("Interrupted operation belongs to a different activity")
            before = recovery.source_files(recovery.manifest(root, operation["snapshot_id"]))
            altered = {p for p in set(current) | set(before) if current.get(p) != before.get(p)}
            validate_paths(root, set(operation["paths"]) | altered)
            operation["paths"] = sorted(set(operation["paths"]) | altered)
            operation["postimage"] = {p: current.get(p) for p in operation["paths"]}
            operation["state"] = OperationState.VERIFIED
            write_json(file, operation)
            pending.append((file, operation))
        if not pending:
            previous = read_json(root / CONTROL / "index/publication.json")["sources"]
            altered = {p for p in set(current) | set(previous) if current.get(p) != previous.get(p)}
            if altered:
                selected = None
                for snapshot_file in sorted((root / CONTROL / "recovery/snapshots").glob("*/manifest.json"), reverse=True):
                    saved = read_json(snapshot_file)
                    if saved["task_id"] != args.task:
                        continue
                    source_before = recovery.source_files(saved)
                    if source_before == previous:
                        selected = recovery.manifest(root, saved["snapshot_id"])
                        break
                if selected is None:
                    raise ValueError("No exact prechange snapshot; restore or establish a reviewed recovery plan before rebasing")
                operation_id = identifier()
                operation = {"operation_id": operation_id, "task_id": args.task, "activity": args.activity, "snapshot_id": selected["snapshot_id"],
                             "created_at": now(), "state": OperationState.VERIFIED, "recovery_available": True,
                             "paths": sorted(altered), "postimage": {p: current.get(p) for p in altered}, "origin": "external_edit"}
                file = root / CONTROL / "recovery/operations" / (operation_id + ".json")
                write_json(file, operation)
                pending.append((file, operation))
        require_verified_sources(root, result)
        with Index(root) as index:
            publication = index.publish()
        require_verified_sources(root, result)
        register(root, task, args.activity, changed | {p for _, item in pending for p in item["paths"]})
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
        return assemble(root, json_value(args.request))
    if name == "connect":
        package = Path(args.skill_root).resolve() if args.skill_root else Path(__file__).resolve().parents[3]
        if not (package / "SKILL.md").is_file() and (package / "hs-dev-skill/SKILL.md").is_file():
            package = package / "hs-dev-skill"
        if not (package / "SKILL.md").is_file():
            raise ValueError("connect requires the complete bundle via --skill-root")
        target = local(root, args.target)
        text = target.read_text(encoding="utf-8") if target.exists() else ""
        marker = "<!-- hs-dev-skill:5 -->"
        if marker not in text:
            entry = package / "scripts/hs_dev.py"
            if not entry.is_file():
                entry = package / "hs-dev-skill/scripts/hs_dev.py"
            text += ("\n" + marker + "\n## Development entry\n\nBefore project investigation or mutation, read `" + str(package / "SKILL.md") + "`. "
                     "Run `python " + str(entry) + " --root " + str(root) + " status`. "
                     "Run its status gate; unresolved work or code/document/index drift blocks new tasks. "
                     "Classify with deterministic signals, lexical NLP and model reasoning. "
                     "Use current activity contracts, recovery and consistency checks. Pure consultation creates no task.\n")
            atomic(target, text)
            with Index(root) as index:
                index.publish()
        return {"ok": True, "path": str(target), "note": "Validate host triggering in a new session; this file cannot enforce an unloaded host"}
    if name == "install":
        from .support.update import install
        return install(args.source, args.target)
    raise ValueError("Unsupported command")
