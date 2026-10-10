---
name: hs-dev-skill
description: >-
  Use when building or changing product features, APIs, DB schema, UI, domain
  models, six-tuple logic, architecture, bugfixes in hs_dev_docs projects, or
  resuming mid-feature work. Quality-first: grill-style DESIGN alignment,
  stepwise correctness, tests as first-class (seams + vertical TDD), deep-module
  vocabulary, local frontend aesthetic defaults. Right-sized S/M/L; paradigm by
  scale/type (DDD optional); DESIGN vs IMPLEMENT ask policy, PRD freeze, ADR,
  task state machine, SQLite context packs, local Commit. First step always
  change_size (S/M/L) + work_mode; tiny fixes use S-path—do not run full 0→6.
  Do not use for one-off scripts, drive-by third-party edits, or when the user
  opts out.
license: MIT
compatibility: Requires Python >= 3.8 (stdlib sqlite3; Win/Linux/macOS)
metadata:
  author: hardstone
  version: "2.20"
---

# 产品开发 Skill (hs-dev-skill)

版本：v2.20  
核心定位：**质量优先（分步正确 + 测试一等公民）+ 文档驱动 + 变更分级（S/M/L）+ 审讯式 DESIGN 对齐 + 深模块词汇 + 本地默认审美 + 装载门闩 + 规则库远程按需 + 六元组；默认本地 Commit**

**装载门闩（反合理化 × Token）**：动手前必须完成 [`load_latch.md`](references/load_latch.md) L0～L2（分级 + 索引路由 + **恰好 1 份**详规）。禁止「跳过 Skill 先干」；也禁止整目录通读。场景有 ≥1% 可能适用 → **必须跑** `skill_ref_index search`（或读 `_index` 一行），命中再打开。

---

## 核心驱动铁律

0. **质量优先**：分步的正确最大可能保证最终的正确；测试是一等公民（[`testing.md`](references/testing.md)）。可演示但无测试证明的行为不算完成（S 无逻辑变更除外）。
1. **先分级 + 定模式**：写 `change_size=S|M|L` 与 `work_mode=DESIGN|IMPLEMENT`（[`right_sizing.md`](references/right_sizing.md) / [`confidence_decision.md`](references/confidence_decision.md)）。禁止未分级按满配 0→6。不确定：`change_size=M`，`work_mode=DESIGN`。
2. **装载门闩**：未过 L0～L2 禁止探代码开工或写 PRD 正文（[`load_latch.md`](references/load_latch.md)）。
3. **持续推进**：除 DESIGN 前沿等待 / 实现期询问闸门 /（M/L）冻结未过 / `BLOCKED` 外禁止空转；确认后立刻继续至路径终点（测试绿+门禁+归档+本地 Commit）。
4. **审讯式对齐后再编码**：`DESIGN` 走 [`grill_orchestration.md`](references/grill_orchestration.md)（设计树前沿轮询，可跳过）；S 数行 DoD；M/L 阶段 0。禁止无对齐开干。
5. **产品冻结（M/L）**：触达面/完整 PRD 须完整、正确、无冲突；S 不写完整 PRD。
6. **按路径设计**：L 须 1→2→3；M 只改触达 DB/API/六元组/调用链；S 禁止空 ADR/空四要素。**先按规模/类型选范式**→[`dev_paradigm.md`](references/dev_paradigm.md)（DDD 只是选项之一，禁止默认上）；模块接口用深模块词汇→[`deep_modules.md`](references/deep_modules.md)；仅当范式含 DDD→[`ddd_design.md`](references/ddd_design.md)；后端分层→[`backend_arch.md`](references/backend_arch.md)；前端模块→[`frontend_arch.md`](references/frontend_arch.md)；UI 默认审美→[`frontend_aesthetic.md`](references/frontend_aesthetic.md)；项目身份→[`design_md.md`](references/design_md.md)+根目录 `DESIGN.md`；UI 手艺→[`frontend_craft.md`](references/frontend_craft.md)；API→[`api_engineering.md`](references/api_engineering.md)；不够再用 [`rule_library.md`](references/rule_library.md) / `rule_fetch`。
7. **路径内单向门禁**：L=`0→1→2→3→4→5→6`；M/S 按 right_sizing。
8. **设计多问 / 实现少问**：`DESIGN` = 审讯式澄清（可跳过）；`IMPLEMENT` 仅四条件闸门才问（[`confidence_decision.md`](references/confidence_decision.md)）。实现中暴露产品空白 → 回切 DESIGN。
9. **实现必测**：确认 seam → 垂直切片红绿重构（[`testing.md`](references/testing.md)）；阶段 6 / 提交前测试必须绿。
10. **学习/偏好**：`~/.hs-dev-skill/`；`global_index_db.py search`，禁止整目录通读。
11. **模糊新技术/UI/架构**：GitHub 高星对标 ≥2；范式见 `dev_paradigm`；深模块见 `deep_modules`；前端结构见 `frontend_arch`；后端见 `backend_arch`；复杂域才读 `ddd_design`（远程按需）。
12. **三端**：`pathlib` + `python3`/`python`/`py -3`（[`cross_platform.md`](references/cross_platform.md)）。
13. **Token**：门闩 + `doc_index_db` / `skill_ref_index` / `rule_fetch` → 切片 → context_pack；禁止整树/`spec_v2_4`/远程规则包开局通读（[`token_budget.md`](references/token_budget.md)）。
14. **默认 Commit；明确要求才 push**。

