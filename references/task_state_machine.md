# 任务生命周期与状态机规范指南

**状态与验收分离**：以下为任务工作状态。阶段验收状态按 [`stage_acceptance.md`](stage_acceptance.md) 独立记录；`COMPLETED` 迁移必须提供有效结构化验收记录、DoD 证据、开发者确认记录和已闭合的 REQ 项。CLI 校验这些字段，但不能鉴别签收记录是否真实来自开发者。

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

### COMPLETED 前置流转条件（硬阻断门禁）

任务从 `VERIFYING` 流转至 `COMPLETED` 必须满足以下门禁：
1. **全量自动化测试 100% 绿灯**（`make test` 0 失败、0 挂起）；
2. **严格质量门禁 0 错误 0 警告**（`verify_consistency.py --strict` PASS）；
3. **需求覆盖率 100%**：`task_detail` 中声明的所有原子需求（`REQ-*`）必须处于 `verified` 状态，严禁带未解决需求宣告成功。

此外，命令必须传 `--acceptance-record <workspace-relative-path>`。记录须包含已接受状态、开发者确认字段、测试命令/退出码/证据、逐项闭合的验收 checklist、带证据的 DoD 项，以及明确为空的未实现清单。CLI 会在归档前执行严格一致性校验；项目测试仍由项目自己的测试命令执行并记录。REQ 未闭合或 `--force` 都不能绕过完成门禁。示例：

```bash
python3 scripts/task_manager.py status --id {task_id} --set COMPLETED --acceptance-record <workspace-relative-acceptance-record.md>
```

### 步骤策略与副作用治理 (Step Policy & Side-Effect Strategy)

在 `task_detail.md` 的步骤 Checklist 中，为每一步标注执行属性：
- **`[idempotent: true|false]`**：标记操作是否具备幂等安全性。有副作用（写库/调用第三方付款）必须配对业务操作 ID 或幂等键；遇超时不可盲目重试，先查后断。
- **`[side_effect: none|local|external]`**：区分无副作用纯函数测试、本地文件生成与跨服务网络调用。
- **`[retry: N, backoff: exp]`**：瞬态网络异常按有限次数指数退避重试；格式或逻辑错误坚决就地修补，禁止机械重试。

---

## 2. 三文件强一致性 + plan_log

创建/流转/完成须同步：

1. `_00_task.idx`
2. `_01_task_brief/`
3. `_02_task_detail/`

任务简述与详情可分别参考 [`task_brief.md`](../resources/templates/task/task_brief.md) 和 [`task_detail.md`](../resources/templates/task/task_detail.md)。

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

---

## 5. 实时执行看板 (Live Dashboard)

通过 CLI 一键渲染包含当前阶段流转图 (Mermaid)、任务矩阵与门禁状态的 Markdown 看板，可直接输出为会话 Artifact：

```bash
python scripts/task_manager.py dashboard --intent BUILD --phase 3 --change-size M --output <artifact_path>
```

