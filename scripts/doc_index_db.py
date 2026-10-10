#!/usr/bin/env python3
"""
跨平台文档索引库（Windows / Linux / macOS）。

- 仅依赖 Python 标准库 sqlite3 + pathlib
- Markdown / JSONL .idx 为权威源；SQLite 为 Agent 廉价查询面
- 优先 FTS5；不可用或中文查询时回退 LIKE，保证三端可检索
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from hs_paths import ensure_utf8_stdout
from idx_manager import IdxManager, calculate_digest

# 相对仓库根：权威文档树下的可重建缓存（勿手改）
DB_REL_DIR = Path("hs_dev_docs") / "_00_project" / "_18_doc_index"
DB_FILE_NAME = "doc_index.sqlite"
SUMMARY_MAX = 480
BODY_MAX = 12000
DEFAULT_LIMIT = 8
SLICE_MAX_LINES = 80


def db_path_for_root(workspace_root: Path) -> Path:
    return (workspace_root / DB_REL_DIR / DB_FILE_NAME).resolve()


def _posix_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        try:
            return Path(os.path.relpath(str(path), str(root))).as_posix()
        except Exception:
            return path.as_posix().replace("\\", "/")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def _extract_summary(text: str, title: str = "") -> str:
    if not text:
        return (title or "")[:SUMMARY_MAX]
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            if s.startswith("#"):
                # 保留标题行语义
                lines.append(s.lstrip("#").strip())
            continue
        if s.startswith("```") or s.startswith("---"):
            continue
        lines.append(s)
        if sum(len(x) for x in lines) >= SUMMARY_MAX:
            break
    summary = " ".join(lines).strip() or (title or text[:SUMMARY_MAX])
    return summary[:SUMMARY_MAX]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""


class DocIndexDB:
    def __init__(self, workspace_root: str | Path):
        self.root = Path(workspace_root).resolve()
        self.docs_root = self.root / "hs_dev_docs"
        self.mock_root = self.root / "mock"
        self.db_path = db_path_for_root(self.root)
        self.fts_available = False
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        # 跨平台：超时避免偶发锁；使用 DELETE 日志模式，避免 Windows 上 WAL 残留锁导致临时目录无法清理
        conn.execute("PRAGMA busy_timeout=5000")
        try:
            conn.execute("PRAGMA journal_mode=DELETE")
        except sqlite3.Error:
            pass
        self._conn = conn
        self._ensure_schema(conn)
        return conn

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS docs (
                doc_key TEXT PRIMARY KEY,
                domain TEXT,
                model TEXT,
                title TEXT,
                path TEXT NOT NULL,
                digest TEXT,
                status TEXT DEFAULT 'active',
                summary TEXT,
                body TEXT,
                kind TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_docs_domain ON docs(domain);
            CREATE INDEX IF NOT EXISTS idx_docs_path ON docs(path);
            """
        )
        self.fts_available = self._try_init_fts(conn)
        conn.commit()

    def _try_init_fts(self, conn: sqlite3.Connection) -> bool:
        try:
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
                    doc_key UNINDEXED,
                    title,
                    summary,
                    body,
                    path,
                    tokenize='unicode61'
                )
                """
            )
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def rebuild(self) -> Dict[str, Any]:
        conn = self.connect()
        conn.execute("DELETE FROM docs")
        if self.fts_available:
            try:
                conn.execute("DELETE FROM docs_fts")
            except sqlite3.Error:
                self.fts_available = False

        inserted = 0
        for row in self._iter_index_entries():
            self._upsert(conn, row)
            inserted += 1

        # 补充：无 idx 覆盖的关键 markdown（如词典）
        for path in self._iter_orphan_docs():
            rel = _posix_rel(path, self.root)
            doc_key = f"file:{rel}"
            text = _read_text(path)
            digest = calculate_digest(str(path))
            self._upsert(
                conn,
                {
                    "doc_key": doc_key,
                    "domain": self._guess_domain(rel),
                    "model": "",
                    "title": path.name,
                    "path": rel,
                    "digest": digest or "",
                    "status": "active",
                    "summary": _extract_summary(text, path.name),
                    "body": text[:BODY_MAX],
                    "kind": path.suffix.lstrip(".") or "file",
                    "updated_at": _utc_now(),
                },
            )
            inserted += 1

        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("rebuilt_at", _utc_now()),
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("fts", "1" if self.fts_available else "0"),
        )
        conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("root", str(self.root)),
        )
        conn.commit()
        payload = {
            "ok": True,
            "db_path": str(self.db_path),
            "db_path_posix": self.db_path.as_posix(),
            "inserted": inserted,
            "fts": self.fts_available,
            "rebuilt_at": _utc_now(),
        }
        # 重建后释放连接，避免 Windows 文件锁
        self.close()
        return payload

    def _guess_domain(self, rel_posix: str) -> str:
        parts = rel_posix.split("/")
        if len(parts) >= 2 and parts[0] == "hs_dev_docs":
            return parts[1]
        if parts and parts[0] == "mock":
            return "mock"
        return ""

    def _iter_index_entries(self) -> Iterable[Dict[str, Any]]:
        roots: List[Path] = []
        if self.docs_root.exists():
            roots.append(self.docs_root)
        if self.mock_root.exists():
            roots.append(self.mock_root)

        seen_paths = set()
        for base in roots:
            for idx_file in sorted(base.rglob("*.idx")):
                try:
                    mgr = IdxManager(str(idx_file))
                except Exception:
                    continue
                try:
                    idx_rel_parts = _posix_rel(idx_file, self.root).split("/")
                    if idx_rel_parts and idx_rel_parts[0] == "hs_dev_docs" and len(idx_rel_parts) > 1:
                        domain = idx_rel_parts[1]
                    elif idx_rel_parts and idx_rel_parts[0] == "mock":
                        domain = "mock"
                    else:
                        domain = mgr.metadata.get("category", "")
                except Exception:
                    domain = mgr.metadata.get("category", "")

                # 索引文件自身也入库，便于路由
                idx_rel = _posix_rel(idx_file, self.root)
                yield {
                    "doc_key": f"idx:{idx_rel}",
                    "domain": domain,
                    "model": "",
                    "title": f"[idx] {idx_file.name}",
                    "path": idx_rel,
                    "digest": calculate_digest(str(idx_file)) or "",
                    "status": "active",
                    "summary": json.dumps(mgr.metadata, ensure_ascii=False)[:SUMMARY_MAX],
                    "body": "\n".join(
                        json.dumps(e, ensure_ascii=False) for e in mgr.entries
                    )[:BODY_MAX],
                    "kind": "idx",
                    "updated_at": _utc_now(),
                }

                for entry in mgr.entries:
                    rel_path = entry.get("path") or ""
                    entry_id = entry.get("id") or rel_path
                    target = (idx_file.parent / rel_path)
                    try:
                        path_for_store = _posix_rel(target.resolve(), self.root) if target.exists() else _posix_rel(target, self.root)
                    except ValueError:
                        path_for_store = target.as_posix()

                    if not target.exists() or target.is_dir():
                        yield {
                            "doc_key": f"{domain}:{entry_id}",
                            "domain": domain,
                            "model": self._model_from_path(path_for_store),
                            "title": entry.get("title") or entry_id,
                            "path": Path(path_for_store).as_posix(),
                            "digest": entry.get("digest") or "",
                            "status": entry.get("status") or "active",
                            "summary": entry.get("title") or entry_id,
                            "body": "",
                            "kind": "idx_entry",
                            "updated_at": _utc_now(),
                        }
                        continue

                    rel = path_for_store
                    if rel in seen_paths:
                        continue
                    seen_paths.add(rel)
                    text = (
                        _read_text(target)
                        if target.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".sql"}
                        else ""
                    )
                    title = entry.get("title") or target.name
                    yield {
                        "doc_key": f"{domain}:{entry_id}",
                        "domain": domain,
                        "model": self._model_from_path(rel),
                        "title": title,
                        "path": rel,
                        "digest": entry.get("digest") or calculate_digest(str(target.resolve())) or "",
                        "status": entry.get("status") or "active",
                        "summary": _extract_summary(text, title),
                        "body": text[:BODY_MAX],
                        "kind": target.suffix.lstrip(".") or "file",
                        "updated_at": _utc_now(),
                    }

    def _iter_orphan_docs(self) -> Iterable[Path]:
        if not self.docs_root.exists():
            return
        extras = [
            self.docs_root / "_00_project" / "_02_project_word.dict.yaml",
        ]
        for p in extras:
            if p.is_file():
                yield p

    def _model_from_path(self, rel_posix: str) -> str:
        parts = rel_posix.split("/")
        for p in parts:
            if re.match(r"^_\d+_.+", p) and p not in {
                "_00_project",
                "_01_product_design",
                "_02_tech_select",
                "_03_architecture_design",
                "_04_db_schema",
                "_05_interface_design",
                "_06_method_design",
                "_07_call_chain",
                "_08_dev_process",
            }:
                # _01_payment -> payment
                m = re.match(r"^_\d+_(.+)$", p)
                if m and m.group(1) not in {"product_design", "task_brief", "task_detail", "task_context_pack"}:
                    return m.group(1)
        return ""

    def _upsert(self, conn: sqlite3.Connection, row: Dict[str, Any]) -> None:
        conn.execute(
            """
            INSERT OR REPLACE INTO docs(
                doc_key, domain, model, title, path, digest, status,
                summary, body, kind, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["doc_key"],
                row.get("domain") or "",
                row.get("model") or "",
                row.get("title") or "",
                row["path"],
                row.get("digest") or "",
                row.get("status") or "active",
                row.get("summary") or "",
                row.get("body") or "",
                row.get("kind") or "",
                row.get("updated_at") or _utc_now(),
            ),
        )
        if self.fts_available:
            try:
                conn.execute("DELETE FROM docs_fts WHERE doc_key = ?", (row["doc_key"],))
                conn.execute(
                    """
                    INSERT INTO docs_fts(doc_key, title, summary, body, path)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["doc_key"],
                        row.get("title") or "",
                        row.get("summary") or "",
                        row.get("body") or "",
                        row["path"],
                    ),
                )
            except sqlite3.Error:
                self.fts_available = False

    def search(
        self,
        query: str,
        *,
        domain: str = "",
        model: str = "",
        limit: int = DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        conn = self.connect()
        q = (query or "").strip()
        if not q:
            return {
                "ok": False,
                "error": "empty query",
                "results": [],
                "hint": "Provide --q with keywords from task/PRD.",
            }

        ranked: Dict[str, Dict[str, Any]] = {}

        use_fts = self.fts_available and not _has_cjk(q)
        if use_fts:
            fts_q = self._fts_query(q)
            try:
                sql = """
                    SELECT d.doc_key, d.domain, d.model, d.title, d.path, d.digest,
                           d.status, d.summary, d.kind, bm25(docs_fts) AS score
                    FROM docs_fts
                    JOIN docs d ON d.doc_key = docs_fts.doc_key
                    WHERE docs_fts MATCH ?
                """
                params: List[Any] = [fts_q]
                if domain:
                    sql += " AND d.domain = ?"
                    params.append(domain)
                if model:
                    sql += " AND d.model = ?"
                    params.append(model)
                sql += " ORDER BY score LIMIT ?"
                params.append(limit * 3)
                for r in conn.execute(sql, params):
                    ranked[r["doc_key"]] = self._row_to_result(r, source="fts")
            except sqlite3.Error:
                use_fts = False

        # LIKE 回退 / 中文 / 补召回（三端一致）
        like = f"%{q}%"
        sql = """
            SELECT doc_key, domain, model, title, path, digest, status, summary, kind,
                   0.0 AS score
            FROM docs
            WHERE (title LIKE ? OR summary LIKE ? OR body LIKE ? OR path LIKE ? OR doc_key LIKE ?)
        """
        params = [like, like, like, like, like]
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        if model:
            sql += " AND model = ?"
            params.append(model)
        sql += " LIMIT ?"
        params.append(limit * 3)
        for r in conn.execute(sql, params):
            if r["doc_key"] not in ranked:
                ranked[r["doc_key"]] = self._row_to_result(r, source="like")

        def _rank_key(item: Dict[str, Any]) -> Tuple[int, int, str]:
            kind = item.get("kind") or ""
            # 内容文档优先于纯 idx / idx_entry
            kind_penalty = 2 if kind in {"idx", "idx_entry"} else 0
            source_penalty = 0 if item.get("source") == "fts" else 1
            return (kind_penalty, source_penalty, item.get("path") or "")

        results = sorted(ranked.values(), key=_rank_key)[:limit]
        return {
            "ok": True,
            "query": q,
            "domain": domain or None,
            "model": model or None,
            "fts_used": use_fts,
            "count": len(results),
            "results": results,
            "hint": (
                "Token budget: read ONLY these paths (prefer slice). "
                "Do not walk full domain trees or re-read Skill references already loaded."
            ),
            "db_path": str(self.db_path),
        }

    def _fts_query(self, q: str) -> str:
        tokens = re.findall(r"[A-Za-z0-9_\.\-]+", q)
        if not tokens:
            return '"' + q.replace('"', " ") + '"'
        return " OR ".join(f'"{t}"' for t in tokens)

    def _row_to_result(self, row: sqlite3.Row, source: str) -> Dict[str, Any]:
        return {
            "doc_key": row["doc_key"],
            "domain": row["domain"],
            "model": row["model"],
            "title": row["title"],
            "path": row["path"],
            "digest": row["digest"],
            "status": row["status"],
            "summary": row["summary"],
            "kind": row["kind"],
            "source": source,
        }

    def get(self, path: str) -> Dict[str, Any]:
        conn = self.connect()
        rel = Path(path).as_posix()
        row = conn.execute(
            "SELECT * FROM docs WHERE path = ? OR doc_key = ? LIMIT 1",
            (rel, path),
        ).fetchone()
        if not row:
            # 尝试相对 hs_dev_docs
            alt = Path("hs_dev_docs") / path
            row = conn.execute(
                "SELECT * FROM docs WHERE path = ? LIMIT 1",
                (alt.as_posix(),),
            ).fetchone()
        if not row:
            return {"ok": False, "error": f"not found: {path}", "result": None}
        return {
            "ok": True,
            "result": {
                "doc_key": row["doc_key"],
                "domain": row["domain"],
                "model": row["model"],
                "title": row["title"],
                "path": row["path"],
                "digest": row["digest"],
                "status": row["status"],
                "summary": row["summary"],
                "kind": row["kind"],
                "body_preview": (row["body"] or "")[:800],
            },
            "hint": "Use slice for precise line ranges before editing.",
        }

    def slice(
        self,
        path: str,
        start: int = 1,
        end: Optional[int] = None,
        max_lines: int = SLICE_MAX_LINES,
    ) -> Dict[str, Any]:
        rel = Path(path).as_posix()
        candidates = [
            self.root / rel,
            self.docs_root / path,
            self.root / "hs_dev_docs" / path,
        ]
        target = next((p for p in candidates if p.is_file()), None)
        if target is None:
            return {"ok": False, "error": f"file not found: {path}", "lines": []}

        all_lines = _read_text(target).splitlines()
        start = max(1, int(start))
        if end is None:
            end = min(len(all_lines), start + max_lines - 1)
        end = min(int(end), len(all_lines))
        if end < start:
            return {"ok": False, "error": "invalid range", "lines": []}
        if end - start + 1 > max_lines:
            end = start + max_lines - 1

        chunk = []
        for i in range(start, end + 1):
            chunk.append({"line": i, "text": all_lines[i - 1]})

        return {
            "ok": True,
            "path": _posix_rel(target, self.root),
            "start": start,
            "end": end,
            "total_lines": len(all_lines),
            "lines": chunk,
            "text": "\n".join(all_lines[start - 1 : end]),
            "hint": "Inject only this slice into context_pack / prompt.",
        }

    def stats(self) -> Dict[str, Any]:
        conn = self.connect()
        count = conn.execute("SELECT COUNT(*) AS c FROM docs").fetchone()["c"]
        meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}
        return {
            "ok": True,
            "db_path": str(self.db_path),
            "docs": count,
            "fts": self.fts_available or meta.get("fts") == "1",
            "meta": meta,
        }


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Cross-platform hs_dev_docs SQLite index (Windows/Linux/macOS)"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root (contains hs_dev_docs/)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("rebuild", help="Rebuild SQLite cache from .idx + docs")
    sub.add_parser("stats", help="Show index stats")

    p_search = sub.add_parser("search", help="Search docs (FTS5 + LIKE fallback)")
    p_search.add_argument("--q", required=True, help="Query string")
    p_search.add_argument("--domain", default="", help="Filter domain folder name")
    p_search.add_argument("--model", default="", help="Filter model slug")
    p_search.add_argument("--limit", type=int, default=DEFAULT_LIMIT)

    p_get = sub.add_parser("get", help="Get one doc by path or doc_key")
    p_get.add_argument("--path", required=True)

    p_slice = sub.add_parser("slice", help="Return a line-range slice as JSON")
    p_slice.add_argument("--path", required=True)
    p_slice.add_argument("--start", type=int, default=1)
    p_slice.add_argument("--end", type=int, default=None)
    p_slice.add_argument("--max-lines", type=int, default=SLICE_MAX_LINES)

    args = parser.parse_args(argv)
    db = DocIndexDB(args.root)
    try:
        if args.command == "rebuild":
            _print_json(db.rebuild())
            return 0
        if args.command == "stats":
            _print_json(db.stats())
            return 0
        if args.command == "search":
            if not db.db_path.exists():
                db.rebuild()
            _print_json(
                db.search(
                    args.q,
                    domain=args.domain,
                    model=args.model,
                    limit=args.limit,
                )
            )
            return 0
        if args.command == "get":
            if not db.db_path.exists():
                db.rebuild()
            _print_json(db.get(args.path))
            return 0
        if args.command == "slice":
            _print_json(
                db.slice(
                    args.path,
                    start=args.start,
                    end=args.end,
                    max_lines=args.max_lines,
                )
            )
            return 0
    finally:
        db.close()
    return 1


if __name__ == "__main__":
    sys.exit(main())
