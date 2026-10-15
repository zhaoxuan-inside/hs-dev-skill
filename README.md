# hs-dev-skill: 产品开发 Skill

> **质量优先 + 审讯式对齐 + 测试一等公民 + 深模块词汇 + 文档驱动 + S/M/L 分级**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Spec Version](https://img.shields.io/badge/skill-v2.43.0.0-blue.svg)](SKILL.md)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](references/cross_platform.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

`hs-dev-skill` 是可安装到 Cursor / Claude Code 等 Agent 的**单体**产品开发技能包（Windows / Linux / macOS），**替代已废弃的 `hs-project-skill`**。目标：**质量大于一切**——开场确认（新需求先对齐理解/假设/约束/分级建议，防返工）+ 全场景意图路由（BUILD 从零构建 / REVERSE 存量反向重建 / FIX 调试修复 / REFACTOR 重构 / EXPLORE 只读理解 / RESUME 续做）、审讯式 DESIGN（跳过收紧；**MVP 范围裁定并入产品设计沟通**）、一源双视图（人类产品设计书 + VibeCoding 执行契约）、双轨原型必产（Mermaid 拓扑 + ASCII 比例线框）、**业务语义签收 + 冻结确认单（开发者评审双轨）**、垂直领域能力融合（OpenPencil / Generative UI 原型、Modern Web Guidance 规范、Chrome DevTools 运行时/a11y/CWV 门禁）、全局统一术语与词态矩阵（Ubiquitous Language 单一事实源 · Command动词原形/Event过去分词/Attribute时间戳严格解耦 · Search-Before-Name · 零裸字符串）、多端代码与构建产物强制收敛隔离（apps/ 与 output/ 强管控）、四段式多级版本控制（`v[主版本].[需求版本].[修复版本].[打包版本]` · 多级子版本号精确包区分）、工程附属机制全景治理支撑（环境配置与机密隔离 · 软件供应链与 CVE 阻断 · CI/CD 流水线与制品防伪 SBOM · 可观测性与三态健康探针 · 数据韧性与双向容灾回滚 · 安全防御与 PII 隐私脱敏 · Agent 执行安全沙箱护栏）、选型架构顶置契约切片（隔离废案）+ **选型拍板单（低成本确认点）**、**新增业务触达数据库设计必须经开发者决策**、**需求变更通道（变更请求单）**、GoF 23 种设计模式选型决策树与模式协同集群档案、方法类型七分类与七维契约画像（精准测试矩阵 + patternCluster 关联指针毫秒级局部命中 · 抗方法爆炸门禁与写前意图检索选型 `doc_index_db method-search`）、分步正确（seam + 垂直 TDD）。续做靠 `plan_log`/`change_log`（语义「继续」）；回退靠快照而非 git。入口 [`SKILL.md`](SKILL.md)；先跑开场确认、写 `intent`+`change_size`+`work_mode`，过装载门闩后再干活。

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

0. **全场景立体意图路由（BUILD / REVERSE / FIX / REFACTOR / EXPLORE / RESUME）**：根据工程诉求无缝分流——从零构建 0→6、已有项目反向重建（Schema/API 提取与索引化）、系统化调试与先红后绿 Bug 修复、行为等价保护网重构、纯只读免交付代码理解。见 [right_sizing.md](references/right_sizing.md) / [reverse_engineering.md](references/reverse_engineering.md) / [systematic_debugging.md](references/systematic_debugging.md) / [code_refactoring.md](references/code_refactoring.md) / [code_exploration.md](references/code_exploration.md)。
1. **质量优先与硬阻断门禁**：分步正确 + 测试一等公民（测试 100% PASS 零报错绝对阻断交付、代码静态检测零告警零错误、DDT 与双轨制 E2E 规约）。见 [testing.md](references/testing.md) / [quality_gates.md](references/quality_gates.md)。
2. **审讯式 DESIGN 对齐与方案博弈（轮询不限次）**：设计树前沿轮询 + 产品探索拷问（`gstack /office-hours`）+ 交互方案 Trade-offs 比选 + **按返工代价排序提问**；跳过澄清收紧。见 [grill_orchestration.md](references/grill_orchestration.md) / [confidence_decision.md](references/confidence_decision.md)。
3. **开场确认协议**：新需求第一步复述需求 + 假设/空白 + 约束/干系人盘点 + 分级建议，**开发者确认后才进审讯**——把理解错位挡在第一步，防整链返工。见 [opening_alignment.md](references/opening_alignment.md)。
4. **产品设计一源双视图与 MVP 范围前置**：先产品探索五步推演，**MVP 范围（Q1/Q2/Q3）在产品设计沟通时由开发者裁定，再写 MVP 内详细规格**，输出**面向人类的《产品设计书》**（PRD + 双轨线框原型）与**面向 VibeCoding 的《机器执行契约》**（Tokens/组件树/状态机/Gherkin DoD）；冻结 = Agent 10 维自审 + **开发者业务语义签收 + 冻结确认单**双轨。见 [product_design.md](references/product_design.md) / [product_roadmap.md](references/product_roadmap.md) / [product_prototype.md](references/product_prototype.md)。
5. **变更分级（Right-Sizing）**：`change_size=S|M|L`；**新增业务触达数据库设计 → 至少 M 且必须开发者决策**。见 [right_sizing.md](references/right_sizing.md)。
6. **装载门闩**：开场确认 + 分级 + 索引路由 + 核心 1 份详规（阶段链附属 ≤5 份）。见 [load_latch.md](references/load_latch.md)。
7. **续做 / 非 git 回退**：`plan_log` + `change_log` + 快照；语义「继续」。见 [process_continuity.md](references/process_continuity.md)。
8. **需求变更通道**：冻结后变更走《变更请求单》（影响评估 + 开发者裁定），禁止静默改/静默砍。见 [requirement_change.md](references/requirement_change.md)。
9. **深模块词汇**：Module / Interface / Seam / Adapter / Depth / 删除测试。见 [deep_modules.md](references/deep_modules.md)。
10. **本地默认审美 + 远程按需**：见 [frontend_aesthetic.md](references/frontend_aesthetic.md) / [design_md.md](references/design_md.md)。
11. **产品冻结（M/L）+ Token 预算**：PRD（+原型）+ 冻结确认单闭合后选型；索引切片禁止整树通读。
12. **范式与架构**：[dev_paradigm](references/dev_paradigm.md) → deep_modules / ddd / backend / frontend / API。
13. **GoF 23 种设计模式选型决策树与协同集群档案**：依据代码异味定位模式；复杂协作落地 `_02_pattern_clusters/`，方法属性 `patternCluster` 挂载单向指针直达护栏，按需局部切片，避免全量通读。见 [design_patterns.md](references/design_patterns.md)。
14. **六元组 + 合法状态机 + Mock + verify；默认本地 Commit**。
15. **版本号双轨控制与防漂移**：遵循 SemVer；Skill 自身三处强一致；交付 S/M/L 映射 PATCH/MINOR/MAJOR；API 与 DB 迁移版本防破坏。见 [version_control.md](references/version_control.md)。

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
| [references/opening_alignment.md](references/opening_alignment.md) | **新需求开场确认（复述/假设/约束/分级建议）** |
| [references/load_latch.md](references/load_latch.md) | **动手前装载门闩** |
| [references/right_sizing.md](references/right_sizing.md) | 变更分级 + work_mode（触 DB 变更 → 至少 M） |
| [references/grill_orchestration.md](references/grill_orchestration.md) | 审讯式 DESIGN 对齐（轮询不限次；MVP 范围裁定并入） |
| [references/confidence_decision.md](references/confidence_decision.md) | 设计多问 / 实现少问 / 跳过收紧 |
| [references/requirement_change.md](references/requirement_change.md) | **冻结后需求变更通道（变更请求单）** |
| [references/product_design.md](references/product_design.md) | **产品设计规范（设计语言 + 产品功能双支柱 · 产出纯净铁律）** |
| [references/product_roadmap.md](references/product_roadmap.md) | **MVP 范围裁定（并入产品设计沟通）与分阶段规划** |
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
