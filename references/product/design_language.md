# 1. 第一层：宏观品味与全局设计系统宪章 (Project Taste Charter)

**何时读**：处理1. 第一层：宏观品味与全局设计系统宪章 (Project Taste Charter)时；先沿用[入口公共约束](../product_design.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 1. 第一层：宏观品味与全局设计系统宪章 (Project Taste Charter)

宏观品味定义产品的“灵魂与审美基准”，统一落盘于**项目根目录 `DESIGN.md`**（详见 [`design_md.md`](../design_md.md)），全项目唯一且常驻。

### 1.1 设计哲学与视觉调性 (Philosophy & Mood)
- **具象对标参照物**：禁止使用“大气、干净、现代、高级”等空洞形容词。必须给出具象对标或物理隐喻（如：“瑞士国际主义网格排版的高密度金融终端”、“复古温润纸张质感的沉浸式创作桌面”、“Linear 式克制深色高对比度工作台”）。
- **内容密度 (Density)**：明确界面的信息密度取向（`Airy` 宽松通透 / `Balanced` 均衡标准 / `Compact` 紧凑专业）。
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
   - **字阶梯次**：`Hero`: 40–56px；`H1`: 工作台 24px / 展示页 32–36px；`H2`: 工作台 20px / 展示页 24–28px；`H3`: 18–20px；`Body`: 14–16px（行宽约束 `60ch–75ch`）；`Caption`: 12–13px。
3. **空间与网格 (Spacing & Grid Layout)**：
   - 基于 4px / 8px 基础步进：`4px` (2xs)、`8px` (xs)、`12px` (sm)、`16px` (md)、`24px` (lg)、`32px` (xl)；容器最大宽度约束 `max-w-[1200px]` 或 `max-w-[1440px]`。
4. **圆角与投影高程 (Radius & Elevation)**：
   - 圆角梯度：小圆角 4px（输入框/徽标）、中圆角 8px（常规按钮/卡片）、大圆角 12–16px（模态弹窗/抽屉）；
   - 投影高程：`Flat` (1px 描边) → `Raised` (微卡片投影) → `Overlay` (下拉抽屉投影) → `Modal` (遮罩弹窗深投影)。

### 1.3 宏观品味底线与硬护栏 (Anti-Slop Taste Bar & Do's/Don'ts)
- **Do**：建立统一的 Design Tokens 并全站复用；首屏主操作按钮唯一显著；用真实业务样本数据检验布局（含超长名称与 0 数据）。
- **Don't**：严禁滥用廉价 AI 默认质感（如紫粉万能渐变、无意义的发光霓虹、每节盲目 fade-up 上浮、千篇一律的图标三列卡片）；严禁未定义对比度的低对比度灰字；严禁假数据与空洞文案堆砌。

---
