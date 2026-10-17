import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from stage_review import inventory


class TestStageReview(unittest.TestCase):
    def test_resolves_project_paths_deduplicates_and_binds_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "设计 文档.md"
            document.write_text("first", encoding="utf-8")
            rows = inventory(root, [document.name, str(document), "./" + document.name])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["name"], document.name)
            self.assertEqual(rows[0]["path"], str(document.resolve()))
            self.assertEqual(rows[0]["sha256"], hashlib.sha256(b"first").hexdigest())
            document.write_text("changed", encoding="utf-8")
            self.assertNotEqual(rows[0]["sha256"], inventory(root, [document.name])[0]["sha256"])

    def test_missing_files_and_directories_are_visible_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = inventory(directory, ["missing.md", "."])
            self.assertEqual([row["status"] for row in rows], ["MISSING", "MISSING"])
            self.assertTrue(all(row["error"] for row in rows))

    def test_cli_from_other_cwd_keeps_missing_file_and_nonzero_exit(self):
        script = Path(__file__).resolve().parent.parent / "scripts" / "stage_review.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            root.mkdir()
            document = root / "review|文件.md"
            document.write_text("review", encoding="utf-8")
            command = [sys.executable, str(script), "--root", str(root), "--stage", "0B",
                       "--document", document.name]
            success = subprocess.run(command, cwd=directory, capture_output=True, text=True)
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertIn(str(root), success.stdout)
            self.assertIn("review&#124;文件.md", success.stdout)
            failure = subprocess.run(command + ["--document", "missing.md"], cwd=directory,
                                     capture_output=True, text=True)
            self.assertEqual(failure.returncode, 1)
            self.assertIn(str(root / "missing.md"), failure.stdout)
            self.assertIn("MISSING", failure.stdout)


if __name__ == "__main__":
    unittest.main()