---

## 执行流程（先分级）

```text
[change_size + work_mode] ── load_latch L0～L2
  ├─ DESIGN: 审讯式设计树多问 → 冻结 → 切 IMPLEMENT
  ├─ S + IMPLEMENT: 轻量对齐 → seam+测驱动实现 → 门禁子集 → Commit
  ├─ M: 迷你阶段0 → 触达面详设 → 任务/pack → 测驱动实现 → 门禁 → Commit
  └─ L: 0→1→2→3→4→5→6（细则见 spec_driven_lifecycle.md）
```

**L 满配**：0 审讯对齐/冻结 → 1 选型 ADR → 2 架构（深模块词汇）→ 3 四要素（API/UI：aesthetic→DESIGN.md→craft / rule_fetch）→ 4 任务+pack+seam → 5 三同步+垂直 TDD → 6 测试绿+门禁+归档+Commit。

**跃迁**：未分级/未过门闩禁止开工；L 的 0→1 须冻结门禁；M/S 禁止为空跑造空文档；`BLOCKED`→落盘→继续至终点。

---

## CLI 速查

| 工具 | 用途 | 示例 |
|---|---|---|
| `skill_ref_index.py` | Skill references 场景检索 | `python scripts/skill_ref_index.py search --q 幂等` |
| `rule_fetch.py` | 本地/远程领域规则目录与缓存 | `python scripts/rule_fetch.py search --q React` |
| `doc_index_db.py` | 项目文档 search/slice | `python scripts/doc_index_db.py --root . search --q kw` |
| `global_index_db.py` | 全局偏好/学习标签 | `python scripts/global_index_db.py search --tag 反向代理` |
| `task_manager.py` | 任务三文件+状态机 | `python scripts/task_manager.py create --id x --title "…" --change-size M` |
| `verify_consistency.py` | 提交前门禁 | `python scripts/verify_consistency.py --root .` |
| `init_hs_dev_docs.py` / `init_hs_global.py` | 初始化项目文档 / 全局区 | `python scripts/init_hs_global.py` |
| `hs_paths.py` / `idx_manager.py` / `dead_code_scanner.py` | 路径 / 索引 / 死代码 | 见各脚本 `--help` |

解释器：Linux/macOS `python3`；Windows `python` 或 `py -3`。

---

## 手册指针

- [`_index.md`](references/_index.md) · [`load_latch.md`](references/load_latch.md) · [`right_sizing.md`](references/right_sizing.md) · [`token_budget.md`](references/token_budget.md)
- [`grill_orchestration.md`](references/grill_orchestration.md) · [`confidence_decision.md`](references/confidence_decision.md)（审讯式 DESIGN / IMPLEMENT 少问）
- [`testing.md`](references/testing.md) · [`quality_gates.md`](references/quality_gates.md) · [`deep_modules.md`](references/deep_modules.md)
- [`dev_paradigm.md`](references/dev_paradigm.md) · [`ddd_design.md`](references/ddd_design.md) · [`backend_arch.md`](references/backend_arch.md) · [`frontend_arch.md`](references/frontend_arch.md)
- [`frontend_aesthetic.md`](references/frontend_aesthetic.md) · [`design_md.md`](references/design_md.md) · [`frontend_craft.md`](references/frontend_craft.md) · [`api_engineering.md`](references/api_engineering.md) · [`rule_library.md`](references/rule_library.md)
- [`learn_and_prefer.md`](references/learn_and_prefer.md) · [`spec_driven_lifecycle.md`](references/spec_driven_lifecycle.md)
- [`six_tuple_runtime.md`](references/six_tuple_runtime.md) · [`four_level_routing.md`](references/four_level_routing.md)
- [`task_state_machine.md`](references/task_state_machine.md) · [`mock_contract_guide.md`](references/mock_contract_guide.md)
- [`cross_platform.md`](references/cross_platform.md)
- [`spec_v2_4.md`](references/spec_v2_4.md)（争议按节；禁止开局通读）
- [`resources/rule_sources.yaml`](resources/rule_sources.yaml) · [`resources/templates/`](resources/templates/) · [`examples/order_service/`](examples/order_service/)
