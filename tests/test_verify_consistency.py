import os
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from init_hs_dev_docs import init_full_workspace
from verify_consistency import ConsistencyVerifier


class TestVerifyConsistency(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        init_full_workspace(str(self.root))
        self.verifier = ConsistencyVerifier(str(self.root))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_clean_workspace_passes(self):
        self.assertTrue(self.verifier.check_all())

    def test_detect_missing_undo_migration(self):
        # 创建一个缺少 U 脚本的迁移
        mig_dir = self.root / "hs_dev_docs/_04_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1.0.0__create_order.sql").write_text("CREATE TABLE orders (id BIGINT);", encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("missing corresponding rollback script" in e for e in self.verifier.errors))

        # 补齐 U 脚本后应当通过
        (mig_dir / "U1.0.0__create_order.sql").write_text("DROP TABLE orders;", encoding="utf-8")
        self.assertTrue(self.verifier.check_all())

    def test_detect_sql_reserved_keyword(self):
        mig_dir = self.root / "hs_dev_docs/_04_db_schema/_01_order/migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        (mig_dir / "V1.0.0__create_order.sql").write_text("CREATE TABLE orders (id BIGINT, desc VARCHAR(255));", encoding="utf-8")
        (mig_dir / "U1.0.0__create_order.sql").write_text("DROP TABLE orders;", encoding="utf-8")

        self.assertFalse(self.verifier.check_all())
        self.assertTrue(any("forbidden SQL reserved keyword 'desc'" in e for e in self.verifier.errors))


if __name__ == "__main__":
    unittest.main()
