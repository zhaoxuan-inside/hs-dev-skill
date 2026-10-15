#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import fake_code_scanner as fcs  # noqa: E402

CORPUS = Path(__file__).resolve().parent / "fixtures" / "fake_code_corpus"


class TestFakeCodeScanner(unittest.TestCase):
    @classmethod
    def scan_corpus(cls, code_dirs):
        return fcs.FakeCodeScanner(CORPUS, code_dirs=code_dirs).scan()

    def test_detects_every_category(self):
        findings = self.scan_corpus(["backend", "frontend"])
        categories = {f["category"] for f in findings}
        expected = {
            "marker-todo", "stub-not-implemented", "stub-empty-body",
            "test-skipped", "empty-catch", "assert-true", "mock-branch",
        }
        self.assertEqual(categories, expected)
        for f in findings:
            self.assertIn("path", f)
            self.assertGreater(f["line"], 0)
            self.assertNotEqual(f["snippet"].strip(), "")

    def test_python_findings_reported_at_correct_lines(self):
        findings = self.scan_corpus(["backend"])
        hits = {(f["path"], f["line"], f["category"]) for f in findings}
        self.assertIn(("backend/service.py", 5, "stub-empty-body"), hits)
        self.assertIn(("backend/service.py", 10, "stub-not-implemented"), hits)
        self.assertIn(("backend/service.py", 13, "stub-empty-body"), hits)
        self.assertIn(("backend/service.py", 17, "marker-todo"), hits)
        self.assertIn(("backend/service.py", 26, "empty-catch"), hits)
        self.assertIn(("backend/test_service.py", 5, "test-skipped"), hits)
        self.assertIn(("backend/test_service.py", 7, "assert-true"), hits)

    def test_frontend_findings_reported_at_correct_lines(self):
        findings = self.scan_corpus(["frontend"])
        hits = {(f["path"], f["line"], f["category"]) for f in findings}
        self.assertIn(("frontend/api.ts", 2, "mock-branch"), hits)
        self.assertIn(("frontend/api.ts", 5, "stub-not-implemented"), hits)
        self.assertIn(("frontend/api.ts", 13, "test-skipped"), hits)
        self.assertIn(("frontend/api.ts", 21, "empty-catch"), hits)

    def test_clean_sources_yield_zero_findings(self):
        # 覆盖：真实实现、abstractmethod/Protocol 接口桩、hs-allow 行内豁免、NotImplemented 捕获
        self.assertEqual(self.scan_corpus(["clean_src"]), [])

    def test_missing_code_dirs_yield_zero_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(fcs.FakeCodeScanner(tmp).scan(), [])

    def test_scan_root_helper(self):
        findings = fcs.scan_root(CORPUS, code_dirs=["frontend"])
        self.assertNotEqual(findings, [])

    def test_cli_blocks_by_default(self):
        argv = ["fake_code_scanner.py", "--root", str(CORPUS),
                "--code-dirs", "backend,frontend"]
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(fcs.main(), 1)

    def test_cli_warn_only_exits_zero(self):
        argv = ["fake_code_scanner.py", "--root", str(CORPUS),
                "--code-dirs", "frontend", "--warn-only"]
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(fcs.main(), 0)

    def test_cli_clean_root_passes(self):
        argv = ["fake_code_scanner.py", "--root", str(CORPUS),
                "--code-dirs", "clean_src"]
        with mock.patch.object(sys, "argv", argv):
            self.assertEqual(fcs.main(), 0)


if __name__ == "__main__":
    unittest.main()
