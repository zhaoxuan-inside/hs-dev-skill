---
name: hs-dev-skill
description: >-
  Use for product project lifecycle & code engineering: supports full scenarios
  (BUILD new project, REVERSE brownfield onboarding, FIX systematic debugging,
  REFACTOR invariant-safe restructuring, EXPLORE read-only comprehension, and RESUME).
  Quality-first: grill DESIGN (skip tightly gated), tests first-class (zero errors),
  intent matrix + S/M/L right-sizing, PRD freeze, ADR, legal task transitions,
  SQLite packs, local Commit. First step: intent + change_size + work_mode.
license: MIT
compatibility: Requires Python >= 3.8 (stdlib sqlite3; Win/Linux/macOS)
metadata:
  author: hardstone
  version: "2.43.0.0"
---

# 产品开发 Skill (hs-dev-skill)

版本：v2.43.0.0  
核心定位：**全场景意图路由（BUILD 从零构建 · REVERSE 存量反向重建 · FIX 系统化调试 · REFACTOR 行为等价重构 · EXPLORE 只读代码理解 · RESUME 任务续做）+ 质量优先（分步正确 + 测试一等公民 · 测试零报错硬阻断交付 · 静态检测零告警零错误 · 数据驱动测试 DDT 与双轨制 E2E 规约 · 多语言编码规范与 Linter 门禁矩阵 · 全局统一术语与防歧义词典 Ubiquitous Language / 词态矩阵 Command/Event/Attribute / Search-Before-Name / 零裸字符串 Zero Magic Strings）+ 三层收口漏斗与抗脆弱机制（L0 物理代码真理 ➔ L1 文档业务契约 ➔ L2 顶层极速索引；符号锚点 Symbol Anchor 动态求值彻底消除静态行号漂移）+ 核心功能两级目录规约（一级功能 _01_ ~ _06_ + 二级子功能原子拆分，严格遵循 _01_xxx 顺序命名规则，彻底消除深层嵌套，实现 Domain+Category 二元高信噪比精准检索与极速切片装配）+ 全局文档阅读说明与直接索引罗盘（`hs_dev_docs/_00_docs_compass.md` 置顶 [VIBE_CONTRACT] 机器索引契约与 7 大域直接索引表 · 10 大专用 CLI 检索指令全景导航）+ 文档驱动（方法类型七分类 · 属性契约七维画像 · patternCluster 单向指针局部切片防破坏 · 物理行号实现后自动回填 · 精准测试分级矩阵 · 局部依赖拓扑 · 三段式修改原理 · 抗方法爆炸门禁与写前意图检索选型 `doc_index_db method-search`）+ 变更分级（S/M/L）+ 审讯式 DESIGN 对齐 + 强化产品设计（单文件可交互 HTML 原型预览 · 多端四态视口仿真 · 开发者签收门禁 · 宏观品味宪章与微观施工图两层解耦 · 一源双视图：面向人类《产品设计书》+ 面向 VibeCoding《机器执行契约》vibe_spec）+ 架构与模式设计（[VIBE_CONTRACT] 顶置切片 · GoF 23 种设计模式选型决策树 · 模式协同集群档案 · VibeCoding 防破坏三铁律）+ MVP 范围裁定（CEO 质疑式裁剪【开发者裁定】并入产品设计沟通审讯 · 团队胃口时间箱 · Day 1 垂直曳光弹切片）+ 垂直领域能力融合（OpenPencil 矢量规约 · Generative UI 动态交互仿真 · Modern Web Guidance 现代合规 · Chrome DevTools 运行态/CWV/a11y 质量门禁 · 专用 SDK 防腐 Adapter）+ 多端代码与构建产物强制收敛隔离（apps/ 与 output/ 强管控）+ 四段式多级版本控制（v[主版本].[需求版本].[修复版本].[打包版本] · 多级子版本号精确包区分）+ 工程附属机制全景治理支撑（环境配置与机密隔离 · 软件供应链与 CVE 阻断 · CI/CD 流水线与制品防伪 SBOM · 可观测性与三态健康探针 · 数据韧性与双向容灾回滚 · 安全防御与 PII 隐私脱敏 · Agent 执行安全沙箱护栏）+ 深模块词汇 + 本地默认审美 + 任务包编译装配 + 装载门闩 + 规则库远程按需 + 六元组；plan_log/change_log 续做与非 git 回退；默认本地 Commit**  
**替代**：原 `hs-project-skill` 已废弃，统一用本 Skill。

