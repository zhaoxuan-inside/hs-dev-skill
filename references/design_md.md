# DESIGN.md 视觉方向协议（本地高频 · 按需加载）

**何时读**：要落盘/更新项目根 `DESIGN.md`；用户说「像 Stripe/Linear…」或「极简/编辑风…」；品牌/审美族对标；每会话最多一次。  
**分工**：**默认审美纪律** → [`frontend_aesthetic.md`](frontend_aesthetic.md)（本地优先）；本文 = **何时写 DESIGN.md / 怎么对标远程品牌与气质**；手艺 → [`frontend_craft.md`](frontend_craft.md)。

```bash
python scripts/rule_fetch.py search --q DESIGN.md
python scripts/rule_fetch.py resolve --id voltagent.design-md-catalog      # 品牌目录（awesome-design-md）
python scripts/rule_fetch.py resolve --id voltagent.design-md --rule stripe
python scripts/rule_fetch.py resolve --id bergside.design-skills-catalog   # 审美族目录
python scripts/rule_fetch.py resolve --id bergside.design-skills --rule editorial
python scripts/rule_fetch.py resolve --id google.design-md-philosophy
python scripts/rule_fetch.py resolve --id google.design-md-spec
```

**溯源**：

| 库 | Stars（量级） | 用途 |
|----|---------------|------|
| [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) | ~12 万★ | **品牌** DESIGN.md（Stripe / Linear / Vercel…） |
| [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills) | ~3k★ | **审美族** DESIGN.md + SKILL.md（minimal / editorial…） |
| [google-labs-code/design.md](https://github.com/google-labs-code/design.md) | ~2.8 万★ | 格式规范 + 写作哲学 |

---

## 1. 宏观品味宪章与微观特性的两层解耦

| 文件 | 谁读 | 级别与生命周期 | 定义什么 |
|------|------|----------------|----------|
| **`DESIGN.md`（项目根）** | 设计向 Agent / 全局常驻 | **项目级 · 宏观品味宪章**（极度稳定） | **全站看起来与感觉如何**（具象参照物、隐喻、全站 Design Tokens、Anti-Slop 护栏、10 星体验） |
| `{feature}_prd.md` / `prototype.md` | 产品/前端 Agent | **特性级 · 微观施工图**（高频迭代） | **特定任务的交互与契约**（JTBD、首屏渐进披露、ASCII 线框、字段约束、Gherkin DoD，**声明 Inherits: /DESIGN.md**） |
| `AGENTS.md` / 本 Skill | 编码 Agent | 工具链与工程门禁 | 怎么建、怎么改、状态机、测试门禁与 Git 规范 |

**继承铁律**：无 `DESIGN.md` 时，先遵守 [`frontend_aesthetic.md`](frontend_aesthetic.md) 本地默认，并在阶段 0A 尽快落盘本项目根目录 `DESIGN.md`。后续所有特性的 PRD 与原型必须**显式声明继承根目录 `DESIGN.md`**，**严禁在具体特性中各自重新发明色彩、字体族或设计哲学**，彻底杜绝多特性品味漂移！有方向文件后，再叠 [`frontend_craft.md`](frontend_craft.md)。更多设计需要 → `rule_fetch`（Anthropic 原文 / 品牌库 / 审美族），禁止跳过本地默认直接通读远程。

---

## 2. 强制时机（UI 方向）

| 触发 | 动作 |
|------|------|
| 项目根已有 `DESIGN.md` | **必读**（或 `search-cache` 切片）；实现 UI 时以它为权威视觉契约 |
| 用户点名品牌 / 「像 X」 | `voltagent.design-md --rule <slug>` → 改编进本项目 `DESIGN.md` |
| 用户点名气质 / 「极简、编辑风、新粗野…」 | `bergside.design-skills --rule <slug>` → 改编；需要组件细则再拉 `bergside.design-skill-md` |
| 模糊 UI、无品牌、无设计系统 | 先 `frontend_aesthetic` 两遍计划；可选品牌/审美族 ≥1～2 对标 → 写出本项目 `DESIGN.md` 再编码 |
| 仅改交互/逻辑、视觉已冻 | 可不新写；仍遵守现有 `DESIGN.md` + `frontend_craft` |

禁止：无方向文件却大改营销/品牌 UI；禁止把对标当模板整页复制（学 token 与原则，不抄 logo/专有文案/像素级布局）。

---

## 3. 推荐结构（Stitch 九段 + Google token）

项目模板：[`resources/templates/design/DESIGN.md`](../resources/templates/design/DESIGN.md)。

**正文建议顺序**（可省略无关节，勿乱序堆砌）：

1. Visual Theme & Atmosphere（或 Overview）— **具体参照物**，禁「现代/干净/高级」空形容词  
2. Color Palette & Roles — 语义名 + hex + 用途  
3. Typography Rules — 族、层级、字距/行高  
4. Component Stylings — 按钮/卡片/输入/导航及状态  
5. Layout Principles — 间距阶梯、栅格、留白哲学  
6. Depth & Elevation — 阴影或色阶层级  
7. Do's and Don'ts — 硬护栏  
8. Responsive Behavior — 断点与触控  
9. Agent Prompt Guide（可选）— 给 Agent 的短提示词

**可选 YAML front matter**（Google 规范）：`colors` / `typography` / `spacing` / `rounded` / `components`；token 服务散文，散文才是灵魂。

---

## 4. 对标工作流

### 4a 品牌库（awesome-design-md）

```text
1) resolve voltagent.design-md-catalog
2) 选 ≥2 slug（stripe, linear.app, vercel, notion, apple…）
3) resolve --id voltagent.design-md --rule <slug>   # 每次 1 个；任务 ≤2 source
4) 摘采纳/拒绝 → 写入项目根 DESIGN.md（改色名、去品牌专属、贴合题材）
5) 再读 frontend_craft；编码时显式引用 DESIGN.md
```

### 4b 审美族库（awesome-design-skills）

```text
1) resolve bergside.design-skills-catalog（index.json）
2) 选气质 slug（minimal, editorial, premium, corporate, paper, neobrutalism…）
3) resolve --id bergside.design-skills --rule <slug>        # DESIGN.md 气质
4) （可选）resolve --id bergside.design-skill-md --rule <slug>  # Agent 组件/门禁细则
5) 同样改编进本项目根 DESIGN.md，禁止原样当产品身份
```

**怎么选库**：要「像某产品」→ 品牌库；要「某种风格气质」→ 审美族；两者可各取 1 案交叉，仍只落盘**一份**本项目 `DESIGN.md`。

落盘位置：**项目根 `DESIGN.md`**（大写）。有 `hs_dev_docs` 时可链过去，但 Agent 默认读根目录这份。

---

## 5. 写作红线（哲学蒸馏）

- **具体参照 > 形容词堆**：一句「1970 年代研究生讲义」胜过十个「专业、高级」。  
- **负向约束定义性格**：明确 Don't（禁 glow/万能紫/每节 fade-up 等）。  
- **对标是证据不是克隆**：换 logo 后仍应是**本产品**身份。  
- **无真实数字/证言不编造**（与 anti-slop 一致）。  
- DESIGN 期可多问视觉偏好；IMPLEMENT 期有 `DESIGN.md` 则少问，按文件执行。

---

## 6. 与 craft / 门闩

- 模糊 UI → 本文件（或已有项目 `DESIGN.md`）作 L2 详规之一；手艺细则另开会话再读 `frontend_craft`。  
- 远程禁止通读多品牌/多审美族；**按 slug resolve + search-cache**。  
- 每任务远程 source ≤2（见 [`rule_library.md`](rule_library.md)）。
