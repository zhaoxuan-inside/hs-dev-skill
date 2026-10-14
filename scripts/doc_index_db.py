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
from code_skeleton import CodeSkeletonExtractor

# 相对仓库根：权威文档树下的可重建缓存（勿手改）
DB_REL_DIR = Path("hs_dev_docs") / "_00_project_foundation" / "_05_doc_index"
DB_LEGACY_REL_DIR = Path("hs_dev_docs") / "_00_project" / "_18_doc_index"
DB_FILE_NAME = "doc_index.sqlite"
SUMMARY_MAX = 480
BODY_MAX = 12000
DEFAULT_LIMIT = 8
SLICE_MAX_LINES = 80


def db_path_for_root(workspace_root: Path) -> Path:
    p_new = workspace_root / DB_REL_DIR / DB_FILE_NAME
    p_old = workspace_root / DB_LEGACY_REL_DIR / DB_FILE_NAME
    if p_new.parent.exists():
        return p_new.resolve()
    if p_old.parent.exists():
        return p_old.resolve()
    return p_new.resolve()


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


def _parse_method_profile(text: str, doc_rel_path: str) -> Optional[Dict[str, Any]]:
    is_method_path = "_06_method_design" in doc_rel_path or "method_design" in doc_rel_path
    has_method_header = "方法类型" in text or "基础与位置画像" in text or "基础画像与位置" in text
    if not (is_method_path or has_method_header):
        return None

    name = ""
    m_title = re.search(r"^#\s*方法设计(?:规范|与契约画像模板)?[:：]\s*([A-Za-z0-9_]+)", text, re.MULTILINE)
    if m_title:
        name = m_title.group(1).strip()

    m_sig = re.search(r"-\s*\*\*方法签名\*\*[:：]\s*`?([^\r\n`]+)`?", text)
    signature = m_sig.group(1).strip() if m_sig else ""
    if (not name or name == "{method_name}") and signature:
        sig_match = re.search(r"(?:[A-Za-z0-9_<>\[\]]+\s+)?([A-Za-z0-9_]+)\s*\(", signature)
        if sig_match:
            name = sig_match.group(1).strip()
    if not name or name == "{method_name}":
        base = Path(doc_rel_path).stem
        base = re.sub(r"^_\d+_", "", base)
        base = re.sub(r"_design$", "", base)
        name = base

    m_arch = re.search(r"-\s*\*\*方法类型\*\*[:：]\s*`?([A-Za-z_]+)`?", text)
    archetype = m_arch.group(1).strip() if m_arch else ""
    if "{" in archetype:
        archetype = ""

    m_mod = re.search(r"-\s*\*\*所属模块\*\*[:：]\s*`?([^\r\n`]+)`?", text)
    module = m_mod.group(1).strip() if m_mod else ""
    if "（" in module or "(" in module:
        module = re.split(r"[（\(]", module)[0].strip()
    if "{" in module:
        module = ""

    m_layer = re.search(r"-\s*\*\*所属层次\*\*[:：]\s*([^\r\n]+)", text)
    layer = m_layer.group(1).strip() if m_layer else ""
    if "{" in layer:
        layer = ""

    m_desc = re.search(r"-\s*\*\*功能描述\*\*[:：]\s*([^\r\n]+)", text)
    description = m_desc.group(1).strip() if m_desc else ""
    if "{" in description:
        description = ""

    m_file = re.search(r"-\s*\*\*文件路径\*\*[:：]\s*`?([^\r\n`]+)`?", text)
    file_path = m_file.group(1).strip() if m_file else ""
    if "{" in file_path:
        file_path = ""

    start_line = None
    line_count = None
    end_line = None
    m_loc = re.search(r"第\s*`?(\d+)`?\s*行.*?共\s*`?(\d+)`?\s*行.*?`?(\d+)[-~](\d+)`?", text)
    if m_loc:
        start_line = int(m_loc.group(1))
        line_count = int(m_loc.group(2))
        end_line = int(m_loc.group(4))
    else:
        m_range = re.search(r"行范围[:：]\s*`?(\d+)[-~](\d+)`?", text)
        if m_range:
            start_line = int(m_range.group(1))
            end_line = int(m_range.group(2))
            line_count = end_line - start_line + 1

    m_sens = re.search(r"-\s*\*\*改动敏感度\*\*[:：]\s*`?([A-Za-z_]+)`?", text)
    sensitivity = m_sens.group(1).strip() if m_sens else "LOW"
    if "{" in sensitivity:
        sensitivity = "LOW"

    return {
        "method_key": f"method:{name}@{doc_rel_path}",
        "name": name,
        "archetype": archetype,
        "module": module,
        "layer": layer,
        "description": description,
        "signature": signature,
        "file_path": file_path,
        "start_line": start_line,
        "line_count": line_count,
        "end_line": end_line,
        "sensitivity": sensitivity,
        "doc_path": doc_rel_path,
        "updated_at": _utc_now(),
    }



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

            CREATE TABLE IF NOT EXISTS methods (
                method_key TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                archetype TEXT,
                module TEXT,
                layer TEXT,
                description TEXT,
                signature TEXT,
                file_path TEXT,
                start_line INTEGER,
                line_count INTEGER,
                end_line INTEGER,
                sensitivity TEXT,
                doc_path TEXT NOT NULL,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_methods_name ON methods(name);
            CREATE INDEX IF NOT EXISTS idx_methods_archetype ON methods(archetype);
            CREATE INDEX IF NOT EXISTS idx_methods_module ON methods(module);

            CREATE TABLE IF NOT EXISTS code_symbols (
                symbol_key TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                kind TEXT,
                file_path TEXT NOT NULL,
                signature TEXT,
                start_line INTEGER,
                end_line INTEGER,
                docstring TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_symbols_name ON code_symbols(name);
            CREATE INDEX IF NOT EXISTS idx_symbols_file ON code_symbols(file_path);

            -- 1 & 3: 产品功能与子规格详情表
            CREATE TABLE IF NOT EXISTS features (
                feature_key TEXT PRIMARY KEY,
                feature_id TEXT NOT NULL,
                name TEXT NOT NULL,
                domain TEXT,
                module TEXT,
                summary TEXT,
                prd_path TEXT,
                priority TEXT DEFAULT 'P1',
                status TEXT DEFAULT 'active',
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_features_id ON features(feature_id);
            CREATE INDEX IF NOT EXISTS idx_features_domain ON features(domain);

            -- 2: 页面名称与具体布局拓扑表
            CREATE TABLE IF NOT EXISTS pages (
                page_key TEXT PRIMARY KEY,
                page_id TEXT NOT NULL,
                name TEXT NOT NULL,
                route TEXT,
                module TEXT,
                prototype_html TEXT,
                layout_type TEXT,
                summary TEXT,
                doc_path TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_pages_id ON pages(page_id);
            CREATE INDEX IF NOT EXISTS idx_pages_route ON pages(route);

            -- 4 & 9: 架构模式协同集群表
            CREATE TABLE IF NOT EXISTS pattern_clusters (
                cluster_key TEXT PRIMARY KEY,
                feature_id TEXT NOT NULL,
                pattern_name TEXT NOT NULL,
                cluster_name TEXT NOT NULL,
                participating_symbols TEXT,
                guardrails TEXT,
                doc_path TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_patterns_feature ON pattern_clusters(feature_id);
            CREATE INDEX IF NOT EXISTS idx_patterns_name ON pattern_clusters(pattern_name);

            -- 10 & 11: 数据模式与存储结构功能映射表
            CREATE TABLE IF NOT EXISTS data_schemas (
                schema_key TEXT PRIMARY KEY,
                feature_id TEXT,
                table_name TEXT NOT NULL,
                layer TEXT,
                module TEXT,
                description TEXT,
                ddl_path TEXT,
                fields_summary TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_schemas_table ON data_schemas(table_name);
            CREATE INDEX IF NOT EXISTS idx_schemas_feature ON data_schemas(feature_id);

            -- 12, 13 & 14: 测试用例与执行说明表
            CREATE TABLE IF NOT EXISTS test_cases (
                case_key TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                feature_id TEXT,
                target_symbol TEXT,
                layer TEXT,
                module TEXT,
                description TEXT,
                test_file TEXT,
                test_command TEXT,
                ddt_dataset TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_tests_case_id ON test_cases(case_id);
            CREATE INDEX IF NOT EXISTS idx_tests_target ON test_cases(target_symbol);

            -- 7 & 8: 方法全局与局部微依赖拓扑表
            CREATE TABLE IF NOT EXISTS method_dependencies (
                dep_key TEXT PRIMARY KEY,
                source_symbol TEXT NOT NULL,
                target_symbol TEXT NOT NULL,
                dep_type TEXT,
                source_file TEXT,
                target_file TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_deps_source ON method_dependencies(source_symbol);
            CREATE INDEX IF NOT EXISTS idx_deps_target ON method_dependencies(target_symbol);

            -- 16: 物理审计变更历史表 (时间与简述双索引)
            CREATE TABLE IF NOT EXISTS audit_changes (
                audit_key TEXT PRIMARY KEY,
                checkpoint_id TEXT NOT NULL,
                task_id TEXT,
                timestamp TEXT NOT NULL,
                summary TEXT,
                affected_files TEXT,
                affected_symbols TEXT,
                raw_log_path TEXT,
                updated_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_audit_checkpoint ON audit_changes(checkpoint_id);
            CREATE INDEX IF NOT EXISTS idx_audit_time ON audit_changes(timestamp);
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
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS methods_fts USING fts5(
                    method_key UNINDEXED,
                    name,
                    description,
                    signature,
                    module,
                    tokenize='unicode61'
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5(
                    symbol_key UNINDEXED,
                    name,
                    signature,
                    file_path,
                    docstring,
                    tokenize='unicode61'
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS features_fts USING fts5(
                    feature_key UNINDEXED,
                    feature_id,
                    name,
                    summary,
                    domain,
                    module,
                    tokenize='unicode61'
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                    page_key UNINDEXED,
                    page_id,
                    name,
                    route,
                    summary,
                    tokenize='unicode61'
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS test_cases_fts USING fts5(
                    case_key UNINDEXED,
                    case_id,
                    description,
                    target_symbol,
                    test_command,
                    tokenize='unicode61'
                )
                """
            )
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS audit_changes_fts USING fts5(
                    audit_key UNINDEXED,
                    checkpoint_id,
                    summary,
                    affected_files,
                    affected_symbols,
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
        conn.execute("DELETE FROM methods")
        conn.execute("DELETE FROM code_symbols")
        conn.execute("DELETE FROM features")
        conn.execute("DELETE FROM pages")
        conn.execute("DELETE FROM pattern_clusters")
        conn.execute("DELETE FROM data_schemas")
        conn.execute("DELETE FROM test_cases")
        conn.execute("DELETE FROM method_dependencies")
        conn.execute("DELETE FROM audit_changes")
        if self.fts_available:
            try:
                conn.execute("DELETE FROM docs_fts")
                conn.execute("DELETE FROM methods_fts")
                conn.execute("DELETE FROM symbols_fts")
                conn.execute("DELETE FROM features_fts")
                conn.execute("DELETE FROM pages_fts")
                conn.execute("DELETE FROM test_cases_fts")
                conn.execute("DELETE FROM audit_changes_fts")
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

        # 索引业务代码与脚本中的符号（类、函数、签名与行号）
        symbols_inserted = self._index_code_symbols(conn)

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
            "symbols_inserted": symbols_inserted,
            "fts": self.fts_available,
            "rebuilt_at": _utc_now(),
        }
        # 重建后释放连接，避免 Windows 文件锁
        self.close()
        return payload

    def _index_code_symbols(self, conn: sqlite3.Connection) -> int:
        extractor = CodeSkeletonExtractor()
        code_dirs = [
            self.root / "backend",
            self.root / "frontend",
            self.root / "apps",
            self.root / "packages",
            self.root / "src",
            self.root / "scripts",
        ]
        count = 0
        for cdir in code_dirs:
            if not cdir.exists():
                continue
            for ext in (".py", ".ts", ".js", ".go", ".rs", ".java"):
                for fpath in cdir.rglob(f"*{ext}"):
                    rel_p = _posix_rel(fpath, self.root)
                    if any(x in rel_p for x in ("node_modules", ".git", "output", "__pycache__", "dist", "vendor", ".hs_cache")):
                        continue
                    syms = extractor.extract_symbols_metadata(fpath)
                    for s in syms:
                        s_key = f"sym:{s['name']}@{rel_p}:{s['start_line']}"
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO code_symbols (
                                symbol_key, name, kind, file_path, signature, start_line, end_line, docstring, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                s_key,
                                s["name"],
                                s["kind"],
                                rel_p,
                                s["signature"],
                                s["start_line"],
                                s["end_line"],
                                s["docstring"],
                                _utc_now(),
                            ),
                        )
                        if self.fts_available:
                            try:
                                conn.execute(
                                    "INSERT INTO symbols_fts (symbol_key, name, signature, file_path, docstring) VALUES (?, ?, ?, ?, ?)",
                                    (s_key, s["name"], s["signature"], rel_p, s["docstring"]),
                                )
                            except sqlite3.Error:
                                pass
                        count += 1
        return count

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

        # 扫描方法设计目录（兼容新旧结构）
        for method_dir in [
            self.docs_root / "_04_engineering_contract" / "_04_method_design",
            self.docs_root / "_06_method_design",
        ]:
            if method_dir.exists():
                for p in sorted(method_dir.rglob("*.md")):
                    if p.is_file():
                        yield p

    def _model_from_path(self, rel_posix: str) -> str:
        parts = rel_posix.split("/")
        for p in parts:
            if re.match(r"^_\d+_.+", p) and p not in {
                "_00_project_foundation",
                "_01_product_vision",
                "_02_feature_spec",
                "_03_architecture_design",
                "_04_engineering_contract",
                "_05_task_orchestration",
                "_06_dev_process",
                "_00_project",
                "_01_product_design",
                "_02_tech_select",
                "_04_db_schema",
                "_05_interface_design",
                "_06_method_design",
                "_07_call_chain",
                "_08_dev_process",
                "_01_db_schema",
                "_02_interface_design",
                "_03_mock_contract",
                "_04_method_design",
                "_05_call_chain",
            }:
                # _01_payment -> payment
                m = re.match(r"^_\d+_(.+)$", p)
                if m and m.group(1) not in {
                    "product_design", "task_brief", "task_detail", "task_context_pack",
                    "design_charter", "phased_roadmap", "human_prd", "vibe_spec",
                    "system_architecture", "plan_log", "change_log", "verify_log"
                }:
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

        # 自动提取并注册方法契约画像（若属于方法设计文档）
        body = row.get("body") or ""
        path = row.get("path") or ""
        if body and ("_06_method_design" in path or "method_design" in path or "方法类型" in body):
            method_prof = _parse_method_profile(body, path)
            if method_prof and method_prof.get("name"):
                self._upsert_method(conn, method_prof)

    def _upsert_method(self, conn: sqlite3.Connection, m: Dict[str, Any]) -> None:
        conn.execute(
            """
            INSERT OR REPLACE INTO methods(
                method_key, name, archetype, module, layer, description,
                signature, file_path, start_line, line_count, end_line,
                sensitivity, doc_path, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                m["method_key"],
                m.get("name") or "",
                m.get("archetype") or "",
                m.get("module") or "",
                m.get("layer") or "",
                m.get("description") or "",
                m.get("signature") or "",
                m.get("file_path") or "",
                m.get("start_line"),
                m.get("line_count"),
                m.get("end_line"),
                m.get("sensitivity") or "LOW",
                m["doc_path"],
                m.get("updated_at") or _utc_now(),
            ),
        )
        if self.fts_available:
            try:
                conn.execute("DELETE FROM methods_fts WHERE method_key = ?", (m["method_key"],))
                conn.execute(
                    """
                    INSERT INTO methods_fts(method_key, name, description, signature, module)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        m["method_key"],
                        m.get("name") or "",
                        m.get("description") or "",
                        m.get("signature") or "",
                        m.get("module") or "",
                    ),
                )
            except sqlite3.Error:
                pass

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
        m_count = conn.execute("SELECT COUNT(*) AS c FROM methods").fetchone()["c"]
        s_count = conn.execute("SELECT COUNT(*) AS c FROM code_symbols").fetchone()["c"]
        f_count = conn.execute("SELECT COUNT(*) AS c FROM features").fetchone()["c"]
        p_count = conn.execute("SELECT COUNT(*) AS c FROM pages").fetchone()["c"]
        pat_count = conn.execute("SELECT COUNT(*) AS c FROM pattern_clusters").fetchone()["c"]
        sch_count = conn.execute("SELECT COUNT(*) AS c FROM data_schemas").fetchone()["c"]
        t_count = conn.execute("SELECT COUNT(*) AS c FROM test_cases").fetchone()["c"]
        dep_count = conn.execute("SELECT COUNT(*) AS c FROM method_dependencies").fetchone()["c"]
        aud_count = conn.execute("SELECT COUNT(*) AS c FROM audit_changes").fetchone()["c"]
        meta = {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM meta")}
        return {
            "ok": True,
            "db_path": str(self.db_path),
            "docs": count,
            "methods": m_count,
            "code_symbols": s_count,
            "features": f_count,
            "pages": p_count,
            "pattern_clusters": pat_count,
            "data_schemas": sch_count,
            "test_cases": t_count,
            "method_dependencies": dep_count,
            "audit_changes": aud_count,
            "fts": self.fts_available or meta.get("fts") == "1",
            "meta": meta,
        }

    def _row_to_method_result(self, r: sqlite3.Row, source: str) -> Dict[str, Any]:
        start = r["start_line"]
        end = r["end_line"]
        lines = f"{start}-{end}" if start and end else (str(start) if start else "")
        return {
            "method_key": r["method_key"],
            "name": r["name"],
            "archetype": r["archetype"],
            "module": r["module"],
            "layer": r["layer"],
            "description": r["description"],
            "signature": r["signature"],
            "file_path": r["file_path"],
            "lines": lines,
            "sensitivity": r["sensitivity"],
            "doc_path": r["doc_path"],
            "source": source,
        }

    def method_search(
        self,
        query: str,
        *,
        archetype: str = "",
        module: str = "",
        limit: int = 5,
    ) -> Dict[str, Any]:
        conn = self.connect()
        q = (query or "").strip()
        if not q:
            return {
                "ok": False,
                "error": "empty query",
                "count": 0,
                "candidates": [],
                "hint": "Provide --q with natural language intent or method name.",
            }

        ranked: Dict[str, Dict[str, Any]] = {}
        use_fts = self.fts_available and not _has_cjk(q)
        if use_fts:
            fts_q = self._fts_query(q)
            try:
                sql = """
                    SELECT m.method_key, m.name, m.archetype, m.module, m.layer,
                           m.description, m.signature, m.file_path, m.start_line,
                           m.line_count, m.end_line, m.sensitivity, m.doc_path,
                           bm25(methods_fts) AS score
                    FROM methods_fts
                    JOIN methods m ON m.method_key = methods_fts.method_key
                    WHERE methods_fts MATCH ?
                """
                params: List[Any] = [fts_q]
                if archetype:
                    sql += " AND m.archetype = ?"
                    params.append(archetype.upper())
                if module:
                    sql += " AND m.module = ?"
                    params.append(module)
                sql += " ORDER BY score LIMIT ?"
                params.append(limit * 2)
                for r in conn.execute(sql, params):
                    ranked[r["method_key"]] = self._row_to_method_result(r, source="fts")
            except sqlite3.Error:
                use_fts = False

        like = f"%{q}%"
        sql = """
            SELECT method_key, name, archetype, module, layer, description,
                   signature, file_path, start_line, line_count, end_line,
                   sensitivity, doc_path, 0.0 AS score
            FROM methods
            WHERE (name LIKE ? OR description LIKE ? OR signature LIKE ? OR module LIKE ?)
        """
        params = [like, like, like, like]
        if archetype:
            sql += " AND archetype = ?"
            params.append(archetype.upper())
        if module:
            sql += " AND module = ?"
            params.append(module)
        sql += " LIMIT ?"
        params.append(limit * 2)
        for r in conn.execute(sql, params):
            if r["method_key"] not in ranked:
                ranked[r["method_key"]] = self._row_to_method_result(r, source="like")

        candidates = list(ranked.values())[:limit]
        for c in candidates:
            c["action_recommendation"] = (
                "REUSE_OR_EXTEND (优先直接复用或通过可选入参扩展现有方法，绝对禁止新建影子函数或同义变体)"
            )

        guidance = (
            "Anti-Method-Explosion Gate: If candidate matches intent >=80%, REUSE or EXTEND it with optional arguments. "
            "If no candidate matches and you MUST create a new method, register its contract in hs_dev_docs/_06_method_design first, "
            "and strictly enforce Deep Module & Rule of Three (inline trivial 1-3 line logic)."
            if candidates
            else "No matching method found. If logic is trivial (<=3 lines) and single-use, INLINE it. "
                 "If truly a new reusable domain method, create its contract profile under hs_dev_docs/_06_method_design first."
        )

        return {
            "ok": True,
            "query": q,
            "archetype": archetype or None,
            "module": module or None,
            "fts_used": use_fts,
            "count": len(candidates),
            "candidates": candidates,
            "guidance": guidance,
            "db_path": str(self.db_path),
        }

    def symbol_search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """按符号名或签名搜索代码中的类、函数、方法（毫秒级，防止盲目扫代码）"""
        conn = self.connect()
        q = (query or "").strip()
        if not q:
            return {"ok": True, "query": q, "count": 0, "symbols": []}

        rows = []
        if self.fts_available and not _has_cjk(q):
            try:
                cur = conn.execute(
                    """
                    SELECT s.name, s.kind, s.file_path, s.signature, s.start_line, s.end_line, s.docstring
                    FROM symbols_fts f
                    JOIN code_symbols s ON f.symbol_key = s.symbol_key
                    WHERE symbols_fts MATCH ?
                    LIMIT ?
                    """,
                    (f'"{q}"*', limit),
                )
                rows = [dict(r) for r in cur.fetchall()]
            except sqlite3.Error:
                pass

        if not rows:
            cur = conn.execute(
                """
                SELECT name, kind, file_path, signature, start_line, end_line, docstring
                FROM code_symbols
                WHERE name LIKE ? OR signature LIKE ?
                ORDER BY CASE WHEN name = ? THEN 0 WHEN name LIKE ? THEN 1 ELSE 2 END
                LIMIT ?
                """,
                (f"%{q}%", f"%{q}%", q, f"{q}%", limit),
            )
            rows = [dict(r) for r in cur.fetchall()]

        return {
            "ok": True,
            "query": q,
            "count": len(rows),
            "symbols": rows,
            "db_path": str(self.db_path),
        }

    def symbol_slice(self, symbol_name: str) -> Dict[str, Any]:
        """根据符号名称直接定位并提取源代码切片（免全量文件读取）"""
        conn = self.connect()
        cur = conn.execute(
            """
            SELECT name, kind, file_path, signature, start_line, end_line, docstring
            FROM code_symbols
            WHERE name = ? OR name LIKE ?
            ORDER BY CASE WHEN name = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (symbol_name, f"%.{symbol_name}", symbol_name),
        )
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": f"Symbol '{symbol_name}' not found in code_symbols index"}
        r = dict(row)
        full_path = self.root / r["file_path"]
        if not full_path.exists():
            return {"ok": False, "error": f"Source file '{r['file_path']}' not found on disk"}

        lines = full_path.read_text(encoding="utf-8", errors="replace").splitlines()
        s_line = max(1, r["start_line"])
        e_line = min(len(lines), r["end_line"])
        slice_content = "\n".join(lines[s_line - 1 : e_line])
        return {
            "ok": True,
            "symbol": r,
            "total_file_lines": len(lines),
            "start_line": s_line,
            "end_line": e_line,
            "content": slice_content,
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

    p_method = sub.add_parser(
        "method-search",
        help="Search method contracts in hs_dev_docs/_06_method_design to prevent method explosion",
    )
    p_method.add_argument("--q", required=True, help="Intent or keywords (e.g. '手机号脱敏' or 'payment')")
    p_method.add_argument("--archetype", default="", help="Filter by archetype: TRANSFORM/ALGO/GUARD/STATE/ORCHESTRATE/ADAPTER/PRESENT")
    p_method.add_argument("--module", default="", help="Filter by module")
    p_method.add_argument("--limit", type=int, default=5)

    p_sym = sub.add_parser("symbol-search", help="Search code symbols (classes, functions, methods) in codebase")
    p_sym.add_argument("--q", required=True, help="Symbol name or keyword")
    p_sym.add_argument("--limit", type=int, default=10)

    p_sym_slice = sub.add_parser("symbol-slice", help="Slice code directly by symbol name")
    p_sym_slice.add_argument("--name", required=True, help="Symbol name (e.g. 'TaskManager' or 'render_dashboard')")

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
        if args.command == "method-search":
            if not db.db_path.exists():
                db.rebuild()
            _print_json(
                db.method_search(
                    args.q,
                    archetype=args.archetype,
                    module=args.module,
                    limit=args.limit,
                )
            )
            return 0
        if args.command == "symbol-search":
            if not db.db_path.exists():
                db.rebuild()
            _print_json(db.symbol_search(args.q, limit=args.limit))
            return 0
        if args.command == "symbol-slice":
            if not db.db_path.exists():
                db.rebuild()
            _print_json(db.symbol_slice(args.name))
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
