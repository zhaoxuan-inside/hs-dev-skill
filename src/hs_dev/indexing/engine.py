"""Exact, tag, FTS5 and relationship search. Published indices are derived artifacts."""

import ast
import hashlib
import json
import os
import re
import sqlite3
from functools import wraps
from pathlib import Path
from ..config import resolve
from ..storage import CONTROL, atomic, identifier, local, managed_files, now, read_json, sha, write_json, workspace_lock
from .cache import ByteLRU

FILE_INDEX = "hs_dev_docs/file_index.jsonl"
PUBLICATION = f"{CONTROL}/state/publication.json"
DATABASE = f"{CONTROL}/cache/search.sqlite"
TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".sql", ".txt", ".html", ".js", ".ts", ".tsx", ".go", ".java", ".env"}
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u3400-\u9fff]+")
METADATA = re.compile(r"^<!--\s*hs:\s*(\{[^\n]*\})\s*-->\s*$", re.MULTILINE)
OBJECT_IDS = re.compile(r"\b(?:REQ|FEAT|RULE|SCN|MOD|API|DATA|METHOD|TASK|TEST|EVIDENCE)-[A-Za-z0-9_-]+\b")
METADATA_FIELDS = {"id", "activity", "stage", "tags", "status", "relations", "module", "kind"}
SOURCE_STATES = {"current", "draft", "superseded"}
MAX_SOURCE_FILES = 50_000
SOURCE_READ_BLOCK_BYTES = 65_536
CONTENT_CHUNK_LINES = 80
MAX_QUERY_CHARACTERS = 1024
MAX_QUERY_TERMS = 16
MAX_PHRASE_TERMS = 32
DEFAULT_RESULT_LIMIT = 10
PARSER_REVISION = 2
OBJECT_GRAPH = "hs_dev_docs/_00_foundation/object_graph.json"


def consistent_read(function):
    @wraps(function)
    def guarded(self, *args, **kwargs):
        lock = read_json(self.root / CONTROL / "mutation.lock")
        if lock and lock.get("pid") == os.getpid():
            return function(self, *args, **kwargs)
        with workspace_lock(self.root):
            result = function(self, *args, **kwargs)
            if not self.verify()["ok"]:
                self.cache.clear()
                raise ValueError("Source changed during query; no result published")
            return result
    return guarded


def tokens(text):
    result = []
    for word in TOKEN_PATTERN.findall(text.casefold()):
        if re.fullmatch(r"[\u3400-\u9fff]+", word):
            result.extend(word)
        else:
            result.append(word)
    return result


def grams(text):
    return [word[i:i + 2] for word in re.findall(r"[\u3400-\u9fff]+", text) for i in range(len(word) - 1)]


def fingerprint(path):
    digest = hashlib.sha256()
    before = path.stat()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(SOURCE_READ_BLOCK_BYTES), b""):
            digest.update(block)
    after = path.stat()
    if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
        raise ValueError("Source changed during inspection: " + str(path))
    return digest.hexdigest()


def stamp(path):
    stat = path.stat()
    return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)


def inventory(root, verified=None, maximum=MAX_SOURCE_FILES):
    result = {}
    for path in managed_files(root):
        if len(result) >= maximum:
            raise ValueError("Workspace file count exceeds bounded index; partition the workspace")
        key = str(path.relative_to(root))
        current = stamp(path)
        cached = verified.get(key) if verified is not None else None
        digest = cached[1] if cached and cached[0] == current else fingerprint(path)
        if verified is not None:
            verified[key] = (current, digest)
        result[key] = digest
    if verified is not None:
        for key in list(verified):
            if key not in result:
                del verified[key]
    return result


def chunks(path, text):
    """Bounded heading sections; locations are verified against the source digest."""
    lines = text.splitlines()
    starts = [0] + [i for i, line in enumerate(lines) if i and re.match(r"^#{1,6}\s", line)]
    for ordinal, start in enumerate(starts):
        stop = starts[ordinal + 1] if ordinal + 1 < len(starts) else len(lines)
        # Bound each chunk even when the author has not provided headings.
        for offset in range(start, max(start + 1, stop), CONTENT_CHUNK_LINES):
            end = min(offset + CONTENT_CHUNK_LINES, stop)
            yield {"key": f"{path}#{offset + 1}", "title": lines[start].lstrip("# ") if lines else path,
                   "start": offset + 1, "end": end, "body": "\n".join(lines[offset:end])}


