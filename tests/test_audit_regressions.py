import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from init_hs_dev_docs import init_full_workspace
from verify_consistency import ConsistencyVerifier
from fake_code_scanner import FakeCodeScanner
from idx_manager import IdxManager


class AuditRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def verify(self, **kwargs):
        verifier = ConsistencyVerifier(str(self.root), **kwargs)
        with contextlib.redirect_stdout(io.StringIO()):
            result = verifier.check_all()
        return result, verifier

    def test_incomplete_root_never_falls_back_to_demo(self):
        init_full_workspace(str(self.root / "demo_project"))
        (self.root / "hs_dev_docs").mkdir()
        result, verifier = self.verify()
        self.assertFalse(result)
        self.assertTrue(any("_00_hs_dev_docs.idx" in e for e in verifier.errors))
        self.assertEqual(verifier.docs_root, self.root / "hs_dev_docs")

    def test_explicit_demo_checks_package_and_demo(self):
        init_full_workspace(str(self.root / "demo_project"))
        self.assertTrue(self.verify(demo=True, strict=True)[0])

    def test_initialization_includes_qa_log(self):
        init_full_workspace(str(self.root))
        self.assertTrue((self.root / "hs_dev_docs/_06_dev_process/_03_qa_log").is_dir())

    def test_missing_rebuildable_cache_does_not_block_strict(self):
        init_full_workspace(str(self.root))
        (self.root / "hs_dev_docs/_00_project_foundation/_05_doc_index/doc_index.sqlite").unlink()
        self.assertTrue(self.verify(strict=True)[0])

    def test_fake_code_blocks_consistency_gate(self):
        init_full_workspace(str(self.root))
        (self.root / "backend/service.py").write_text("def handle():\n    pass\n", encoding="utf-8")
        result, verifier = self.verify()
        self.assertFalse(result)
        self.assertTrue(any("FAKE CODE" in e for e in verifier.errors))

    def test_source_strings_are_not_executable_assertions(self):
        (self.root / "src").mkdir()
        source = self.root / "src/example.py"
        source.write_text('example = "assert True"\nassert True\n', encoding="utf-8")
        hits = FakeCodeScanner(self.root).scan()
        self.assertEqual([(h["line"], h["category"]) for h in hits], [(2, "assert-true")])

    def test_ignored_comparison_clone_does_not_require_lockfile(self):
        init_full_workspace(str(self.root))
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / ".gitignore").write_text("local-clones/\n", encoding="utf-8")
        clone = self.root / "local-clones/vendor"
        clone.mkdir(parents=True)
        (clone / "package.json").write_text("{}", encoding="utf-8")
        self.assertTrue(self.verify(strict=True)[0])
        app = self.root / "frontend/package.json"
        app.write_text("{}", encoding="utf-8")
        self.assertFalse(self.verify(strict=True)[0])

    def test_rebuild_updates_child_before_parent_and_rejects_missing_target(self):
        docs = self.root / "hs_dev_docs"
        docs.mkdir()
        (docs / "leaf.md").write_text("before", encoding="utf-8")
        child = IdxManager(str(docs / "child.idx"))
        child.init_idx("child", "hs_dev_docs")
        child.add_entry("leaf", "Leaf", "leaf.md")
        parent = IdxManager(str(docs / "_00_hs_dev_docs.idx"))
        parent.init_idx("root", "hs_dev_docs")
        parent.add_entry("child", "Child", "child.idx")
        (docs / "leaf.md").write_text("after", encoding="utf-8")
        command = [sys.executable, str(ROOT / "scripts/idx_manager.py"), "rebuild", "--root", str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(IdxManager(str(parent.idx_file_path)).verify()[0])
        self.assertTrue(IdxManager(str(child.idx_file_path)).verify()[0])
        (docs / "leaf.md").unlink()
        self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_rebuild_cycle_fails_without_rewriting_indices(self):
        from idx_manager import rebuild_indices
        docs = self.root / "hs_dev_docs"
        docs.mkdir()
        first = IdxManager(str(docs / "first.idx"))
        second = IdxManager(str(docs / "second.idx"))
        first.init_idx("first", "hs_dev_docs")
        second.init_idx("second", "hs_dev_docs")
        first.add_entry("second", "Second", "second.idx")
        second.add_entry("first", "First", "first.idx")
        before = {p: p.read_bytes() for p in docs.glob("*.idx")}
        with self.assertRaisesRegex(ValueError, "Cyclic index"):
            rebuild_indices(self.root)
        self.assertEqual(before, {p: p.read_bytes() for p in docs.glob("*.idx")})

    def test_actual_legacy_directory_is_blocked(self):
        init_full_workspace(str(self.root))
        legacy = self.root / "hs_dev_docs/_08_dev_process"
        legacy.mkdir()
        result, verifier = self.verify()
        self.assertFalse(result)
        self.assertTrue(any("DEPRECATED PATH ERROR" in e for e in verifier.errors))

    def test_demo_mode_still_detects_legacy_package_docs(self):
        init_full_workspace(str(self.root / "demo_project"))
        (self.root / "hs_dev_docs/_08_dev_process").mkdir(parents=True)
        result, verifier = self.verify(demo=True)
        self.assertFalse(result)
        self.assertTrue(any("DEPRECATED PATH ERROR" in e for e in verifier.errors))
