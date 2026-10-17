# 装载门闩（Load Latch）— 反合理化 × Token 平衡

**何时读**：会话开工、切换任务、或想「跳过 Skill 直接干」时；同内容同范围默认只装载一次，后续按 §5 感知变化后决定是否重读（极短，优先于大详规）。**新需求先跑 [`opening_alignment.md`](opening_alignment.md) O1～O4，再回本文 L0～L2。**

问题：Superpowers 式「1% 可能适用就整份 invoke」能防偷懒，但会把多份 Skill 全文灌进上下文。  
本 Skill 的平衡：**强制便宜的门闩（索引查询 + 至多一份核心详规 + 阶段链附属详规上限），禁止跳过门闩；禁止用门闩当借口整目录通读。**

---

## 1. 门闩步骤（动手前强制，≤5 步）

主 Skill 已先选定当前过程与触达功能，依 [子 Skill 协议](subskill_contract.md) 加载对应入口；下列检索只服务当前子 Skill。过程与功能入口不要求通读所有详规，未变化且当前上下文仍可用的已装载内容不重复加载；检测与恢复按 §5。

大规则按业务主题/阶段物理拆分，旧入口只保留公共约束和导航。当前主题已明确时直达 `_index.md` 命中的分册；公共约束尚未加载才补读入口，禁止递归加载其全部链接。分册分别登记摘要和范围，修改一册不让其他分册的装载记录自动失效；跨册依赖仍按实际影响核验。模板的 include 片段由工具组装，Agent 只读当前需要填写/审阅的主题，不为组装而通读所有片段。