**装载门闩（反合理化 × Token）**：动手前必须完成 [`opening_alignment.md`](references/opening_alignment.md) 开场确认（新需求）与 [`load_latch.md`](references/load_latch.md) L0～L2（分级 + 索引路由 + **至多 1 份核心详规 + 阶段链附属详规总 ≤5 份**）。禁止「跳过 Skill 先干」；也禁止整目录通读。场景有 ≥1% 可能适用 → **必须跑** `skill_ref_index search`（或读 `_index` 一行），命中再打开。

---

## 核心驱动铁律

0. **质量优先（测试零报错硬阻断 + 静态检测零告警 + 全局统一定义单一事实源）**：分步的正确最大可能保证最终的正确；测试是一等公民（[`testing.md`](references/testing.md)）。全量测试必须 100% PASS 且 0 报错；静态代码检测（Linter / TypeChecker / 死代码扫描 / 多语言规范矩阵，见 [`coding_standards.md`](references/coding_standards.md)）必须 0 Warning 且 0 Error；强制执行**单一事实源与词态矩阵**（Command 动词原形 / Event 过去分词如 `order.updated` / Attribute `_at` 时间戳，严禁使用 `update` 或 `updated_at` 当事件名；严禁硬编码裸字符串；严禁发明同义词别名，见 `_02_project_word.dict.yaml`）；未达标前**绝对禁止**流转 COMPLETED 交付或执行 Commit（严禁向用户汇报「已完成但有若干报错待修」）；可演示但无测试证明的行为不算完成（S 无逻辑变更除外）。
1. **全场景意图路由与变更分级**：会话第一步判定 `intent=BUILD|REVERSE|FIX|REFACTOR|EXPLORE|RESUME`（[`right_sizing.md`](references/right_sizing.md)）。**新需求先跑 [`opening_alignment.md`](references/opening_alignment.md) 开场确认（需求复述 + 假设/空白 + 约束/干系人 + 分级建议，开发者确认）**，再写分级。交付型（BUILD/REVERSE/FIX/REFACTOR）写 `change_size=S|M|L` 与 `work_mode=DESIGN|IMPLEMENT`（[`confidence_decision.md`](references/confidence_decision.md)）；只读型（`EXPLORE`）自动锁定 `work_mode=READONLY`，仅检索切片回答，彻底豁免任务包、PRD、Commit 与门禁阻断（[`code_exploration.md`](references/code_exploration.md)）。禁止未分级按满配 0→6。不确定：`intent=BUILD`，`change_size=M`，`work_mode=DESIGN`。
2. **装载门闩**：未过 L0～L2 禁止探代码开工或写 PRD 正文（[`load_latch.md`](references/load_latch.md)）。语义为「继续/继续任务」时 L2 优先 [`process_continuity.md`](references/process_continuity.md)。
3. **持续推进**：除 DESIGN 前沿等待 / 实现期询问闸门 /（M/L）冻结未过 / `BLOCKED` 外禁止空转；确认后立刻继续至路径终点（测试全绿+静态零告警+门禁+归档+本地 Commit）。
4. **开场确认 + 审讯式对齐与方案比选后再编码**：新需求先走 [`opening_alignment.md`](references/opening_alignment.md)（需求复述 + 假设/空白 + 约束/干系人 + 分级建议，开发者确认）再进审讯；`DESIGN` 走 [`grill_orchestration.md`](references/grill_orchestration.md)（融合 `gstack /office-hours` 痛点拷问与 `superpowers` 多方案 Trade-offs 博弈）；**跳过澄清收紧**（不可逆/计费权限/对外契约/持久化/影响选型的产品空白 → 禁止跳过，见 confidence_decision）。**新增业务触达数据库设计必须经开发者决策**（不受置信度自决约束）。S 数行 DoD；M/L 阶段 0。
5. **单文件 HTML 可交互原型与多端可视化确认（开发者签收门禁）**：专业级产品与 UX 设计能力（[`product_design.md`](references/product_design.md) / [`product_prototype.md`](references/product_prototype.md)）；
   - **宏观品味宪章**：项目根目录 `DESIGN.md`（[`design_md.md`](references/design_md.md)）作为永久记忆，确立具象物理隐喻、Design Tokens、Anti-Slop 审美红线与 10 星标准；
   - **可交互 HTML 原型真理源**：有前端界面时，必须配套生成零依赖单文件 `{feature}_prototype.html`（内联 Tailwind CDN + 多端 1440/768/390px 视口切换 + 正常/空态/骨架/报错四态仿真），供开发者双击浏览器直读预览；
   - **多端字符与 UI 标注**：在 Markdown 原型中提供 Mermaid 空间拓扑与 ASCII 比例线框，融合 **OpenPencil PenNode 矢量层级** 与 **Generative UI 动态交互仿真**，内联标注**布局网格、字体字阶（含 tabular-nums）、间距步进与 Tokens**；
   - **开发者可视化确认签收**：进入技术选型与编码前，开发者必须基于 HTML 预览与字符规约完成 6 项可视化检查并签署 Sign-off (APPROVED)，杜绝盲目编码；
   - **微观特性设计与双视图**：声明 `Inherits: /DESIGN.md`，输出面向人类《产品设计书》（PRD + 原型）与面向 VibeCoding《机器执行契约》（`vibe_spec.md`：Tokens 映射/DOM 骨架/状态机/Gherkin DoD/硬护栏）；严禁技术细节反向侵入。
