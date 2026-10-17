import io
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from skill_update import check_update, extract_bundle, install_local, parse_release_version, read_version


class TestSkillUpdate(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = Path(__file__).resolve().parent.parent

    def copy_bundle(self, name, version):
        destination = self.root / name
        destination.mkdir()
        for entry in ("SKILL.md", "skills", "scripts", "references", "resources"):
            original = self.bundle / entry
            if original.is_dir():
                shutil.copytree(original, destination / entry, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(original, destination / entry)
        current = read_version(destination)
        skill = destination / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace(current, version), encoding="utf-8")
        registry = destination / "resources/skill_routes.json"
        data = json.loads(registry.read_text(encoding="utf-8"))
        data["bundle_version"] = version
        registry.write_text(json.dumps(data), encoding="utf-8")
        return destination

    def release(self, version):
        return {"tag_name": "v" + version, "draft": False, "prerelease": False,
                "html_url": "https://github.com/zhaoxuan-inside/hs-dev-skill/releases/tag/v" + version,
                "assets": []}

    def test_numeric_release_order_and_prompt_without_mutation(self):
        self.assertGreater(parse_release_version("v4.10.0.0"), parse_release_version("4.9.9.9"))
        bundle = self.copy_bundle("installed", "4.9.0.0")
        before = (bundle / "SKILL.md").read_bytes()
        with patch("skill_update.fetch_release", return_value=self.release("4.10.0.0")):
            result = check_update(bundle)
        self.assertTrue(result["update_available"])
        self.assertEqual(result["status"], "update_available")
        self.assertIn("4.10.0.0", result["message"])
        self.assertEqual(before, (bundle / "SKILL.md").read_bytes())

    def test_ahead_offline_and_prerelease_do_not_claim_new_stable_release(self):
        bundle = self.copy_bundle("installed", "4.2.0.0")
        with patch("skill_update.fetch_release", return_value=self.release("4.1.0.0")):
            self.assertEqual(check_update(bundle)["status"], "ahead")
        with patch("skill_update.fetch_release", side_effect=OSError("offline")):
            result = check_update(bundle)
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["update_available"])
        release = self.release("4.3.0.0")
        release["prerelease"] = True
        with patch("skill_update.fetch_release", return_value=release):
            self.assertEqual(check_update(bundle)["status"], "unavailable")
        with self.assertRaises(ValueError):
            parse_release_version("v4.2.0.0-rc.1")

    def test_source_checkout_prompt_uses_git_instead_of_overwrite_command(self):
        bundle = self.copy_bundle("checkout", "4.1.0.0")
        (bundle / ".git").mkdir()
        with patch("skill_update.fetch_release", return_value=self.release("4.2.0.0")):
            result = check_update(bundle)
        self.assertEqual(result["update_method"], "git")
        self.assertEqual(result["update_command"], ["git", "-C", str(bundle), "pull", "--ff-only"])

    def test_full_local_update_removes_obsolete_files_and_validates_version(self):
        source = self.copy_bundle("source", "4.2.0.0")
        target = self.copy_bundle("installed", "4.1.0.0")
        (target / "obsolete.txt").write_text("old", encoding="utf-8")
        result = install_local(source, target)
        self.assertEqual(result["status"], "updated")
        self.assertEqual(read_version(target), "4.2.0.0")
        self.assertTrue((target / "scripts/baseline_gate.py").is_file())
        self.assertFalse((target / "obsolete.txt").exists())

    def test_invalid_bundle_and_failed_swap_leave_original_install_intact(self):
        source = self.copy_bundle("source", "4.2.0.0")
        target = self.copy_bundle("installed", "4.1.0.0")
        original = (target / "SKILL.md").read_bytes()
        with patch("skill_update.validate_bundle", side_effect=[None, None, OSError("post-swap validation failed")]):
            with self.assertRaises(OSError):
                install_local(source, target)
        self.assertEqual((target / "SKILL.md").read_bytes(), original)

    def test_checksum_failure_never_changes_installation(self):
        from skill_update import install_release
        target = self.copy_bundle("installed", "4.1.0.0")
        release = self.release("4.2.0.0")
        prefix = "https://github.com/zhaoxuan-inside/hs-dev-skill/releases/download/v4.2.0.0/"
        filename = "hs-dev-skill-v4.2.0.0.zip"
        release["assets"] = [{"name": name, "browser_download_url": prefix + name} for name in (filename, "SHA256SUMS")]
        checksums = ("0" * 64 + "  " + filename + "\n").encode("utf-8")
        with patch("skill_update.fetch_release", return_value=release), patch("skill_update.fetch_bytes", side_effect=[checksums, b"wrong archive"]):
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                install_release(target)
        self.assertEqual(read_version(target), "4.1.0.0")

    def test_same_version_repair_is_explicit(self):
        source = self.copy_bundle("source", "4.2.0.0")
        target = self.copy_bundle("installed", "4.2.0.0")
        original = (target / "SKILL.md").read_bytes()
        (target / "skills/hs-dev-discovery/SKILL.md").unlink()
        with self.assertRaises(ValueError):
            install_local(source, target)
        self.assertEqual(install_local(source, target, reinstall=True)["status"], "updated")
        self.assertTrue((target / "skills/hs-dev-discovery/SKILL.md").is_file())
        (source / "skills/hs-dev-discovery/SKILL.md").unlink()
        with self.assertRaises(ValueError):
            install_local(source, target)
        self.assertEqual((target / "SKILL.md").read_bytes(), original)

    def test_online_update_checks_digest_and_installs_whole_bundle(self):
        from skill_update import install_release
        source = self.copy_bundle("source", "4.2.0.0")
        target = self.copy_bundle("installed", "4.1.0.0")
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in source.rglob("*"):
                if path.is_file():
                    archive.write(path, "hs-dev-skill/" + path.relative_to(source).as_posix())
        data = stream.getvalue()
        release = self.release("4.2.0.0")
        prefix = "https://github.com/zhaoxuan-inside/hs-dev-skill/releases/download/v4.2.0.0/"
        filename = "hs-dev-skill-v4.2.0.0.zip"
        release["assets"] = [{"name": name, "browser_download_url": prefix + name} for name in (filename, "SHA256SUMS")]
        checksum = (hashlib.sha256(data).hexdigest() + "  " + filename + "\n").encode("utf-8")
        with patch("skill_update.fetch_release", return_value=release), patch("skill_update.fetch_bytes", side_effect=[checksum, data]):
            self.assertEqual(install_release(target)["status"], "updated")
        self.assertEqual(read_version(target), "4.2.0.0")
        self.assertTrue((target / "skills/hs-dev-discovery/SKILL.md").is_file())

    def test_worktree_symlink_and_downgrade_are_protected(self):
        source = self.copy_bundle("source", "4.1.0.0")
        target = self.copy_bundle("installed", "4.2.0.0")
        with self.assertRaisesRegex(ValueError, "downgrade"):
            install_local(source, target)
        (target / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "Git"):
            install_local(source, target)
        link = self.root / "linked"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            install_local(source, link)

    def test_zip_rejects_escape_symlink_and_duplicate_members(self):
        for name, mode in (("../escape", None), ("hs-dev-skill/../../escape", None),
                           ("hs-dev-skill/link", 0o120777 << 16), ("hs-dev-skill/C:/escape", None)):
            with self.subTest(name=name):
                stream = io.BytesIO()
                with zipfile.ZipFile(stream, "w") as archive:
                    info = zipfile.ZipInfo(name)
                    if mode:
                        info.external_attr = mode
                    archive.writestr(info, "bad")
                with self.assertRaises(ValueError):
                    extract_bundle(stream.getvalue(), self.root / "extract")
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("hs-dev-skill/a", "one")
            archive.writestr("hs-dev-skill/A", "two")
        with self.assertRaises(ValueError):
            extract_bundle(stream.getvalue(), self.root / "duplicate")


if __name__ == "__main__":
    unittest.main()
