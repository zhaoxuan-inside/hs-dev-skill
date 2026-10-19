"""Command parsing and presentation; application owns orchestration."""
import argparse
import json
import sqlite3
import sys
import time
from uuid import uuid4
from . import __version__
from .config import resolve
from .storage import workspace_lock
from .application import execute
from .presentation import metadata, render

def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--output", choices=["json", "text"], default="text")
    p.add_argument("--operation", help="UUID of an existing modification operation")
    p.add_argument("--fence", type=int)
    p.add_argument("--trace", action="store_true", default=None)
    p.add_argument("--wait", type=float)
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
    q.add_argument("--unit-id", required=True)
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
    q.add_argument("--activity", required=True)
    q.add_argument("--decision", choices=["continue"], required=True)
    q.add_argument("--checks", required=True)
    q = sub.add_parser("rollback")
    q.add_argument("recovery_operation")
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
    q.add_argument("request", help="Context request JSON or @JSON-file")
    q = sub.add_parser("service-query")
    q.add_argument("payload")
    q = sub.add_parser("connect")
    q.add_argument("--target", default="AGENTS.md")
    q.add_argument("--skill-root")
    q = sub.add_parser("install")
    q.add_argument("--source", required=True)
    q.add_argument("--target", required=True)
    for name in ("operation-start", "operation-finish", "operation-status", "operation-cancel", "repair-index"):
        q = sub.add_parser(name)
        if name == "operation-start":
            q.add_argument("--task")
            q.add_argument("--scope", action="append", default=[])
    q = sub.add_parser("operation-revoke")
    q.add_argument("--reason", required=True)
    q = sub.add_parser("dependency-bind")
    q.add_argument("task")
    q.add_argument("consumer")
    q.add_argument("producer")
    q.add_argument("unit_id")
    q.add_argument("--actor", choices=["human", "model"], required=True)
    q.add_argument("--confirmation", required=True)
    q = sub.add_parser("trace-query")
    q.add_argument("--limit", type=int, default=20)
    q.add_argument("--run-id")
    q.add_argument("--task-id")
    q.add_argument("--operation-id")
    q.add_argument("--activity-id")
    q.add_argument("--event")
    q.add_argument("--outcome")
    q.add_argument("--since")
    q.add_argument("--until")
    return p


MUTATIONS = {"init", "task-start", "task-continue", "check", "approve", "complete", "commit", "rollback", "task-rollback", "snapshot", "reconcile", "retention", "connect", "acceptance-material", "acceptance-decide", "dependency-bind", "repair-index"}


def main(argv=None):
    args = parser().parse_args(argv)
    from .workspace import Workspace
    from .support.trace import RUN, ENABLED, emit
    run_token = RUN.set(str(uuid4()))
    trace_token = ENABLED.set(args.trace)
    started = time.monotonic()
    try:
        workspace = Workspace(args.root)
        exempt = {"init", "status", "verify", "operation-status", "operation-start", "operation-revoke",
                  "operation-finish", "operation-cancel", "recover-lock", "reconcile", "rollback", "task-rollback", "repair-index", "install"}
        settings = resolve(args.root)["values"]
        args.wait = settings["workspace"]["wait_seconds"] if args.wait is None else args.wait
        if args.wait < 0 or args.wait > 60:
            raise ValueError("Wait budget must be between 0 and 60 seconds")
        meta = metadata(args.command, getattr(args, "mode", None) or settings["execution"]["mode"], args.trace or settings["trace"]["enabled"])
        if args.output == "text":
            print(render({}, meta).split("\n", 1)[0], flush=True)
        if args.command not in exempt and not args.operation:
            workspace.ticket(args.wait)
        if args.command in MUTATIONS:
            with workspace_lock(args.root, recovery=args.command in {"reconcile", "rollback", "task-rollback", "repair-index"},
                                initialize=args.command == "init", operation_id=args.operation, fence=args.fence,
                                task_id=getattr(args, "task", None)):
                result = execute(args)
        else:
            result = execute(args)
        settings = resolve(args.root)["values"]
        meta = metadata(args.command, settings["execution"]["mode"], args.trace or settings["trace"]["enabled"])
        ok = not isinstance(result, dict) or result.get("ok") is not False
        emit(args.root, "command", {"name": args.command, "ok": ok, "duration_ms": round((time.monotonic()-started)*1000, 3)})
        if args.output == "json":
            if args.command == "context":
                from .context_budget import encode
                print(encode({"meta": meta, "result": result}))
            else:
                print(json.dumps({"meta": meta, "result": result}, ensure_ascii=False, indent=2))
        else:
            print(render(result, meta).split("\n", 1)[1].lstrip("\n"))
        return 0 if ok else 1
    except (ValueError, OSError, KeyError, SyntaxError, TypeError, sqlite3.Error) as error:
        emit(args.root, "command", {"name": args.command, "ok": False, "reason_code": type(error).__name__})
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    finally:
        RUN.reset(run_token)
        ENABLED.reset(trace_token)
