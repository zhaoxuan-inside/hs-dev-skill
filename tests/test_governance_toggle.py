import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from governance_toggle import (
    load_governance_config,
    save_governance_config,
    is_feature_enabled,
    DEFAULT_GOVERNANCE_CONFIG,
)


class TestGovernanceToggle(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_features_state(self):
        # 验证默认配置状态
        cfg = load_governance_config(self.root)
        features = cfg["features"]

        # 核心机制默认启用
        self.assertTrue(features["version_control"])
        self.assertTrue(features["env_and_secrets"])
        self.assertTrue(features["supply_chain_security"])
        self.assertTrue(features["security_privacy"])
        self.assertTrue(features["agent_guardrails"])

        # 明确要求的重型机制默认不启用 (Disabled)
        self.assertFalse(features["cicd_and_artifacts"])
        self.assertFalse(features["observability_telemetry"])
        self.assertFalse(features["data_resilience_dr"])

    def test_save_and_reload_config(self):
        # 初始化并保存配置
        cfg = load_governance_config(self.root)
        save_governance_config(self.root, cfg)

        cfg_file = self.root / "config" / "governance.yaml"
        self.assertTrue(cfg_file.exists())

        # 修改开关
        cfg["features"]["cicd_and_artifacts"] = True
        cfg["features"]["env_and_secrets"] = False
        save_governance_config(self.root, cfg)

        # 重新加载验证
        reloaded = load_governance_config(self.root)
        self.assertTrue(reloaded["features"]["cicd_and_artifacts"])
        self.assertFalse(reloaded["features"]["env_and_secrets"])

    def test_is_feature_enabled_helper(self):
        # 未创建文件时读取默认值
        self.assertFalse(is_feature_enabled(self.root, "cicd_and_artifacts"))
        self.assertTrue(is_feature_enabled(self.root, "version_control"))

        # 写入启用配置后即时生效
        cfg = load_governance_config(self.root)
        cfg["features"]["cicd_and_artifacts"] = True
        save_governance_config(self.root, cfg)
        self.assertTrue(is_feature_enabled(self.root, "cicd_and_artifacts"))


if __name__ == "__main__":
    unittest.main()
