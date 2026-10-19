"""Exercise complete bundles and host entry points after directory relocation."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hs_dev.bundle import validate
from hs_dev.support.update import install


ROOT = Path(__file__).resolve().parents[3]


class LayoutTests(unittest.TestCase):
    def test_installed_bundle_can_initialize_connect_and_update(self):
        self.assertTrue(validate(ROOT)["ok"], validate(ROOT))
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target, project = base / "installed", base / "project"
            project.mkdir()
            for _ in range(2):
                self.assertTrue(install(ROOT, target)["ok"])
                self.assertTrue(validate(target)["ok"])
                self.assertTrue((target / "hs-dev-skill/references/workflow/README.md").is_file())
            entry = target / "hs-dev-skill/scripts/hs_dev.py"
            for command in ("init", "connect"):
                result = subprocess.run(
                    [sys.executable, str(entry), "--root", str(project),
                     "--output", "json", command], cwd=base,
                    capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)["result"]
                if command == "connect":
                    self.assertTrue(payload["ok"])
                else:
                    self.assertIn("generation", payload)
            instructions = (project / "AGENTS.md").read_text()
            self.assertIn(str(entry), instructions)
            self.assertIn(str(target / "SKILL.md"), instructions)


if __name__ == "__main__":
    unittest.main()
