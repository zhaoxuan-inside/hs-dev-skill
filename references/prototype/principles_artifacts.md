# 0. 核心规则（为什么需要双轨线框？）

**何时读**：处理0. 核心规则（为什么需要双轨线框？）时；先沿用[入口公共约束](../product_prototype.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 0. 核心规则（为什么需要双轨线框？）

单纯的 Mermaid `subgraph` 只能表达“页面有哪些区块以及怎么跳转”（**拓扑关系**），却无法直观传达**界面的空间比例、主次视觉锚点、留白密度、控件相对位置与真实微文案**。因此，本规范强制采用**「Mermaid 区域/流转拓扑 + ASCII 空间比例线框图」双轨原型表达**：

1. **产出纯净性**：原型与设计语言文档专注刻画**视觉调性、Design Tokens、UX 认知四定律、组件六态与页面四态双轨线框**，严禁混入后端选型、数据库 DDL 或代码实现细节。
2. **商业计划可选**：`_01_product_vision/_03_business_plan/` 有则读入冲突扫描；无则跳过，不阻断。
3. **原型必有**：M/L 且触及 UI/信息架构/多屏流程时，冻结前必须存在承载设计语言与双轨布局的原型产物。
4. **用户未提供 → Agent 生成**；不得空着进选型/编码。
5. **三位一体原型表达（字符拓扑 + 物理标注 + 可交互 HTML 预览）**：
   - **轨 1（Mermaid 空间与交互拓扑）**：清晰表达页面壳层划分、多端布局容器（Web 栅格 / 桌面多窗格 / 移动端纵向流）、抽屉/弹窗唤起路径与导航跳转；
   - **轨 2（ASCII 空间比例线框图 · 融合 OpenPencil PenNode 语义）**：以字符网格精准还原首屏视觉层级（Primary/Secondary/Tertiary）、按钮具体文案、表格列与留白比例，内联物理参数标注（字阶/间距/Tokens）；针对专业设计交付场景，兼容 **OpenPencil PenNode Schema** 规范（Frame / Text / Component 语义层级与矢量坐标约束），支持批量设计 DSL 表达；
   - **轨 3（单文件可交互 HTML 预览 · 融合 Generative UI 动态仿真）**：
     - **落盘路径**：`hs_dev_docs/_02_feature_spec/_03_prototype_html/{feature}_prototype.html`（基于 `prototype_html_template.html` 生成）；
     - **极简独立**：零外部构建依赖，内联 Tailwind CDN + Google Fonts + 品牌 Tokens；**内网/离线环境无法访问 CDN 时，将所需样式内联为本地静态资源再交付，确保开发者双击可直读签收**；
     - **多端视口仿真**：顶部自带 1440px 桌面端 / 768px 平板 / 390px 移动端单键切换；
     - **动态交互与页面四态**：融合 Generative UI 交互组件规范，一键切换正常数据态 (Populated)、空白引导态 (FTUE)、加载骨架态 (Loading)、异常错误态 (Error)，支持表单与微动效的实时交互走查；
     - **真机/浏览器直读**：开发者直接在浏览器双击打开或本地预览，所见即所得进行可视化核准。
6. **开发者可视化确认机制 (Developer Visual Confirmation Gate)**：进入阶段 1 选型与代码开发前，开发者必须基于 HTML 预览与字符/Mermaid 线框完成可视化确认签收（Visual Sign-off），杜绝盲目编码与返工。**视觉签收只代表「好看」，业务语义（权限/规则/流程/Gherkin DoD）另有《冻结确认单》A 部分由开发者逐条确认**（见 [`product_design.md`](../product_design.md) §5.2 与 `resources/templates/process/freeze_signoff.md`）。
7. **S**：无 UI 语义变更可不写原型；一旦改布局/主路径 → 升 M 并补原型。

落盘：
- 文档规约：`hs_dev_docs/_02_feature_spec/_04_prototype_wireframe/{feature}_prototype.md`（含 Tokens、Mermaid、ASCII 标注、OpenPencil 节点映射、签收单）
- 可视化原型：`hs_dev_docs/_02_feature_spec/_03_prototype_html/{feature}_prototype.html`（可交互多端四态 HTML 预览，内嵌 Generative UI 交互部件）


---

## 1. 产物构成（设计语言 + 双轨功能原型 + 可视化确认）

模板：`resources/templates/product_design/prototype_template.md`。

| 模块 | 核心要求 |
|---|---|
| **视觉调性与隐喻** | 具体的参照物（非“现代/大气”空词）+ 内容密度取向（`Compact` / `Balanced` / `Airy`） |
| **Design Tokens** | 色彩（Primary/Secondary/Accent/Canvas/Semantic）、排版层级（含 `tabular-nums`）、间距步进、圆角与投影 |
| **多端适配规范** | 明确目标前端形态：**桌面端 (Desktop)** / **移动端 (Mobile)** / **Web 端 (Responsive Web)** 的断点与布局形态 |
| **UX 认知与可用性法则** | **渐进式披露**（首屏收拢低频项）、**视觉扫视动线**（F/Z 型与三级锚点）、**费茨与希克定律**、**真实微文案规范** |
| **组件全状态** | 核心组件（Button/Input/Drawer 等）必须定义 Default / Hover / Active / Loading / Disabled / Error 六态 |
| **双轨信息架构与线框** | **Mermaid 区域/流转拓扑** + **ASCII 空间比例线框图**（内联字体/间距/布局 UI Spec 标注） |
| **页面四态全覆盖** | **强制覆盖四态**：正常数据态 (Populated)、空白引导态 (Empty/FTUE)、加载骨架态 (Loading)、异常错误态 (Error) |
| **与 PRD / Gherkin DoD 映射** | 原型交互节点与 PRD 功能点及 Gherkin (`Given/When/Then`) 验收断言显式关联 |
| **开发者可视化确认签收** | 开发者对照原型完成 6 项可视化检查（布局/字体/热区/四态等）并签字 Sign-off，作为阶段 0 冻结硬前提 |

有用户提供的 Figma/截图/PDF：在文档中登记链接或仓库相对路径，并**用文字 + Tokens + Mermaid + ASCII 提炼核心设计语言与布局**（防链接失效、便检索与落地）。

---
