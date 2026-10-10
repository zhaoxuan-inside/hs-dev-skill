# 上下文装载包 (Context Pack)：{task_name}

- **change_size**：`{S|M|L}`
- **任务 ID**：`{task_id}`
- **生成时间**：`{timestamp}`
- **目标域**：`{domain_name}`
- **Token 预估**：`~{token_estimate}`
- **装载纪律**：**必须物化切片正文**（签名表、字段、DoD 断言原文），禁止只列路径后在实现期再整篇读设计。

查询（Windows / Linux / macOS，解释器按平台选用 `python` / `python3` / `py -3`）：

```bash
python scripts/doc_index_db.py --root . search --q "{keywords}" --limit 8
python scripts/doc_index_db.py --root . slice --path "{rel_path}" --start 1 --end 40
python scripts/skill_ref_index.py search --q "{scenario}" --limit 5
```

UI 触达读 `references/frontend_craft.md`；API 触达读 `references/api_engineering.md`（各每会话最多一次）。

---

## 1. 业务目标与需求切片（物化）
<!-- 从 _01_product_design 粘贴精确段落；注明 path + Lx-Ly；S 可仅 3～8 行 DoD -->

{从需求文档抽取的精准上下文}

---

## 2. 核心数据模型与表结构（物化）
<!-- 引用 _04_db_schema：字段/约束原文片段；未触达可写 N/A -->

{相关字段与约束原文}

---

## 3. 接口与六元组方法签名（物化）
<!-- 引用 _05_interface_design 与 _06_method_design；API 细则见 api_engineering.md -->

{相关签名原文}

---

## 4. 依赖调用链与外部契约（物化）
<!-- 引用 _07_call_chain 与 _13_mock_contract -->

{依赖与契约原文}

---

## 5. 质量与覆盖率门禁要求
- 单测分支覆盖率 ≥ 85%（S 可仅触达分支）
- 补偿/降级分支 100% 覆盖（若触达）
- 契约测试 100% 通过（若触达）

---

## 6. 查询轨迹（审计 / 续跑）
- `doc_index_db` 命中 path 列表：
- `skill_ref_index` 命中 path 列表：
- 本会话已读 Skill references（禁止重复整读）：
