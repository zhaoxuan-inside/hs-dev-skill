---
name: hs-dev-skill
description: >-
  Use when building or changing product features, APIs, DB schema, UI, domain
  models, six-tuple logic, architecture, bugfixes in hs_dev_docs projects, or
  resuming mid-feature work. Right-sized S/M/L paths, PRD freeze, ADR, task
  state machine, SQLite context packs, local Commit. First step is always
  change_size (S/M/L); tiny fixes use S-path—do not run full 0→6. Do not use for
  one-off scripts, drive-by third-party edits, or when the user opts out.
license: MIT
compatibility: Requires Python >= 3.8 (stdlib sqlite3; Win/Linux/macOS)
metadata:
  author: hardstone
  version: "2.12"
---

# 产品开发 Skill (hs-dev-skill)

版本：v2.12  
核心定位：**文档驱动 + 变更分级（S/M/L）+ 门禁交付 + Token 预算 + 置信度决策 + 六元组；默认本地 Commit**

**装载**：先 [`references/_index.md`](references/_index.md) 或 `python scripts/skill_ref_index.py search`；再打开**一份**详规。阶段细则只在 [`spec_driven_lifecycle.md`](references/spec_driven_lifecycle.md) / [`right_sizing.md`](references/right_sizing.md)。

---

## 核心驱动铁律

0. **先分级**：第一步写 `change_size=S|M|L`（[`right_sizing.md`](references/right_sizing.md)）。禁止未分级按满配 0→6。S=轻量对齐→实现→门禁子集；M=只补触达面；L=完整 0→6。不确定取 M。
1. **持续推进**：除询问闸门 /（M/L）冻结未过 / `BLOCKED` 外禁止空转；确认后立刻继续至路径终点（门禁+归档+本地 Commit）。
2. **对齐后再编码**：S 数行 DoD；M/L 阶段 0（迷你或完整 PRD）。禁止无对齐开干。
3. **产品冻结（M/L）**：触达面/完整 PRD 须完整、正确、无冲突；S 不写完整 PRD。
4. **按路径设计**：L 须 1→2→3；M 只改触达 DB/API/六元组/调用链；S 禁止空 ADR/空四要素。UI→[`frontend_craft.md`](references/frontend_craft.md)；API→[`api_engineering.md`](references/api_engineering.md)。
5. **路径内单向门禁**：L=`0→1→2→3→4→5→6`；M/S 按 right_sizing。
6. **置信度询问**：仅影响面广+项目特有+资料未提+多方案接近时问（[`confidence_decision.md`](references/confidence_decision.md)）。
7. **学习/偏好**：`~/.hs-dev-skill/`；`global_index_db.py search`，禁止整目录通读。
8. **模糊新技术/UI**：GitHub 高星对标 ≥2 候选后再定案。
9. **三端**：`pathlib` + `python3`/`python`/`py -3`（[`cross_platform.md`](references/cross_platform.md)）。
10. **Token**：`doc_index_db` / `skill_ref_index` → 切片 → context_pack；禁止整树/`spec_v2_4` 开局通读（[`token_budget.md`](references/token_budget.md)）。
11. **默认 Commit；明确要求才 push**。

---

## 执行流程（先分级）

```text
[change_size=S|M|L] ── right_sizing.md
  ├─ S: 轻量对齐 → (可选 pack) → 实现+测 → 门禁子集 → Commit
  ├─ M: 迷你阶段0 → 只补触达面详设 → 任务/pack → 实现 → 门禁 → Commit
  └─ L: 0→1→2→3→4→5→6（细则见 spec_driven_lifecycle.md）
```

**L 满配**：0 对齐/冻结 → 1 选型 ADR → 2 架构 → 3 四要素（API/UI 按需读 craft）→ 4 任务+pack → 5 三同步实现 → 6 门禁+归档+Commit。

**跃迁**：未分级禁止开工；L 的 0→1 须冻结门禁；M/S 禁止为空跑造空文档；`BLOCKED`→落盘→继续至终点。

阶段 checklist、产出路径、门禁条文：**只读** [`spec_driven_lifecycle.md`](references/spec_driven_lifecycle.md) 当前阶段节（S 可不读全文）。

---

## CLI 速查

| 工具 | 用途 | 示例 |
|---|---|---|
| `skill_ref_index.py` | Skill references 场景检索 | `python scripts/skill_ref_index.py search --q 幂等` |
| `doc_index_db.py` | 项目文档 search/slice | `python scripts/doc_index_db.py --root . search --q kw` |
| `global_index_db.py` | 全局偏好/学习标签 | `python scripts/global_index_db.py search --tag 反向代理` |
| `task_manager.py` | 任务三文件+状态机 | `python scripts/task_manager.py create --id x --title "…" --change-size M` |
| `verify_consistency.py` | 提交前门禁 | `python scripts/verify_consistency.py --root .` |
| `init_hs_dev_docs.py` / `init_hs_global.py` | 初始化项目文档 / 全局区 | `python scripts/init_hs_global.py` |
| `hs_paths.py` / `idx_manager.py` / `dead_code_scanner.py` | 路径 / 索引 / 死代码 | 见各脚本 `--help` |

解释器：Linux/macOS `python3`；Windows `python` 或 `py -3`。

---

## 手册指针

- [`_index.md`](references/_index.md) · [`right_sizing.md`](references/right_sizing.md) · [`token_budget.md`](references/token_budget.md)
- [`frontend_craft.md`](references/frontend_craft.md) · [`api_engineering.md`](references/api_engineering.md)（按需）
- [`confidence_decision.md`](references/confidence_decision.md) · [`learn_and_prefer.md`](references/learn_and_prefer.md)
- [`spec_driven_lifecycle.md`](references/spec_driven_lifecycle.md) · [`six_tuple_runtime.md`](references/six_tuple_runtime.md)
- [`four_level_routing.md`](references/four_level_routing.md) · [`task_state_machine.md`](references/task_state_machine.md)
- [`mock_contract_guide.md`](references/mock_contract_guide.md) · [`quality_gates.md`](references/quality_gates.md) · [`cross_platform.md`](references/cross_platform.md)
- [`spec_v2_4.md`](references/spec_v2_4.md)（争议按节；禁止开局通读）
- [`resources/templates/`](resources/templates/) · [`examples/order_service/`](examples/order_service/)
