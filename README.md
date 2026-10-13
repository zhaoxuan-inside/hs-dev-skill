# hs-dev-skill: 产品开发 Skill

> **质量优先 + 审讯式对齐 + 测试一等公民 + 深模块词汇 + 文档驱动 + S/M/L 分级**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Spec Version](https://img.shields.io/badge/skill-v2.28-blue.svg)](SKILL.md)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](references/cross_platform.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

`hs-dev-skill` 是可安装到 Cursor / Claude Code 等 Agent 的**单体**产品开发技能包（Windows / Linux / macOS），**替代已废弃的 `hs-project-skill`**。目标：**质量大于一切**——审讯式 DESIGN（跳过收紧）、一源双视图（人类产品设计书 + VibeCoding 执行契约）、双轨原型必产（Mermaid 拓扑 + ASCII 比例线框）、选型架构顶置契约切片（隔离废案）、分步正确（seam + 垂直 TDD）。续做靠 `plan_log`/`change_log`（语义「继续」）；回退靠快照而非 git。入口 [`SKILL.md`](SKILL.md)；先写 `change_size`+`work_mode`，过装载门闩后再干活。

---

## 安装（生态分发）

根目录即为单个 Skill（含 `SKILL.md` / `scripts/` / `references/`），可用官方 skills CLI：

```bash
# 安装到当前项目（多 Agent 可选）
npx skills add zhaoxuan-inside/hs-dev-skill

# 全局安装
npx skills add zhaoxuan-inside/hs-dev-skill -g

# 仅浏览是否被发现
npx skills add zhaoxuan-inside/hs-dev-skill --list
```

若本机仍装着已废弃的 `hs-project-skill`，从 Agent 技能目录删掉（`~/.cursor/skills/hs-project-skill`、`~/.agents/skills/hs-project-skill`），改装本仓库 `hs-dev-skill`。

手动（任选其一）：

```bash
git clone https://github.com/zhaoxuan-inside/hs-dev-skill.git
# Cursor 用户技能目录示例：
#   ln -s /path/to/hs-dev-skill ~/.cursor/skills/hs-dev-skill   # Linux/macOS
#   mklink /J %USERPROFILE%\.cursor\skills\hs-dev-skill C:\path\to\hs-dev-skill  # Windows（管理员/开发者模式）
```

装后首次建议：

```bash
python scripts/init_hs_global.py          # 或 py -3 / python3
python scripts/skill_ref_index.py rebuild # Skill 详规场景索引
```

依赖：`Python >= 3.8`（标准库 `sqlite3` + `pathlib`）。

---

## 核心特性

1. **质量优先**：分步正确 + 测试一等公民（seam 确认 → 垂直 TDD）。见 [testing.md](references/testing.md) / [quality_gates.md](references/quality_gates.md)。
2. **审讯式 DESIGN 对齐与方案博弈**：设计树前沿轮询 + 产品探索拷问（`gstack /office-hours`）+ 交互方案 Trade-offs 比选；跳过澄清收紧。见 [grill_orchestration.md](references/grill_orchestration.md) / [confidence_decision.md](references/confidence_decision.md)。
3. **产品设计一源双视图与 MVP 规划**：先产品探索五步推演，再输出**面向人类的《产品设计书》**（PRD + 双轨线框原型）与**面向 VibeCoding 的《机器执行契约》**（Tokens/组件树/状态机/Gherkin DoD），彻底杜绝 AI 叙事幻觉与 Token 浪费；通过人机交互对齐产出《产品开发分阶段规划书》。见 [product_design.md](references/product_design.md) / [product_roadmap.md](references/product_roadmap.md) / [product_prototype.md](references/product_prototype.md)。
4. **变更分级（Right-Sizing）**：`change_size=S|M|L`。见 [right_sizing.md](references/right_sizing.md)。
5. **装载门闩**：分级 + 索引路由 + 恰好 1 份详规。见 [load_latch.md](references/load_latch.md)。
6. **续做 / 非 git 回退**：`plan_log` + `change_log` + 快照；语义「继续」。见 [process_continuity.md](references/process_continuity.md)。
7. **深模块词汇**：Module / Interface / Seam / Adapter / Depth / 删除测试。见 [deep_modules.md](references/deep_modules.md)。
8. **本地默认审美 + 远程按需**：见 [frontend_aesthetic.md](references/frontend_aesthetic.md) / [design_md.md](references/design_md.md)。
9. **产品冻结（M/L）+ Token 预算**：PRD（+原型）闭合后选型；索引切片禁止整树通读。
10. **范式与架构**：[dev_paradigm](references/dev_paradigm.md) → deep_modules / ddd / backend / frontend / API。
11. **六元组 + 合法状态机 + Mock + verify；默认本地 Commit**。
12. **版本号双轨控制与防漂移**：遵循 SemVer；Skill 自身三处强一致；交付 S/M/L 映射 PATCH/MINOR/MAJOR；API 与 DB 迁移版本防破坏。见 [version_control.md](references/version_control.md)。

---

## 快速命令

```bash
make paths          # 全局路径
make test
make verify
make skill-ref-rebuild
make skill-ref-search Q="幂等"
make rule-list
make rule-search Q="React"
make rule-resolve ID=vercel.react-rules RULE=async-parallel
make index-rebuild
make init-docs
make init-global
# Windows: make test PYTHON="py -3"
```

```bash
python scripts/hs_paths.py
python scripts/init_hs_global.py
python scripts/skill_ref_index.py search --q "幂等" --limit 5
python scripts/rule_fetch.py resolve --id local.frontend.core
python scripts/doc_index_db.py --root . search --q "订单 创建" --limit 8
python scripts/task_manager.py create --id order_create --title "创建交易订单" --change-size L --priority P0
python scripts/process_log.py resume-scan --root .
python scripts/process_log.py checkpoint --id order_create --step S2 --summary "改支付主路径" --paths backend/payment_service.py
python scripts/verify_consistency.py --root .
```

---

## 目录指引

| 路径 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | Agent 入口（薄）；铁律 + 路径图 + CLI |
| [references/_index.md](references/_index.md) | 详规场景表（禁止整目录通读） |
| [references/load_latch.md](references/load_latch.md) | **动手前装载门闩** |
| [references/right_sizing.md](references/right_sizing.md) | 变更分级 + work_mode |
| [references/grill_orchestration.md](references/grill_orchestration.md) | 审讯式 DESIGN 对齐 |
| [references/product_design.md](references/product_design.md) | **产品设计规范（设计语言 + 产品功能双支柱 · 产出纯净铁律）** |
| [references/product_roadmap.md](references/product_roadmap.md) | **产品分阶段规划与 MVP 裁剪（人机交互对齐驱动）** |
| [references/product_prototype.md](references/product_prototype.md) | 原型必产（Tokens + 四态线框） |
| [references/process_continuity.md](references/process_continuity.md) | plan/change 续做与非 git 回退 |
| [references/task_state_machine.md](references/task_state_machine.md) | 合法状态迁移 |
| [references/version_control.md](references/version_control.md) | 双轨版本号控制与单源防漂移 / SemVer / 发布 Tag |
| [references/testing.md](references/testing.md) | 测试方法（一等公民） |
| [references/deep_modules.md](references/deep_modules.md) | 深模块 / seam / Adapter |
| [references/dev_paradigm.md](references/dev_paradigm.md) | 按规模/类型选开发范式（先于 DDD） |
| [references/ddd_design.md](references/ddd_design.md) | DDD 子集（仅当范式选定含 DDD） |
| [references/backend_arch.md](references/backend_arch.md) | 后端分层 / 微服务 / Saga |
| [references/frontend_arch.md](references/frontend_arch.md) | 前端模块 / FSD / 与业务边界对齐 |
| [references/frontend_aesthetic.md](references/frontend_aesthetic.md) | UI 本地默认审美 |
| [references/design_md.md](references/design_md.md) | DESIGN.md / 品牌对标 |
| [references/frontend_craft.md](references/frontend_craft.md) / [api_engineering.md](references/api_engineering.md) | UI 手艺 / API 本地高频 |
| [references/rule_library.md](references/rule_library.md) | 远程规则按需协议 |
| [resources/rule_sources.yaml](resources/rule_sources.yaml) | 规则源目录 |
| [references/token_budget.md](references/token_budget.md) | 装载纪律 |
| [references/spec_driven_lifecycle.md](references/spec_driven_lifecycle.md) | L 满配阶段细则 |
| [scripts/](scripts/) | CLI（索引 / 规则拉取 / 任务 / 门禁） |
| [resources/templates/](resources/templates/) | 文档与 Mock 脚手架 |
| [examples/order_service/](examples/order_service/) | 订单服务参考用例 |