```text
L0  开场确认（新需求）+ 判定意图与分级：
    · 新需求先跑 opening_alignment O1～O4（复述/假设/约束/分级建议，开发者确认）；续做语义跳过
    · 写 intent=BUILD|REVERSE|FIX|REFACTOR|EXPLORE|RESUME
    · 交付型（BUILD/REVERSE/FIX/REFACTOR）写 change_size=S|M|L 与 work_mode=DESIGN|IMPLEMENT
    · 只读型（EXPLORE）自动为 work_mode=READONLY（豁免任务三文件、PRD、Commit 与门禁）
    · 语义为「继续/继续任务/接着做/resume」→ intent=RESUME，沿用既有 plan_log，勿当新需求
L1  路由：python scripts/skill_ref_index.py search --q <场景词> --limit 5
    或只读 references/_index.md 表格一行（二选一，勿两者都做）
L2  打开命中的 1 份核心详规 + 阶段满配链附属详规（合计 ≤5 份；已读内容按 §5 检查后复用或增量重读）
    · 从零构建 / 完整特性 → `product_design.md` / `spec_driven_lifecycle.md` 导航，正文只取当前产品/生命周期业务分册
    · 已有项目反向重建 → `reverse_engineering.md`
    · Bug 修复 / 系统化排查 → `systematic_debugging.md`
    · 代码重构 / 消除坏味道 → `code_refactoring.md`
    · 代码理解 / 只读探查 → `code_exploration.md`
    · 继续 / 续做 / 回退 → `process_continuity.md`（并跑 process_log resume-scan）
    · 需求变更 / 冻结后变更 → `requirement_change.md`
    · DESIGN 审讯对齐 / grilling → `grill_orchestration.md`
    · 原型 / 线框 / 无图布局 → `product_prototype.md`
    · 测试 / TDD / seam → `testing.md`
    · 多语言代码规范 / Linter 门禁 → `coding_standards.md`
    · 深模块 / 重构接口 → `deep_modules.md`
    · 模糊 UI 默认审美 → `frontend_aesthetic.md`（项目已有 DESIGN.md 则切片读它）
    · UI 品牌对标 / 落盘 DESIGN.md → `design_md.md`
    · UI 实现手艺 / 反 slop → `frontend_craft.md`
    · 架构/范式选型（规模·类型）→ `dev_paradigm.md`（先于 DDD）
    · 已选 DDD / 限界上下文 → `ddd_design.md`
    · 后端分层 / 微服务 / Saga → `backend_arch.md`
    · 前端模块 / FSD → `frontend_arch.md`
    · API 契约 → `api_engineering.md`
    · 方法设计 / 契约画像 / 精准跑测 → `method_archetypes.md`
    · 任务状态迁移 → `task_state_machine.md`
L3  触达 UI/API/架构且本地不够用 → `rule_fetch`（书规则、FSD、wshobson、品牌 DESIGN.md…）；禁止预拉全部远程包
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
| 「需求一句话直接开干」 | 先 opening_alignment O1 复述 + O4 分级建议，开发者确认 |
| 「先写规格再确认理解」 | 理解错位时先对齐再写；规格建立在已确认理解上 |
| 「把 references 全打开保险」 | Token 违规；只开核心 1 份 + 阶段链附属（≤5 份）+ 按需 rule_fetch |
| 「远程规则库全拉下来」 | 只 resolve 命中 id，search 切片，禁止整包灌上下文 |
| 「实现期也按设计轨狂问」 | work_mode=IMPLEMENT 走少问闸门 |
| 「设计期少问省事」 | 模糊产品语义必须审讯式 DESIGN；跳过须过 confidence §1.5 |
| 「继续=当新需求重开」 | 续做走 process_continuity + plan/change |
| 「回退只能 git」 | 走 change_log 快照 rollback |
| 「先写完再补测」 | 质量优先；IMPLEMENT 走 testing 红绿，禁止事后仪式测 |
| 「审美先远程拉全文」 | 先 `frontend_aesthetic` 本地默认；不够再 rule_fetch ≤2 source |

---

## 3. Token 预算挂钩（硬限制）

| 项 | 上限 |
|---|---|
| 开局装载 | SKILL 铁律（已在系统里）+ 门闩 + 核心 **1** 份详规 + 阶段满配链附属详规（合计 **≤5** 份） |
| S 会话 | 禁止再加载 lifecycle 全文 + 多份 craft |
| 远程规则 | 每次任务最多 **2** 个 source id 的缓存正文；优先 `rule_fetch.py search` 命中行段 |
| 重复阅读 | 未变化、范围已覆盖且上下文仍可用则复用；变化/缺失才按 §5 重读必要片段 |

详见 [`token_budget.md`](token_budget.md)。

---

## 4. 与「强制装载」的关系（一句话）

- **强制的是门闩**（开场确认 + 分级 + 索引路由 + 核心单份详规），不是强制灌入全部 references。  
- **若场景有 ≥1% 可能需要某详规**：必须跑 L1 检索；命中则 L2 打开；未命中不得假装读过。

## 5. 变化感知与装载缓存（统一重读规则）

本节统一解释本包所有“每会话最多一次”“只读一次”“已读不重复”的说法：**相同内容、相同范围且当前上下文仍可用时只加载一次**，不是按文件路径永久禁止重读。开场充分确认、产品冻结和开发者验收要求不因此减少。

### 检查时点与两层检查

- 不在每轮对话、每个命令或每次提及文档时检查；只在该文档再次成为当前决策/执行依据时检查。
- 第一次加载时登记真实绝对路径、范围（整份或行段）、文件 SHA-256 和文件元数据；清单只证明曾输出该范围，不证明模型当前仍记得内容。
- 同阶段再次依赖时，先查元数据（设备/文件标识、大小、mtime_ns、ctime_ns）。未变化则复用，不读取正文；元数据变化后才由工具计算摘要。仅时间变化、摘要相同，不向模型再次输出正文。
- 已知编辑/替换/更新、恢复会话、阶段切换，以及实现/验收前的基线核验时，对**当前依赖文件**执行 `--verify-content`，即使元数据相同也核对 SHA-256。只输出结论，不输出正文。不轮询全包，也不扫描所有曾读文件。
- 元数据相同不构成绝对未变化保证（如部分文件系统时间精度、人工还原时间）；上述边界的摘要校验用于补足。读期间检测到文件变化或文件不可读/删除时返回 ERROR，停止受影响工作并重新定位，不沿用失效内容。

### 结果与重读范围

| 结果 | 动作 |
|---|---|
| `READ` | 尚未加载所需范围，按需读取该范围 |
| `REUSE` | 文件未变化；当前范围可用时直接复用，不输出正文 |
| `RELOAD` | 内容摘要变化，旧范围失效；定位变更后重读当前依赖片段，无法确定边界时重读当前章节，必要时才扩大 |
| `RESTORE_CONTEXT` | 内容可能未变，但压缩/截断后必要规则已丢失，按需恢复当前片段；不能把“以前读过”当作当前仍可用 |
| `ERROR` | 缺失、不可读、状态损坏或读取中变化；如实报告并修复，不能当作 REUSE |

同一文件未读过的新章节是新增范围，不能凭其他章节的读取记录跳过。工具保守按整文件摘要判变化，不判断语义差异或自动确定受影响章节；Agent 按差异/标题定位，默认不重读全文件。规则改动引发的产品基线/签收失效仍走原协议，缓存不自动刷新签收。

### 工具与会话状态

`scripts/read_cache.py` 提供只读 `check` 和输出片段后登记的 `load`。每个 Agent/会话使用独立状态文件（推荐宿主临时目录；Windows 使用系统临时目录），串行操作；不写入 Skill 安装目录或目标工程，不共享多个 Agent 的“已读”状态，不存正文。临时状态损坏使用新状态文件恢复必要范围，不静默判为已读。

```bash
# 示例状态名需替换为本 Agent/会话唯一值；路径换成真实绝对路径
python <安装根>/scripts/read_cache.py load --state /tmp/hs-read-<唯一会话ID>.json --path <文档绝对路径> --start 1 --end 40
# 同阶段再次依赖：元数据未变则不会读取正文
python <安装根>/scripts/read_cache.py check --state /tmp/hs-read-<唯一会话ID>.json --path <文档绝对路径> --start 1 --end 40
# 已知变更、恢复/阶段切换、实现/验收边界：只核对当前依赖的摘要
python <安装根>/scripts/read_cache.py check --state /tmp/hs-read-<唯一会话ID>.json --path <文档绝对路径> --start 1 --end 40 --verify-content
```

`check` 不写状态、不把新摘要记成“已读”；RELOAD 后只有实际 `load` 当前范围才更新记录，其他范围仍保留各自旧摘要、等待按需核查。工具的 `load` 输出若被截断或未进入模型上下文，不得声称装载成功，应缩小范围再加载。无工具读取的内容不能伪造登记；若需要机械变化追踪，首次读取直接使用 `load`，不先读一遍再用 `load` 重复读取。

上下文压缩时交接状态文件位置、依赖路径/范围、已读摘要及仍可用的关键约束。恢复时核对当前依赖摘要；只有必要规则缺失才传 `--context-missing` 并恢复相应片段。跨新会话默认使用新状态，除非有明确交接；磁盘上存在缓存不代表新会话已读取。
