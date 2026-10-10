#!/usr/bin/env python3
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import hs_paths  # noqa: E402


class TestHsPaths(unittest.TestCase):
    def test_global_root_under_home(self):
        root = hs_paths.global_root()
        self.assertEqual(root, Path.home() / ".hs-dev-skill")
        self.assertTrue(str(root).startswith(str(Path.home())))

    def test_platform_id_known(self):
        pid = hs_paths.platform_id()
        self.assertIn(pid, {"windows", "linux", "macos", "other"})
        if sys.platform.startswith("win"):
            self.assertEqual(pid, "windows")
        elif sys.platform == "darwin":
            self.assertEqual(pid, "macos")
        elif sys.platform.startswith("linux"):
            self.assertEqual(pid, "linux")

    def test_display_contains_three_os_hints(self):
        info = hs_paths.global_root_display()
        self.assertIn("linux_macos", info)
        self.assertIn("windows_cmd", info)
        self.assertIn("windows_pwsh", info)
        self.assertIn(".hs-dev-skill", info["linux_macos"])
        self.assertIn(".hs-dev-skill", info["windows_cmd"])


if __name__ == "__main__":
    unittest.main()