6. **MVP 范围裁定并入产品设计沟通（CEO 法则 · 团队胃口 · 垂直切片）**：**MVP 裁剪不再作为产品设计完成后的独立决策步**，而是在**产品设计沟通（审讯）阶段随 Q1 核心假设 / Q2 CEO 质疑式裁剪 / Q3 团队胃口一并提出，由开发者逐项拍板**（[`product_roadmap.md`](references/product_roadmap.md)）——**先定 MVP 范围，再写详细功能规格与原型**，严禁先全量设计再砍半造成返工；
   - **CEO 质疑式裁剪 (The Radical Cut · 质疑式裁剪)**：强迫单一核心假设，**禁止 Agent 擅自直接砍半**！Agent 站在 CEO 视角对所有非核心辅助功能发起**尖锐质疑**（质询其是否为 MVP 闭环必需、缺少是否致命），提出推荐裁剪清单与替代方案，**最终由开发者逐项确认与拍板裁定**；严守 **No Admin in MVP**（由开发者最终确认）；
   - **团队胃口 (Appetite)**：定界时间箱，执行断路器原则（砍功能保上线，绝不延期）；
   - **垂直曳光弹 (Tracer Bullet)**：规划 Day 1 贯通 UI+API+DB 的端到端首日冒烟切片，严禁水平脱节分层施工；
   - **范围先决（反返工）**：Q1/Q2/Q3 在详细规格**之前**完成裁定；**详细功能设计与整体交互逻辑只覆盖已确认的 MVP 范围**（[`product_design.md`](references/product_design.md)），据此**客观评估工程规模**后，方可进入阶段 1 技术选型（**先交互与功能，后技术选型**）。非 MVP 功能仅登记 MoSCoW 池，不写详细规格/原型。S 不写完整规划书。




