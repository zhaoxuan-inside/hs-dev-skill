# 开发范式选型（本地高频 · 指导设计）

**何时读**：阶段 1～2 写架构前；新开产品/大改边界；团队规模或产品形态变化；每会话最多一次。  
**分工**：本文 = **先选范式**；选中后再打开子集详规。DDD 只是复杂领域的一种选项，**禁止默认上 DDD**。

```bash
python scripts/rule_fetch.py search --q 范式
python scripts/rule_fetch.py resolve --id local.dev.paradigm
python scripts/rule_fetch.py resolve --id local.ddd.design          # 仅当范式含 DDD
python scripts/rule_fetch.py resolve --id local.backend.arch
python scripts/rule_fetch.py resolve --id local.frontend.arch
```

---

## 1. 先判规模与类型（落盘 3～6 行）

在 ADR / 架构文首写：

| 维度 | 取值（示例） |
|------|----------------|
| **产品规模** | 原型 / 小（单人～3）/ 中（一队）/ 大（多队或多域） |
| **变更档** | 跟会话 `change_size=S\|M\|L`（S 不新建范式文档） |
| **产品类型** | 见 §2 |
| **复杂度信号** | 规则密度、集成数、一致性要求、读写比、实时性 |
| **选定范式** | 后端 + 前端各写一条；「为何不选更高档」一行 |

不确定：规模取**更小**、类型取**更简单**；禁止「保险起见上完整 DDD/微服务」。

---

## 2. 产品类型 → 默认范式

| 类型 | 典型信号 | 后端默认 | 前端默认 | 何时升级 |
|------|----------|----------|----------|----------|
| **工具 / 脚本 / CLI** | 无长期域模型 | 过程式 / 薄分层 | 无或单页 | 几乎不升 |
| **营销站 / 内容站** | 展示为主 | 薄 API 或 SSG/CMS | 按页 + `DESIGN.md` | 有会员交易再升 |
| **CRUD / 后台管理** | 表单、列表、权限 | **事务脚本 + 简单分层** | 按资源/页面模块 | 出现复杂状态机 → 轻量领域 |
| **标准 B2B/B2C 产品** | 多模块、中等规则 | **模块化单体 + 用例层** | Feature 按业务模块 | 核心域规则密 → 轻量/完整 DDD |
| **复杂业务域** | 多模型、术语冲突、跨域集成 | **DDD（轻量或完整）+ 模块化单体** | Feature↔上下文 或 FSD | 独立部署硬需求 → 微服务 |
| **高并发读写分离 / 强审计** | 读模型多、事件重建 | CQRS（± 事件溯源） | 读侧 BFF/投影 | 默认不上；ADR 举证 |
| **实时协作 / 流式** | WS、低延迟 | 事件驱动 + 清晰边界 | 本地状态机 + 同步层 | 与域复杂度正交 |
| **数据管道 / 批处理** | ETL、作业图 | 管道/作业编排，非 DDD | 运维 UI 即可 | — |
| **库 / SDK / 组件包** | 对外 API 稳定 | 小核心 + 清晰公共面 | 若有 demo 站跟 craft | 勿套产品分层仪式 |

原则：**类型定底色，规模与复杂度信号决定是否升级**；升级要写「触发信号」，降级写「为何够用」。

---

## 3. 后端范式阶梯（由简到繁）

| 阶 | 范式 | 何时 | 详规 |
|----|------|------|------|
| B0 | 过程式 / 单模块 | 原型、工具、一周内验证 | 无；直接实现 |
| B1 | 事务脚本 + 简单分层（Controller→Service→Repo） | CRUD/后台为主 | `backend_arch` 轻用分层 |
| B2 | 用例层 + 模块化单体（按业务分包） | 标准产品默认 | `backend_arch` |
| B3 | Hexagonal / Clean（端口适配器） | 核心可测、外部多变 | `backend_arch` + `wshobson` / `clean-arch` |
| B4 | **DDD 轻量**（统一语言 + 聚合/不变量） | 状态机/不变量明显，上下文少 | [`ddd_design.md`](ddd_design.md) |
| B5 | **DDD 完整**（战略 BC + 映射 + 战术齐全） | 多团队/多模型/集成多 | `ddd_design` + 书规则 |
| B6 | 微服务 / 事件驱动拆分 | 部署、扩展、团队**硬边界**已具备 | `backend_arch` + microservices |
| B7 | CQRS / 事件溯源 | 读写显著分离或强审计重建 | 远程 `wshobson.cqrs` 等；勿默认 |

跨阶禁止跳跃：未稳定在 B2 前不上 B6；未切清边界前不上微服务。

---

## 4. 前端范式阶梯

| 阶 | 范式 | 何时 | 详规 |
|----|------|------|------|
| F0 | 单页 / 按路由文件 | 落地、demo、极小工具 | `design_md` + `frontend_craft` |
| F1 | 按页面/资源目录 | CRUD 后台 | 同上 |
| F2 | **按业务 Feature 模块** | 标准产品默认 | [`frontend_arch.md`](frontend_arch.md) A |
| F3 | Feature ↔ 后端模块/上下文对齐 | 已选 B2+ 或 B4+ | `frontend_arch` +（若 DDD）`ddd_design` |
| F4 | Feature-Sliced Design | 多域长期演进 / 多前端团队 | `frontend_arch` B + `fsd.skill` |

小项目禁止全套 FSD；无领域模型时不要伪造「限界上下文」目录名。

---

## 5. 规模 × 复杂度 快查

| | 规则少 / CRUD | 中等用例 | 高规则 / 多模型 |
|--|---------------|----------|-----------------|
| **小团队** | B1 + F1 | B2 + F2 | B4 + F3（慎上 B5） |
| **一队中型** | B2 + F2 | B2/B3 + F2/F3 | B4/B5 + F3 |
| **多队 / 多域** | B2 分包清晰即可 | B3/B5 + F3/F4 | B5（±B6）+ F4 |

`change_size`：S 不改范式；M 只在触达模块内微调；L 阶段 1～2 **必须**落盘选定阶与理由。

---

## 6. 设计产出（阶段 2 入口）

模板：[`arch_design_template.md`](../resources/templates/architecture_design/arch_design_template.md)。

- [ ] 产品类型 + 规模 + 复杂度信号  
- [ ] 后端阶（B0～B7）与前端阶（F0～F4）及「不升级」理由  
- [ ] 模块/边界图（非 DDD 时用模块图即可；选了 DDD 再补 BC 图）  
- [ ] 再按需打开：`ddd_design` / `backend_arch` / `frontend_arch` / `api_engineering`  

```text
[类型+规模] → 选定 B阶/F阶 → 写 ADR 一行
    → 若含 DDD → ddd_design
    → 分层/部署 → backend_arch
    → 前端结构 → frontend_arch
    → 契约 → api_engineering
```

---

## 7. 反模式

| 反模式 | 改为 |
|--------|------|
| 默认完整 DDD / 微服务 | 按 §2～§5 降到够用的最低阶 |
| 用文件夹假装 BC，无统一语言 | 要么真做 B4+，要么退回 B2 业务模块 |
| CRUD 后台套聚合根/仓储仪式 | B1 |
| 未稳定单体就拆微服务 | 先 B2/B5 边界清晰 |
| 前端 FSD + 后端无边界 | FE/BE 同阶对齐，或显式 BFF |

深化（每任务 ≤2 source）：`ciembor` / `wshobson` / `fsd.skill` / `muthub.c4designer` — 见 [`rule_library.md`](rule_library.md)。
