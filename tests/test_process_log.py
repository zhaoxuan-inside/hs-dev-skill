import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from init_hs_dev_docs import init_full_workspace
from process_log import checkpoint, ensure_plan, read_changes, resume_scan, rollback
from task_manager import TaskManager


class TestProcessLog(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir.name)
        init_full_workspace(str(self.root))
        self.tm = TaskManager(str(self.root))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_checkpoint_and_rollback_restores_file(self):
        self.tm.create_task("pay_1", "支付", change_size="M")
        target = self.root / "backend" / "demo.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("v1\n", encoding="utf-8")

        cp1 = checkpoint(
            self.root, "pay_1", "S2", "before edit", ["backend/demo.py"]
        )
        target.write_text("v2\n", encoding="utf-8")
        checkpoint(
            self.root, "pay_1", "S2", "second edit", ["backend/demo.py"]
        )
        target.write_text("v3\n", encoding="utf-8")

        result = rollback(self.root, "pay_1", cp1["checkpoint_id"])
        self.assertTrue(result["ok"])
        self.assertEqual(target.read_text(encoding="utf-8"), "v1\n")
        changes = read_changes(self.root, "pay_1")
        self.assertTrue(any(c.get("rollback_of") == cp1["checkpoint_id"] for c in changes))

    def test_resume_scan_lists_active(self):
        self.tm.create_task("r1", "续做扫描", change_size="S")
        self.tm.set_status("r1", "IN_PROGRESS")
        scan = resume_scan(self.root)
        self.assertEqual(scan["count"], 1)
        self.assertEqual(scan["tasks"][0]["task_id"], "r1")
        self.assertTrue(scan["tasks"][0]["plan_exists"])

    def test_rollback_deletes_created_file_and_reopens_completed(self):
        self.tm.create_task("pay_new", "新建文件回退", change_size="S")
        self.tm.set_status("pay_new", "IN_PROGRESS")
        created = self.root / "backend" / "brand_new.py"
        cp = checkpoint(
            self.root, "pay_new", "S2", "will create", ["backend/brand_new.py"]
        )
        created.parent.mkdir(parents=True, exist_ok=True)
        created.write_text("new\n", encoding="utf-8")
        self.tm.set_status("pay_new", "VERIFYING")
        self.tm.set_status("pay_new", "COMPLETED")

        result = rollback(self.root, "pay_new", cp["checkpoint_id"])
        self.assertTrue(result["ok"])
        self.assertFalse(created.exists())
        idx = self.root / "hs_dev_docs/_05_task_orchestration/_00_task.idx"
        if not idx.exists():
            idx = self.root / "hs_dev_docs/_08_dev_process/_09_task/_00_task.idx"
        self.assertIn("pay_new", idx.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