7. **按路径设计与顶置契约切片**：L 须 1→2→3；选型（阶段 1）与架构（阶段 2）强制在**文档顶部 1～35 行置顶 `[VIBE_CONTRACT]` 机器执行契约**，隔离下半部人类论证与落选废案；涉及垂直领域 SDK（如 Gemini 大模型 API/Live、Android、Chrome 扩展 MV3）时必须建立防腐层（Adapter）；阶段 3（DB/API/六元组/方法设计）保持**天然人机同构不拆分**，依据 [`design_patterns.md`](references/design_patterns.md) 决策树选用设计模式，复杂模式必须建立模式集群档案（`_02_pattern_clusters/`），参与方法通过 `patternCluster` 挂载单向指针直达护栏，严禁全局通读；阶段 4 `task_context_pack` 编译装配 Vibe Spec + `[VIBE_CONTRACT]` 置顶切片。范式选型见 [`dev_paradigm.md`](references/dev_paradigm.md)；深模块见 [`deep_modules.md`](references/deep_modules.md)；设计模式选型见 [`design_patterns.md`](references/design_patterns.md)；UI 默认审美见 [`frontend_aesthetic.md`](references/frontend_aesthetic.md)；UI 手艺见 [`frontend_craft.md`](references/frontend_craft.md)（融合 Modern Web Guidance 铁律）；API 见 [`api_engineering.md`](references/api_engineering.md)。
8. **路径内单向门禁**：L=`0→1→2→3→4→5→6`；M/S 按 right_sizing。
9. **设计多问 / 实现少问 + 需求变更通道**：`DESIGN` = 开场确认（O1～O4）+ 审讯式澄清（跳过受 §4 收紧，**审讯轮询不受次数限制，问答落盘 `_03_qa_log/`**）；`IMPLEMENT` 仅四条件闸门才问（[`confidence_decision.md`](references/confidence_decision.md)）。实现中暴露产品空白 → 回切 DESIGN。冻结后需求变更 → 走《变更请求单》（[`requirement_change.md`](references/requirement_change.md)），**禁止静默改/静默砍**。
10. **续做 = plan_log + change_log**：语义「继续」→ `process_log.py resume-scan`；**回退不依赖 git** → `process_log.py rollback`（[`process_continuity.md`](references/process_continuity.md)）。
11. **状态机合法迁移**：禁止跳步；终态重开仅回退 `--force`（[`task_state_machine.md`](references/task_state_machine.md)）。
12. **实现必测、运行态干净与抗方法爆炸**：确认 seam → 垂直切片红绿重构（[`testing.md`](references/testing.md)）；**写前意图检索与抗方法爆炸铁律**：编写任何通用转换/计算/校验/适配方法前，严禁直接新建，必须先执行 `python scripts/doc_index_db.py --root . method-search --q <业务意图>` 召回候选，重合 ≥80% 强制复用或可选参数扩展，严禁影子函数；遵从深模块与三次原则，微小单次逻辑就地内联（[`method_archetypes.md`](references/method_archetypes.md) / [`coding_standards.md`](references/coding_standards.md)）；测试数据集（`_08_test_data`）支持 DDT 但严禁脆弱绝对相等，须 Schema Match + 核心不变量断言；Mock 聚焦外部 Adapter 环境；双轨制 E2E（开发走 Mock 冒烟，交付门禁直连容器/沙箱，严禁假 E2E）；提交前与阶段 6 必须 `make test` 100% 绿（0 报错）∧ 静态检测 0 告警 0 错误 ∧ `verify_consistency --strict`；前端集成 Chrome DevTools CDP 自动化排查、WCAG a11y 审计与 LCP/内存泄漏诊断门禁。改文件前先 `process_log.py checkpoint`。
13. **学习/偏好**：`~/.hs-dev-skill/`；`global_index_db.py search`，禁止整目录通读。
14. **模糊新技术/UI/架构**：GitHub 高星对标 ≥2；范式见 `dev_paradigm`；深模块见 `deep_modules`；前端结构见 `frontend_arch`；后端见 `backend_arch`；复杂域才读 `ddd_design`（远程按需）。
15. **三端**：`pathlib` + `python3`/`python`/`py -3`（[`cross_platform.md`](references/cross_platform.md)）。
16. **Token 与降噪（免全量扫描与精准索引收口铁律）**：门闩 + `doc_index_db` / `skill_ref_index` / `rule_fetch` → 切片 → context_pack；代码与文档探索**绝对禁止整目录通读大文件**，必须使用 `doc_index_db` 专属子命令按需召回：查需求走 `feature-search`、查页面拓扑走 `page-search`、查模式集群走 `pattern-search`、查库表DDL走 `schema-search`、查方法依赖/爆炸半径走 `dep-graph`、查方法防膨胀走 `method-search`、查测试单跑走 `test-search`、查审计历史走 `audit-search`、代码精准切片走 `symbol-slice`；禁止整树/`spec_v2_4`/远程规则包开局通读（[`token_budget.md`](references/token_budget.md) / [`four_level_routing.md`](references/four_level_routing.md)）。
17. **默认 Commit；明确要求才 push**。
18. **四段式多级版本号与包区分双轨体系（本地自治生成 + MMddHHmmss 时间戳）**：遵循 `v[主版本].[需求版本].[修复版本].[打包版本]`（`vMAJOR.FEATURE.PATCH.BUILD`）；Skill 自身三处元数据（metadata/正文/README）强一致；项目交付 S/M/L 映射 PATCH/FEATURE/MAJOR；**第四段打包版本严禁强依赖外部 CI/CD 流水线，必须由本地自主生成，且优先采用 `MMddHHmmss` 格式时间戳（10位月日时分秒）**（如 `python scripts/version_tool.py generate` 生成 `v1.2.0.1014172807`），单调自增、秒级防重、出包时间直观，并支持附加环境阶段（`-alpha`/`-beta`/`-rc`/`-ga`）与多端分包（`+web`/`+apk`/`+ipa`/`+desktop`/`+srv`）精准包区分；API/DB/Git Tag 严格按多级版本协同演化（[`version_control.md`](references/version_control.md)）。
19. **多端架构与产出收敛控制**：多端客户端工程（Web/移动端/桌面端）代码必须严格收敛于 `apps/<client>/`（`apps/mobile/`, `apps/desktop/`, `apps/web/`, `apps/server/`），跨端共享契约与数据模型收敛于 `packages/`，配置收敛于 `config/`（强制提供 `.env.example`，敏感变量绝不上库）；单工程或经典 Web 分离工程采用 `backend/` 与 `frontend/`；Web、桌面端（Desktop）、移动端（Mobile）打包产物必须通过脚手架配置重定向至根目录 `output/<client>/` 对应子目录，移动端发布包强制配对混淆符号表（Mapping/dSYM），严禁散落破坏工程整洁度。
20. **工程附属机制与功能模式启用控制（治理模式动态插拔 · CI/CD/可观测/数据韧性默认不启用）**：Skill 具备附属治理机制的**功能启用控制能力**（[`auxiliary_governance.md`](references/auxiliary_governance.md)），通过 `config/governance.yaml` 或 `python scripts/governance_toggle.py [status|enable|disable]` 按需插拔，拒绝无脑强塞重型负担；**默认启用轻量安全基线**（四段式版本控制 `version_control`、环境机密防泄漏 `env_and_secrets`、依赖锁一致性 `supply_chain_security`、安全防御与 PII 脱敏 `security_privacy`、Agent 行为护栏 `agent_guardrails`）；**明确不启用重型功能模式**（**CI/CD 流水线与制品防伪 `cicd_and_artifacts=false`**、**可观测性与运行时遥测探针 `observability_telemetry=false`**、**数据韧性与容灾回滚 `data_resilience_dr=false`**），项目有明确重型企业级需求时才显式开启。

