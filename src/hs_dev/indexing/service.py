"""Sequential local Unix-socket service with a strict address-space ceiling."""

from ..contracts import TaskStatus

import json
import os
import socket
from pathlib import Path
from ..config import resolve
from ..storage import CONTROL, now, read_json, sha
from .engine import Index, fingerprint, tokens

MAX_REQUEST = 65_536
MAX_RESPONSE = 2_000_000
SOCKET_TIMEOUT = 5
SOCKET_BACKLOG = 4
SOCKET_READ_BYTES = 4096
SOCKET_PRIVATE_MODE = 0o600


class Resident:
    """Only small active task files are pinned, never global history or evidence logs."""
    def __init__(self, root, maximum):
        self.root = Path(root)
        self.maximum = maximum
        self.items = {}
        self.used = 0

    def refresh(self):
        selected = {}
        used = 0
        for task_file in sorted((self.root / CONTROL / "task").glob("*/task.json"), reverse=True):
            task = read_json(task_file)
            if task.get("status") != TaskStatus.ACTIVE:
                continue
            directory = task_file.parent
            candidates = [directory / "context/current.md", directory / "handoff.md"]
            if task.get("current_activity") in task["activities"]:
                candidates.append(directory / "activities" / task["current_activity"] / "checklist.md")
            for path in candidates:
                if not path.is_file() or path.stat().st_size > MAX_REQUEST:
                    continue
                size = path.stat().st_size + len(str(path).encode()) + 512
                if used + size > self.maximum:
                    continue
                relative = str(path.relative_to(self.root))
                digest = fingerprint(path)
                previous = self.items.get(relative)
                if previous and previous["source_digest"] == digest:
                    text = previous["text"]
                else:
                    data = path.read_bytes()
                    if sha(data) != digest:
                        raise ValueError("Active task changed during reading; retry")
                    text = data.decode("utf-8")
                selected[relative] = {"path": relative, "source_digest": digest, "text": text, "task_id": directory.name}
                used += size
        self.items, self.used = selected, used

    def search(self, query, limit=10, task_id=None):
        self.refresh()
        terms = tokens(query)
        return [dict(value, source="resident") for value in self.items.values()
                if (not task_id or value["task_id"] == task_id)
                and all(term in value["text"].casefold() for term in terms)][:limit]


def dispatch(index, resident, request):
    if resolve(index.root)["values"]["index"] != index.config:
        raise ValueError("Effective task/project index budgets changed; restart the service before querying")
    action = request.get("action")
    if action == "search":
        rows = index.search(request.get("query", ""), request.get("filters"), request.get("limit", 10), request.get("match", "terms"))
        hot = [] if request.get("filters") else resident.search(request.get("query", ""), request.get("limit", 10), request.get("task_id"))
        return {"ok": True, "stable": rows, "active": hot, "generation": index.generation}
    if action == "read":
        return {"ok": True, **index.exact(request["path"], request.get("start", 1), request.get("end"))}
    if action == "status":
        resident.refresh()
        return {"ok": True, "lru_bytes": index.cache.used, "resident_bytes": resident.used, "created_at": now()}
    raise ValueError("Unknown read-only service action")


def serve(root, socket_path=None):
    settings = resolve(root)["values"]["index"]
    try:
        import resource
    except ImportError:
        raise ValueError("Strict 200 MB service currently requires POSIX resource limits; use bounded CLI queries on this host") from None
    limit = settings["memory_bytes"]
    _, existing_hard = resource.getrlimit(resource.RLIMIT_AS)
    hard = min(limit, existing_hard) if existing_hard != resource.RLIM_INFINITY else limit
    resource.setrlimit(resource.RLIMIT_AS, (hard, hard))
    path = Path(socket_path) if socket_path else Path(root) / CONTROL / "cache/index.sock"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError("Socket already exists; inspect running service before removal")
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(path))
    os.chmod(path, SOCKET_PRIVATE_MODE)
    listener.listen(SOCKET_BACKLOG)
    resident = Resident(root, settings["resident_bytes"])
    try:
        with Index(root, settings) as index:
            while True:
                connection, _ = listener.accept()
                with connection:
                    connection.settimeout(SOCKET_TIMEOUT)
                    data = bytearray()
                    try:
                        while b"\n" not in data:
                            block = connection.recv(min(SOCKET_READ_BYTES, MAX_REQUEST + 1 - len(data)))
                            if not block:
                                raise ValueError("Incomplete request")
                            data.extend(block)
                            if len(data) > MAX_REQUEST:
                                raise ValueError("Request too large")
                        result = dispatch(index, resident, json.loads(data.split(b"\n", 1)[0]))
                        payload = json.dumps(result, ensure_ascii=False).encode()
                        if len(payload) > MAX_RESPONSE:
                            raise ValueError("Response too large; narrow the query")
                    except (ValueError, KeyError, OSError, MemoryError) as error:
                        index.cache.clear()
                        payload = json.dumps({"ok": False, "error": str(error)}).encode()
                    connection.sendall(payload + b"\n")
    finally:
        listener.close()
        path.unlink(missing_ok=True)


def request(path, payload):
    data = json.dumps(payload).encode() + b"\n"
    if len(data) > MAX_REQUEST:
        raise ValueError("Request too large")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(SOCKET_TIMEOUT)
        client.connect(str(path))
        client.sendall(data)
        received = bytearray()
        while b"\n" not in received:
            block = client.recv(SOCKET_READ_BYTES)
            if not block:
                raise ValueError("Incomplete service response")
            received.extend(block)
            if len(received) > MAX_RESPONSE:
                raise ValueError("Response too large")
    return json.loads(received)