class Index:
    def __init__(self, root, config=None):
        self.root = Path(root).resolve()
        self.config = config or resolve(root)["values"]["index"]
        self.cache = ByteLRU(self.config["lru_bytes"])
        self.generation = None
        self.db = None
        self.verified_sources = {}
        self.verified_indices = {}
        self.verified_database = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def connect(self):
        if self.db is None:
            path = self.root / DATABASE
            path.parent.mkdir(parents=True, exist_ok=True)
            self.db = sqlite3.connect(path)
            self.db.row_factory = sqlite3.Row
            self.db.execute(f"PRAGMA cache_size=-{self.config['sqlite_cache_kib']}")
            self.db.execute("PRAGMA mmap_size=0")
            self.db.execute("PRAGMA temp_store=FILE")
            self.db.execute("PRAGMA busy_timeout=3000")
            self.db.executescript('''
                CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS items(
                    key TEXT PRIMARY KEY, path TEXT NOT NULL, title TEXT NOT NULL,
                    start INTEGER, end INTEGER, digest TEXT NOT NULL, properties TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS items_path ON items(path);
                CREATE TABLE IF NOT EXISTS attributes(name TEXT, value TEXT, item TEXT,
                    PRIMARY KEY(name,value,item));
                CREATE INDEX IF NOT EXISTS attributes_item ON attributes(item);
                CREATE TABLE IF NOT EXISTS relations(source TEXT, target TEXT, kind TEXT, path TEXT,
                    PRIMARY KEY(source,target,kind,path));
                CREATE INDEX IF NOT EXISTS relations_target ON relations(target,kind);
                CREATE VIRTUAL TABLE IF NOT EXISTS text_fts USING fts5(
                    key UNINDEXED, title, body, ngrams, prefix='2 3', tokenize='unicode61');
            ''')
        return self.db

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
        self.cache.clear()

    def logical_digest(self):
        digest = hashlib.sha256()
        for table, order in (("items", "key"), ("attributes", "name,value,item"),
                             ("relations", "source,target,kind,path"), ("text_fts", "key")):
            for row in self.connect().execute(f"SELECT * FROM {table} ORDER BY {order}"):
                digest.update(json.dumps(list(row), ensure_ascii=False).encode())
        return digest.hexdigest()

    def normalize_tags(self, values):
        if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
            raise ValueError("tags must be an array of strings")
        aliases = read_json(self.root / "hs_dev_docs/_00_foundation/tag_aliases.json", {})
        if not isinstance(aliases, dict) or any(not isinstance(v, str) for v in aliases.values()):
            raise ValueError("Tag aliases must map strings to canonical strings")
        result = []
        for value in values:
            value = value.strip().casefold()
            seen = set()
            while value in aliases:
                if value in seen:
                    raise ValueError("Cyclic tag aliases")
                seen.add(value)
                value = aliases[value].strip().casefold()
            if value and value not in result:
                result.append(value)
        return result

    def publish(self):
        stamp, generation = now(), identifier()
        source = inventory(self.root, self.verified_sources)
        previous = read_json(self.root / PUBLICATION, {})
        db = self.connect()
        stored = db.execute("SELECT value FROM meta WHERE key='generation'").fetchone()
        intact = bool(stored and stored[0] == previous.get("generation") and previous.get("parser_revision") == PARSER_REVISION
                      and self.logical_digest() == previous.get("database_digest"))
        changed = {p for p in set(source) | set(previous.get("sources", {})) if source.get(p) != previous.get("sources", {}).get(p)} if intact else set(source)
        if "hs_dev_docs/_00_foundation/tag_aliases.json" in changed:
            changed.update(source)
        db.execute("BEGIN")
        groups = {"hs_dev_docs": []}
        try:
            if not intact:
                for table in ("items", "attributes", "relations", "text_fts"):
                    db.execute(f"DELETE FROM {table}")
            else:
                for relative in changed:
                    db.execute("DELETE FROM text_fts WHERE key IN(SELECT key FROM items WHERE path=?)", (relative,))
                    db.execute("DELETE FROM attributes WHERE item IN(SELECT key FROM items WHERE path=?)", (relative,))
                    db.execute("DELETE FROM items WHERE path=?", (relative,))
                    db.execute("DELETE FROM relations WHERE path=?", (relative,))
            for relative, digest in source.items():
                path = self.root / relative
                if relative.startswith("hs_dev_docs/"):
                    groups.setdefault(str(path.parent.relative_to(self.root)), [])
                if path.suffix not in TEXT_SUFFIXES or path.stat().st_size > self.config["max_file_bytes"]:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                meta_match = METADATA.search(text)
                meta = json.loads(meta_match.group(1)) if meta_match else {}
                graph = None
                if relative == OBJECT_GRAPH:
                    from ..verification import coverage
                    graph = json.loads(text)
                    result = coverage(graph["objects"], graph["relations"])
                    if not result["ok"]:
                        raise ValueError("Invalid object registry: " + "; ".join(result["errors"]))
                    meta = {"kind": "registry", "tags": ["traceability"], "relations": graph["relations"]}
                if not isinstance(meta, dict):
                    raise ValueError("Content metadata must be an object")
                if set(meta) - METADATA_FIELDS or meta.get("status", "current") not in SOURCE_STATES:
                    raise ValueError("Unknown metadata field or source status: " + relative)
                properties = {"kind": path.suffix.lstrip("."), "status": "current", **{key: value for key, value in meta.items() if key != "relations"}}
                properties["tags"] = self.normalize_tags(properties.get("tags", []))
                archived = "history" in Path(relative).parts
                if archived:
                    properties["status"] = "archived"
                entries = []
                for chunk in chunks(relative, text):
                    entry = {k: v for k, v in chunk.items() if k != "body"}
                    source_time = previous.get("timestamps", {}).get(relative, stamp) if previous.get("sources", {}).get(relative) == digest else stamp
                    entry.update(source_digest=digest, properties=properties, content_updated_at=source_time)
                    entries.append(entry)
                    if relative not in changed:
                        continue
                    db.execute("INSERT INTO items VALUES(?,?,?,?,?,?,?)", (chunk["key"], relative, chunk["title"],
                               chunk["start"], chunk["end"], digest, json.dumps(properties, ensure_ascii=False)))
                    db.execute("INSERT INTO text_fts VALUES(?,?,?,?)", (chunk["key"], " ".join(tokens(chunk["title"])), " ".join(tokens(chunk["body"])), " ".join(grams(chunk["body"]))))
                    for name, value in properties.items():
                        if isinstance(value, dict) or name == "relations":
                            continue
                        for field in value if isinstance(value, list) else [value]:
                            db.execute("INSERT OR IGNORE INTO attributes VALUES(?,?,?)", (name, str(field).casefold(), chunk["key"]))
                if relative.startswith("hs_dev_docs/"):
                    groups.setdefault(str(path.parent.relative_to(self.root)), []).extend(entries)
                if graph is not None and relative in changed:
                    for obj in graph["objects"]:
                        key = relative + "#object:" + obj["id"]
                        props = {"kind": "object", "object_kind": obj["kind"], "id": obj["id"], "status": "current",
                                 "target_path": obj.get("path"), "symbol": obj.get("symbol"), "tags": ["traceability"]}
                        title = obj.get("title", obj["id"])
                        db.execute("INSERT INTO items VALUES(?,?,?,?,?,?,?)", (key, relative, title, None, None, digest, json.dumps(props, ensure_ascii=False)))
                        db.execute("INSERT INTO text_fts VALUES(?,?,?,?)", (key, " ".join(tokens(title)), " ".join(tokens(obj["id"])), " ".join(grams(title))))
                        for name, value in props.items():
                            for field in value if isinstance(value, list) else [value]:
                                if field is not None:
                                    db.execute("INSERT INTO attributes VALUES(?,?,?)", (name, str(field).casefold(), key))
                if path.suffix == ".py" and not archived and relative in changed:
                    tree = ast.parse(text, filename=relative)
                    for node in ast.walk(tree):
                        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            continue
                        symbol = relative + ":" + node.name + ":" + str(node.lineno)
                        props = {"kind": "symbol", "name": node.name, "module": relative, "symbol": relative + ":" + node.name, "status": "current"}
                        db.execute("INSERT INTO items VALUES(?,?,?,?,?,?,?)", (symbol, relative, node.name,
                                   node.lineno, node.end_lineno, digest, json.dumps(props)))
                        description = ast.get_docstring(node) or ""
                        db.execute("INSERT INTO text_fts VALUES(?,?,?,?)", (symbol, " ".join(tokens(node.name)), " ".join(tokens(description)), " ".join(grams(description))))
                        for name, value in props.items():
                            db.execute("INSERT INTO attributes VALUES(?,?,?)", (name, value.casefold(), symbol))
                        if not isinstance(node, ast.ClassDef):
                            for call in ast.walk(node):
                                if isinstance(call, ast.Call):
                                    db.execute("INSERT OR IGNORE INTO relations VALUES(?,?,?,?)", (relative + ":" + node.name,
                                               ast.unparse(call.func), "calls_unresolved", relative))
                for relation in meta.get("relations", []):
                    if not isinstance(relation, dict) or not all(relation.get(k) for k in ("source", "target", "kind")):
                        raise ValueError("Relations require source, target and kind")
                    if relative in changed:
                        db.execute("INSERT OR IGNORE INTO relations VALUES(?,?,?,?)", (relation["source"], relation["target"], relation["kind"], relative))
            # Empty stage/activity directories also receive a valid empty index.
            for directory in (self.root / "hs_dev_docs").rglob("*"):
                if directory.is_dir() and not directory.is_symlink() and "history" not in directory.relative_to(self.root).parts:
                    groups.setdefault(str(directory.relative_to(self.root)), [])
            documents = {}
            for directory, entries in groups.items():
                relative = directory + "/content_index.jsonl"
                data = "\n".join(json.dumps(row, ensure_ascii=False) for row in [
                    {"schema_version": 1, "generation": generation, "scope": directory, "recursive": False,
                     "complete": True, "indexed_at": stamp}, *entries]) + "\n"
                atomic(local(self.root, relative), data)
                documents[relative] = sha(data.encode())
            data = "\n".join(json.dumps(row, ensure_ascii=False) for row in [
                {"schema_version": 1, "generation": generation, "indexed_at": stamp, "complete": True},
                *({"path": p, "source_digest": d,
                   "content_index": str(Path(p).parent / "content_index.jsonl") if p.startswith("hs_dev_docs/") and Path(p).suffix in TEXT_SUFFIXES else None,
                   "locator": "symbol" if p.endswith(".py") else "content" if p.startswith("hs_dev_docs/") and Path(p).suffix in TEXT_SUFFIXES else "exact",
                   "content_updated_at":
                   previous.get("timestamps", {}).get(p, stamp) if previous.get("sources", {}).get(p) == d else stamp}
                  for p, d in sorted(source.items()))]) + "\n"
            atomic(self.root / FILE_INDEX, data)
            documents[FILE_INDEX] = sha(data.encode())
            if inventory(self.root, self.verified_sources) != source:
                raise ValueError("Workspace changed while publishing; index not valid")
            db.execute("INSERT OR REPLACE INTO meta VALUES('generation',?)", (generation,))
            db.commit()
            timestamps = {p: previous.get("timestamps", {}).get(p, stamp) if previous.get("sources", {}).get(p) == d else stamp for p, d in source.items()}
            write_json(self.root / PUBLICATION, {"schema_version": 1, "generation": generation, "published_at": stamp,
                       "parser_revision": PARSER_REVISION, "sources": source, "timestamps": timestamps, "indices": documents, "database_digest": self.logical_digest()})
            self.generation = generation
            self.cache.clear()
            return {"generation": generation, "files": len(source), "content_indices": len(groups), "changed_files": len(changed)}
        except Exception:
            db.rollback()
            raise

    def verify(self):
        published = read_json(self.root / PUBLICATION)
        if not published:
            return {"ok": False, "errors": ["No committed publication; initialize explicitly"]}
        errors = []
        if published.get("parser_revision") != PARSER_REVISION:
            errors.append("Parser revision drift")
        current = inventory(self.root, self.verified_sources)
        changed = sorted(p for p in set(current) | set(published["sources"]) if current.get(p) != published["sources"].get(p))
        errors.extend("Source drift: " + p for p in changed)
        for path, digest in published["indices"].items():
            file = local(self.root, path)
            cached = self.verified_indices.get(path)
            if file.is_file():
                current_stamp = stamp(file)
                actual = cached[1] if cached and cached[0] == current_stamp else fingerprint(file)
                self.verified_indices[path] = (current_stamp, actual)
            else:
                actual = None
            if actual != digest:
                errors.append("Index drift: " + path)
        generation = self.connect().execute("SELECT value FROM meta WHERE key='generation'").fetchone()
        database_stamp = stamp(self.root / DATABASE)
        if self.verified_database and self.verified_database[0] == database_stamp:
            actual_database = self.verified_database[1]
        else:
            actual_database = self.logical_digest()
            self.verified_database = (database_stamp, actual_database)
        if not generation or generation[0] != published["generation"] or actual_database != published["database_digest"]:
            errors.append("SQLite generation/content drift")
        if self.generation != published["generation"]:
            self.cache.clear()
            self.generation = published["generation"]
        return {"ok": not errors, "errors": errors, "generation": published["generation"]}

    def ensure(self):
        status = self.verify()
        # Missing/damaged derived content can be rebuilt only when the source baseline is intact.
        if not status["ok"] and not any(e.startswith("Source drift") or e.startswith("No committed") for e in status["errors"]):
            owner = read_json(self.root / CONTROL / "mutation.lock")
            if owner and owner.get("pid") == os.getpid():
                self.publish()
            else:
                with workspace_lock(self.root):
                    self.publish()
            status = self.verify()
        if not status["ok"]:
            self.cache.clear()
            raise ValueError("Inconsistent workspace; continue repair or rollback: " + "; ".join(status["errors"][:8]))

    @consistent_read
    def search(self, query="", filters=None, limit=DEFAULT_RESULT_LIMIT, match="terms"):
        if not 1 <= limit <= self.config["max_results"]:
            raise ValueError("Search result limit outside configured bound")
        if len(query) > MAX_QUERY_CHARACTERS or match not in {"terms", "phrase", "prefix"}:
            raise ValueError("Invalid search length or matching mode")
        self.ensure()
        filters = {"status": "current", **(filters or {})}
        cache_key = json.dumps([self.generation, query, filters, limit, match], sort_keys=True)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        parameters, conditions = [], []
        for name, values in filters.items():
            if name in {"any", "exclude"}:
                if not isinstance(values, dict):
                    raise ValueError("any/exclude must map attribute names to arrays")
                for field, options in values.items():
                    if not isinstance(options, list) or not options:
                        raise ValueError("Tag alternatives cannot be empty")
                    if field == "tags":
                        options = self.normalize_tags(options)
                    placeholders = ",".join("?" for _ in options)
                    existence = "NOT EXISTS" if name == "exclude" else "EXISTS"
                    conditions.append(f"{existence}(SELECT 1 FROM attributes a WHERE a.item=i.key AND a.name=? AND a.value IN ({placeholders}))")
                    parameters.extend([field, *(str(v).casefold() for v in options)])
                continue
            if name == "tags":
                values = self.normalize_tags(values if isinstance(values, list) else [values])
            for value in values if isinstance(values, list) else [values]:
                conditions.append("EXISTS(SELECT 1 FROM attributes a WHERE a.item=i.key AND a.name=? AND a.value=?)")
                parameters.extend([name, str(value).casefold()])
        if query:
            terms = tokens(query)[:MAX_PHRASE_TERMS] if match == "phrase" else list(dict.fromkeys(tokens(query)))[:MAX_QUERY_TERMS]
            if not terms:
                return []
            if match == "phrase":
                expression = '{title body} : "' + " ".join(terms) + '"'
            else:
                expression = " AND ".join('"' + t.replace('"', '""') + '"' + ("*" if match == "prefix" else "") for t in terms)
            sql = "SELECT i.*,bm25(text_fts,0,5,1,2) AS score FROM text_fts JOIN items i ON i.key=text_fts.key WHERE text_fts MATCH ?"
            parameters.insert(0, expression)
        else:
            sql = "SELECT i.*,0 AS score FROM items i WHERE 1=1"
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        sql += " ORDER BY score,i.key LIMIT ?"
        rows = [dict(row) for row in self.connect().execute(sql, [*parameters, limit])]
        for row in rows:
            row["properties"] = json.loads(row["properties"])
            row["generation"] = self.generation
        self.cache.put(cache_key, rows)
        return rows

    @consistent_read
    def relationships(self, object_id):
        self.ensure()
        return [dict(r) for r in self.connect().execute(
            "SELECT source,target,kind,path FROM relations WHERE source=? OR target=? ORDER BY source,target LIMIT ?",
            (object_id, object_id, self.config["max_results"]))]

    @consistent_read
    def exact(self, path, start=1, end=None):
        self.ensure()
        file = local(self.root, path)
        published = read_json(self.root / PUBLICATION)
        if path in published["indices"]:
            source = published["indices"][path]
            if start < 1 or (end is not None and end < start):
                raise ValueError("Invalid index range")
            stop = min(end or start + CONTENT_CHUNK_LINES - 1, start + CONTENT_CHUNK_LINES - 1)
            selected = []
            with file.open(encoding="utf-8") as stream:
                for number, line in enumerate(stream, 1):
                    if number > stop:
                        break
                    if number >= start:
                        selected.append(line)
            if fingerprint(file) != source:
                raise ValueError("Index changed during reading")
            return {"path": path, "generation": self.generation, "source_digest": source,
                    "text": "".join(selected), "start": start, "end": stop, "next_start": stop + 1}
        if file.stat().st_size > self.config["max_file_bytes"]:
            raise ValueError("Read requires a smaller source file")
        data = file.read_bytes()
        source = published["sources"].get(path)
        if sha(data) != source:
            raise ValueError("Source changed during read")
        lines = data.decode("utf-8").splitlines()
        if start < 1 or (end is not None and end < start):
            raise ValueError("Invalid content range")
        return {"path": path, "generation": self.generation, "source_digest": source, "text": "\n".join(lines[start - 1:end])}
