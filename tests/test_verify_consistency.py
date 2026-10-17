import os
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from init_hs_dev_docs import init_full_workspace
from task_manager import TaskManager
from verify_consistency import ConsistencyVerifier


class TestVerifyConsistency(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir.name)
        init_full_workspace(str(self.root))
        self.verifier = ConsistencyVerifier(str(self.root))

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_acceptance_record(self, task_id):
        env_example = self.root / "config/.env.example"
        env_example.parent.mkdir(parents=True, exist_ok=True)
        if not env_example.exists():
            env_example.write_text("# test environment template\n", encoding="utf-8")
        path = self.root / "hs_dev_docs/_06_dev_process" / f"{task_id}_acceptance.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "schema_version": 1, "task_id": task_id, "acceptance_status": "ACCEPTED",
            "developer_confirmation": {"decision": "ACCEPTED", "reviewer": "developer",
                "confirmed_at": "2026-10-15T12:00:00Z", "source": "test conversation",
                "excerpt": "Confirmed acceptance for this task"},
            "verification": {"tests": [{"command": "make test", "exit_code": 0, "evidence": "test output"}]},
            "checks": [{"rule_id": "DELIV-01", "result": "PASS", "evidence": "test report"}],
            "dod": [{"criterion": "All task REQ items verified", "result": "PASS", "evidence": "task detail matrix"}],
            "unimplemented": [],
        }
        from acceptance_fixture import bind_acceptance
        bind_acceptance(self.root, task_id, record, ["REQ-001", "REQ-002"])
        path.write_text("<!-- HS_ACCEPTANCE_GATE_V1\n" + json.dumps(record) + "\nHS_ACCEPTANCE_GATE_V1 -->\n", encoding="utf-8")
        return str(path.relative_to(self.root))

    def test_clean_workspace_passes(self):
        self.assertTrue(self.verifier.check_all())

    def test_detect_missing_undo_migration(self):
        # 创建一个缺少 U 脚本的迁移
        mig_dir = self.root / "hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1.0.0__create_order.sql").write_text("CREATE TABLE orders (id BIGINT);", encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("missing corresponding rollback script" in e for e in self.verifier.errors))

        # 补齐 U 脚本后应当通过
        (mig_dir / "U1.0.0__create_order.sql").write_text("DROP TABLE orders;", encoding="utf-8")
        self.assertTrue(self.verifier.check_all())

    def test_detect_sql_reserved_keyword(self):
        mig_dir = self.root / "hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1.0.0__create_order.sql").write_text("CREATE TABLE orders (id BIGINT, desc VARCHAR(255));", encoding="utf-8")
        (mig_dir / "U1.0.0__create_order.sql").write_text("DROP TABLE orders;", encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("forbidden SQL reserved keyword 'desc'" in e for e in self.verifier.errors))

    def test_detect_skill_version_mismatch(self):
        skill_file = self.root / "SKILL.md"
        readme_file = self.root / "README.md"
        
        # 1. Body version mismatch with metadata
        skill_file.write_text(
            "---\nmetadata:\n  version: \"2.22\"\n---\n# hs-dev-skill\n版本：v2.21\n",
            encoding="utf-8",
        )
        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[SKILL VERSION MISMATCH]" in e for e in self.verifier.errors))

        # 2. README badge mismatch
        skill_file.write_text(
            "---\nmetadata:\n  version: \"2.22\"\n---\n# hs-dev-skill\n版本：v2.22\n",
            encoding="utf-8",
        )
        readme_file.write_text(
            "[![Spec Version](https://img.shields.io/badge/skill-v2.20-blue.svg)](SKILL.md)\n",
            encoding="utf-8",
        )
        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[SKILL VERSION MISMATCH]" in e for e in self.verifier.errors))

        # 3. All matching -> pass
        readme_file.write_text(
            "[![Spec Version](https://img.shields.io/badge/skill-v2.22-blue.svg)](SKILL.md)\n",
            encoding="utf-8",
        )
        self.assertTrue(self.verifier.check_all())

    def test_detect_migration_format_error(self):
        mig_dir = self.root / "hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "Vinvalid_format.sql").write_text("CREATE TABLE orders (id BIGINT);", encoding="utf-8")
        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[DB MIGRATION FORMAT ERROR]" in e for e in self.verifier.errors))

    def test_detect_stray_artifacts(self):
        # 模拟在项目根目录下散落未收敛的安装包
        stray_apk = self.root / "app-release.apk"
        stray_apk.write_bytes(b"dummy apk content")
        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[ARTIFACT ERROR]" in e for e in self.verifier.errors))

        # 移除散落安装包后恢复通过
        stray_apk.unlink()
        self.assertTrue(self.verifier.check_all())

    def test_strict_mode_blocks_warnings(self):
        # 产生一个 warning: 存在 .env 但无 .env.example
        env_example = self.root / "config" / ".env.example"
        if env_example.exists():
            env_example.unlink()
        dot_env = self.root / ".env"
        dot_env.write_text("SECRET=123\n", encoding="utf-8")
        
        # 默认模式下仅产生 warning，返回 True
        default_verifier = ConsistencyVerifier(str(self.root), strict=False)
        self.assertTrue(default_verifier.check_all())
        self.assertTrue(len(default_verifier.warnings) > 0)

        # strict 模式下（零告警策略），warning 升级为 blocking error，返回 False
        strict_verifier = ConsistencyVerifier(str(self.root), strict=True)
        self.assertFalse(strict_verifier.check_all())
        self.assertTrue(any("[STRICT GATE ERROR]" in e for e in strict_verifier.errors))

    def test_detect_forbidden_alias(self):
        # 写入一个包含禁用别名 'bill_order' 的 DB 迁移文件
        mig_dir = self.root / "hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1.0.0__create_order.sql").write_text("CREATE TABLE bill_order (id BIGINT);", encoding="utf-8")
        (mig_dir / "U1.0.0__create_order.sql").write_text("DROP TABLE bill_order;", encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[TERMINOLOGY ERROR]" in e and "bill_order" in e for e in self.verifier.errors))

        # 修复为合法名称 'orders' 后通过
        (mig_dir / "V1.0.0__create_order.sql").write_text("CREATE TABLE orders (id BIGINT);", encoding="utf-8")
        (mig_dir / "U1.0.0__create_order.sql").write_text("DROP TABLE orders;", encoding="utf-8")
        self.assertTrue(self.verifier.check_all())

    def test_detect_event_grammar_drift(self):
        # 在 backend 源码中使用了动词原形作为事件 topic: 'order.update'
        backend_dir = self.root / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        code_file = backend_dir / "order_events.py"
        code_file.write_text('ORDER_EVENT = "order.update"\n', encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[EVENT GRAMMAR ERROR]" in e and "order.update" in e for e in self.verifier.errors))

        # 纠正为过去分词 'order.updated'
        code_file.write_text('ORDER_EVENT = "order.updated"\n', encoding="utf-8")
        self.assertTrue(self.verifier.check_all())

    def test_detect_event_grammar_timestamp(self):
        # 在 backend 源码中将时间戳字段误用为事件 topic: 'order.updated_at'
        backend_dir = self.root / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        code_file = backend_dir / "order_events.py"
        code_file.write_text('ORDER_EVENT = "order.updated_at"\n', encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[EVENT GRAMMAR ERROR]" in e and "order.updated_at" in e for e in self.verifier.errors))

        code_file.unlink()
        self.assertTrue(self.verifier.check_all())

    def test_four_segment_version_and_migrations(self):
        # 1. 验证四段式 Skill 版本匹配
        skill_file = self.root / "SKILL.md"
        readme_file = self.root / "README.md"
        skill_file.write_text(
            "---\nmetadata:\n  version: \"2.41.0.0\"\n---\n# hs-dev-skill\n版本：v2.41.0.0\n",
            encoding="utf-8",
        )
        readme_file.write_text(
            "[![Spec Version](https://img.shields.io/badge/skill-v2.41.0.0-blue.svg)](SKILL.md)\n",
            encoding="utf-8",
        )
        self.assertTrue(self.verifier.check_all())

        # 2. 验证四段式 DB 迁移脚本格式
        mig_dir = self.root / "hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1.2.3.10__create_build_logs.sql").write_text(
            "CREATE TABLE build_logs (id BIGINT, build_no INT);", encoding="utf-8"
        )
        (mig_dir / "U1.2.3.10__create_build_logs.sql").write_text(
            "DROP TABLE build_logs;", encoding="utf-8"
        )
        self.assertTrue(self.verifier.check_all())

    def test_detect_secret_leak(self):
        backend_dir = self.root / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        secret_file = backend_dir / "api_client.py"
        # 写入假密钥触发检测
        secret_file.write_text(
            'API_KEY = "sk-abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLM"\n',
            encoding="utf-8",
        )
        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("[SECRET LEAK ERROR]" in e for e in self.verifier.errors))

        # 修复为从环境变量读取后通过
        secret_file.write_text(
            'import os\nAPI_KEY = os.environ.get("OPENAI_API_KEY", "")\n',
            encoding="utf-8",
        )
        self.assertTrue(self.verifier.check_all())

    def test_detect_missing_lockfile(self):
        frontend_dir = self.root / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        pkg_json = frontend_dir / "package.json"
        pkg_json.write_text('{"name": "test-app", "version": "1.0.0"}\n', encoding="utf-8")

        # 无 lockfile 时应产生供应链警告
        verifier = ConsistencyVerifier(str(self.root), strict=False)
        self.assertTrue(verifier.check_all())
        self.assertTrue(any("[SUPPLY CHAIN WARNING]" in w for w in verifier.warnings))

        # 补齐 package-lock.json 后警告消失
        (frontend_dir / "package-lock.json").write_text('{"lockfileVersion": 3}\n', encoding="utf-8")
        verifier_clean = ConsistencyVerifier(str(self.root), strict=False)
        self.assertTrue(verifier_clean.check_all())
        self.assertFalse(any("[SUPPLY CHAIN WARNING]" in w for w in verifier_clean.warnings))

    def test_detect_unverified_requirements_on_completed_task(self):
        tm = TaskManager(str(self.root))
        res = tm.create_task(
            task_id="req_gate_test",
            title="测试需求覆盖门禁",
            owner="developer",
            priority="P1",
            goal="验证 100% 需求覆盖率门禁",
            criteria="所有 REQ 必须 verified 才能 COMPLETED",
            change_size="M",
        )
        detail_path = Path(res["detail_path"])

        # 追加包含未验证需求的需求追踪矩阵
        req_table = (
            "\n### 2b. 需求追踪与覆盖矩阵 (Requirement Traceability Matrix)\n\n"
            "| 需求 ID | 需求描述 | 对应模块/步骤 | 验收证据 (测试用例 / 报告) | 状态 |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| `REQ-001` | 用户身份合法性校验 | Step 1 | `tests/test_auth.py::test_valid_user` | `verified` |\n"
            "| `REQ-002` | 余额扣减及防重试防超扣 | Step 2 | `tests/test_balance.py::test_deduct` | `pending` |\n"
        )
        detail_path.write_text(detail_path.read_text(encoding="utf-8") + req_table, encoding="utf-8")

        # 任务处于 IN_PROGRESS 时，未完成需求不阻断
        tm.set_status("req_gate_test", "IN_PROGRESS")
        self.assertTrue(self.verifier.check_all())

        # 任务推进到 VERIFYING
        tm.set_status("req_gate_test", "VERIFYING")
        self.assertTrue(self.verifier.check_all())

        # 任务推进到 COMPLETED 时，由于 REQ-002 处于 pending，归档前必须拦截
        acceptance_record = self.write_acceptance_record("req_gate_test")
        with self.assertRaisesRegex(ValueError, "REQ-002"):
            tm.set_status("req_gate_test", "COMPLETED", acceptance_record=acceptance_record)
        self.assertTrue(self.verifier.check_all())

        # 修复 REQ-002 为 verified
        repaired_content = detail_path.read_text(encoding="utf-8").replace("`pending`", "`verified`")
        detail_path.write_text(repaired_content, encoding="utf-8")
        from idx_manager import IdxManager
        IdxManager(str(self.root / "hs_dev_docs/_05_task_orchestration/_00_task.idx")).update_digest()
        IdxManager(str(self.root / "hs_dev_docs/_05_task_orchestration/_02_task_detail/_00_task_detail.idx")).update_digest()
        tm.set_status("req_gate_test", "COMPLETED", acceptance_record=acceptance_record)
        verifier_clean = ConsistencyVerifier(str(self.root))
        self.assertTrue(verifier_clean.check_all())


if __name__ == "__main__":
    unittest.main()

