"""Durable workspace ownership. UUID identifies work; fence invalidates old owners."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sqlite3
import time
from uuid import uuid4

CURRENT = ContextVar("hs_workspace_permit", default=None)
BUSY = {"MUTATING", "VERIFYING", "PUBLISHING", "ROLLING_BACK"}


@dataclass(frozen=True)
class OperationPermit:
    root: str
    operation_id: str
    fence: int
    pid: int
    task_id: str | None = None
    scope: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReadTicket:
    revision: str | None
    fence: int


class Workspace:
    def __init__(self, root):
        self.root = Path(root).resolve()
        from .storage import local
        self.path = local(self.root, "hs-dev-skill/state/workspace.sqlite")

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.path, timeout=5)
        db.execute("CREATE TABLE IF NOT EXISTS workspace(id INTEGER PRIMARY KEY CHECK(id=1), value TEXT NOT NULL)")
        db.execute("INSERT OR IGNORE INTO workspace VALUES(1,?)", (json.dumps({
            "schema_version": 1, "status": "UNINITIALIZED", "fence": 0,
            "operation_id": None, "pid": None, "revision": None, "heartbeat": None}),))
        db.commit()
        return db

    def inspect(self):
        if not self.path.exists():
            return {"status": "UNINITIALIZED", "fence": 0, "revision": None, "operation_id": None}
        with sqlite3.connect(f"file:{self.path}?mode=ro", uri=True) as db:
            value = json.loads(db.execute("SELECT value FROM workspace WHERE id=1").fetchone()[0])
        if value.get("schema_version") != 1:
            raise ValueError("Unsupported workspace state format")
        return value

    def update(self, transform):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            value = json.loads(db.execute("SELECT value FROM workspace WHERE id=1").fetchone()[0])
            transform(value)
            db.execute("UPDATE workspace SET value=? WHERE id=1", (json.dumps(value),))
        return value

    def acquire(self, recovery=False, initialize=False, task_id=None, scope=()):
        operation_id = str(uuid4())
        def take(value):
            allowed = {"SAFE"}
            if initialize:
                allowed.add("UNINITIALIZED")
            if recovery:
                allowed.add("RECOVERY_REQUIRED")
            if value["status"] not in allowed:
                raise ValueError(f"Workspace {value['status']}; current UUID {value['operation_id']}")
            value.update(status="MUTATING", operation_id=operation_id, fence=value["fence"] + 1,
                         pid=os.getpid(), writer_pid=None, heartbeat=time.time(), base_revision=value.get("revision"),
                         task_id=task_id, scope=list(scope))
        state = self.update(take)
        from .support.trace import emit
        emit(self.root, "operation_acquire", {"operation_id": operation_id, "task_id": task_id, "outcome": "MUTATING"})
        return OperationPermit(str(self.root), operation_id, state["fence"], os.getpid(), task_id, tuple(scope))

    def writer(self, permit, release=False):
        """Same-UUID commands share ownership, but cannot overwrite each other."""
        def update(value):
            if value["operation_id"] != permit.operation_id or value["fence"] != permit.fence:
                raise ValueError("Stale workspace writer")
            if release:
                if value.get("writer_pid") == os.getpid():
                    value["writer_pid"] = None
                return
            if value.get("writer_pid") is not None:
                raise ValueError("Another participant is writing; wait before joining this UUID")
            value.update(writer_pid=os.getpid(), heartbeat=time.time())
        return self.update(update)

    def assert_owner(self, permit):
        state = self.inspect()
        if (permit is None or permit.root != str(self.root) or state["operation_id"] != permit.operation_id
                or state["fence"] != permit.fence or state["status"] not in BUSY):
            raise ValueError("Stale or mismatched workspace UUID/fence")
        return state

    def transition(self, permit, status, revision=None):
        if status not in BUSY | {"SAFE", "RECOVERY_REQUIRED"}:
            raise ValueError("Invalid workspace status")
        def move(value):
            if value["operation_id"] != permit.operation_id or value["fence"] != permit.fence:
                raise ValueError("Stale workspace owner")
            value.update(status=status, heartbeat=time.time())
            if revision is not None:
                value["revision"] = revision
            if status in {"SAFE", "RECOVERY_REQUIRED"}:
                value.update(operation_id=None, pid=None, writer_pid=None)
        state = self.update(move)
        from .support.trace import emit
        emit(self.root, "workspace_transition", {"operation_id": permit.operation_id, "task_id": permit.task_id, "outcome": status})
        return state

    def revoke(self, reason):
        if not reason.strip():
            raise ValueError("Revocation requires a reason")
        def revoke(value):
            for pid in {value.get("pid"), value.get("writer_pid")} - {None}:
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    raise ValueError("Owner is still alive; stop it before revocation")
            value.update(fence=value["fence"] + 1, status="RECOVERY_REQUIRED", operation_id=None,
                         pid=None, writer_pid=None, reason=reason)
        return self.update(revoke)

    def ticket(self, timeout=0):
        deadline = time.monotonic() + timeout
        while True:
            state = self.inspect()
            permit = CURRENT.get()
            if permit and permit.root == str(self.root):
                self.assert_owner(permit)
                return ReadTicket(state.get("revision"), state["fence"])
            if state["status"] == "SAFE":
                return ReadTicket(state["revision"], state["fence"])
            if state["status"] not in BUSY or time.monotonic() >= deadline:
                raise ValueError(f"Workspace {state['status']}; wait or recover before reading")
            time.sleep(min(0.05, max(0, deadline - time.monotonic())))

    def validate_ticket(self, ticket):
        if self.ticket() != ticket:
            raise ValueError("Workspace changed during reading; discard and retry")


@contextmanager
def operation(root, recovery=False, initialize=False, operation_id=None, fence=None, task_id=None, scope=()):
    workspace = Workspace(root)
    existing = CURRENT.get()
    if existing and existing.root == str(workspace.root):
        workspace.assert_owner(existing)
        yield existing
        return
    supplied = operation_id is not None
    state = workspace.inspect()
    if supplied and state.get("task_id") and task_id and task_id != state["task_id"]:
        raise ValueError("UUID belongs to a different task")
    permit = (OperationPermit(str(workspace.root), operation_id, fence, os.getpid(), state.get("task_id"), tuple(state.get("scope", []))) if supplied
              else workspace.acquire(recovery=recovery, initialize=initialize, task_id=task_id, scope=scope))
    workspace.assert_owner(permit)
    workspace.writer(permit)
    token = CURRENT.set(permit)
    try:
        yield permit
        if supplied:
            return
        from .verification import verify_workspace
        result = verify_workspace(root)
        if not result["ok"]:
            raise ValueError("Cannot release unsafe workspace: " + "; ".join(result["errors"][:8]))
        workspace.transition(permit, "SAFE", result["generation"])
    except BaseException:
        if workspace.inspect().get("operation_id") == permit.operation_id:
            # Invalid arguments need not poison an otherwise intact published version.
            from .verification import verify_workspace
            try:
                intact = verify_workspace(root)["ok"]
            except (ValueError, OSError, sqlite3.Error):
                intact = False
            if not (supplied and intact):
                workspace.transition(permit, "SAFE" if intact else "RECOVERY_REQUIRED")
        raise
    finally:
        state = workspace.inspect()
        if state.get("operation_id") == permit.operation_id and state["fence"] == permit.fence:
            workspace.writer(permit, release=True)
        CURRENT.reset(token)
