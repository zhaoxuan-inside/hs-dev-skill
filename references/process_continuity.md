# 过程连续性（plan_log / change_log / 续做 / 回退）

**何时读**：用户说「继续 / 继续任务 / 接着做 / resume」；中断后续做；任务或阶段回退；写计划步骤或登记变更。按 [变化感知协议](load_latch.md#5-变化感知与装载缓存统一重读规则) 复用已读规则；恢复时核对当前依赖摘要，仅变更或必要上下文丢失时恢复对应片段。**需求变更治理 → [`requirement_change.md`](requirement_change.md)**。
**分工**：状态合法迁移 → [`task_state_machine.md`](task_state_machine.md)；冻结/阶段链 → [`spec_driven_lifecycle.md`](spec_driven_lifecycle.md)。

---

## 0. 原则

1. **续做真理源** = `plan_log`（计划与断点）+ `change_log`（已落地变更账本），不是会话记忆，也不是 git 历史。  
2. **回退不依赖 git**：git 无法可靠「只撤销很久以前夹在中间的一次提交」；回退按 `change_log` 逆序恢复快照。  
3. **语义入口**：用户意图含「继续 / 接着 / 续做 / resume / 继续任务」等 → 先走 §2，禁止当新需求重开满配。  
4. **最小集**：过程目录只强制维护 `plan_log`、`change_log`、以及回退用的 `error_recovery/snapshots`；其余 `_06_todo` 等可选。

路径根：`hs_dev_docs/_06_dev_process/`。

| 目录 | 用途 |
|------|------|
| `_01_plan_log/` | 每任务一份计划：有序步骤 + 状态 + 当前断点 |
| `_02_change_log/` | 每任务 JSONL：每步变更的文件/文档清单 + 快照引用 |
| `_03_qa_log/` | **Q&A 决策日志**（审讯/开场确认/变更裁定问答与拍板，跨会话可追溯；使用 [`qa_log.md`](../resources/templates/process/qa_log.md)） |
| `_04_error_recovery/snapshots/{checkpoint_id}/` | 变更前文件副本（回退原料） |
| `_05_session_handoff/` | 可选补充；**续做不依赖它**，以 plan/change 为准；中断时可用 [`session_handoff.md`](../resources/templates/task/session_handoff.md) 整理交接 |

---

## 1. plan_log（计划账本）

文件：`_01_plan_log/{task_id}_plan.md`（模板见 `resources/templates/process/plan_log.md`）。

必填：

- `task_id`、`change_size`、`work_mode`、当前阶段（0～6 或 S/M 路径步）
- 有序步骤表：`step_id` / 描述 / `pending|doing|done|skipped` / 备注
- **断点行**：下一刀该做哪一步（续做入口只读此行 + 首个非 done 步骤）

规则：

- 建任务或进入阶段 4 时创建；之后每完成一步立刻改状态。  
- 禁止只改代码不改 plan_log。  
- CLI：`python scripts/process_log.py plan-show --id {task_id}`；`plan-set-step --id … --step … --status done`。

---

## 2. 续做（语义触发）

### 2.1 触发语（非穷尽，按意图）

继续、接着做、续做、继续任务、接着上次、resume、继续开发、把上次的做完……

### 2.2 强制步骤

```text
R0  语义判定为「续做」→ 本详规可作 L2（勿当新需求）
R1  process_log.py --root . resume-scan
    （列出 IN_PROGRESS/BLOCKED/VERIFYING 任务 + 各 plan 断点 + 最近 change 条）
R2  用户指定了 task_id → 用它；否则取唯一活跃任务；多个则简短列出请用户选一个
R3  读该任务 plan_log 断点 + 最近 ≤20 条 change_log；按需 slice 相关设计
R4  从断点下一步推进；禁止重做已 done 步骤，禁止忽略 BLOCKED 原因
```

合法停点仍适用（DESIGN 等待 / 冻结未过 / BLOCKED）。解除后立刻继续，勿空等第二次「请继续」。

---

## 3. change_log（变更账本）

文件：`_02_change_log/{task_id}_changes.jsonl`（一行一个 checkpoint）。

字段（最小）：

```json
{
  "checkpoint_id": "cp_20260328_153012_01",
  "task_id": "order_create",
  "at": "2026-03-28T15:30:12Z",
  "step_id": "S3",
  "summary": "实现 create_order 主路径",
  "paths": [
    {"path": "backend/order_service.py", "snapshot": "_04_error_recovery/snapshots/cp_…/backend__order_service.py"},
    {"path": "hs_dev_docs/_04_engineering_contract/_04_method_design/.../….md", "snapshot": "…"}
  ],
  "status_before": "IN_PROGRESS",
  "plan_step_before": "S3"
}
```

规则：

1. **改文件前**先 `process_log.py checkpoint --id {task_id} --step {step_id} --summary "…" --paths a,b`：对每个 path 若存在则拷入 snapshots（尚无文件则标记 `created: true` 无快照）。  
2. 再改代码/文档。  
3. 一步可多个 path；禁止「先改完再补账」。  
4. 索引：可用 `doc_index_db` 搜 change_log 摘要；勿整树通读。

---

## 4. 回退（非 git）

### 4.1 含义

将任务工作区恢复到某 `checkpoint_id` **之前**的文件内容，并回写 plan_log 步骤状态；**不**要求 `git revert` / `git rebase`。

可选：若用户同时要求 git 且该 checkpoint 恰有单 commit 对应，可额外本地 commit 记录回退——**git 只是附赠，不是回退引擎**。

### 4.2 步骤

```text
B1  process_log.py rollback --id {task_id} --to {checkpoint_id}
    · 逆序处理该 checkpoint 及之后的所有 change 条
    · 有 snapshot → 覆写回 path；created:true 且无 snapshot → 删除该 path
    · 将 plan 中受影响 step 标回 pending/doing；断点指到 --to 对应步
B2  任务状态：`rollback` 会尝试 `task_manager status --set IN_PROGRESS --force`
    （COMPLETED/ABORTED 先从归档拉回；日常推进禁止用 --force）
B3  追加一条 change_log：summary="ROLLBACK to {checkpoint_id}"，paths 记录本次恢复的 path
B4  向用户报告：恢复了哪些文件、当前断点、下一步
```

### 4.3 禁止

- 用「git 回退不到中间提交」拒绝用户回退请求——改走 change_log。  
- 无 change_log/快照时假装回退成功；应说明缺口并改为人工对照 plan 逐步撤销。  
- 只改任务状态、不恢复文件。

---

## 5. 与状态机、门闩

- 状态迁移合法表见 [`task_state_machine.md`](task_state_machine.md)。  
- 续做时 load_latch：L0 仍写/确认 `change_size`+`work_mode`（可从 plan 读取）；L1/L2 优先本详规。  
- 回退若暴露产品语义被撤掉 → 回切 `DESIGN` 并检查冻结门禁。

## 6. 与需求变更通道的分工

- **执行层**（本文）：断点、续做、快照回退；**需求层**（[`requirement_change.md`](requirement_change.md)）：冻结后需求变更治理（《变更请求单》+ 影响评估 + 开发者裁定）。  
- 变更确认后：先 `process_log.py checkpoint` 记录变更前状态，再落变更，保证可回退。
