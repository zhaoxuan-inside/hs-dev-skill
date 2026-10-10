# 前端手艺清单（本地高频 · 按需加载）

**何时读**：阶段 3/5 或 S/M 实现涉及 UI/组件/页面/样式时；每会话最多一次。  
**分层**：本文 = **高频必守**；更深社区规则 → [`rule_library.md`](rule_library.md) + `rule_fetch`（Vercel / Anthropic / Addy），禁止开局通读远程全文。

```bash
python scripts/rule_fetch.py search --q React
python scripts/rule_fetch.py resolve --id vercel.react-rules --rule async-parallel
python scripts/rule_fetch.py resolve --id anthropic.frontend-design
```

---

## 1. 开工前（≤1 屏）

1. 明确页面**单一工作**：首屏通常只要品牌/主标题、一句支持文案、一组 CTA、一块主视觉。
2. 有设计系统则跟 token；无则写 4～6 色 + 1～2 字体族 + 间距阶梯，再编码。
3. 模糊 UI：先 GitHub 高星对标 2 案，记「采纳/拒绝」各 3 点，禁止凭空套模板皮。
4. 产品语义未冻 → `work_mode=DESIGN` 多问；仅实现已冻视觉/组件 → `IMPLEMENT` 少问。

---

## 2. 反 AI 默认审美（出现即改）

| 避免 | 改为 |
|------|------|
| 紫靛渐变万能主题、奶油底+赤陶点缀、报纸细线密排 | 服务题材的明确方向 |
| 满屏同圆角卡片 + 同灰阴影 + 装饰渐变 | 按信息优先级排版；卡片仅用于可交互容器 |
| 首屏堆统计/日程/地址/促销条 | 首屏做一件事 |
| 英雄图上浮徽章/贴纸/chip | 英雄区干净 |
| Inter/Roboto/Arial 无理由堆叠 | 有性格的字体选择 |
| 每个 section 统一 fade-up | 至多 1 个编排入场 + 交互反馈动效 |

深化审美 / 文案语气：`resolve --id anthropic.frontend-design` 后用 `search-cache`，勿整篇粘进上下文。

---

## 3. 组件与状态

- 组合优于超大配置 props；展示与数据容器分离。
- 状态选型由简到繁：`useState` → 上提 → Context（读多写少）→ URL → 服务端缓存（Query/SWR）→ 全局 store。
- 必备状态：loading（骨架优先于转圈）、empty、error、success；权限不足单独处理。
- 交互元素用真正的 `button`/`a`；图标按钮补 `aria-label`；dialog 打开时焦点管理。

深化组件/表单：`resolve --id addy.frontend-ui`。

---

## 4. 可访问与响应式（底线）

- 对比度：正文 ≥ 4.5:1；不单靠颜色传达状态。
- 键盘可走完主路径；可见 `:focus-visible`；尊重 `prefers-reduced-motion`。
- 移动优先；关键断点自测约 320 / 768 / 1024。
- 表单：可见 label、明确错误与修复方式；CTA 动作用语一致（Publish → Published）。

合规复审：`resolve --id vercel.web-guidelines`。

---

## 5. React/Next 性能（高影响先做）

| 优先级 | 做 | 远程单条（示例） |
|--------|----|------------------|
| 关键 | 独立请求 `Promise.all`；避免无谓 await 瀑布；能同步判断的先判断再 await | `--rule async-parallel` / `async-defer-await` |
| 关键 | 禁止无树摇 barrel 大包；重组件 `dynamic`；分析/日志 hydration 后再加载 | `--rule bundle-barrel-imports` |
| 高 | RSC/服务端少传冗余 props；认证与 Route Handler 同等对待 | `--rule server-cache-react` |
| 中 | 派生状态在 render 计算；勿用 effect 同步可派生数据 | `--rule rerender-derived-state` |

完整规则名在 Vercel skill 的 `async-*` / `bundle-*` / `server-*` / `rerender-*`；**按名** `resolve --id vercel.react-rules --rule <name>`，禁止整读 `AGENTS.md`。

---

## 6. 交付自检（勾选即可）

- [ ] 无控制台错误；主路径键盘可达
- [ ] loading/empty/error 齐；真实文案长度下无溢出
- [ ] 跟项目 spacing/color/type token；无「万能 AI 皮」
- [ ] 关键路径无请求瀑布、无多余大包
