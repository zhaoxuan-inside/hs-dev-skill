# 产品设计规范指南（宏观品味宪章 · 微观特性施工图 · 执行契约）

**何时读**：阶段 0 / `work_mode=DESIGN` / 需求规划 / UI 与功能设计；每会话最多一次。  
**核心分工**：
- **产品设计核心指南（本文）**：融合业界标杆（Google Labs `DESIGN.md`、YC `gstack` 品味评审、`pm-skills` 四层漏斗、`superpowers` 方案权衡），确立「**宏观品味宪章（项目级）与微观特性施工图（特性级一源双视图）两层解耦**」之铁律；
- **项目根设计系统宪章** → [`design_md.md`](design_md.md) + 根目录 `DESIGN.md`；
- **产品原型与双轨线框（Mermaid + ASCII）** → [`product_prototype.md`](product_prototype.md)；
- **MVP 裁剪与分阶段规划** → [`product_roadmap.md`](product_roadmap.md)；
- **设计对齐编排 (Grill)** → [`grill_orchestration.md`](grill_orchestration.md)；
- **前端默认审美与手艺** → [`frontend_aesthetic.md`](frontend_aesthetic.md) / [`frontend_craft.md`](frontend_craft.md)；
- **远程产品与 UX 规则按需拉取** → [`rule_library.md`](rule_library.md)（`gstack.office-hours` / `gstack.plan-design-review` / `deanpeters.pm-prd` / `uipro.ux-design`）。

---

## 0. 两层解耦体系与产出边界铁律

