"""Session-local, scope-aware document reads with metadata and content checks."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def stamp(path):
    stat = path.stat()
    return [stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]


def snapshot(path):
    before = stamp(path)
    data = path.read_bytes()
    if stamp(path) != before:
        raise ValueError("file changed during reading; retry this file")
    return data, hashlib.sha256(data).hexdigest(), before


def read_state(path):
    if not path.exists():
        return {"schema_version": 1, "entries": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(state, dict) or state.get("schema_version") != 1
            or not isinstance(state.get("entries"), dict)):
        raise ValueError("invalid read cache; use a new session state file")
    for entry in state["entries"].values():
        if (not isinstance(entry, dict) or not isinstance(entry.get("stamp"), list)
                or len(entry["stamp"]) != 5 or not isinstance(entry.get("sha256"), str)
                or len(entry["sha256"]) != 64):
            raise ValueError("invalid read cache entry; use a new session state file")
    return state


def inspect(state, path, start=1, end=None, verify=False, context_missing=False):
    key = json.dumps([str(path), start, end], ensure_ascii=False)
    entry = state["entries"].get(key)
    current = stamp(path)
    if not path.is_file():
        raise ValueError("document is not a regular file")
    if entry is None:
        action = "READ"
    elif context_missing:
        action = "RESTORE_CONTEXT"
    elif verify or entry["stamp"] != current:
        _, digest, _ = snapshot(path)
        action = "REUSE" if digest == entry["sha256"] else "RELOAD"
    else:
        action = "REUSE"
    return {"action": action, "path": str(path), "start": start, "end": end}


def load(state, path, start=1, end=None):
    data, digest, metadata = snapshot(path)
    lines = data.decode("utf-8").splitlines(keepends=True)
    if start > len(lines) and (lines or start != 1):
        raise ValueError("start line is outside document")
    text = "".join(lines[start - 1:end])
    key = json.dumps([str(path), start, end], ensure_ascii=False)
    state["entries"][key] = {"sha256": digest, "stamp": metadata}
    return {"action": "LOADED", "path": str(path), "start": start, "end": end,
            "sha256": digest, "text": text}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "load"])
    parser.add_argument("--state", required=True, help="Private per-agent session JSON, preferably in tmp")
    parser.add_argument("--path", required=True)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int)
    parser.add_argument("--verify-content", action="store_true")
    parser.add_argument("--context-missing", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.start < 1 or (args.end is not None and args.end < args.start):
            raise ValueError("invalid line range")
        path = Path(args.path).expanduser().resolve(strict=True)
        state_path = Path(args.state).expanduser().resolve()
        if state_path == path:
            raise ValueError("state file must not overwrite source document")
        state = read_state(state_path)
        if args.command == "check":
            result = inspect(state, path, args.start, args.end,
                             args.verify_content, args.context_missing)
        else:
            result = load(state, path, args.start, args.end)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            temporary = state_path.with_name(state_path.name + ".tmp")
            temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            os.replace(str(temporary), str(state_path))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({"action": "ERROR", "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