---

## 执行流程（意图路由 + 变更分级）

```text
[新需求开场确认 O1～O4 ── opening_alignment] → [intent + change_size + work_mode] ── load_latch L0～L2
  ├─ BUILD (从零构建): 0→1→2→3→4→5→6 满配 (或 M/S 剪枝) → TDD → 门禁 → Commit
  ├─ REVERSE (反向重建): 资产扫描 → Schema/API提取 → 建立四级索引与词典 → 对齐门禁
  ├─ FIX (Bug修复): 根因假设 → 最小复现用例 RED → 精准修复 GREEN → 回归门禁 → Commit
  ├─ REFACTOR (代码重构): 固化行为保护网 → 消除坏味道/深模块提炼 → 零行为漂移验证 → Commit
  ├─ EXPLORE (代码理解): 索引检索 → 切片阅读 → 结构化输出业务图谱/时序解答 (纯只读免交付)
  └─ RESUME (任务续做): process_log resume-scan 恢复断点 → 沿既有 plan 继续至终点
```

**L 满配（BUILD）**：0 产品设计（开场确认 → 审讯含 MVP 范围裁定 → 设计语言 + MVP 内功能规格 + 冻结签收）+ 分阶段规划 → 1 选型 ADR（按当前阶段范围，末附选型拍板单）→ 2 架构（深模块词汇）→ 3 四要素（API/UI：aesthetic→DESIGN.md→craft / rule_fetch；**触达 DB 必先开发者决策**）→ 4 任务+pack+seam → 5 三同步+垂直 TDD → 6 测试全绿（0 报错）+ 静态检测零告警零错误 + 门禁 + 归档 + Commit。