### 0.1 核心解耦架构：宏观品味宪章 vs 微观特性施工图
为了彻底杜绝**“讨论宏观被微观表单细节带偏”**以及**“每个小功能都自造调性导致品味漂移”**的两大通病，产品设计严格解耦为两个独立层级：

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 第一层：宏观品味宪章 (Project-Level Taste & Design System Charter)      │
│ · 载体：项目根目录 DESIGN.md + _01_product_vision/ (商业愿景与反目标)   │
│ · 频次：项目初始化或全局重构时建立一次，极度稳定                       │
│ · 内容：具象参照物、物理隐喻、Design Tokens、Anti-Slop 护栏、10 星体验  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼ 全项目所有特性严格声明 Inherits: /DESIGN.md
┌────────────────────────────────────────────────────────────────────────┐
│ 第二层：微观特性施工图 (Feature-Level Construction Specs & Contracts)   │
│ · 载体：一源双视图 (Human PDD/PRD + Machine Vibe Spec)                 │
│ · 频次：每个具体功能 (Feature) 迭代时高频输出                          │
│ · 内容：当前任务 JTBD 痛点、方案 Trade-offs、首屏 20% 披露、ASCII 线框、│
│         字段约束矩阵、状态机、Gherkin DoD，严禁重复定义全局哲学与色彩   │
└────────────────────────────────────────────────────────────────────────┘
```

### 0.2 产出边界铁律（绝对纯净原则）
**产品设计阶段（阶段 0）的产出只需要且必须包含两大核心支柱：**
1. **产品的设计语言与品味宪章 (Design Language & Taste Charter)**：继承根目录 `DESIGN.md` 的视觉调性与 Design Tokens，在特性中落实 UX 认知与可用性四定律（渐进式披露/视觉动线/费茨与希克定律/微文案规范）及组件六态；
2. **产品的功能与执行契约 (Features & Contracts)**：微观层 JTBD、核心交互方案比选（Trade-offs）、功能架构全景、双轨多态原型（Mermaid + ASCII 四态）、Gherkin 行为级验收标准 (`Given/When/Then`) 与工程规模客观评估。

> [!IMPORTANT]
> **严禁底层技术细节反向侵入产品设计**：
> 产品设计产出中**严禁**包含技术选型（如 MySQL vs PostgreSQL）、物理数据库 DDL 表结构、后端接口代码签名、内部六元组方法设计、分布式 Saga 补偿机制、代码单元测试覆盖率指标（如 85% 单测）等工程实现细节！  
> 技术架构与实现细节属于阶段 1（选型）至阶段 3（四要素详设）。产品设计只对**产品价值、用户体验、界面语言与功能规格**负责。

### 0.3 拒绝“填表式设计”：微观特性探索五步推演 (Feature Discovery)
针对当前特性动笔写功能列表或画线框前，Agent 必须先完成以下五项针对性推演：

| 推演维度 | 核心追问（借鉴 `gstack /office-hours` & `pm-skills`） | 产出要求 |
|---|---|---|
| **1. 现状与摩擦 (Status Quo)** | 用户今天没有本功能时，是如何凑合解决问题的（如手工表格/多系统切换）？最痛的摩擦成本在哪？ | 明确现状痛点与替代成本，拒绝臆造伪需求 |
| **2. 用户雇佣任务 (JTBD)** | 用户在什么情境下“雇佣”本功能？ | 标准句式：`When [特定触发情境], I want to [完成的核心动作], so I can [达成可感知的核心价值]` |
| **3. 惊喜时刻 (Aha Moment)** | 用户进入后，哪一个瞬间让他觉得比旧方式好十倍？如何在 **30 秒或 3 步内** 让他触达该时刻？ | 定义核心价值感知点与最短直达路径 |
| **4. 冷启动体验 (FTUE / Onboarding)** | 首次进入、数据完全为空时，第一分钟如何零门槛完成首次操作？ | 提供示例数据/模板一键载入/引导，严禁冷清死胡同 |
| **5. 形态方案比选 (Approaches & Trade-offs)** | 达成该目标有哪 **2～3 种差异化的产品/交互形态**？（如：主从抽屉式 vs 分步向导式 vs 极速命令流） | 对比各方案的心智负担与优劣（Trade-offs），给出明确推荐后再定稿 |

---

## 1. 第一层：宏观品味与全局设计系统宪章 (Project Taste Charter)

宏观品味定义产品的“灵魂与审美基准”，统一落盘于**项目根目录 `DESIGN.md`**（详见 [`design_md.md`](design_md.md)），全项目唯一且常驻。

### 1.1 设计哲学与视觉调性 (Philosophy & Mood)
- **具象对标参照物**：禁止使用“大气、干净、现代、高级”等空洞形容词。必须给出具象对标或物理隐喻（如：“瑞士国际主义网格排版的高密度金融终端”、“复古温润纸张质感的沉浸式创作桌面”、“Linear 式克制深色高对比度工作台”）。
- **内容密度 (Density)**：明确界面的信息密度取向（`Airy` 宽松通透 / `Balanced` 均衡标准 / `Dense` 紧凑专业）。
- **受众与主职 (Audience & Primary Job)**：明确界面的核心受众是谁、首屏第一核心任务是什么。

### 1.2 全局 Design Tokens 规范基准
设计语言必须建立在精确可落地的 Design Tokens 之上：
1. **色彩系统 (Color System)**：
   - **Primary (主色)**：品牌主色与核心视觉基准；
   - **Secondary (辅色)**：辅助平衡色；
   - **Accent / Tertiary (强调色)**：核心行为召唤色（CTA），严格执行**强调色预算**（首屏仅允许 3～5 处高亮）；
   - **Neutral / Surface / Background (中性底色与表面色)**：界面的画布底色与容器背景色；
   - **Semantic (语义功能色)**：Success (成功绿)、Warning (告警黄)、Error (错误红)、Info (信息蓝)；
   - **对比度合规**：文本与背景对比度必须满足 WCAG AA 级以上（常规文本 ≥ 4.5:1，大文本 ≥ 3:1）。
2. **排版字体层级 (Typography Scale)**：
   - **字体族**：Display / Sans（正文） / Mono（数据与代码），全站字体族 ≤ 2 种；数据的数字列强制启用 `tabular-nums`（等宽数字对齐）；
   - **字阶梯次**：`Hero`: 40–56px；`H1`: 32–36px；`H2`: 24–28px；`H3`: 18–20px；`Body`: 14–16px（行宽约束 `60ch–75ch`）；`Caption`: 12–13px。
3. **空间与网格 (Spacing & Grid Layout)**：
   - 基于 4px / 8px 基础步进：`4px` (xs)、`8px` (sm)、`16px` (md)、`24px` (lg)、`32px` (xl)；容器最大宽度约束 `max-w-[1200px]` 或 `max-w-[1440px]`。
4. **圆角与投影高程 (Radius & Elevation)**：
   - 圆角梯度：小圆角 4px（输入框/徽标）、中圆角 8px（常规按钮/卡片）、大圆角 12–16px（模态弹窗/抽屉）；
   - 投影高程：`Flat` (1px 描边) → `Raised` (微卡片投影) → `Overlay` (下拉抽屉投影) → `Modal` (遮罩弹窗深投影)。

### 1.3 宏观品味底线与硬护栏 (Anti-Slop Taste Bar & Do's/Don'ts)
- **Do**：建立统一的 Design Tokens 并全站复用；首屏主操作按钮唯一显著；用真实业务样本数据检验布局（含超长名称与 0 数据）。
- **Don't**：严禁滥用廉价 AI 默认质感（如紫粉万能渐变、无意义的发光霓虹、每节盲目 fade-up 上浮、千篇一律的图标三列卡片）；严禁未定义对比度的低对比度灰字；严禁假数据与空洞文案堆砌。

---

## 2. 第二层：微观特性施工图与执行契约 (Feature Construction & Contract)

微观特性在既定 `DESIGN.md` 框架下展开，**声明 `Inherits: /DESIGN.md`，专精于当前界面的交互、状态与业务边界，拒绝重复发明全局品味**。

### 2.1 UX 认知心理学与可用性四定律落地 (UX Usability Laws)
1. **渐进式披露 (Progressive Disclosure — 严控首屏负荷)**：
   - 首屏工作区只暴露 **80% 用户高频使用的 20% 核心控件**；
   - 高级筛选、低频配置与次要元数据收进**「高级筛选 ▾」折叠区、侧滑抽屉 (Drawer) 或二级浮层 (Popover)**。
2. **视觉层级与扫视动线 (Visual Hierarchy & Scanning Pattern)**：
   - 遵循人类 **F 型（列表/文档）或 Z 型（看板/营销）** 视觉扫视路径；
   - 每屏明确划分三层权重：**一级主锚点（Primary：唯一主标题 + 唯一高亮主 CTA）** → **二级核心内容（Secondary：核心数据卡片/表格主列）** → **三级辅助元数据（Tertiary：时间戳、状态辅文）**。
3. **费茨定律与希克定律 (Fitts's & Hick's Law)**：
   - 核心 CTA 保证充足可点击热区（桌面端高度 ≥ 36px，移动端触控区 ≥ 44×44px）；危险操作（如“删除”）移入二级菜单并保持安全间距；
   - 同一视觉分组内的主选项或导航项控制在 **≤ 5 个**，超出必须分组或提供即时过滤。
4. **真实界面微文案规范 (UX Microcopy & Honesty)**：
   - **行动按钮具象化**：禁止写笼统的“确定/提交”；必须使用**“具象动词 + 核心对象”**（如“立即发布商品”、“导出月度账单”）；
   - **报错文案可行动化**：必须包含**“原因 + 修复指引”**（如“库存数量必须为大于 0 的有效整数，请重新输入”）；
   - **零虚假占位符**：严禁出现 `Lorem ipsum` 或 `测试文本`，必须使用贴合真实业务的行业文字。

### 2.2 核心组件规范与全状态覆盖 (Component Specs & States)
所有核心交互组件（Button、Input、Card、Drawer 等）必须定义完整的**六态矩阵**：
- **默认态 (Default)**：正常静态展示；
- **悬停/聚焦态 (Hover/Focus)**：鼠标移入与键盘 Tab 聚焦的高亮反馈（2px focus ring 外发光描边）；
- **按压态 (Active)**：点击瞬时的微位移或按压色差；
- **加载态 (Loading)**：操作提交中的 Spinner 旋转或骨架屏（保持原按钮宽度防抖动）；
- **禁用态 (Disabled)**：不可操作状态（灰度降低、光标禁用 `cursor-not-allowed`，Tooltip 说明原因）；
- **错误态 (Error)**：校验未通过的警示色红框与原位内联错误提示。

### 2.3 核心方案比选与功能架构全景 (Trade-offs & Feature Architecture)
1. **核心交互形态比选（至少 2 种方案权衡）**：
   | 维度 | 方案 A（推荐采纳） | 方案 B（备选弃用） | 取舍理由 (Trade-off Decision) |
   |---|---|---|---|
   | **核心交互模式** | 例：单屏主从工作台 + 侧边抽屉即时预览 | 例：多页面跳转 + 独立详情页 | 方案 A 保持列表上下文不丢失，适合高频连续处理 |
   | **优势 / 劣势** | 切换零延迟，首屏信息密度略高 | 单页简单，但频繁跳转打断心流 | 通过渐进式披露化解方案 A 的密度压力 |

2. **功能架构全景树 (Feature Tree)**：
   使用 Mermaid 树状图划定业务模块边界（工作台、流转处理、统计配置）。

### 2.4 端到端用户核心旅程 (Core User Journeys)
梳理端到端核心旅程，强制覆盖**首次冷启动 FTUE 分支**、**常规主成功流**与**校验拦截原位恢复分支**。

### 2.5 界面信息架构与双轨多态原型 (Dual-Track Prototypes)
在原型设计中（详见 [`product_prototype.md`](product_prototype.md)），采用**「Mermaid 流转拓扑 + ASCII 空间比例线框图」双轨表达**，覆盖页面四态：
- **空白引导态 (Empty State / FTUE)**：引导插画、原因说明及「+ 创建首条记录 / 载入示例」主 CTA；
- **加载骨架态 (Loading State)**：1:1 比例脉冲骨架屏，消灭布局抖动 (CLS = 0)；
- **正常数据态 (Populated State)**：真实空间排布、主视觉锚点（★ 主 CTA）与折叠筛选；
- **异常错误态 (Error State)**：人话原因说明、保留用户已填草稿及原位「重新加载 / 重试」按钮。

### 2.6 详细功能规格矩阵 (Detailed Feature Specifications)
明确输入要素、触发前置条件、业务分支矩阵、默认值与边界极端异常。

### 2.7 整体交互逻辑网络与防丢失机制
- **路由与组件层级拓扑**：主列表 ↔ 右侧抽屉 (Drawer) ↔ 确认弹窗 (Modal)；
- **脏数据退出拦截**：用户在抽屉/弹窗中修改了表单但未保存时，点击遮罩或按 `Esc` 强制二次确认拦截（防止误触丢失工作成果）；
- **提交防抖锁定**：核心提交按钮 300ms–500ms 防抖锁定。

### 2.8 Gherkin 行为驱动产品验收标准 (Functional DoD)
采用 **`Given（前置情境）/ When（用户动作）/ Then（可观测界面结果）`** 编写，强制覆盖主成功流（Happy Path）、校验拦截与草稿保护流（Validation）、异常恢复流（Error Recovery）。

### 2.9 工程规模与复杂度客观评估 (Scale Assessment)
评估交互复杂度（轻/中/高）、数据规则规模（简/中/复）、通信实时性（标准/推送/协同），输出量化评级，作为阶段 1 技术选型的输入约束。

---

## 3. 产出文档结构与“单一真实源 · 双重视图”落地约定

```text
hs_dev_docs/_01_product_design/
├── _00_product_design.idx                 # 索引文件
├── _01_business_plan/                     # 【第一层：宏观愿景】商业模式、用户客群主职、战略反目标
├── _02_product_design/                    # 【第二层：微观施工图与契约】
│   ├── {feature_name}_prd.md              # 视图一（面向人）：产品功能规格书（JTBD/方案比选/规格矩阵/规模评估，声明 Inherits: /DESIGN.md）
│   └── {feature_name}_vibe_spec.md        # 视图二（面向 VibeCoding）：机器执行契约（Tokens代码映射/组件树DOM骨架/状态机/Gherkin）
├── _03_product_figma/                     # 【第二层补全：双轨原型】
│   └── {feature_name}_prototype.md        # 原型施工图：Mermaid 拓扑 + ASCII 空间比例四态线框（声明 Inherits: /DESIGN.md）
└── _04_phased_roadmap/                    # 【演进规划】
    └── {feature_name}_phased_plan.md      # MVP 假设、人机交互对齐记录、MoSCoW 分级矩阵与路线图
