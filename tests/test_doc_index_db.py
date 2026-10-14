#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from doc_index_db import DocIndexDB, db_path_for_root  # noqa: E402
from idx_manager import IdxManager  # noqa: E402


class TestDocIndexDB(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        docs = self.root / "hs_dev_docs"
        product = docs / "_01_product_design" / "_02_product_design"
        product.mkdir(parents=True)
        prd = product / "demo_prd.md"
        prd.write_text(
            "# Demo PRD\n\n支付流程与账户冻结。\n\n## DoD\n- 超时触发补偿\n",
            encoding="utf-8",
        )
        idx = docs / "_01_product_design" / "_00_product_design.idx"
        mgr = IdxManager(str(idx))
        mgr.init_idx("product_design", "_01_product_design")
        mgr.add_entry(
            "demo_prd",
            "Demo PRD 支付",
            "_02_product_design/demo_prd.md",
            auto_digest=True,
        )

    def tearDown(self):
        try:
            self.tmp.cleanup()
        except PermissionError:
            # Windows: 偶发句柄延迟释放
            pass

    def test_db_path_under_docs_index(self):
        p = db_path_for_root(self.root)
        self.assertTrue(
            any(
                str(p).replace("\\", "/").endswith(suffix)
                for suffix in [
                    "hs_dev_docs/_00_project_foundation/_05_doc_index/doc_index.sqlite",
                    "hs_dev_docs/_00_project/_18_doc_index/doc_index.sqlite",
                ]
            )
        )

    def test_rebuild_search_slice_cross_platform_paths(self):
        db = DocIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertTrue(info["ok"])
            self.assertGreaterEqual(info["inserted"], 1)
            self.assertTrue(Path(info["db_path"]).is_file())

            # 中文 LIKE 回退；内容文档应排在 idx 之前
            zh = db.search("支付", limit=5)
            self.assertTrue(zh["ok"])
            self.assertGreaterEqual(zh["count"], 1)
            hit = next(
                (r for r in zh["results"] if r["path"].endswith("demo_prd.md")),
                zh["results"][0],
            )
            self.assertTrue(hit["path"].endswith("demo_prd.md"))
            self.assertIn("hs_dev_docs/", hit["path"])

            # ASCII / FTS 或 LIKE
            en = db.search("Demo", limit=5)
            self.assertTrue(en["ok"])
            self.assertGreaterEqual(en["count"], 1)

            path = hit["path"]
            sl = db.slice(path, start=1, end=3, max_lines=10)
            self.assertTrue(sl["ok"])
            self.assertEqual(sl["start"], 1)
            self.assertIn("Demo PRD", sl["text"])
            # 路径一律 posix 相对根
            self.assertNotIn("\\", sl["path"])

            got = db.get(path)
            self.assertTrue(got["ok"])
            self.assertIn("支付", got["result"]["summary"] + got["result"]["title"])
        finally:
            db.close()

    def test_cli_search_json(self):
        from doc_index_db import main

        db = DocIndexDB(self.root)
        try:
            db.rebuild()
        finally:
            db.close()

        code = main(["--root", str(self.root), "stats"])
        self.assertEqual(code, 0)

    def test_method_search_anti_explosion(self):
        docs = self.root / "hs_dev_docs"
        method_dir = docs / "_06_method_design" / "_01_privacy"
        method_dir.mkdir(parents=True, exist_ok=True)
        m_file = method_dir / "_01_mask_phone_design.md"
        m_file.write_text(
            "# 方法设计规范：mask_phone\n\n"
            "## 1. 基础与位置画像 (Location & Profile)\n"
            "- **所属层次**：领域核心层\n"
            "- **所属模块**：`privacy`\n"
            "- **文件路径**：`src/utils/privacy.py`\n"
            "- **代码定位**：第 `20` 行，共 `15` 行（行范围：`20-34`）\n"
            "- **方法签名**：`str mask_phone(phone: str, country_code: str = '')`\n"
            "- **方法类型**：`TRANSFORM`\n"
            "- **功能描述**：手机号脱敏掩码，保留前3后4位\n\n"
            "## 2. 特征与属性契约 (Attributes Contract)\n"
            "- **改动敏感度**：`LOW`\n"
            "- **副作用类型**：`NONE`\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            db.rebuild()
            stats = db.stats()
            self.assertGreaterEqual(stats["methods"], 1)

            # 语义 / 关键词检索
            res = db.method_search("脱敏")
            self.assertTrue(res["ok"])
            self.assertEqual(res["count"], 1)
            candidate = res["candidates"][0]
            self.assertEqual(candidate["name"], "mask_phone")
            self.assertEqual(candidate["archetype"], "TRANSFORM")
            self.assertEqual(candidate["lines"], "20-34")
            self.assertIn("REUSE_OR_EXTEND", candidate["action_recommendation"])

            # 英文符号查询
            res_en = db.method_search("mask_phone", archetype="TRANSFORM")
            self.assertTrue(res_en["ok"])
            self.assertEqual(res_en["count"], 1)

            # 空查询或无匹配
            res_none = db.method_search("不存在的复杂计算方法XYZ")
            self.assertEqual(res_none["count"], 0)
            self.assertIn("No matching method found", res_none["guidance"])
        finally:
            db.close()

    def test_symbol_search_and_slice(self):
        backend_dir = self.root / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        py_file = backend_dir / "user_service.py"
        py_file.write_text(
            "class UserService:\n"
            "    def register_user(self, username: str) -> bool:\n"
            "        '''Register new user'''\n"
            "        return True\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            db.rebuild()
            stats = db.stats()
            self.assertGreaterEqual(stats["code_symbols"], 2)

            res = db.symbol_search("register_user")
            self.assertTrue(res["ok"])
            self.assertGreaterEqual(res["count"], 1)
            self.assertEqual(res["symbols"][0]["name"], "UserService.register_user")

            # Slice test
            slice_res = db.symbol_slice("register_user")
            self.assertTrue(slice_res["ok"])
            self.assertIn("def register_user", slice_res["content"])
            self.assertEqual(slice_res["start_line"], 2)
            self.assertEqual(slice_res["end_line"], 4)
        finally:
            db.close()

    def test_hierarchical_schema_tables(self):
        db = DocIndexDB(self.root)
        try:
            db.rebuild()
            stats = db.stats()
            self.assertIn("features", stats)
            self.assertIn("pages", stats)
            self.assertIn("pattern_clusters", stats)
            self.assertIn("data_schemas", stats)
            self.assertIn("test_cases", stats)
            self.assertIn("method_dependencies", stats)
            self.assertIn("audit_changes", stats)
            self.assertGreaterEqual(stats["features"], 1)
            self.assertEqual(stats["pattern_clusters"], 0)
        finally:
            db.close()

    def test_feature_and_page_indexing_and_search(self):
        # 准备 PRD 文件
        prd_dir = self.root / "hs_dev_docs" / "_01_product_design" / "_02_product_design" / "features"
        prd_dir.mkdir(parents=True, exist_ok=True)
        feat_file = prd_dir / "checkout_prd.md"
        feat_file.write_text(
            "# 子特性需求与功能规格说明书 (Feature PRD)：极速收银台\n\n"
            "- **特性ID (Feature ID)**：`FEAT-101`\n"
            "- **特性名称**：极速收银台与聚合支付\n"
            "- **所属模块**：checkout\n"
            "- **优先级**：P0\n"
            "- **状态**：active\n\n"
            "## 1. 特性洞察与核心价值界定\n"
            "- **一句话价值主张**：一键拉起收银台，支持微信与支付宝聚合扫码支付。\n",
            encoding="utf-8",
        )

        # 准备原型与页面布局文件
        proto_dir = self.root / "hs_dev_docs" / "_01_product_design" / "_03_product_figma"
        proto_dir.mkdir(parents=True, exist_ok=True)
        page_file = proto_dir / "checkout_prototype.md"
        page_file.write_text(
            "# 产品设计语言与界面原型规范：极速收银台\n\n"
            "- **页面ID**：`PAGE-101`\n"
            "- **路由 / Route**：`/order/checkout`\n"
            "- **所属模块**：checkout\n"
            "- **内容密度 / 布局类型**：主从分栏 (Split View)\n"
            "- **可交互 HTML 原型预览**：`_03_product_figma/checkout_prototype.html`\n\n"
            "## 页面布局\n"
            "左侧展示商品清单与优惠明细，右侧固定 380px 收银支付抽屉面板。\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertGreaterEqual(info["features_inserted"], 1)
            self.assertGreaterEqual(info["pages_inserted"], 1)

            # Feature Search 测试
            f_res = db.feature_search("聚合支付")
            self.assertTrue(f_res["ok"])
            self.assertGreaterEqual(f_res["count"], 1)
            f_item = f_res["features"][0]
            self.assertEqual(f_item["feature_id"], "FEAT-101")
            self.assertEqual(f_item["module"], "checkout")

            # Page Search 测试
            p_res = db.page_search("收银台")
            self.assertTrue(p_res["ok"])
            self.assertGreaterEqual(p_res["count"], 1)
            p_item = p_res["pages"][0]
            self.assertEqual(p_item["page_id"], "PAGE-101")
            self.assertEqual(p_item["route"], "/order/checkout")
            self.assertIn("主从分栏", p_item["layout_type"])
        finally:
            db.close()

    def test_pattern_cluster_and_data_schema_indexing_and_search(self):
        # 1. 准备设计模式集群档案
        cluster_dir = self.root / "hs_dev_docs" / "_03_architecture_design" / "_02_pattern_clusters"
        cluster_dir.mkdir(parents=True, exist_ok=True)
        cluster_file = cluster_dir / "payment_strategy_cluster.md"
        cluster_file.write_text(
            "# 设计模式协同集群档案：payment_strategy_cluster\n\n"
            "## 1. 模式元数据 (Pattern Metadata)\n"
            "- **设计模式 (Design Pattern)**：`Strategy`\n"
            "- **所属业务域与模块**：`payment / checkout`\n"
            "- **关联特性 (Feature ID)**：`FEAT-101`\n\n"
            "## 2. 参与者矩阵与物理定位 (Participant Matrix)\n"
            "| 模式角色 (Pattern Role) | 承载类 / 方法物理定位 | 方法原型 | 核心职责 |\n"
            "|---|---|---|---|\n"
            "| **Context** | `backend/payment/pay_context.py#10-35` | `ORCHESTRATE` | 调度支付策略执行 |\n"
            "| **Contract** | `backend/payment/iprecise_strategy.py#5-15` | `CONTRACT` | 支付标准抽象接口 |\n\n"
            "## 4. VibeCoding 防破坏红线\n"
            "严禁在 Context 中通过 if-else 穿透破坏策略多态！\n",
            encoding="utf-8",
        )

        # 2. 准备数据表规格文档与 SQL 迁移
        schema_dir = self.root / "hs_dev_docs" / "_04_db_schema" / "_01_order"
        schema_dir.mkdir(parents=True, exist_ok=True)
        tbl_file = schema_dir / "order_tbl_design.md"
        tbl_file.write_text(
            "# 数据表设计文档：t_order\n\n"
            "## 1. 表基础信息\n"
            "- **表名**：`t_order`\n"
            "- **说明**：交易订单主表\n"
            "- **所属模块**：`order`\n"
            "- **关联特性 (Feature ID)**：`FEAT-101`\n\n"
            "## 2. 字段定义\n"
            "| 字段名 | 类型 | 长度/精度 | 允许空 |\n"
            "|---|---|---|---|\n"
            "| `id` | BIGINT | 64 | 否 |\n"
            "| `order_no` | VARCHAR | 64 | 否 |\n"
            "| `amount` | DECIMAL | 10,2 | 否 |\n",
            encoding="utf-8",
        )

        mig_dir = schema_dir / "migrations"
        mig_dir.mkdir(parents=True, exist_ok=True)
        sql_file = mig_dir / "V1.0.0__create_order.sql"
        sql_file.write_text(
            "-- Description: 交易订单主表物理定义\n"
            "-- Feature: FEAT-101\n"
            "CREATE TABLE IF NOT EXISTS t_order (\n"
            "    id BIGINT PRIMARY KEY,\n"
            "    order_no VARCHAR(64) NOT NULL,\n"
            "    amount DECIMAL(10,2) NOT NULL\n"
            ");\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertGreaterEqual(info["pattern_clusters_inserted"], 1)
            self.assertGreaterEqual(info["data_schemas_inserted"], 1)

            # Pattern Search 测试
            pat_res = db.pattern_search("Strategy")
            self.assertTrue(pat_res["ok"])
            self.assertGreaterEqual(pat_res["count"], 1)
            pat_item = pat_res["patterns"][0]
            self.assertEqual(pat_item["cluster_name"], "payment_strategy_cluster")
            self.assertIn("Context", pat_item["participating_symbols"])

            # Schema Search 测试
            sch_res = db.schema_search("t_order")
            self.assertTrue(sch_res["ok"])
            self.assertGreaterEqual(sch_res["count"], 1)
            sch_item = sch_res["schemas"][0]
            self.assertEqual(sch_item["table_name"], "t_order")
            self.assertEqual(sch_item["feature_id"], "FEAT-101")
            self.assertIn("order_no", sch_item["fields_summary"])
        finally:
            db.close()

    def test_method_dependencies_and_dep_graph(self):
        backend_dir = self.root / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        code_file = backend_dir / "service.py"
        code_file.write_text(
            "class OrderService:\n"
            "    def create_order(self, uid: int) -> bool:\n"
            "        self.validate_user(uid)\n"
            "        self.save_record()\n"
            "        return True\n"
            "    def validate_user(self, uid: int) -> bool:\n"
            "        return True\n"
            "    def save_record(self) -> None:\n"
            "        pass\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertGreaterEqual(info["method_dependencies_inserted"], 2)

            # Ego Graph 测试
            ego = db.dep_graph("OrderService.create_order")
            self.assertTrue(ego["ok"])
            self.assertEqual(ego["scope"], "EGO")
            self.assertGreaterEqual(ego["callees_count"], 2)
            self.assertIn("validate_user", ego["mermaid"])
            self.assertIn("save_record", ego["mermaid"])

            # Global Graph 测试
            glob = db.dep_graph("")
            self.assertTrue(glob["ok"])
            self.assertEqual(glob["scope"], "GLOBAL")
            self.assertGreaterEqual(glob["total_dependencies"], 2)
        finally:
            db.close()

    def test_test_case_indexing_and_search(self):
        # 1. 建立测试规格说明书
        test_doc_dir = self.root / "hs_dev_docs" / "_07_test_design"
        test_doc_dir.mkdir(parents=True, exist_ok=True)
        spec_file = test_doc_dir / "test_auth_service_spec.md"
        spec_file.write_text(
            "# 测试用例规格说明书：用户身份认证鉴权契约\n\n"
            "- **用例标识**：`TC-AUTH-001`\n"
            "- **关联业务特性**：`FEAT-AUTH-LOGIN`\n"
            "- **所属业务模块**：`auth`\n"
            "- **测试层级**：`INTEGRATION`\n"
            "- **目标方法/符号**：`AuthService.verify_token`\n"
            "- **测试代码文件**：`tests/test_auth.py`\n"
            "- **精确单跑指令**：`pytest tests/test_auth.py::test_verify_token_valid`\n"
            "- **DDT 数据集**：`tests/data/tokens.json`\n"
            "- **业务意图**：校验 JWT 令牌在有效期内的解析与权限校验逻辑\n",
            encoding="utf-8",
        )

        # 2. 建立实际测试代码文件
        test_code_dir = self.root / "tests"
        test_code_dir.mkdir(parents=True, exist_ok=True)
        py_test_file = test_code_dir / "test_auth.py"
        py_test_file.write_text(
            "def test_verify_token_valid():\n"
            "    '''Verify valid auth token returns expected user'''\n"
            "    assert True\n",
            encoding="utf-8",
        )

        db = DocIndexDB(self.root)
        try:
            info = db.rebuild()
            self.assertGreaterEqual(info["test_cases_inserted"], 2)

            # 按关键字搜索测试用例
            res = db.test_search("TC-AUTH-001")
            self.assertTrue(res["ok"])
            self.assertGreaterEqual(res["count"], 1)
            first = res["tests"][0]
            self.assertEqual(first["case_id"], "TC-AUTH-001")
            self.assertEqual(first["feature_id"], "FEAT-AUTH-LOGIN")
            self.assertIn("pytest tests/test_auth.py", first["test_command"])

            # 按 target_symbol 过滤搜索
            target_res = db.test_search("", target="AuthService.verify_token")
            self.assertTrue(target_res["ok"])
            self.assertGreaterEqual(target_res["count"], 1)

            # 搜索从代码提取的测试
            code_res = db.test_search("test_verify_token_valid")
            self.assertTrue(code_res["ok"])
            self.assertGreaterEqual(code_res["count"], 1)

            # 验证 stats
            st = db.stats()
            self.assertGreaterEqual(st["test_cases"], 2)
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()

