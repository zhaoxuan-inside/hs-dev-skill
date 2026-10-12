# 审讯式编排（Grill）— 设计对齐纪律

**何时读**：`work_mode=DESIGN`；需求/验收/边界模糊；用户说「对齐一下 / 帮我问清楚」；每会话最多一次。  
**分工**：本文 = **审讯式是什么 + 怎么跑**；闸门与少问 → [`confidence_decision.md`](confidence_decision.md)；分级 → [`right_sizing.md`](right_sizing.md)。

---

## 0. 是什么（融入本 Skill 的含义）

**审讯式编排**（社区口语 *grilling*，如 mattpocock `grill-me`）：Agent **不先写代码**，而是像严厉产品经理一样，按**设计树前沿**轮询用户，把未决产品语义逼成可冻结结论；通用工程问题自查自决，不问人。

**社区心智**：爆款 Skill 教 Agent「先对齐再动手」——用户主动 `/grill`，或 Agent 在 DESIGN 期自动进入同一套路。本 Skill **不另装第三方**，把同一心智写进 DESIGN 轨：多问 = 审讯式；IMPLEMENT = 少问闸门。

| 社区说法 | 本 Skill |
|----------|----------|
| grill / grilling | DESIGN 轨设计树澄清（§1） |
| grill-with-docs | 澄清时同步 PRD / 词典 / ADR 假设 |
| 跳过澄清（收紧） | 仅可跳过「可逆 + 不影响选型/契约」的工程偏好；见 confidence_decision §1.5 |
| 实现对齐后再 TDD | 冻结后 `work_mode=IMPLEMENT` + [`testing.md`](testing.md) |

---

## 1. 强制原则

1. **质量优先于速度**：未闭合的产品语义禁止假装冻结；分步问清 = 分步正确。  
2. **事实自查、决策问人**：代码/文档/工具能答的禁止问。  
3. **只问前沿**：前置未定的节点不提前问；每轮 2～5 题。  
4. **带推荐**：每题给推荐，让「好/yes」可落地。  
5. **跳过收紧**：用户说「跳过澄清」时，对照 [`confidence_decision.md`](confidence_decision.md) §1.5；命中禁止清单 → 拒绝跳过并继续审讯或 `BLOCKED`。  
6. **闭合才切模式**：核心场景 / DoD / 影响架构的约束齐且无冲突 → 宣布冻结 → `IMPLEMENT`。有 UI → 原型齐套（[`product_prototype.md`](product_prototype.md)）。

---

## 2. 运行步骤（DESIGN）

```text
G0  已过 load_latch L0～L2；本详规可作 L2
G1  列出设计树领地（见 confidence_decision §1.3），标「已定 / 前沿 / 未就绪」
G2  对前沿出题（格式同 confidence_decision §1.2）
G3  答复 → 补丁更新 PRD/词典/ADR 假设；重算前沿
G4  前沿空且冻结条件满足 → work_mode=IMPLEMENT；否则继续 G2
```

**S**：轻量审讯（DoD + 影响面 1～3 题）即可；勿空跑完整 PRD。  
**M/L**：触及产品语义则审讯至冻结门禁；可与阶段 0 合并，禁止「先选型再问需求」。

---

## 3. 领地速查（缺则入前沿）

- 是什么 / 为谁 / 成功与失败长什么样（含反目标）  
- 核心场景与 DoD；非目标  
- 权限、计费、归属、审计等业务特有规则  
- 对外契约与持久化是否牵动多端/迁移  
- 模块 seam：测什么界面、谁拥有不变量（见 [`deep_modules.md`](deep_modules.md)）  
- 模糊 UI：题材与受众先定，再方向取舍（见 [`frontend_aesthetic.md`](frontend_aesthetic.md)）  
- 有 UI：原型布局（用户提供或 Agent 生成 Mermaid 线框，见 [`product_prototype.md`](product_prototype.md)）  
- **MVP 裁剪与分阶段实施边界**：Must-have 核心假设 vs Phase 2/3 延期清单（见 [`product_roadmap.md`](product_roadmap.md)）  
- 商业计划：有则对照；无则跳过，不入阻断前沿  

---

## 4. 反模式

| 禁止 | 改为 |
|------|------|
| 一上来写实现再「顺便问」 | 先 G1～G3 |
| 问卷灌水（通用 REST/命名） | 自决；只问产品特有 |
| 用「行业常识」填产品空白后强行冻结 | 入前沿或记假设并标风险 |
| 用户一说跳过就冻结算选型 | 先过 §1.5 禁止清单 |
| 无原型（有 UI）进编码 | 生成 Mermaid 线框后再冻结 |
| IMPLEMENT 里继续审讯式狂问 | 回切 DESIGN 或走四条件闸门 |

实现期暴露产品空白 → **回切 DESIGN** 再跑一轮迷你审讯，禁止静默猜业务。