```

同时，在项目根目录维护 **`DESIGN.md`**，作为全局宏观品味与 Design Tokens 的单一真实源。

---

## 4. 全量产品设计后的下一步：MVP 与分阶段实施

全量产品设计完成后，**绝对禁止一次性全量研发 (Big Bang)**。
必须紧跟 **MVP 裁剪与分阶段实施规划（详见 [`product_roadmap.md`](product_roadmap.md)）**：
1. **触发人机交互对齐**：Agent 向人类决策者提出 Q1 核心假设、Q2 范围裁剪与 MoSCoW 分级、Q3 里程碑；
2. **落盘规划书**：输出《产品开发分阶段规划书》(`{feature_name}_phased_plan.md`)；
3. **锁定研发范围**：后续阶段 1（选型）至阶段 6（交付）**严格收敛于当前阶段（Phase 1 MVP）**，坚决不超前开发。

---

## 5. 阶段 0 产品评审与冻结门禁 (Product Review & Freeze Gate)

### 5.1 产品与体验 10 维自审标尺（借鉴 `gstack /plan-design-review`）
1. **宏观品味合规**：根目录是否存在 `DESIGN.md`？特性是否显式声明继承它，杜绝私自造调性？
2. **痛点与 JTBD 真伪**：是否写清了现状替代方案（Status Quo）与具体 JTBD？
3. **Aha Moment 与冷启动 (FTUE)**：新用户进首屏为空时，是否有清晰引导在 3 步内体验核心价值？
4. **方案博弈 (Trade-offs)**：核心交互模式是否对比过 ≥2 种形态并给出决策理由？
5. **渐进式披露与视觉动线**：首屏是否收拢了次要项？是否有唯一主视觉锚点与清晰的三级层次？
6. **双轨原型表现力**：是否同时提供了 Mermaid 流转拓扑与 **ASCII 比例线框图**？
7. **页面四态与组件六态**：Empty / Loading / Populated / Error 四态是否齐备？异常时是否保护已填草稿？
8. **真实微文案 (Microcopy)**：按钮是否为具象动词？报错是否提供人话修复建议？零 `Lorem ipsum`？
9. **Gherkin 验收标准 (`Given/When/Then`)**：DoD 是否全部转化为可观测的用户交互断言？
10. **绝对纯净无技术污染**：PRD 中是否 100% 剔除了数据库 DDL、代码签名、Saga 与单测指标？

### 5.2 阶段 0 冻结门禁表

| 校验维度 | 通过条件 |
|---|---|
| **宏观品味宪章就绪** | 项目根目录存在 `DESIGN.md`，定义了具象参照物、Design Tokens 与 Anti-Slop 护栏； |
| **一源双视图齐套** | 特性级存在面向人的 `{feature}_prd.md`（+双轨原型）与面向机器的 `{feature}_vibe_spec.md`，均显式声明继承 `DESIGN.md`，无语义冲突； |
| **产品探索与方案比选完备** | 明确定义了 Status Quo、JTBD、Aha Moment、FTUE 冷启动引导及 ≥2 种交互形态的 Trade-offs 比选； |
| **功能与双轨交互完备** | 功能架构树、端到端旅程（含 FTUE）、详细规格矩阵清晰；双轨原型（Mermaid 拓扑 + ASCII 比例线框）覆盖四态；DoD 采用 Gherkin (`Given/When/Then`) 行为断言； |
| **分阶段规划与规模评估就绪** | 完成人机交互对齐，`_04_phased_roadmap/` 存在《产品开发分阶段规划书》，MVP 范围明确，完成客观规模评估； |
| **纯净无技术侵入** | 严格杜绝在阶段 0 文档中提前塞入底层选型、物理表 DDL、RPC 签名、Saga 补偿、代码单测覆盖率等实现细节； |
| **无冲突一致性** | PRD 内部及与设计语言、原型、规划书、既有资料之间无未裁决矛盾。 |

门禁通过后，正式冻结阶段 0，进入技术选型与 ADR 阶段（按当前阶段范围收敛实施）。
