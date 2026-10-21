"""Release archives match validated Skill directories and published checksums."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_release import release
from hs_dev import __version__


class ReleaseTests(unittest.TestCase):
    def test_complete_installable_assets_and_checksums(self):
        root = Path(__file__).resolve().parents[3]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            result = release(root, output, __version__)
            self.assertEqual(result["packages"], 32)
            self.assertEqual(len(list(output.glob("*.zip"))), 33)
            self.assertEqual(len(json.loads((output / "catalog.json").read_text())["skills"]), 32)
            for line in (output / "SHA256SUMS").read_text().splitlines():
                checksum, name = line.split("  ", 1)
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), checksum)
            with zipfile.ZipFile(output / f"hs-dev-skill-v{__version__}.zip") as archive:
                self.assertIn("hs-dev-skill/SKILL.md", archive.namelist())
                self.assertIn("hs-dev-skill/scripts/hs_dev/support/trace_graph.py", archive.namelist())
                self.assertFalse(any("__pycache__" in name for name in archive.namelist()))
                self.assertNotIn("hs-dev-skill/scripts/build_release.py", archive.namelist())
            with zipfile.ZipFile(output / f"hs-dev-trace-v{__version__}.zip") as archive:
                self.assertIn("hs-dev-trace/SKILL.md", archive.namelist())
            with self.assertRaises(ValueError):
                release(root, output, __version__)

    def test_invalid_release_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                release(Path(temporary), Path(temporary) / "assets", "../version")
