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


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir.name)
        init_full_workspace(str(self.root))
        self.tm = TaskManager(str(self.root))

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_acceptance_record(self, task_id):
        path = self.root / "hs_dev_docs/_06_dev_process" / f"{task_id}_acceptance.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "schema_version": 1, "task_id": task_id, "acceptance_status": "ACCEPTED",
            "developer_confirmation": {"decision": "ACCEPTED", "reviewer": "developer",
                "confirmed_at": "2026-10-15T12:00:00Z", "source": "test conversation",
                "excerpt": "Confirmed acceptance for this task"},
            "verification": {"tests": [{"command": "make test", "exit_code": 0, "evidence": "test output"}]},
            "checks": [{"rule_id": "DELIV-01", "result": "PASS", "evidence": "test report"}],
            "dod": [{"criterion": "Task acceptance criterion", "result": "PASS", "evidence": "test report"}],
            "unimplemented": [],
        }
        path.write_text("<!-- HS_ACCEPTANCE_GATE_V1\n" + json.dumps(record) + "\nHS_ACCEPTANCE_GATE_V1 -->\n", encoding="utf-8")
        return str(path.relative_to(self.root))

    def test_task_lifecycle_and_triple_file_consistency(self):
        # 1. 创建任务
        res = self.tm.create_task(
            task_id="order_create_test",
            title="实现订单创建服务",
            owner="developer",
            priority="P0",
            goal="完成核心六元组订单创建与补偿逻辑",
            criteria="1. 单测100%覆盖",
            change_size="L",
        )
        self.assertEqual(res["status"], "READY")
        self.assertEqual(res["change_size"], "L")

        detail = Path(res["detail_path"]).read_text(encoding="utf-8")
        self.assertIn("**变更分级**：`L`", detail)
        pack = Path(res["context_pack_path"]).read_text(encoding="utf-8")
        self.assertIn("**change_size**：`L`", pack)

        # 2. 校验三文件一致性
        verifier = ConsistencyVerifier(str(self.root))
        self.assertTrue(verifier.check_all())
        self.assertFalse(
            any("RIGHT-SIZING" in w for w in verifier.warnings),
            msg=verifier.warnings,
        )

        # 3. 合法迁移：READY → IN_PROGRESS → VERIFYING → COMPLETED
        self.tm.set_status("order_create_test", "IN_PROGRESS")
        self.assertTrue(verifier.check_all())
        self.tm.set_status("order_create_test", "VERIFYING")
        record = self.write_acceptance_record("order_create_test")
        self.tm.set_status("order_create_test", "COMPLETED", acceptance_record=record)
        self.assertTrue(verifier.check_all())

        plan = self.root / "hs_dev_docs/_06_dev_process/_01_plan_log/order_create_test_plan.md"
        if not plan.exists():
            plan = self.root / "hs_dev_docs/_06_dev_process/_01_plan_log/order_create_test_plan.md"
        self.assertTrue(plan.exists())

    def test_illegal_transition_rejected(self):
        self.tm.create_task("t_illegal", "非法迁移", change_size="S")
        with self.assertRaises(ValueError):
            self.tm.set_status("t_illegal", "COMPLETED")
        # 日常禁止 force 跳步以外：force 仅用于终态重开
        self.tm.set_status("t_illegal", "IN_PROGRESS")
        self.tm.set_status("t_illegal", "VERIFYING")
        with self.assertRaisesRegex(ValueError, "force cannot bypass"):
            self.tm.set_status("t_illegal", "COMPLETED", force=True)
        record = self.write_acceptance_record("t_illegal")
        self.tm.set_status("t_illegal", "COMPLETED", acceptance_record=record)
        self.tm.set_status("t_illegal", "IN_PROGRESS", force=True)

    def test_completed_requires_closed_acceptance_record(self):
        self.tm.create_task("t_gate", "完成门禁")
        self.tm.set_status("t_gate", "IN_PROGRESS")
        self.tm.set_status("t_gate", "VERIFYING")
        with self.assertRaisesRegex(ValueError, "acceptance-record"):
            self.tm.set_status("t_gate", "COMPLETED")

        record = self.write_acceptance_record("t_gate")
        record_path = self.root / record
        record_path.write_text(
            record_path.read_text(encoding="utf-8").replace('"result": "PASS"', '"result": "PENDING"', 1),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "not closed"):
            self.tm.set_status("t_gate", "COMPLETED", acceptance_record=record)

        record_path.write_text(
            record_path.read_text(encoding="utf-8").replace('"result": "PENDING"', '"result": "PASS"', 1),
            encoding="utf-8",
        )
        self.tm.set_status("t_gate", "COMPLETED", acceptance_record=record)

    def test_create_defaults_change_size_m(self):
        res = self.tm.create_task("task_size_default", "默认分级")
        self.assertEqual(res["change_size"], "M")
        brief_dir = self.root / "hs_dev_docs/_05_task_orchestration/_01_task_brief"
        if not brief_dir.exists():
            brief_dir = self.root / "hs_dev_docs/_05_task_orchestration/_01_task_brief"
        brief_text = "\n".join(p.read_text(encoding="utf-8") for p in brief_dir.glob("*.md"))
        self.assertIn("**change_size**：`M`", brief_text)

    def test_missing_change_size_warns(self):
        res = self.tm.create_task("task_legacy_size", "旧任务模拟", change_size="S")
        detail = Path(res["detail_path"])
        text = detail.read_text(encoding="utf-8")
        detail.write_text(text.replace("- **变更分级**：`S`\n", ""), encoding="utf-8")
        pack = Path(res["context_pack_path"])
        pack.write_text(
            pack.read_text(encoding="utf-8").replace("- **change_size**：`S`\n", ""),
            encoding="utf-8",
        )
        # 模拟「旧任务缺分级」时内容已改过：同步 digest，门禁应仅 warning 不 fail
        from idx_manager import IdxManager

        idx_path = self.root / "hs_dev_docs/_05_task_orchestration/_00_task.idx"
        if not idx_path.exists():
            idx_path = self.root / "hs_dev_docs/_05_task_orchestration/_00_task.idx"
        IdxManager(str(idx_path)).update_digest()
        verifier = ConsistencyVerifier(str(self.root))
        self.assertTrue(verifier.check_all())
        self.assertTrue(any("RIGHT-SIZING" in w and "task_legacy_size" in w for w in verifier.warnings))

    def test_session_handoff_creation(self):
        self.tm.create_task("task_002", "任务2", change_size="S")
        handoff_path = self.tm.create_session_handoff(
            task_id="task_002",
            checkpoint_desc="正在编写 V1.0.0__init_order.sql",
            completed_steps=["完成接口设计"],
            remaining_steps=["执行 DB 迁移", "编写单元测试"]
        )
        self.assertTrue(os.path.exists(handoff_path))

    def test_render_dashboard(self):
        self.tm.create_task("task_dash_1", "看板测试任务", change_size="M")
        dash_md = self.tm.render_dashboard(intent="BUILD", phase="3", change_size="M")
        self.assertIn("实时执行看板", dash_md)
        self.assertIn("```mermaid", dash_md)
        self.assertIn("task_dash_1", dash_md)
        self.assertIn("Phase 3: 阶段 3: 契约六元组", dash_md)

        # Output to file test
        out_file = self.root / "dashboard.md"
        self.tm.render_dashboard(intent="BUILD", phase="2", output_path=str(out_file))
        self.assertTrue(out_file.exists())
        self.assertIn("Phase 2", out_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
