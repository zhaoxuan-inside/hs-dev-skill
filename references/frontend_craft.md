# 前端手艺清单（本地高频 · 按需加载）

**何时读**：阶段 3/5 或 S/M 实现涉及 UI/组件/页面/样式/动效时；每会话最多一次。  
**分层**：**默认审美** → [`frontend_aesthetic.md`](frontend_aesthetic.md)；项目 `DESIGN.md` / 品牌对标 → [`design_md.md`](design_md.md)；本文 = **手艺与反 slop 高频**；更深 → [`rule_library.md`](rule_library.md) + `rule_fetch`。

```bash
python scripts/rule_fetch.py resolve --id local.frontend.aesthetic # 本地默认审美
python scripts/rule_fetch.py resolve --id local.design.md          # DESIGN.md 协议
python scripts/rule_fetch.py resolve --id anthropic.frontend-design # 远程原文（本地不够时）
python scripts/rule_fetch.py resolve --id voltagent.design-md --rule stripe
python scripts/rule_fetch.py search --q anti-slop
python scripts/rule_fetch.py resolve --id antislop.core
python scripts/rule_fetch.py resolve --id lottie.motion-design
python scripts/rule_fetch.py resolve --id vercel.web-interface
python scripts/rule_fetch.py resolve --id vercel.react-rules --rule async-parallel
```

