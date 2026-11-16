"""Explicit local knowledge index and content-bound evidence sources.

Only snapshots already collected by the caller are accepted; this module never
fetches network data. `usable` is mechanical freshness/provenance eligibility,
not a claim that a publisher, a user statement, or its contents are truthful.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
from functools import wraps
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
from urllib.parse import unquote, urlsplit
from uuid import uuid4

INDEX = "hs-dev/execution/index.sqlite"
MANIFEST = "hs-dev/execution/index-manifest.json"
SOURCES = "hs-dev/deliveries/sources.json"
EVIDENCE = "hs-dev/execution/evidence/"
PARSER_VERSION = 1
MAX_FILE_BYTES = 2_000_000
MAX_SOURCE_FILES = 50_000
MAX_REGISTRY_BYTES = 8_000_000
MAX_QUERY_BYTES = 4096
MAX_RESULT_BYTES = 65_536
TEXT_SUFFIXES = {".md", ".mdx", ".rst", ".txt", ".log", ".csv", ".tsv", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".html", ".xml", ".sql", ".graphql", ".proto", ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".kts", ".swift", ".dart", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".sh", ".rb", ".php", ".vue", ".svelte"}
CODE_SUFFIXES = TEXT_SUFFIXES - {".md", ".mdx", ".rst", ".txt", ".log", ".csv", ".tsv", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".html", ".xml"}
IGNORED_DIRS = {".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".cache", "dist", "build", "target", ".next", ".dart_tool", ".gradle", "coverage", "history", "draft", "superseded"}
SECRET_NAMES = {".env", "id_rsa", "id_ed25519", "id_ecdsa", "credentials", "credentials.json", "secrets.json", "secrets.yaml", "secrets.yml", ".netrc", ".npmrc", ".pypirc", "kubeconfig", "service-account.json"}
WORDS = re.compile(r"[A-Za-z0-9_]+|[\u3400-\u9fff]+")
KINDS = {"document", "code", "user", "private", "official", "primary", "execution"}
CLAIMS = {"fact", "requirement", "decision", "hypothesis"}
FIELDS = {"id", "kind", "path", "version", "observed_at", "valid_until", "scope", "claim_type", "url", "publisher", "quality_reason", "title", "notes"}
VAGUE_VERSIONS = {"latest", "unknown", "current", "tbd", "todo", "head", "main", "master", "stable", "nightly", "vnext", "n/a", "na", "none", "null", "最新", "未知", "待定", "当前", "当前版本", "最新版", "待核实", "不详"}


def _encode(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _root(root: str | Path) -> Path:
    value = Path(root).absolute()
    if not value.is_dir():
        raise ValueError("Project root must already exist")
    if value.is_symlink() or any(p.is_symlink() for p in value.parents):
        raise ValueError("Project root cannot use symlink ancestry")
    return value.resolve()


def _path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative.strip() or "\\" in relative or "\x00" in relative:
        raise ValueError("Expected a nonempty POSIX project-relative path")
    part = Path(relative)
    if part.is_absolute() or ".." in part.parts or relative.startswith("/"):
        raise ValueError("Absolute and parent-traversal paths are forbidden")
    value = root / part
    for ancestor in (value, *value.parents):
        if ancestor == root:
            break
        if ancestor.is_symlink():
            raise ValueError("Symlink content is forbidden")
    value.resolve().relative_to(root)
    return value


def _secret(path: Path) -> bool:
    name = path.name.casefold()
    return name in SECRET_NAMES or name.startswith(".env.") or path.suffix.casefold() in {".pem", ".key", ".p12", ".pfx", ".keystore"}


def _secret_content(raw: bytes) -> bool:
    return b"-----BEGIN " in raw and b"PRIVATE KEY-----" in raw


def _signature(stat) -> list:
    return [stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns]


def _stable_bytes(file: Path, capture: dict | None = None) -> bytes:
    before = file.stat()
    raw = file.read_bytes()
    after = file.stat()
    if _signature(before) != _signature(after):
        raise ValueError("Source changed during snapshot read")
    if capture is not None:
        capture["signature"] = _signature(after)
    return raw


def _readable(relative: str, *, evidence: bool = False) -> bool:
    path = Path(relative)
    if any(p.casefold() in IGNORED_DIRS for p in path.parts) or _secret(path):
        return False
    if relative == "hs-dev/execution" or relative.startswith("hs-dev/execution/"):
        return evidence and relative.startswith(EVIDENCE)
    return path.suffix.casefold() in TEXT_SUFFIXES


def _source_allowed(relative: str) -> bool:
    path = Path(relative)
    if _secret(path) or any(p.casefold() in IGNORED_DIRS for p in path.parts):
        return False
    return not relative.startswith("hs-dev/execution/") or relative.startswith(EVIDENCE)


def _atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".knowledge-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def _mutation(root: Path):
    try:
        import fcntl
    except ImportError:
        raise ValueError("Knowledge mutations require POSIX flock") from None
    lock = _path(root, "hs-dev/execution/knowledge.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with lock.open("a+b") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Knowledge mutation is busy; retry without replacing another writer's state") from None
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _serialized(function):
    @wraps(function)
    def guarded(root, *args, **kwargs):
        project = _root(root)
        with _mutation(project):
            return function(project, *args, **kwargs)
    return guarded


def _load(path: Path, default=None):
    if not path.exists():
        return default
    if path.stat().st_size > MAX_REGISTRY_BYTES:
        raise ValueError("Knowledge control file exceeds size limit")
    return json.loads(path.read_text(encoding="utf-8"))


def _metadata(text: str) -> dict:
    """Read the small documented frontmatter subset, without pretending to parse YAML."""
    result = {}
    if text.startswith("---\n") or text.startswith("---\r\n"):
        lines = text.splitlines()
        end = next((i for i, line in enumerate(lines[1:101], 1) if line.strip() == "---"), None)
        if end:
            for line in lines[1:end]:
                match = re.match(r"^(status|title|aliases):\s*(.+)$", line)
                if match:
                    key, value = match.groups()
                    if key == "aliases":
                        try:
                            value = json.loads(value)
                        except json.JSONDecodeError:
                            value = []
                        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                            value = []
                        result[key] = value[:16]
                    else:
                        result[key] = value.strip("\"'")[:256]
    return result


def _inventory(root: Path, known: dict | None = None, signatures: dict | None = None) -> tuple[dict, list]:
    files, skipped = {}, []
    known = known or {}
    for folder, directories, names in os.walk(root, followlinks=False):
        base = Path(folder)
        directories[:] = sorted(d for d in directories if d.casefold() not in IGNORED_DIRS and not (base / d).is_symlink() and (base / d).relative_to(root).as_posix() != "hs-dev/execution")
        for name in sorted(names):
            file = base / name
            relative = file.relative_to(root).as_posix()
            if file.is_symlink() or relative == SOURCES or not _readable(relative):
                continue
            if len(files) >= MAX_SOURCE_FILES:
                raise ValueError("Knowledge source count exceeds 50000; partition the project")
            stat = file.stat()
            if stat.st_size > MAX_FILE_BYTES:
                if len(skipped) < 20:
                    skipped.append({"path": relative, "reason": "oversized"})
                continue
            signature = _signature(stat)
            if relative in known.get("sources", {}) and signature == known.get("signatures", {}).get(relative):
                files[relative] = known["sources"][relative]
                if signatures is not None:
                    signatures[relative] = signature
                continue
            captured = {}
            raw = _stable_bytes(file, captured)
            if _secret_content(raw):
                continue
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                if len(skipped) < 20:
                    skipped.append({"path": relative, "reason": "non_utf8"})
                continue
            if _metadata(text).get("status", "current").casefold() in {"draft", "superseded", "history"}:
                continue
            files[relative] = _hash(raw)
            if signatures is not None:
                signatures[relative] = captured["signature"]
    return files, skipped


def _words(text: str) -> str:
    result = []
    for group in WORDS.findall(text.casefold()):
        result.extend(group if re.fullmatch(r"[\u3400-\u9fff]+", group) else [group])
    return " ".join(result)


def _pairs(text: str) -> str:
    return " ".join(g[i:i + 2] for g in re.findall(r"[\u3400-\u9fff]+", text) for i in range(len(g) - 1))


def _units(path: str, text: str) -> list[dict]:
    lines = text.splitlines()
    meta = _metadata(text)
    headings, fence = [], None
    if Path(path).suffix.casefold() in {".md", ".mdx"}:
        for number, line in enumerate(lines, 1):
            marker = re.match(r"^\s*(`{3,}|~{3,})", line)
            if marker:
                value = marker.group(1)
                if fence is None:
                    fence = value[0]
                elif fence == value[0]:
                    fence = None
                continue
            match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
            if match and fence is None:
                headings.append((number, match.group(1)))
    elif Path(path).suffix.casefold() == ".py":
        try:
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    headings.append((min([node.lineno] + [d.lineno for d in node.decorator_list]), node.name))
        except SyntaxError:
            pass  # Incomplete code remains searchable as source, never claimed executable.
    if not headings:
        headings = [(i + 1, meta.get("title", path) if i == 0 else f"{path} L{i + 1}") for i in range(0, len(lines), 80)] or [(1, meta.get("title", path))]
    elif headings[0][0] > 1:
        headings.insert(0, (1, meta.get("title", path)))
    headings.sort()
    result = []
    for i, (start, title) in enumerate(headings):
        end = headings[i + 1][0] - 1 if i + 1 < len(headings) else max(start, len(lines))
        body = "\n".join(lines[start - 1:end])
        preview = " ".join(line.strip() for line in body.splitlines() if line.strip() and not line.lstrip().startswith(("#", "```", "~~~")))[:160]
        result.append({"key": f"{path}#L{start}-{end}", "path": path, "heading": title,
                       "start": start, "end": end, "preview": preview, "body": body,
                       "aliases": " ".join(meta.get("aliases", []))})
    return result


def _relations(root: Path, path: str, text: str) -> list[tuple]:
    result = []
    for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", text):
        target = unquote(target.strip("<>"))
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        candidate = (root / path).parent / parsed.path
        try:
            resolved = candidate.resolve().relative_to(root).as_posix()
            file = _path(root, resolved)
        except (ValueError, OSError):
            continue
        if not _readable(resolved) or resolved == SOURCES:
            continue
        line = re.fullmatch(r"L(\d+)(?:-L?\d+)?", parsed.fragment)
        result.append((path, resolved, int(line.group(1)) if line else None, int(file.is_file())))
    return list(dict.fromkeys(result))


@_serialized
def reindex(root) -> dict:
    root = _root(root)
    target, manifest_file = _path(root, INDEX), _path(root, MANIFEST)
    signatures = {}
    inventory, skipped = _inventory(root, signatures=signatures)
    previous = _load(manifest_file, {})
    reusable = target.is_file() and previous.get("parser_version") == PARSER_VERSION and previous.get("database_digest") == _hash(target.read_bytes())
    if reusable and previous.get("sources") == inventory:
        return {"ok": True, "status": "unchanged", "generation": previous["generation"], "indexed_files": len(inventory), "changed_files": 0, "skipped": skipped}
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".index-", suffix=".sqlite", dir=target.parent)
    os.close(fd)
    try:
        if reusable:
            shutil.copyfile(target, temporary)
        db = sqlite3.connect(temporary)
        try:
            db.executescript("""PRAGMA journal_mode=DELETE; PRAGMA temp_store=FILE;
                CREATE TABLE IF NOT EXISTS units(key TEXT PRIMARY KEY,path TEXT,heading TEXT,start INTEGER,end INTEGER,preview TEXT,digest TEXT,kind TEXT);
                CREATE INDEX IF NOT EXISTS units_path ON units(path);
                CREATE TABLE IF NOT EXISTS links(source TEXT,target TEXT,line INTEGER,present INTEGER,UNIQUE(source,target,line));
                CREATE INDEX IF NOT EXISTS links_source ON links(source);
                CREATE INDEX IF NOT EXISTS links_target ON links(target);
                CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(key UNINDEXED,title,body,pairs,tokenize='unicode61');""")
            changed = {p for p in set(inventory) | set(previous.get("sources", {})) if inventory.get(p) != previous.get("sources", {}).get(p)} if reusable else set(inventory)
            for path in sorted(changed):
                db.execute("DELETE FROM search WHERE key IN (SELECT key FROM units WHERE path=?)", (path,))
                db.execute("DELETE FROM units WHERE path=?", (path,))
                db.execute("DELETE FROM links WHERE source=?", (path,))
                if path not in inventory:
                    continue
                raw = _stable_bytes(_path(root, path))
                if _hash(raw) != inventory[path]:
                    raise ValueError("Source changed while indexing: " + path)
                text = raw.decode("utf-8")
                for unit in _units(path, text):
                    kind = "code" if Path(path).suffix.casefold() in CODE_SUFFIXES else "document"
                    db.execute("INSERT INTO units VALUES(?,?,?,?,?,?,?,?)", (unit["key"], path, unit["heading"], unit["start"], unit["end"], unit["preview"], inventory[path], kind))
                    db.execute("INSERT INTO search VALUES(?,?,?,?)", (unit["key"], _words(unit["heading"] + " " + path + " " + unit["aliases"]), _words(unit["body"]), _pairs(unit["body"])))
                db.executemany("INSERT OR IGNORE INTO links VALUES(?,?,?,?)", _relations(root, path, text))
            # A linked target can appear/disappear without changing its referring document.
            for target_path, in db.execute("SELECT DISTINCT target FROM links").fetchall():
                present = int(target_path in inventory)
                db.execute("UPDATE links SET present=? WHERE target=?", (present, target_path))
            db.commit()
        finally:
            db.close()
        if _inventory(root)[0] != inventory:
            raise ValueError("Sources changed during indexing; previous index retained")
        generation = uuid4().hex
        digest = _hash(Path(temporary).read_bytes())
        os.replace(temporary, target)
        captured = {}
        if _hash(_stable_bytes(target, captured)) != digest:
            raise ValueError("Index changed while publishing; run explicit reindex")
        _atomic(manifest_file, _encode({"parser_version": PARSER_VERSION, "generation": generation,
                                       "sources": inventory, "signatures": signatures, "database_digest": digest,
                                       "database_signature": captured["signature"]}))
        return {"ok": True, "status": "indexed", "generation": generation, "indexed_files": len(inventory), "changed_files": len(changed), "skipped": skipped}
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _published(root: Path):
    target, manifest = _path(root, INDEX), _load(_path(root, MANIFEST))
    if not target.is_file() or not manifest:
        return None, {"ok": False, "status": "missing_index", "issues": ["Run explicit reindex before knowledge lookup"]}
    same_database = manifest.get("database_signature") == _signature(target.stat())
    if manifest.get("parser_version") != PARSER_VERSION or not same_database and manifest.get("database_digest") != _hash(_stable_bytes(target)):
        return None, {"ok": False, "status": "invalid_index", "issues": ["Index content/version changed; run explicit reindex"]}
    if manifest.get("sources") != _inventory(root, known=manifest)[0]:
        return None, {"ok": False, "status": "stale_index", "issues": ["Searchable sources changed; run explicit reindex"]}
    return manifest, None


def _bounded(value: dict, maximum: int, *, cards: bool = False) -> dict:
    value["usage"] = {"output_bytes": 0, "max_bytes": maximum}
    while True:
        previous = -1
        while previous != value["usage"]["output_bytes"]:
            previous = value["usage"]["output_bytes"]
            value["usage"]["output_bytes"] = len(_encode(value))
        if value["usage"]["output_bytes"] <= maximum:
            return value
        if cards and value.get("results"):
            value["results"].pop()
            value.update(status="truncated", has_more=True)
            continue
        raise ValueError("Response envelope exceeds byte budget; shorten query or raise max_bytes")


def locate(root, query, limit=5, max_bytes=12000) -> dict:
    root = _root(root)
    if not isinstance(query, str) or len(query.encode("utf-8")) > MAX_QUERY_BYTES:
        raise ValueError("Query must be a string of at most 4096 bytes")
    if type(limit) is not int or not 1 <= limit <= 30 or type(max_bytes) is not int or not 512 <= max_bytes <= MAX_RESULT_BYTES:
        raise ValueError("locate requires limit 1..30 and max_bytes 512..65536")
    manifest, problem = _published(root)
    if problem:
        return _bounded(problem, max_bytes)
    query = query.strip()
    results, seen = [], set()
    db = sqlite3.connect(_path(root, INDEX).as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        explicit_id = bool(re.match(r"^(source|unit|document|code|feature|behavior|decision|contract|delivery|symbol):", query))
        lookup = query[5:] if query.startswith("file:") else query
        exact_path, _, fragment = lookup.partition("#")
        path_query = query.startswith("file:") or "/" in lookup or "\\" in lookup or Path(exact_path).suffix.casefold() in TEXT_SUFFIXES
        if query.startswith("source:"):
            source = source_state(root, query[len("source:"):])
            if source["usable"]:
                ranked = [(r, "source-id") for r in db.execute("SELECT *,0 AS score FROM units WHERE path=? ORDER BY start LIMIT ?", (source["path"], limit+1))]
            else:
                return _bounded({"ok": False, "status": source["status"], "source": source}, max_bytes)
        elif explicit_id:
            ranked = []  # These identities belong to their registries; never guess from their words.
        elif path_query:
            _path(root, exact_path)
            rows = db.execute("SELECT *,0 AS score FROM units WHERE path=? ORDER BY start", (exact_path,)).fetchall()
            if fragment:
                line_range = re.fullmatch(r"L(\d+)(?:-L?(\d+))?", fragment)
                if line_range and rows:
                    start = int(line_range.group(1))
                    finish = int(line_range.group(2) or start)
                    if 1 <= start <= finish <= max(r["end"] for r in rows):
                        row = dict(rows[0])
                        row.update(start=start, end=finish, heading=f"{exact_path} L{start}-{finish}", preview="")
                        rows = [row]
                    else:
                        rows = []
                else:
                    rows = [r for r in rows if re.sub(r"\s+", "-", r["heading"].strip().casefold()) == fragment.casefold()]
            ranked = [(r, "exact-path") for r in rows[:limit + 1]]
        elif not query:
            rows = db.execute("SELECT *,0 AS score FROM units GROUP BY path ORDER BY CASE WHEN path LIKE 'hs-dev/project/%' THEN 0 WHEN path LIKE 'hs-dev/deliveries/%' THEN 1 ELSE 2 END,path LIMIT ?", (limit + 1,)).fetchall()
            ranked = [(r, "catalog") for r in rows]
        else:
            groups = WORDS.findall(query.casefold())
            strict, relaxed = [], []
            for group in groups:
                chinese = bool(re.fullmatch(r"[\u3400-\u9fff]+", group))
                phrase = '"' + (_words(group) if chinese else group) + '"'
                strict.append("{title body} : " + phrase)
                if chinese:
                    relaxed += ['pairs : "' + group[i:i + 2] + '"' for i in range(len(group) - 1)]
                    relaxed.append("title : " + phrase)
                else:
                    relaxed.append("{title body} : " + phrase)
            if len(strict) + len(relaxed) > 96:
                raise ValueError("Query has too many lexical terms; narrow it")
            ranked = []
            for expressions, joiner, match in ((strict, " AND ", "phrase"), (relaxed, " OR ", "partial-lexical")):
                if not expressions:
                    continue
                expression = joiner.join("(" + e + ")" for e in expressions)
                sql = "SELECT *,MIN(score) AS best_score FROM (SELECT u.*,bm25(search,0,5,1,2) AS score FROM search JOIN units u ON u.key=search.key WHERE search MATCH ? ORDER BY score LIMIT -1) GROUP BY path ORDER BY best_score,path LIMIT ?"
                ranked.extend((r, match) for r in db.execute(sql, (expression, limit + 1)))
        for row, match in ranked:
            if row["path"] in seen:
                continue
            seen.add(row["path"])
            # Incoming references identify the document that explains this code.
            relations = db.execute("SELECT source,target,line,present FROM links WHERE source=? OR target=? ORDER BY source,target LIMIT 4", (row["path"], row["path"])).fetchall()
            selector = {"path": row["path"], "start": row["start"], "end": row["end"], "source_digest": row["digest"]}
            results.append({"path": row["path"], "heading": row["heading"], "line": row["start"], "kind": row["kind"],
                            "source_digest": row["digest"], "summary": row["preview"], "match": match, "selector": selector,
                            "relations": [{"source": r["source"], "target": r["target"], "line": r["line"], "present": bool(r["present"])} for r in relations]})
        value = {"ok": True, "status": "complete" if results else "not_found", "generation": manifest["generation"],
                 "results": results[:limit], "has_more": len(results) > limit}
    finally:
        db.close()
    current, problem = _published(root)
    if problem or current["generation"] != manifest["generation"]:
        return _bounded({"ok": False, "status": "stale_index", "issues": ["Sources/index changed during lookup; discard results"]}, max_bytes)
    return _bounded(value, max_bytes, cards=True)


def read_unit(root, path, start=1, end=None, expected_digest=None, max_bytes=24000) -> dict:
    root = _root(root)
    file = _path(root, path)
    if type(max_bytes) is not int or not 512 <= max_bytes <= 4_000_000:
        raise ValueError("read_unit max_bytes must be 512..4000000")
    if not _readable(path):
        raise ValueError("Control, secret, dependency, history and unsupported content cannot be read through knowledge")
    manifest, problem = _published(root)
    if problem:
        return _bounded(problem, max_bytes)
    if path not in manifest["sources"] or not file.is_file():
        return _bounded({"ok": False, "status": "not_found", "issues": ["Path is not a current indexed source"]}, max_bytes)
    raw = _stable_bytes(file)
    if _secret_content(raw):
        raise ValueError("Private key content cannot be read through knowledge")
    digest = _hash(raw)
    if digest != manifest["sources"][path] or expected_digest is not None and digest != expected_digest:
        return _bounded({"ok": False, "status": "source_changed", "issues": ["Source digest differs from the requested/published version"]}, max_bytes)
    lines = raw.decode("utf-8").splitlines()
    finish = len(lines) if end is None else end
    if type(start) is not int or type(finish) is not int or start < 1 or finish < start or finish > len(lines):
        raise ValueError("Requested line range is outside the actual source")
    value = {"ok": True, "status": "complete", "path": path, "start": start, "end": finish,
             "source_digest": digest, "text": "\n".join(lines[start - 1:finish])}
    if len(_encode({**value, "usage": {"output_bytes": max_bytes, "max_bytes": max_bytes}})) > max_bytes:
        return _bounded({"ok": False, "status": "over_budget", "path": path, "source_digest": digest,
                         "issues": ["Requested source unit exceeds budget; select a smaller explicit line range"]}, max_bytes)
    current, problem = _published(root)
    if _hash(_stable_bytes(file)) != digest or problem or current["generation"] != manifest["generation"]:
        return _bounded({"ok": False, "status": "source_changed", "issues": ["Source changed during read; discard body"]}, max_bytes)
    return _bounded(value, max_bytes)


def _timestamp(value, field):
    if not isinstance(value, str) or "T" not in value:
        raise ValueError(field + " must be a UTC ISO timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(field + " must be a UTC ISO timestamp")
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError(field + " must explicitly use UTC")
    return parsed


def _validate_source(record):
    required = {"id", "kind", "path", "version", "observed_at", "scope", "claim_type"}
    if not isinstance(record, dict) or required - set(record) or set(record) - FIELDS:
        raise ValueError("Source record has missing or unknown fields")
    if not isinstance(record["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", record["id"]):
        raise ValueError("Source id must be a bounded stable identifier")
    if not isinstance(record["kind"], str) or not isinstance(record["claim_type"], str) or record["kind"] not in KINDS or record["claim_type"] not in CLAIMS:
        raise ValueError("Unknown source kind or claim_type")
    version = record["version"]
    if isinstance(version, dict):
        if set(version) != {"not_applicable_reason"} or not isinstance(version["not_applicable_reason"], str) or not version["not_applicable_reason"].strip():
            raise ValueError("Version exemption requires a concrete not_applicable_reason")
    elif not isinstance(version, str) or not version.strip() or len(version) > 256 or version.strip().casefold() in VAGUE_VERSIONS or re.search(r"(?i)\b(latest|unknown|current|tbd|todo|head|main|master|stable|nightly|vnext)\b|最新|未知|待定|当前版本", version):
        raise ValueError("Version must be verified and concrete, never latest/current/unknown/TBD")
    if not isinstance(record["scope"], str) or not record["scope"].strip() or len(record["scope"]) > 512:
        raise ValueError("Source scope must be a bounded nonempty string")
    observed = _timestamp(record["observed_at"], "observed_at")
    if observed > datetime.now(timezone.utc):
        raise ValueError("observed_at cannot be in the future")
    if record["kind"] in {"official", "primary", "private"} and not record.get("valid_until"):
        raise ValueError("External sources require explicit valid_until")
    if "valid_until" in record and _timestamp(record["valid_until"], "valid_until") <= observed:
        raise ValueError("valid_until must be later than observed_at")
    network = bool(record.get("url")) or record["kind"] in {"official", "primary"}
    if network:
        url = urlsplit(record.get("url", ""))
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            raise ValueError("Network sources require a credential-free http/https URL")
    if network or record["kind"] == "private":
        if any(not isinstance(record.get(key), str) or not record[key].strip() for key in ("publisher", "quality_reason")):
            raise ValueError("External provenance requires publisher and quality_reason")
    return observed


def _source_registry(root):
    value = _load(_path(root, SOURCES), {"schema_version": 1, "sources": {}, "history": []})
    if not isinstance(value, dict) or value.get("schema_version") != 1 or not isinstance(value.get("sources"), dict) or not isinstance(value.get("history", []), list):
        raise ValueError("Source registry is invalid; do not silently replace it")
    return value


@_serialized
def register_source(root, record) -> dict:
    root = _root(root)
    _validate_source(record)
    file = _path(root, record["path"])
    if not _source_allowed(record["path"]) or not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Source must reference an existing bounded nonsecret snapshot, not execution controls")
    raw = _stable_bytes(file)
    if not raw.strip():
        raise ValueError("Source snapshot cannot be empty")
    if _secret_content(raw):
        raise ValueError("Private keys cannot be registered as source snapshots")
    value = {**record, "digest": _hash(raw)}
    registry = _source_registry(root)
    previous = registry["sources"].get(record["id"])
    if previous is not None and previous != value:
        registry.setdefault("history", []).append(previous)
    registry["sources"][record["id"]] = value
    payload = _encode(registry)
    if len(payload) > MAX_REGISTRY_BYTES:
        raise ValueError("Source registry exceeds bounded size; archive explicitly")
    _atomic(_path(root, SOURCES), payload)
    return source_state(root, record["id"])


def source_state(root, id) -> dict:
    root = _root(root)
    if not isinstance(id, str) or not id:
        raise ValueError("Source id must be a nonempty string")
    registry = _source_registry(root)
    value = registry["sources"].get(id)
    if value is None:
        return {"id": id, "usable": False, "status": "missing", "issues": ["Source id is not registered"]}
    if not isinstance(value, dict):
        return {"id": id, "usable": False, "status": "invalid", "issues": ["Registered source has invalid structure"]}
    issues = []
    try:
        observed = _validate_source({k: v for k, v in value.items() if k != "digest"})
    except (ValueError, TypeError):
        issues.append("Source metadata/version/provenance is invalid")
    try:
        file = _path(root, value["path"])
        if not _source_allowed(value["path"]) or not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("Evidence snapshot missing or forbidden")
        raw = _stable_bytes(file)
        if _secret_content(raw):
            raise ValueError("Private key content is forbidden")
        current = _hash(raw)
    except (ValueError, OSError, KeyError):
        current = None
        issues.append("Evidence snapshot missing or forbidden")
    if current is not None and current != value.get("digest"):
        issues.append("Evidence snapshot content drifted")
    try:
        if value.get("valid_until") and _timestamp(value["valid_until"], "valid_until") <= datetime.now(timezone.utc):
            issues.append("Source validity window expired")
    except ValueError:
        pass
    if value.get("claim_type") == "hypothesis":
        issues.append("Hypothesis cannot be consumed as fact or approved requirement/decision")
    status = "usable" if not issues else "expired" if any("expired" in issue for issue in issues) else "drifted" if any("drifted" in issue for issue in issues) else "hypothesis" if value.get("claim_type") == "hypothesis" else "invalid"
    return {**value, "record_digest": _hash(_encode(value)), "current_digest": current, "usable": not issues, "status": status, "issues": issues}


def get_source(root, id, max_bytes=12000):
    """Return one registered source without loading the complete registry into context."""
    if type(max_bytes) is not int or not 512 <= max_bytes <= MAX_RESULT_BYTES:
        raise ValueError('Source budget must be 512..65536 bytes')
    result = source_state(root, id)
    return _bounded({'ok': result['usable'], 'status': result['status'], 'source': result}, max_bytes)


def read_evidence(root, relative, expected_digest, max_bytes=24000):
    """Inspect a specific execution evidence file; controls remain unreadable here."""
    root = _root(root)
    if not isinstance(relative, str) or not relative.startswith(EVIDENCE):
        raise ValueError('Only execution/evidence snapshots may use this reader')
    if type(max_bytes) is not int or not 512 <= max_bytes <= MAX_RESULT_BYTES:
        raise ValueError('Evidence budget must be 512..65536 bytes')
    file = _path(root, relative)
    if not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
        raise ValueError('Evidence is missing or too large; inspect a bounded original through the execution tool')
    raw = _stable_bytes(file)
    actual = _hash(raw)
    if not expected_digest or expected_digest != actual:
        raise ValueError('An exact current evidence digest is required')
    if _secret_content(raw):
        raise ValueError('Private key content is forbidden')
    try:
        text = raw.decode('utf-8')
        if '\x00' in text:
            raise UnicodeError('binary content')
    except UnicodeError:
        return _bounded({'ok': False, 'status': 'binary_evidence', 'path': relative, 'digest': actual,
                         'issues': ['Use the appropriate actual media/binary viewer; no textual understanding is claimed']}, max_bytes)
    value = {'ok': True, 'status': 'complete', 'kind': 'execution', 'path': relative, 'digest': actual, 'text': text}
    if len(_encode(value)) + 100 > max_bytes:
        return _bounded({'ok': False, 'status': 'over_budget', 'path': relative, 'digest': actual,
                         'issues': ['Increase the explicit budget or inspect the original evidence with a bounded execution tool']}, max_bytes)
    return _bounded(value, max_bytes)
