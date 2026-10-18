"""Resolve stable semantic unit identities to their published content revision."""
import re
from pathlib import Path

from ..storage import local, sha
from .engine import Index
from .semantic import file_id, units as parse_units

_LINE_ID = re.compile(r"file:(.+)#lines:(\d+)-(\d+)")


def resolve_units(root, unit_ids):
    """Resolve a bounded set of file, line, section and symbol references."""
    ids = list(dict.fromkeys(unit_ids))
    if len(ids) > 512 or any(not isinstance(key, str) or len(key) > 4096 for key in ids):
        raise ValueError("Invalid semantic unit reference set")
    result = {}
    paths = {}
    indexed = [key for key in ids if not key.startswith("file:") or _LINE_ID.fullmatch(key)]
    if indexed:
        with Index(root) as index:
            db = index.connect()
            for key in indexed:
                row = db.execute("SELECT path FROM items WHERE key=?", (key,)).fetchone()
                if row:
                    paths[key] = row["path"]
                else:
                    line = _LINE_ID.fullmatch(key)
                    if line:
                        paths[key] = line.group(1)
        parsed = {}
        for key, path in paths.items():
            source = local(root, path).read_bytes()
            digest = sha(source)
            text = source.decode("utf-8", errors="replace")
            line = _LINE_ID.fullmatch(key)
            if line:
                start, end = int(line.group(2)), int(line.group(3))
                lines = text.splitlines()
                if end < start or start < 1 or end > len(lines):
                    continue
                selected = "\n".join(lines[start - 1:end])
                result[key] = {"unit_id": key, "unit_revision": sha(selected.encode()),
                               "path": path, "source_digest": digest}
                continue
            if path not in parsed:
                parsed[path] = {item["key"]: item for item in parse_units(path, text)}
            item = parsed[path].get(key)
            if item:
                result[key] = {"unit_id": key, "unit_revision": item["properties"]["unit_revision"],
                               "path": path, "source_digest": digest}
    for key in ids:
        if key.startswith("file:") and key not in result:
            result[key] = _raw_file(root, key)
    missing = [key for key in ids if key not in result]
    if missing:
        raise ValueError("Unknown semantic unit: " + ", ".join(missing[:8]))
    return result


def _raw_file(root, unit_id):
    path = unit_id[5:]
    file = local(root, path)
    if not file.is_file():
        raise ValueError("Unknown semantic unit: " + unit_id)
    digest = sha(file.read_bytes())
    return {"unit_id": file_id(str(file.relative_to(Path(root).resolve()))),
            "unit_revision": digest, "path": str(file.relative_to(Path(root).resolve())),
            "source_digest": digest}
