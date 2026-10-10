import os
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

        # 3. 流转状态为 IN_PROGRESS
        self.tm.set_status("order_create_test", "IN_PROGRESS")
        self.assertTrue(verifier.check_all())

        # 4. 流转为 COMPLETED (自动触发归档)
        self.tm.set_status("order_create_test", "COMPLETED")
        self.assertTrue(verifier.check_all())

    def test_create_defaults_change_size_m(self):
        res = self.tm.create_task("task_size_default", "默认分级")
        self.assertEqual(res["change_size"], "M")
        brief_dir = self.root / "hs_dev_docs/_08_dev_process/_09_task/_01_task_brief"
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

        idx_path = self.root / "hs_dev_docs/_08_dev_process/_09_task/_00_task.idx"
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


if __name__ == "__main__":
    unittest.main()
