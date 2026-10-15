# 上下文装载包 (Context Pack)：{task_name}

- **change_size**：`{S|M|L}`
- **任务 ID**：`{task_id}`
- **生成时间**：`{timestamp}`
- **目标域**：`{domain_name}`
- **Token 预估**：`~{token_estimate}`
- **VibeCoding 装载原则**：**机器执行契约优先物化**。优先装载 `_02_feature_spec/_02_vibe_spec` 中的 `{feature}_vibe_spec.md` 切片（Tokens/组件树/Gherkin），以及 ADR/架构文档顶部的 `[VIBE_CONTRACT]` 置顶切片；严禁整篇灌入人类版背景论证。

查询命令（跨平台按需调用）：

```bash
python scripts/doc_index_db.py --root . search --q "{keywords}" --limit 8
python scripts/doc_index_db.py --root . slice --path "{rel_path}" --start 1 --end 40
python scripts/skill_ref_index.py search --q "{scenario}" --limit 5
```

UI 触达读 `references/frontend_craft.md`；API 触达读 `references/api_engineering.md`（各每会话最多一次）。

---

## 1. 产品与 UI 执行契约切片（物化 Vibe Spec）
<!-- 
  【优先物化 _02_feature_spec/_02_vibe_spec/{feature}_vibe_spec.md】
  包含：精准 Design Tokens、组件树 DOM 骨架、状态机迁移与 Gherkin 验收断言原文。
  S 规模可仅物化 3～8 行 Gherkin DoD 与核心字段。
-->

```yaml
# 引用路径：hs_dev_docs/_02_feature_spec/_02_vibe_spec/{feature}_vibe_spec.md (L10-L80)
{从 vibe_spec.md 抽取的精准机器契约}
```

---

## 2. 选型与架构契约切片（物化 [VIBE_CONTRACT]）
<!-- 
  【物化 ADR 与架构设计文档顶部的 [VIBE_CONTRACT] 区块】
  包含：已锁定的技术栈与版本号、模块路径映射、硬性架构依赖禁令。
  严禁将下方人类论证区被否决的落选方案粘贴至此！
-->

```yaml
# 引用路径：hs_dev_docs/_00_project_foundation/_03_decision_record/ADR_xxx.md ([VIBE_CONTRACT] 行段)
{锁定的架构决策与技术栈约束}
```

---

## 3. 核心数据模型与表结构切片（物化）
<!-- 引用 _04_engineering_contract/_01_db_schema：精准 SQL DDL / 字段与约束原文片段；未触达写 N/A -->

```sql
{相关表结构与约束原文}
```

---

## 4. 接口与方法契约画像切片（物化 Method Archetypes）
<!-- 引用 _04_engineering_contract/_02_interface_design 与 _04_engineering_contract/_04_method_design；细则见 api_engineering.md 与 method_archetypes.md -->

```yaml
# 引用路径：hs_dev_docs/_04_engineering_contract/_04_method_design/.../{method}_design.md
method_name: "{method_name}"
archetype: "{TRANSFORM | ALGO | GUARD | STATE | ORCHESTRATE | ADAPTER | PRESENT}"
location: "{file_path} (L{start_line}-L{end_line})"
sensitivity: "{LOW | MEDIUM | HIGH | CRITICAL}"
test_command: "{specific_test_command}"
# 签名与入参约束：
signature: "exception {method_name}(input, output, context, isolate, metrics, recall)"
```

---

## 5. 质量与覆盖率门禁要求
- 单测分支覆盖率 ≥ 85%（S 可仅触达分支）
- 依据 §1 中的 Gherkin 断言编写并通过自动化测试（Red-Green 垂直 TDD）
- 补偿/降级分支 100% 覆盖（若触达六元组 compensate/fallback）
- 契约测试 100% 通过（若触达外部接口）

---

## 6. 查询轨迹（审计 / 续跑）
- `doc_index_db` 命中 path 列表：
- `skill_ref_index` 命中 path 列表：
- 本会话已读 Skill references（禁止重复整读）：