**溯源**：[awesome-design-md](https://github.com/VoltAgent/awesome-design-md) · [google design.md](https://github.com/google-labs-code/design.md) · Anthropic / Addy / Vercel · [anti-slop](https://github.com/miqdadbadjuber/anti-slop) · [motion-design-skill](https://github.com/LottieFiles/motion-design-skill) · [ui-craft](https://github.com/educlopez/ui-craft)。

---

## 1. 开工前（≤1 屏）

1. **先审美后手艺**：无 `DESIGN.md` → 先 [`frontend_aesthetic.md`](frontend_aesthetic.md)；有则切片读项目根 `DESIGN.md`。品牌/气质远程对标见 [`design_md.md`](design_md.md)。
2. **题材锚定**：产品题材、受众、页面单一工作；视觉从题材语汇来，禁止「万能 SaaS 皮」。
3. **短计划对齐 token**：4～6 色 + 1～2 字体族 + 间距阶梯；有设计系统跟 token。计划像 AI 默认皮 → 先改计划。
4. **产品语义未冻** → `work_mode=DESIGN` 审讯式多问；视觉已写入 `DESIGN.md` 且仅实现 → `IMPLEMENT` 少问。
5. **品牌自测**：换掉 logo/产品名后是否仍有自己的性格？没有 → 太泛，重做方向。

---

## 2. 反 AI 默认审美与诚实内容（出现即改）

| 避免 | 改为 |
|------|------|
| 紫靛渐变万能主题、奶油底+赤陶点缀、报纸细线密排、酸绿暗底万能稿 | 服务题材的明确方向 |
| 满屏同圆角卡片 + 同灰阴影 + 装饰渐变/网格/玻璃堆叠 | 按信息优先级排版；卡片仅用于可交互容器；圆角按层级有级差 |
| 首屏堆统计/日程/地址/促销条；假终端/骨架块当产品图 | 首屏做一件事；真实内容或明确 `[PLACEHOLDER]` |
| 英雄图上浮徽章/贴纸/chip；每标题上 ALL-CAPS eyebrow | 英雄区干净；结构装置须携带信息 |
| Inter/Roboto/Arial/Geist 无理由堆叠；标题里单词异色/斜体强调 | 有性格的字体选择；标题整体一体 |
| 每个 section 统一 fade-up；glow/blob/mesh 无目的堆叠 | ≤1 个编排入场 + 交互反馈；装饰须能说出服务的层级/识别目标 |
| 假数据/假证言/未证实合规口号（「99.9%」「SOC2」等） | 无真实来源就不展示数字与证言（空优于骗） |
| 导航链到不存在的页；不能点的按钮/表单 | 导航=真实可达；交互元素有真实行为否则删除 |
| 「Get Started / Learn More」万能 CTA；营销空话 | 具体动作与结果用语；句子大小写为主 |

**目的测试**（anti-slop）：任何视觉手法先答「服务什么层级/识别/可读目标？」只有「看起来像 AI/很安全」→ 删或重做。  
深化：本地不够时 `resolve --id anthropic.frontend-design` 或 `antislop.core`，用 `search-cache`，勿整篇灌进上下文。

---

## 3. 组件、状态与文案

- 组合优于超大配置 props；展示与数据容器分离。
- 状态由简到繁：`useState` → 上提 → Context（读多写少）→ URL（筛选/页签/分页可分享）→ 服务端缓存（Query/SWR）→ 全局 store。
- 必备状态：loading（骨架优先于转圈）、empty（邀请下一步）、error（含修复方式）、success；权限不足单独处理。
- 交互用真正的 `button`/`a`；图标按钮补 `aria-label`；dialog 打开时焦点管理；破坏性操作需确认或可撤销。
- 文案：用户语言、主动语态、CTA 全流程同名（Publish → Published）；失败/空态给方向不给情绪。

深化组件/表单：`resolve --id addy.frontend-ui`。

---

## 4. 可访问、现代 Web 标准与合规（底线 · 融合 Modern Web Guidance）

- **现代 UI 与原生组件（反陈旧 Hack）**：
  - 弹窗与浮层必须使用原生 `<dialog>` 或 **Popover API**（自动处理顶层渲染 Top-layer、焦点陷阱 Focus Trap 与 Light Dismiss，禁止手写易漏焦点缺陷的 `z-index: 9999` div 遮罩）；
  - 响应式组件优先使用 **Container Queries (`@container`)** 实现内聚容器查询，而非粗暴监听全局窗口视口断点；
  - 巧用 CSS **`:has()`** 关系伪类与 `:user-valid` / `:user-invalid` 状态，替代大量冗余 JS DOM 监听。
- **视图过渡与流畅动效**：单页/跨页切换优先采用 **View Transitions API**（平滑布局变形，告别突兀闪烁）；滚动视差/渐入优先使用 CSS **Scroll-driven animations** 或 `IntersectionObserver`，严禁挂载昂贵的 `window.onscroll` 阻断主线程。
- **资源与渲染性能（CWV 优化）**：
  - 首屏核心图片标注 **`fetchpriority="high"`** 与明确 `width`/`height`（严格防范 LCP 迟滞与 CLS 布局抖动）；首屏外强制 `loading="lazy"` + `decoding="async"`；
  - 接口请求与大数据渲染优先结合 **Streams API** 与轻量 Web Worker，大列表强制虚拟滚动。
- **可访问性（a11y）底线**：
  - 对比度：正文 ≥ 4.5:1；大字 ≥ 3:1；不单靠颜色传达状态；
  - 键盘可走完主路径；可见 `:focus-visible`（禁止无替代的 `outline: none`）；尊重 `prefers-reduced-motion`；
  - 移动优先；关键断点自测约 320 / 768 / 1024；触控目标舒适（约 ≥44px）；注意 `safe-area`；
  - 表单：可见 label、`autocomplete`/正确 `type`；错误贴字段；提交后焦点首错；勿禁粘贴；
  - 排版细节：加载文案用 `…`；数字列 `tabular-nums`；标题可 `text-wrap: balance`。

合规复审：`resolve --id vercel.web-interface` · 遵循 Modern Web Guidance 最新标准。

---

## 5. 动效（有目的才动）

| 原则 | 要求 |
|------|------|
| 人格一致 | 每项目选一种动效人格（如 Corporate / Premium / Playful）并贯穿；默认 UI 偏 Corporate |
| 时长量级 | 微反馈 80–150ms；卡片 200–350ms；Modal 300–400ms；页转 400–600ms；入场略长于出场 |
| 缓动方向 | 入场 decelerate（ease-out）；出场 accelerate（ease-in）；禁空间位移用 linear |
| 属性 | 优先 `transform`/`opacity`；禁 `transition: all`；重要状态勿仅靠透明度 |
| 编排 | 同时运动元素 ≤ 约 1/3；stagger 总预算通常 <500ms；至多 1 个编排入场 |

深化：`resolve --id lottie.motion-design`（按需 `search-cache`）。

---

## 6. React/Next 性能（高影响先做）

| 优先级 | 做 | 远程单条（示例） |
|--------|----|------------------|
| 关键 | 独立请求 `Promise.all`；避免无谓 await 瀑布 | `--rule async-parallel` / `async-defer-await` |
| 关键 | 禁止无树摇 barrel 大包；重组件 `dynamic` | `--rule bundle-barrel-imports` |
| 高 | RSC/服务端少传冗余 props | `--rule server-cache-react` |
| 中 | 派生状态在 render 计算 | `--rule rerender-derived-state` |

完整规则名在 Vercel skill 的 `async-*` / `bundle-*` / `server-*` / `rerender-*`；**按名** `resolve --id vercel.react-rules --rule <name>`。

---

## 7. 交付自检（勾选即可）

- [ ] 无控制台错误；主路径键盘可达；对比度达标
- [ ] loading/empty/error 齐；真实文案长度下无溢出
- [ ] 跟项目 spacing/color/type token；无「万能 AI 皮」；假数据/死链已清
- [ ] 关键路径无请求瀑布、无多余大包；动效有目的且尊重减动
- [ ] （营销/落地页）品牌自测通过；数字与证言可核实
