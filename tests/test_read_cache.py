import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import read_cache


class TestReadCache(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "规则.md"
        self.path.write_text("first\nsecond\nthird\n", encoding="utf-8")
        self.state = {"schema_version": 1, "entries": {}}

    def test_unchanged_fast_check_does_not_read_body(self):
        self.assertEqual(read_cache.inspect(self.state, self.path)["action"], "READ")
        read_cache.load(self.state, self.path)
        with patch.object(Path, "read_bytes", side_effect=AssertionError("body reread")):
            self.assertEqual(read_cache.inspect(self.state, self.path)["action"], "REUSE")

    def test_changed_file_stays_invalid_until_loaded(self):
        read_cache.load(self.state, self.path)
        self.path.write_text("changed\n", encoding="utf-8")
        for _ in range(2):
            self.assertEqual(read_cache.inspect(self.state, self.path)["action"], "RELOAD")
        self.assertEqual(read_cache.load(self.state, self.path)["text"], "changed\n")
        self.assertEqual(read_cache.inspect(self.state, self.path)["action"], "REUSE")

    def test_touch_without_content_change_does_not_require_model_reread(self):
        read_cache.load(self.state, self.path)
        stat = self.path.stat()
        os.utime(self.path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1000000000))
        self.assertEqual(read_cache.inspect(self.state, self.path)["action"], "REUSE")

    def test_strong_check_detects_change_even_with_identical_metadata(self):
        read_cache.load(self.state, self.path)
        entry = next(iter(self.state["entries"].values()))
        self.path.write_text("FIRST\nsecond\nthird\n", encoding="utf-8")
        with patch.object(read_cache, "stamp", return_value=entry["stamp"]):
            self.assertEqual(read_cache.inspect(self.state, self.path, verify=True)["action"], "RELOAD")

    def test_scope_and_context_are_independent_of_file_freshness(self):
        loaded = read_cache.load(self.state, self.path, 2, 2)
        self.assertEqual(loaded["text"], "second\n")
        self.assertEqual(read_cache.inspect(self.state, self.path, 2, 2)["action"], "REUSE")
        self.assertEqual(read_cache.inspect(self.state, self.path, 3, 3)["action"], "READ")
        self.assertEqual(read_cache.inspect(self.state, self.path, 2, 2,
                                          context_missing=True)["action"], "RESTORE_CONTEXT")

    def test_read_race_is_rejected(self):
        with patch.object(read_cache, "stamp", side_effect=[[1], [2]]):
            with self.assertRaises(ValueError):
                read_cache.load(self.state, self.path)
        self.assertFalse(self.state["entries"])

    def test_cli_check_is_readonly_and_missing_file_fails(self):
        script = Path(read_cache.__file__)
        state = self.root / "session.json"
        base = [sys.executable, str(script)]
        flags = ["--state", str(state), "--path", str(self.path)]
        result = subprocess.run(base + ["check"] + flags, capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["action"], "READ")
        self.assertFalse(state.exists())
        result = subprocess.run(base + ["load"] + flags, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)
        saved = state.read_bytes()
        result = subprocess.run(base + ["check"] + flags + ["--verify-content"],
                                capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout)["action"], "REUSE")
        self.assertEqual(saved, state.read_bytes())
        self.path.unlink()
        result = subprocess.run(base + ["check"] + flags, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["action"], "ERROR")

    def test_corrupt_state_is_not_treated_as_loaded(self):
        state = self.root / "broken.json"
        for content in ("[]", '{"schema_version":1,"entries":{"bad":{}}}', "not json"):
            state.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                read_cache.read_state(state)


if __name__ == "__main__":
    unittest.main()
