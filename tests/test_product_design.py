import os
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from skill_ref_index import SkillRefIndex


class TestProductDesignCapability(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent

    def test_product_design_guide_exists(self):
        guide = self.root / "references" / "product_design.md"
        self.assertTrue(guide.exists(), "references/product_design.md must exist")
        content = guide.read_text(encoding="utf-8")
        self.assertIn("产品的设计语言", content)
        self.assertIn("产品的功能", content)
        self.assertIn("Design Tokens", content)
        self.assertIn("绝对纯净原则", content)

    def test_prd_template_is_pure_and_professional(self):
        prd_tpl = self.root / "resources" / "templates" / "product_design" / "prd_template.md"
        self.assertTrue(prd_tpl.exists(), "prd_template.md must exist")
        content = prd_tpl.read_text(encoding="utf-8")
        # 必须包含产品功能与业务规格
        self.assertIn("功能架构全景", content)
        self.assertIn("端到端用户核心旅程", content)
        self.assertIn("详细功能规格与业务规则矩阵", content)
        # 严禁混入底层工程细节
        self.assertNotIn("Saga 模式", content)
        self.assertNotIn("单测覆盖率 ≥ 85%", content)
        self.assertNotIn("P99 ≤", content)

    def test_prototype_template_has_design_language_and_four_states(self):
        proto_tpl = self.root / "resources" / "templates" / "product_design" / "prototype_template.md"
        self.assertTrue(proto_tpl.exists(), "prototype_template.md must exist")
        content = proto_tpl.read_text(encoding="utf-8")
        self.assertIn("Design Tokens 规范定义", content)
        self.assertIn("核心组件全状态矩阵", content)
        self.assertIn("正常数据态", content)
        self.assertIn("空白引导态", content)
        self.assertIn("数据加载态", content)
        self.assertIn("异常错误态", content)

    def test_skill_ref_index_finds_product_design(self):
        idx = SkillRefIndex(self.root)
        hits = idx.search("设计语言", limit=5)
        self.assertTrue(hits["ok"])
        paths = [h["path"] for h in hits["hits"]]
        self.assertTrue(any("product_design.md" in p for p in paths))

    def test_product_roadmap_guide_and_template_exist(self):
        guide = self.root / "references" / "product_roadmap.md"
        self.assertTrue(guide.exists(), "references/product_roadmap.md must exist")
        content = guide.read_text(encoding="utf-8")
        self.assertIn("人机交互", content)
        self.assertIn("MVP", content)
        self.assertIn("MoSCoW", content)
        self.assertIn("产品开发分阶段规划书", content)

        tpl = self.root / "resources" / "templates" / "product_design" / "phased_roadmap_template.md"
        self.assertTrue(tpl.exists(), "phased_roadmap_template.md must exist")
        tpl_content = tpl.read_text(encoding="utf-8")
        self.assertIn("人机交互对齐备忘录", tpl_content)
        self.assertIn("全量功能池 MoSCoW 分级与分期矩阵", tpl_content)
        self.assertIn("阶段一：MVP", tpl_content)

    def test_skill_ref_index_finds_product_roadmap(self):
        idx = SkillRefIndex(self.root)
        hits = idx.search("分阶段规划", limit=5)
        self.assertTrue(hits["ok"])
        paths = [h["path"] for h in hits["hits"]]
        self.assertTrue(any("product_roadmap.md" in p for p in paths))


if __name__ == "__main__":
    unittest.main()

