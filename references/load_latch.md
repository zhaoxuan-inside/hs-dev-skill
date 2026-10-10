# 装载门闩（Load Latch）— 反合理化 × Token 平衡

**何时读**：会话开工、切换任务、或想「跳过 Skill 直接干」时；每会话最多一次（极短，优先于大详规）。

问题：Superpowers 式「1% 可能适用就整份 invoke」能防偷懒，但会把多份 Skill 全文灌进上下文。  
本 Skill 的平衡：**强制便宜的门闩（索引查询 + 至多一份详规），禁止跳过门闩；禁止用门闩当借口整目录通读。**

---

## 1. 门闩步骤（动手前强制，≤5 步）

```text
L0  写 change_size=S|M|L 与 work_mode=DESIGN|IMPLEMENT（见 right_sizing / confidence_decision）
L1  路由：python scripts/skill_ref_index.py search --q <场景词> --limit 5
    或只读 references/_index.md 表格一行（二选一，勿两者都做）
L2  打开命中的恰好 1 份 references/*.md（本会话已读过的不重读）
L3  触达 UI/API 且本地 craft 不够用 → `rule_fetch` search/resolve（[`rule_library.md`](rule_library.md)），禁止预拉全部远程包
L4  项目文档：doc_index_db search|slice → context_pack；禁止整树 hs_dev_docs
```

**未完成 L0～L2 → 禁止**探代码开工、写 PRD 正文、或声称「先看看再说」。  
**≥1% 可能适用某详规** → 必须跑 L1；命中则 L2；未命中不得假装读过（强制的是门闩，不是灌全文）。

---

## 2. 反合理化表（出现即 STOP → 回 §1）

| 念头 | 现实 |
|---|---|
| 「太简单不用 Skill」 | 简单也要 L0 分级；S 路径正是为简单准备的 |
| 「先读代码再装载」 | 门闩在前；Skill 告诉你怎么读 |
| 「我记得流程」 | 流程会变；用 search/_index，勿凭记忆跳过 |
| 「先问用户再装载」 | DESIGN 多问可以，但先 L0～L2，否则问不到点上 |
| 「把 references 全打开保险」 | Token 违规；只开 1 份 + 按需 rule_fetch |
| 「远程规则库全拉下来」 | 只 resolve 命中 id，search 切片，禁止整包灌上下文 |
| 「实现期也按设计轨狂问」 | work_mode=IMPLEMENT 走少问闸门 |
| 「设计期少问省事」 | 模糊产品语义必须 DESIGN 多问或用户显式跳过 |

---

## 3. Token 预算挂钩（硬限制）

| 项 | 上限 |
|---|---|
| 开局装载 | SKILL 铁律（已在系统里）+ 门闩 + **1** 份详规 |
| S 会话 | 禁止再加载 lifecycle 全文 + 多份 craft |
| 远程规则 | 每次任务最多 **2** 个 source id 的缓存正文；优先 `rule_fetch.py search` 命中行段 |
| 重复阅读 | 本会话已读 path 禁止再 Read |

详见 [`token_budget.md`](token_budget.md)。

---

## 4. 与「强制装载」的关系（一句话）

- **强制的是门闩**（分级 + 索引路由 + 单份详规），不是强制灌入全部 references。  
- **若场景有 ≥1% 可能需要某详规**：必须跑 L1 检索；命中则 L2 打开；未命中不得假装读过。