**跃迁**：未分级/未过门闩禁止开工；L 的 0→1 须冻结门禁；M/S 禁止为空跑造空文档；`EXPLORE` 只读直通免门禁；`BLOCKED`→落盘→继续至终点。

---

## CLI 速查

| 工具 | 用途 | 示例 |
|---|---|---|
| `version_tool.py` | 四段式版本号自主生成 (MMddHHmmss 时间戳/多端后缀) 与解析 | `python scripts/version_tool.py generate --major 1 --feature 2 --patch 0 --client apk`<br/>`python scripts/version_tool.py now` |
| `governance_toggle.py` | 工程治理机制与附属功能模式动态启用/禁用控制 | `python scripts/governance_toggle.py status`<br/>`python scripts/governance_toggle.py enable cicd_and_artifacts` |
| `skill_ref_index.py` | Skill references 场景检索 | `python scripts/skill_ref_index.py search --q 幂等` |
| `rule_fetch.py` | 本地/远程领域规则目录与缓存 | `python scripts/rule_fetch.py search --q React` |
| `doc_index_db.py` | 7大底层数据真理与全维度索引检索切片 (免整盘扫描) | `python scripts/doc_index_db.py feature-search --q "登录"`<br/>`python scripts/doc_index_db.py page-search --q "结算"`<br/>`python scripts/doc_index_db.py pattern-search --q "Strategy"`<br/>`python scripts/doc_index_db.py schema-search --q "orders"`<br/>`python scripts/doc_index_db.py dep-graph --symbol "OrderService.create"`<br/>`python scripts/doc_index_db.py method-search --q "手机号脱敏"`<br/>`python scripts/doc_index_db.py symbol-slice --name "DocIndexDB"`<br/>`python scripts/doc_index_db.py embed-search --q "代码骨架提取"`<br/>`python scripts/doc_index_db.py test-search --q "checkpoint"`<br/>`python scripts/doc_index_db.py audit-search --since "2026-10-14"` |
| `global_index_db.py` | 全局偏好/学习标签 | `python scripts/global_index_db.py search --tag 反向代理` |
| `task_manager.py` | 任务三文件+合法状态机+看板渲染 | `python scripts/task_manager.py create --id x --title "…" --change-size M`<br/>`python scripts/task_manager.py dashboard --phase 3` |
| `code_skeleton.py` | AST/多语言代码骨架提取 (省 90% Token) | `python scripts/code_skeleton.py --path backend/` |
| `log_filter.py` | 测试与构建日志降噪过滤 | `python scripts/log_filter.py --cmd "make test"` |
| `process_log.py` | plan/change 续做与非 git 回退 | `python scripts/process_log.py resume-scan` / `checkpoint` / `rollback` |
| `verify_consistency.py` | 提交前门禁 | `python scripts/verify_consistency.py --root .` |
| `init_hs_dev_docs.py` / `init_hs_global.py` | 初始化项目文档 (支持 `--from-existing`、`--generate-guide` 生成阅读说明) / 全局区 | `python scripts/init_hs_dev_docs.py --from-existing`<br/>`python scripts/init_hs_dev_docs.py --generate-guide` |
| `hs_paths.py` / `idx_manager.py` / `dead_code_scanner.py` | 路径 / 索引 / 死代码 | 见各脚本 `--help` |

解释器：Linux/macOS `python3`；Windows `python` 或 `py -3`。

