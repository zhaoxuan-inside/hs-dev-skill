import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from version_tool import generate_timestamp_build, format_version, parse_version


class TestVersionTool(unittest.TestCase):
    def test_generate_timestamp_build_format(self):
        # 验证固定时间生成 MMddHHmmss
        fixed_dt = datetime(2026, 10, 14, 17, 28, 30)
        ts = generate_timestamp_build(fixed_dt)
        self.assertEqual(ts, "1014172830")
        self.assertEqual(len(ts), 10)

        # 默认当前时间也是 10 位纯数字
        now_ts = generate_timestamp_build()
        self.assertEqual(len(now_ts), 10)
        self.assertTrue(now_ts.isdigit())

    def test_format_version_defaults(self):
        fixed_dt = datetime(2026, 5, 20, 9, 8, 7)
        ver = format_version(
            major=2, feature=3, patch=1, build=generate_timestamp_build(fixed_dt)
        )
        self.assertEqual(ver, "v2.3.1.0520090807")

    def test_format_version_with_client_and_tier(self):
        ver = format_version(
            major=1,
            feature=0,
            patch=2,
            build="1014172800",
            env_tier="beta",
            client="apk",
        )
        self.assertEqual(ver, "v1.0.2.1014172800-beta+apk")

    def test_parse_version(self):
        parsed = parse_version("v1.2.3.1014172807+apk")
        self.assertTrue(parsed["valid"])
        self.assertEqual(parsed["major"], 1)
        self.assertEqual(parsed["feature"], 2)
        self.assertEqual(parsed["patch"], 3)
        self.assertEqual(parsed["build"], "1014172807")
        self.assertEqual(parsed["client"], "apk")
        self.assertTrue(parsed["is_timestamp_build"])

    def test_parse_version_three_segment_fallback(self):
        parsed = parse_version("v1.2.3+web")
        self.assertTrue(parsed["valid"])
        self.assertEqual(parsed["major"], 1)
        self.assertEqual(parsed["feature"], 2)
        self.assertEqual(parsed["patch"], 3)
        self.assertEqual(parsed["client"], "web")
        self.assertFalse(parsed["is_timestamp_build"])


if __name__ == "__main__":
    unittest.main()
