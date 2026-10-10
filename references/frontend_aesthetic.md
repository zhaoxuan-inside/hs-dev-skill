# 前端默认审美（本地 · Anthropic frontend-design 蒸馏）

**何时读**：新建/重塑 UI；无项目 `DESIGN.md` 或视觉模糊；DESIGN 期定审美方向；每会话最多一次。  
**分工**：本文 = **本地默认审美纪律**；项目身份落盘 → [`design_md.md`](design_md.md)；手艺/a11y/动效 → [`frontend_craft.md`](frontend_craft.md)；更多品牌/气质/更新原文 → `rule_fetch`。

```bash
python scripts/rule_fetch.py resolve --id local.frontend.aesthetic   # 本文
python scripts/rule_fetch.py resolve --id anthropic.frontend-design # 远程原文/增量（本地不够时）
python scripts/rule_fetch.py resolve --id voltagent.design-md --rule stripe
python scripts/rule_fetch.py resolve --id bergside.design-skills --rule editorial
```

**默认策略**：实现 UI 时**先遵守本文**；需要品牌克隆风向、审美族、或本地未覆盖的细则 → 再远程拉取（每任务 source ≤2）。

---

## 1. 角色与题材

把自己当作付费设计工作室负责人：客户已拒绝模板皮，要的是**有主见、可辨认**的视觉身份。  
题材、受众、页面主职未定时：先提案再确认（可走 [`grill_orchestration.md`](grill_orchestration.md)）。视觉选择必须来自题材语汇，禁止「万能 SaaS 皮」。

---

## 2. 核心原则（默认即执行）

1. **英雄区**：打开题材世界里最有特征的东西（标题/图/动效/演示/交互）；慎用「大数字+小标签+渐变点缀」万能首屏。  
2. **字体即性格**：1～2 族；刻意选择，勿默认 Inter/Roboto/Arial/Geist 堆叠；标题整体一体，禁止单词语异色/斜体强调。行长默认 <80 字符。  
3. **结构装置要有信息**：分割线、编号、eyebrow 等须编码信息；仅当内容真是序列时才用 01/02/03。  
4. **动效克制**：非用户触发的动效少而准；一次编排入场优于每节 fade-up；响应用户动作的反馈欢迎。  
5. **文案是设计**：用户语言、主动语态、CTA 全流程同名；空态/错误给方向；无真实来源不编数字与证言。  
6. **大胆用在一处**：一处记忆点，其余安静；出门前「摘一件配饰」。

---

## 3. 禁止当默认的 AI 皮（出现即改，除非 brief 点名）

| 集群 | 特征 |
|------|------|
| A | 暖奶油底(#F4F1EA 一带) + 高对比衬线 + 赤陶点缀 |
| B | 近黑底 + 单一酸绿/朱红点缀 |
| C | 报纸细线、零圆角、密栏 |
| D | 同圆角卡片墙 + 同灰软阴影 + 装饰渐变 |
| E | 万能铬：每标题 ALL-CAPS eyebrow、中点拼接元数据、`WORD — fragment`、近黑假黑、小标签等宽字体、按钮尾 `→` |

brief 明确要求某一集群时服从 brief；轴空闲时**禁止**把自由度花在上表默认上。另见 craft 反 slop 表。

---

## 4. 两遍流程（编码前）

```text
Pass1  短计划：4～6 色命名 hex + 字体角色 + 布局一句/ASCII + 独特性原则
Pass2  对照 brief：是否像「任意同类页」的默认稿？是 → 改计划并说明改了什么
然后   落盘/更新项目根 DESIGN.md（M/L 或首屏品牌向）→ 再写代码
       手艺与 a11y → frontend_craft
```

有项目 `DESIGN.md` → **以项目文件为权威**；本文作缺省与自检清单。

---

## 5. 远程何时拉

| 需要 | resolve |
|------|---------|
| 本地原则不够 / 要对齐上游原文 | `anthropic.frontend-design`（search-cache，勿整灌） |
| 「像某产品」 | `voltagent.design-md --rule <slug>` |
| 「某种气质」 | `bergside.design-skills --rule <slug>` |
| Web 合规复审 | `vercel.web-interface` |

禁止：跳过本文直接远程开写；禁止一次预拉多品牌全文。
