# 任务生命周期与状态机规范指南

**何时读**：建任务、改状态、回退重开、续做涉及任务态；每会话最多一次。  
**续做/回退账本** → [`process_continuity.md`](process_continuity.md)。

---

## 1. 状态机与合法迁移

```text
DRAFT ──► READY ──► IN_PROGRESS ⇄ BLOCKED
                      │     ▲
                      ▼     │（门禁失败）
                   VERIFYING
                    │     │
                    ▼     ▼
               COMPLETED  ABORTED
```

| 从 \ 到 | 合法下一态 |
|---------|------------|
| DRAFT | READY, ABORTED |
| READY | IN_PROGRESS, ABORTED, DRAFT |
| IN_PROGRESS | BLOCKED, VERIFYING, ABORTED, READY |
| BLOCKED | IN_PROGRESS, ABORTED |
| VERIFYING | COMPLETED, IN_PROGRESS, ABORTED |
| COMPLETED | ∅（终态） |
| ABORTED | ∅（终态） |

CLI 强制校验：

```bash
python scripts/task_manager.py status --id {id} --set VERIFYING
# 非法迁移会失败。仅 process_log 回退后重开可用：
python scripts/task_manager.py status --id {id} --set IN_PROGRESS --force
```

**禁止**：`READY → COMPLETED` 等跳步；用 `--force` 绕过日常推进。

### BLOCKED 与置信度决策

除依赖缺失外，以下必须 `BLOCKED`（或阶段 0–3 未建任务时等价暂停）：

1. **询问闸门触发**（见 [`confidence_decision.md`](confidence_decision.md)）；
2. **产品冻结未过**（见 [`spec_driven_lifecycle.md`](spec_driven_lifecycle.md)）；
3. **有 UI 却无原型齐套**（见 [`product_prototype.md`](product_prototype.md)）。

解除后**立即继续**至路径终点，禁止无确认事项时空等「请继续」。

---

## 2. 三文件强一致性 + plan_log

创建/流转/完成须同步：

1. `_00_task.idx`
2. `_01_task_brief/`
3. `_02_task_detail/`

并维护过程最小集（见 [`process_continuity.md`](process_continuity.md)）：

4. `_01_plan_log/{task_id}_plan.md`（`create` 时自动 ensure）
5. `_02_change_log/{task_id}_changes.jsonl`（改文件前 checkpoint）

---

## 3. 续做入口（语义，非 handoff）

用户说「继续 / 继续任务 / 接着做 / resume」等 →：

1. `python scripts/process_log.py resume-scan --root .`
2. 按 plan_log 断点 + change_log 续做  

handoff 仅为可选补充；**不以 handoff 为续做真理源**。

---

## 4. 回退（非 git）

```bash
python scripts/process_log.py rollback --id {task_id} --to {checkpoint_id}
python scripts/task_manager.py status --id {task_id} --set IN_PROGRESS --force   # 若已 COMPLETED
```

按快照恢复文件；git 可选附赠，不是引擎。
