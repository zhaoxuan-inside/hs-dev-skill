"""Contained paths, atomic JSON, short process transactions and source inventories."""
import contextlib
import datetime
import hashlib
import json
import os
import stat
from pathlib import Path
import uuid

BASE = "hs-dev"
PROJECT = BASE + "/project"
DELIVERIES = BASE + "/deliveries"
EXECUTION = BASE + "/execution"
IGNORED = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", ".zcode"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def uid(prefix=""):
    return prefix + uuid.uuid4().hex[:16]


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def path(root, relative):
    root = Path(root).resolve()
    if not isinstance(relative, str) or not relative:
        raise ValueError("Expected a contained relative POSIX path")
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or "\\" in relative:
        raise ValueError("Expected a contained relative POSIX path")
    p = root / rel
    for part in [p, *p.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("Symlinks are outside the managed boundary")
    p.resolve().relative_to(root)
    return p


def write(file, value):
    file = Path(file)
    file.parent.mkdir(parents=True, exist_ok=True)
    payload = value if isinstance(value, bytes) else value.encode() if isinstance(value, str) else (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
    tmp = file.with_name(".write-" + uid())
    try:
        with tmp.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, file)
    finally:
        tmp.unlink(missing_ok=True)


def read(file, default=None):
    return json.loads(Path(file).read_text()) if Path(file).is_file() else default


def hash_file(file):
    file = Path(file)
    return digest(file.read_bytes()) if file.is_file() else None


def inventory(root):
    root = Path(root).resolve()
    result = {}
    for current, dirs, files in os.walk(root, followlinks=False):
        parent = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and not (parent / d).is_symlink()
                         and (parent / d).relative_to(root).as_posix() != EXECUTION)
        for name in sorted(files):
            p = parent / name
            if p.is_symlink() or not stat.S_ISREG(p.stat().st_mode) or name.startswith(".write-"):
                continue
            rel = p.relative_to(root).as_posix()
            if len(result) >= 50000 or p.stat().st_size > 32_000_000:
                raise ValueError("Source inventory exceeds supported bound; partition the project")
            result[rel] = hash_file(p)
    return result


@contextlib.contextmanager
def transaction(root):
    """The process lock never represents permission to edit source files."""
    try:
        import fcntl
    except ImportError:
        raise ValueError("0.0.2 execution coordination requires POSIX flock") from None
    file = path(root, EXECUTION + "/control.lock")
    if not file.parent.is_dir():
        raise ValueError("Project is not initialized")
    with file.open("a+b") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Another control transaction is running; retry without stealing its lock") from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def contained(relative, scope):
    return relative == scope or relative.startswith(scope.rstrip("/") + "/")
