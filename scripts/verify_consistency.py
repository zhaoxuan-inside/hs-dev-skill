#!/usr/bin/env python3
"""
verify_consistency.py
产品开发规范与提交前门禁全量自检脚本。
检查三文件一致性、.idx 索引防漂移、DB 迁移 V/U 原子同步、SQL 保留字及 Mock 契约完整性。
"""

import os
import sys
import re
import argparse
from pathlib import Path
from idx_manager import IdxManager


class ConsistencyVerifier:
    def __init__(self, workspace_root: str, strict: bool = False):
        self.root = Path(workspace_root).resolve()
        self.docs_root = self.root / "hs_dev_docs"
        self.mock_root = self.root / "mock"
        self.strict = strict
        self.errors = []
        self.warnings = []

    def check_all(self) -> bool:
        print(f"[*] Starting Consistency & Quality Gate Check at: {self.root}")
        self.errors.clear()
        self.warnings.clear()

        if not self.docs_root.exists():
            if (self.root / "demo_project" / "hs_dev_docs").exists():
                self.docs_root = self.root / "demo_project" / "hs_dev_docs"
                self.mock_root = self.root / "demo_project" / "mock"
            else:
                self.errors.append("hs_dev_docs directory does not exist! Please run init_hs_dev_docs.py first.")
                self._print_results()
                return False

        # 0. 检查 Skill 自身三处版本号单源一致性（当处于 Skill 根目录时）
        self._check_skill_version()

        # 1. 检查全量 .idx 索引文件
        self._check_indices()

        # 2. 检查任务三文件强一致性
        self._check_task_consistency()

        # 3. 检查数据库迁移脚本原子性 (V & U Sync) 与 SQL 规范
        self._check_database_migrations()

        # 4. 检查 Mock 契约与 Profile 引用
        self._check_mock_profiles()

        # 5. 文档索引库（SQLite）存在性与可查询性（跨平台缓存，非权威源）
        self._check_doc_index_db()

        # 6. 检查多端工程架构卫生与打包产物输出隔离 (Output & Workspace Hygiene)
        self._check_workspace_hygiene()

        return self._print_results()

    def _check_skill_version(self):
        """检查 Skill 自身三处版本号单源一致性（仅在包含 SKILL.md 的 Skill 根目录触发）"""
        skill_file = self.root / "SKILL.md"
        readme_file = self.root / "README.md"
        if not skill_file.exists():
            return

        print("  -> Checking Skill Package Version Consistency...")
        skill_text = skill_file.read_text(encoding="utf-8")

        m_meta = re.search(r'metadata:\s*\n(?:\s+.*\n)*?\s+version:\s*["\']?([^"\']+)["\']?', skill_text)
        meta_ver = m_meta.group(1).strip() if m_meta else None

        m_body = re.search(r'版本：v?([0-9\.]+)', skill_text)
        body_ver = m_body.group(1).strip() if m_body else None

        if not meta_ver:
            self.errors.append("[SKILL VERSION ERROR] SKILL.md missing metadata.version in frontmatter")
        if not body_ver:
            self.errors.append("[SKILL VERSION ERROR] SKILL.md missing '版本：v...' in body")

        if meta_ver and body_ver and meta_ver != body_ver:
            self.errors.append(
                f"[SKILL VERSION MISMATCH] SKILL.md metadata.version '{meta_ver}' "
                f"does not match body version '{body_ver}'"
            )

        if readme_file.exists():
            readme_text = readme_file.read_text(encoding="utf-8")
            m_readme = re.search(r'badge/skill-v?([0-9\.]+)-blue', readme_text)
            if m_readme:
                readme_ver = m_readme.group(1).strip()
                if meta_ver and readme_ver != meta_ver:
                    self.errors.append(
                        f"[SKILL VERSION MISMATCH] README.md badge version '{readme_ver}' "
                        f"does not match SKILL.md version '{meta_ver}'"
                    )

    def _check_indices(self):
        """遍历并校验所有 .idx 文件"""
        print("  -> Checking all JSONL .idx files...")
        idx_files = list(self.docs_root.rglob("*.idx")) + list(self.mock_root.rglob("*.idx"))
        for idx_file in idx_files:
            try:
                mgr = IdxManager(str(idx_file))
                valid, errs = mgr.verify()
                if not valid:
                    for e in errs:
                        self.errors.append(f"[INDEX ERROR] {idx_file.relative_to(self.root)}: {e}")
            except Exception as ex:
                self.errors.append(f"[INDEX PARSE ERROR] {idx_file.relative_to(self.root)}: {ex}")

    def _check_task_consistency(self):
        """检查 _00_task.idx、task_brief 与 task_detail 三文件一致性"""
        print("  -> Checking Task Triple-File Consistency...")
        task_idx_file = self.docs_root / "_08_dev_process/_09_task/_00_task.idx"
        if not task_idx_file.exists():
            return

        mgr = IdxManager(str(task_idx_file))
        brief_dir = self.docs_root / "_08_dev_process/_09_task/_01_task_brief"
        detail_dir = self.docs_root / "_08_dev_process/_09_task/_02_task_detail"

        # 聚合所有 task_brief 内容
        brief_contents = ""
        for bf in brief_dir.glob("*.md"):
            brief_contents += bf.read_text(encoding="utf-8") + "\n"

        for entry in mgr.entries:
            task_id = entry.get("id")
            title = entry.get("title")
            status = entry.get("status")

            # 1. 检查 task_brief 中是否存在该条目
            if f"### 任务简述：{task_id}" not in brief_contents:
                self.errors.append(f"[TASK CONSISTENCY] Task '{task_id}' missing in _01_task_brief/*.md")
            else:
                # 检查简述中的状态
                if f"### 任务简述：{task_id}" in brief_contents:
                    # 匹配该任务块中的状态
                    pattern = rf"### 任务简述：{task_id}[\s\S]*?- \*\*状态\*\*：`([^`]+)`"
                    m = re.search(pattern, brief_contents)
                    if m:
                        b_status = m.group(1)
                        if b_status != status:
                            self.errors.append(f"[TASK MISMATCH] Task '{task_id}' status mismatch: .idx has '{status}', but brief has '{b_status}'")

            # 2. 检查 task_detail
            rel_path = entry.get("path")
            target_detail = self.docs_root / "_08_dev_process/_09_task" / rel_path
            if not target_detail.exists():
                self.errors.append(f"[TASK CONSISTENCY] Task '{task_id}' detail file missing: {rel_path}")
            else:
                d_content = target_detail.read_text(encoding="utf-8")
                m = re.search(r"- \*\*当前状态\*\*：`([^`]+)`", d_content)
                if m:
                    d_status = m.group(1)
                    if d_status != status:
                        self.errors.append(f"[TASK MISMATCH] Task '{task_id}' status mismatch: .idx has '{status}', but detail has '{d_status}'")

                # change_size：缺失仅 warning（兼容旧任务）
                if not re.search(r"- \*\*(?:变更分级|change_size)\*\*：`([SML])`", d_content):
                    self.warnings.append(
                        f"[RIGHT-SIZING] Active task '{task_id}' missing change_size=S|M|L in detail "
                        f"(set via task_manager create --change-size; see references/right_sizing.md)"
                    )

            # context_pack 同步检查 change_size
            cp_path = (
                self.docs_root
                / "_08_dev_process/_09_task"
                / f"_03_task_context_pack/_01_{task_id}/_00_context_pack.md"
            )
            if cp_path.exists():
                cp_text = cp_path.read_text(encoding="utf-8")
                if not re.search(r"- \*\*change_size\*\*：`([SML])`", cp_text):
                    self.warnings.append(
                        f"[RIGHT-SIZING] Active task '{task_id}' context_pack missing change_size=S|M|L"
                    )

    def _check_database_migrations(self):
        """检查 DB 迁移 V/U 脚本原子配对与 SQL 规范"""
        print("  -> Checking Database Migrations (V/U Sync) and SQL Rules...")
        migration_dirs = list(self.docs_root.rglob("migrations"))
        for m_dir in migration_dirs:
            v_files = list(m_dir.glob("V*.sql"))
            u_files = list(m_dir.glob("U*.sql"))

            v_versions = {}
            for vf in v_files:
                match = re.match(r"V([0-9\.]+__(.+))\.sql", vf.name)
                if match:
                    ver_desc = match.group(1)
                    v_versions[ver_desc] = vf
                else:
                    self.errors.append(f"[DB MIGRATION FORMAT ERROR] {vf.name} does not match V<version>__<description>.sql format")

            for ver_desc, vf in v_versions.items():
                expected_u = m_dir / f"U{ver_desc}.sql"
                if not expected_u.exists():
                    self.errors.append(f"[DB MIGRATION ERROR] Forward migration {vf.name} is missing corresponding rollback script {expected_u.name}")

                # 检查 SQL 中是否含有非法的 desc 字段 (保留字检查)
                v_content = vf.read_text(encoding="utf-8")
                if re.search(r"\bdesc\s+(varchar|text|int|bigint|timestamp|datetime)\b", v_content, re.IGNORECASE):
                    self.errors.append(f"[SQL KEYWORD ERROR] {vf.name} uses forbidden SQL reserved keyword 'desc' as column name. Please rename to 'description'.")

    def _check_mock_profiles(self):
        """检查 Mock Test Profile 的契约引用"""
        print("  -> Checking Mock Profiles...")
        profile_dir = self.mock_root / "_06_test_profile"
        if not profile_dir.exists():
            return

        for pf in profile_dir.glob("*.yaml"):
            content = pf.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("contract_ref:"):
                    ref_path = line.split(":", 1)[1].strip().strip('"').strip("'")
                    target = self.root / ref_path
                    if not target.exists() and (self.docs_root.parent / ref_path).exists():
                        target = self.docs_root.parent / ref_path
                    if not target.exists():
                        self.warnings.append(f"[MOCK PROFILE WARNING] {pf.name} contract_ref not found on disk: {ref_path}")

    def _check_doc_index_db(self):
        """检查 SQLite 文档索引缓存；缺失则告警（不阻断，因可 rebuild）"""
        print("  -> Checking Doc Index DB (SQLite cache)...")
        db_file = self.docs_root / "_00_project" / "_18_doc_index" / "doc_index.sqlite"
        idx_files = list(self.docs_root.rglob("*.idx"))
        if not idx_files:
            return
        if not db_file.exists():
            self.warnings.append(
                "[DOC INDEX] Missing hs_dev_docs/_00_project/_18_doc_index/doc_index.sqlite — "
                "run: python scripts/doc_index_db.py --root . rebuild"
            )
            return
        try:
            from doc_index_db import DocIndexDB

            target_root = self.docs_root.parent
            db = DocIndexDB(target_root)
            st = db.stats()
            db.close()
            if st.get("docs", 0) <= 0:
                self.warnings.append(
                    "[DOC INDEX] SQLite index is empty — run: python scripts/doc_index_db.py --root . rebuild"
                )
        except Exception as ex:
            self.warnings.append(f"[DOC INDEX] Unable to open SQLite cache: {ex}")

    def _check_workspace_hygiene(self):
        """检查工程多端目录卫生：散落二进制产物、配置隔离与 output 规约"""
        print("  -> Checking Workspace Hygiene & Output Directory Isolation...")
        # 1. 检查是否存在直接散落在根目录的安装包或二进制产物 (未收敛至 output/)
        stray_extensions = [".apk", ".aab", ".ipa", ".dmg", ".exe", ".AppImage"]
        for ext in stray_extensions:
            for stray in self.root.glob(f"*{ext}"):
                self.errors.append(
                    f"[ARTIFACT ERROR] Stray binary '{stray.name}' found at workspace root! "
                    f"Must be relocated into output/<platform> directory."
                )

        # 2. 检查敏感环境变量与配置隔离 (.env 存在但无 .env.example)
        dot_env = self.root / ".env"
        dot_env_example = self.root / "config" / ".env.example"
        if not dot_env_example.exists():
            dot_env_example = self.root / ".env.example"
        if dot_env.exists() and not dot_env_example.exists():
            self.warnings.append(
                "[CONFIG WARNING] Local .env exists but missing .env.example template in config/ or root!"
            )

    def _print_results(self) -> bool:
        print("\n" + "=" * 60)
        if self.warnings:
            print(f"[!] WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {w}")

        if self.strict and self.warnings:
            self.errors.append(
                f"[STRICT GATE ERROR] Strict mode enabled (Zero Warnings Policy): "
                f"{len(self.warnings)} warning(s) treated as blocking error(s)!"
            )

        if not self.errors:
            print("[PASS] All consistency and quality gate checks passed successfully! Ready for commit.")
            print("=" * 60)
            return True
        else:
            print(f"[FAIL] Quality gate check failed with {len(self.errors)} errors:")
            for e in self.errors:
                print(f"  {e}")
            print("=" * 60)
            return False


def main():
    parser = argparse.ArgumentParser(description="Skill Quality Gate & Triple-File Consistency Verifier")
    parser.add_argument("--root", default=".", help="Target workspace root")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Zero-warning mode: treat any warnings as blocking errors (Zero Warnings Policy)",
    )
    args = parser.parse_args()

    verifier = ConsistencyVerifier(args.root, strict=args.strict)
    success = verifier.check_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
