#!/usr/bin/env python3
"""
test_deprecated_paths.py
Unit tests to ensure no deprecated historical paths exist in references/ or resources/templates/.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from verify_consistency import ConsistencyVerifier


class TestDeprecatedPaths(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_no_deprecated_paths_in_repo(self):
        verifier = ConsistencyVerifier(str(self.root), strict=True)
        verifier._check_deprecated_paths()
        deprecated_errors = [e for e in verifier.errors if "[DEPRECATED PATH ERROR]" in e]
        self.assertEqual(
            len(deprecated_errors),
            0,
            f"Found deprecated legacy paths in repository:\n" + "\n".join(deprecated_errors)
        )


if __name__ == "__main__":
    unittest.main()
