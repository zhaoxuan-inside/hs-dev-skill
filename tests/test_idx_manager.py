import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from idx_manager import IdxManager, calculate_digest


class TestIdxManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.temp_dir.name)
        self.idx_file = self.dir_path / "_00_test.idx"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_and_add_entry(self):
        mgr = IdxManager(str(self.idx_file))
        mgr.init_idx("test_cat", "test_root")

        # 创建目标被索引文件
        target_file = self.dir_path / "item1.md"
        target_file.write_text("# Item 1 content", encoding="utf-8")

        entry = mgr.add_entry("item_1", "Item 1 Title", "item1.md")
        self.assertEqual(entry["id"], "item_1")
        self.assertIn("digest", entry)

        # 重新加载验证
        mgr2 = IdxManager(str(self.idx_file))
        self.assertEqual(len(mgr2.entries), 1)
        self.assertEqual(mgr2.entries[0]["id"], "item_1")

    def test_verify_valid_and_drift(self):
        mgr = IdxManager(str(self.idx_file))
        mgr.init_idx("test_cat", "test_root")

        target_file = self.dir_path / "doc.md"
        target_file.write_text("initial content", encoding="utf-8")

        mgr.add_entry("doc_1", "Doc 1", "doc.md")

        # 初始验证应当 PASS
        valid, errors = mgr.verify()
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

        # 修改内容引发漂移
        target_file.write_text("modified content", encoding="utf-8")
        valid, errors = mgr.verify()
        self.assertFalse(valid)
        self.assertTrue(any("digest mismatch" in e for e in errors))

        # 更新 digest 后重新验证应当 PASS
        mgr.update_digest()
        valid, errors = mgr.verify()
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
