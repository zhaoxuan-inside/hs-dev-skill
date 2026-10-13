import os
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from skill_ref_index import SkillRefIndex
from rule_fetch import load_catalog, search_catalog


class TestProductDesignCapability(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent

    def test_product_design_guide_exists(self):
        guide = self.root / "references" / "product_design.md"
        self.assertTrue(guide.exists(), "references/product_design.md must exist")
        content = guide.read_text(encoding="utf-8")
        # 双支柱与纯净铁律
        self.assertIn("产品的设计语言", content)
        self.assertIn("产品的功能", content)
        self.assertIn("Design Tokens", content)
        self.assertIn("绝对纯净原则", content)
        # 产品探索五步推演与 UX 四定律、Gherkin DoD、10 维自审标尺
        self.assertIn("Status Quo", content)
        self.assertIn("JTBD", content)
        self.assertIn("Aha Moment", content)
        self.assertIn("FTUE", content)
        self.assertIn("渐进式披露", content)
        self.assertIn("Gherkin", content)
        self.assertIn("Given", content)
        self.assertIn("10 维自审标尺", content)
        # 一源双视图架构
        self.assertIn("一源双视图", content)
        self.assertIn("vibe_spec.md", content)

    def test_prd_template_is_pure_and_professional(self):
        prd_tpl = self.root / "resources" / "templates" / "product_design" / "prd_template.md"
        self.assertTrue(prd_tpl.exists(), "prd_template.md must exist")
        content = prd_tpl.read_text(encoding="utf-8")
        # 必须包含产品洞察、方案比选、功能架构、旅程与 Gherkin DoD
        self.assertIn("JTBD", content)
        self.assertIn("Status Quo", content)
        self.assertIn("FTUE", content)
        self.assertIn("核心产品/交互形态方案比选", content)
        self.assertIn("功能架构全景", content)
        self.assertIn("端到端用户核心旅程", content)
        self.assertIn("详细功能规格与业务规则矩阵", content)
        self.assertIn("Gherkin", content)
        self.assertIn("Given", content)
        # 严禁混入底层工程细节
        self.assertNotIn("Saga 模式", content)
        self.assertNotIn("单测覆盖率 ≥ 85%", content)
        self.assertNotIn("P99 ≤", content)

    def test_prototype_template_has_design_language_and_four_states(self):
        proto_tpl = self.root / "resources" / "templates" / "product_design" / "prototype_template.md"
        self.assertTrue(proto_tpl.exists(), "prototype_template.md must exist")
        content = proto_tpl.read_text(encoding="utf-8")
        self.assertIn("Design Tokens 规范定义", content)
        self.assertIn("UX 认知心理学与可用性四定律", content)
        self.assertIn("渐进式披露", content)
        self.assertIn("核心组件全状态矩阵", content)
        self.assertIn("ASCII", content)
        self.assertIn("正常数据态", content)
        self.assertIn("空白引导态", content)
        self.assertIn("数据加载态", content)
        self.assertIn("异常错误态", content)

    def test_vibe_spec_template_exists_and_is_machine_actionable(self):
        vibe_tpl = self.root / "resources" / "templates" / "product_design" / "vibe_spec_template.md"
        self.assertTrue(vibe_tpl.exists(), "vibe_spec_template.md must exist")
        content = vibe_tpl.read_text(encoding="utf-8")
        self.assertIn("design_tokens:", content)
        self.assertIn("component_tree:", content)
        self.assertIn("state_machine:", content)
        self.assertIn("field_constraints:", content)
        self.assertIn("executable_tests_gherkin:", content)
        self.assertIn("hard_guardrails:", content)

    def test_top_contract_slice_in_tech_select_and_adr_templates(self):
        tech_tpl = self.root / "resources" / "templates" / "tech_select" / "tech_select_template.md"
        self.assertTrue(tech_tpl.exists())
        tech_content = tech_tpl.read_text(encoding="utf-8")
        self.assertIn("[VIBE_CONTRACT]", tech_content)
        self.assertIn("[HUMAN_RATIONALE]", tech_content)

        adr_tpl = self.root / "resources" / "templates" / "hs_dev_docs" / "adr_template.md"
        self.assertTrue(adr_tpl.exists())
        adr_content = adr_tpl.read_text(encoding="utf-8")
        self.assertIn("[VIBE_CONTRACT]", adr_content)
        self.assertIn("[HUMAN_RATIONALE]", adr_content)

        arch_tpl = self.root / "resources" / "templates" / "architecture_design" / "arch_design_template.md"
        self.assertTrue(arch_tpl.exists())
        arch_content = arch_tpl.read_text(encoding="utf-8")
        self.assertIn("[VIBE_CONTRACT]", arch_content)

        cp_tpl = self.root / "resources" / "templates" / "hs_dev_docs" / "context_pack_template.md"
        self.assertTrue(cp_tpl.exists())
        cp_content = cp_tpl.read_text(encoding="utf-8")
        self.assertIn("vibe_spec.md", cp_content)
        self.assertIn("[VIBE_CONTRACT]", cp_content)

    def test_skill_ref_index_finds_product_design_and_new_keywords(self):
        idx = SkillRefIndex(self.root)
        idx.rebuild()
        for kw, target in [
            ("设计语言", "product_design.md"),
            ("JTBD", "product_design.md"),
            ("渐进式披露", "product_design.md"),
            ("ASCII线框", "product_prototype.md"),
        ]:
            hits = idx.search(kw, limit=5)
            self.assertTrue(hits["ok"])
            paths = [h["path"] for h in hits["hits"]]
            self.assertTrue(
                any(target in p for p in paths),
                f"Expected {target} when searching '{kw}', got {paths}",
            )

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

    def test_rule_sources_include_product_and_ux_skills(self):
        catalog = load_catalog(self.root)
        ids = {s["id"] for s in catalog.get("sources", [])}
        self.assertIn("local.product.design", ids)
        self.assertIn("local.product.prototype", ids)
        self.assertIn("local.product.roadmap", ids)
        self.assertIn("gstack.office-hours", ids)
        self.assertIn("gstack.plan-ceo-review", ids)
        self.assertIn("gstack.plan-design-review", ids)
        self.assertIn("deanpeters.pm-prd", ids)
        self.assertIn("uipro.ux-design", ids)

        res = search_catalog(catalog, "JTBD", limit=5)
        self.assertTrue(res["ok"])
        hit_ids = [h["id"] for h in res["hits"]]
        self.assertTrue(any(i in hit_ids for i in ("local.product.design", "gstack.office-hours", "deanpeters.pm-prd")))


if __name__ == "__main__":
    unittest.main()