---

## 手册指针

- [`_index.md`](references/_index.md) · [`load_latch.md`](references/load_latch.md) · [`right_sizing.md`](references/right_sizing.md) · [`token_budget.md`](references/token_budget.md) · [`opening_alignment.md`](references/opening_alignment.md)（新需求开场确认：复述/假设/约束/分级建议）· [`requirement_change.md`](references/requirement_change.md)（冻结后需求变更通道）· [`intent_routing_and_gates.md`](references/intent_routing_and_gates.md)（流程全景：意图路由 + 阶段门禁 + 回环）· [`project_types.md`](references/project_types.md)（项目类型 P1~P6 判定 + 三件套清单组织规范）
- [`reverse_engineering.md`](references/reverse_engineering.md)（已有项目反向重建 · Schema/API 逆向与四级索引）
- [`systematic_debugging.md`](references/systematic_debugging.md)（系统化调试 · 科学假设 · 先红后绿 · 防退化门禁）
- [`code_refactoring.md`](references/code_refactoring.md)（代码重构 · 特征测试保护网 · 深模块演进 · 零行为漂移）
- [`code_exploration.md`](references/code_exploration.md)（代码理解 · 纯只读免交付 · 切片检索与图谱还原）
- [`grill_orchestration.md`](references/grill_orchestration.md) · [`confidence_decision.md`](references/confidence_decision.md)（审讯式 DESIGN / IMPLEMENT 少问；跳过收紧）
- [`product_design.md`](references/product_design.md)（设计语言与产品功能双支柱 · 产出纯净铁律）· [`product_roadmap.md`](references/product_roadmap.md)（MVP 范围裁定并入产品设计沟通 · 分阶段实施 · 人机交互对齐）· [`product_prototype.md`](references/product_prototype.md) · [`process_continuity.md`](references/process_continuity.md)
- [`testing.md`](references/testing.md) · [`quality_gates.md`](references/quality_gates.md) · [`coding_standards.md`](references/coding_standards.md) · [`deep_modules.md`](references/deep_modules.md)
- [`dev_paradigm.md`](references/dev_paradigm.md) · [`ddd_design.md`](references/ddd_design.md) · [`backend_arch.md`](references/backend_arch.md) · [`frontend_arch.md`](references/frontend_arch.md)
- [`frontend_aesthetic.md`](references/frontend_aesthetic.md) · [`design_md.md`](references/design_md.md) · [`frontend_craft.md`](references/frontend_craft.md) · [`api_engineering.md`](references/api_engineering.md) · [`rule_library.md`](references/rule_library.md)
- [`method_archetypes.md`](references/method_archetypes.md)（七大方法类型分类 · 七维契约画像 · 精准测试分级矩阵）
- [`design_patterns.md`](references/design_patterns.md)（GoF 23 种设计模式选型决策树 · 模式协同集群 · VibeCoding 防破坏红线）
- [`learn_and_prefer.md`](references/learn_and_prefer.md) · [`spec_driven_lifecycle.md`](references/spec_driven_lifecycle.md)
- [`six_tuple_runtime.md`](references/six_tuple_runtime.md) · [`four_level_routing.md`](references/four_level_routing.md) · [`doc_reading_guide.md`](references/doc_reading_guide.md)（项目文档阅读说明与跨 Agent 索引机制规范）
- [`task_state_machine.md`](references/task_state_machine.md) · [`mock_contract_guide.md`](references/mock_contract_guide.md)
- [`version_control.md`](references/version_control.md)（四段式版本控制 / 多级包区分 / 发布 Tag） · [`auxiliary_governance.md`](references/auxiliary_governance.md)（工程附属机制全景治理 / 环境机密 / 供应链 / CI/CD / 探针 / 容灾 / 隐私） · [`cross_platform.md`](references/cross_platform.md)
- [`spec_v2_4.md`](references/spec_v2_4.md)（争议按节；禁止开局通读）
- [`resources/rule_sources.yaml`](resources/rule_sources.yaml) · [`resources/templates/`](resources/templates/) · [`examples/order_service/`](examples/order_service/)
