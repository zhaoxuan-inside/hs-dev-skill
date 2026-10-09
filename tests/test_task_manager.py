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
        self.temp_dir = tempfile.TemporaryDirectory()
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
            criteria="1. 单测100%覆盖"
        )
        self.assertEqual(res["status"], "READY")

        # 2. 校验三文件一致性
        verifier = ConsistencyVerifier(str(self.root))
        self.assertTrue(verifier.check_all())

        # 3. 流转状态为 IN_PROGRESS
        self.tm.set_status("order_create_test", "IN_PROGRESS")
        self.assertTrue(verifier.check_all())

        # 4. 流转为 COMPLETED (自动触发归档)
        self.tm.set_status("order_create_test", "COMPLETED")
        self.assertTrue(verifier.check_all())

    def test_session_handoff_creation(self):
        self.tm.create_task("task_002", "任务2")
        handoff_path = self.tm.create_session_handoff(
            task_id="task_002",
            checkpoint_desc="正在编写 V1.0.0__init_order.sql",
            completed_steps=["完成接口设计"],
            remaining_steps=["执行 DB 迁移", "编写单元测试"]
        )
        self.assertTrue(os.path.exists(handoff_path))


if __name__ == "__main__":
    unittest.main()
