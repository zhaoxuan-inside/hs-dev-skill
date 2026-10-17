# Skill 执行轨迹（Trace）详规

**何时读**：开启 trace 的工程在会话开始/关键节点自报事件、或复盘查询轨迹时。
**定位**：自报式执行轨迹的唯一规范源——配置/事件 Schema、时序与依赖约定、CLI 与存储契约、隐私与截断规则。
**来源**：`skill_trace_001` 阶段 0 冻结基线（PRD `hs_dev_docs/_02_feature_spec/_01_human_prd/skill_trace_prd.md`）。

---

## 0. 边界与开关

- **自报式**：Agent 按本规范在关键节点调用 `scripts/skill_trace.py` 记录语义事件；框架不自动捕获工具调用级明细（宿主 Hook 适配器为后续迭代扩展点）。
- **项目隔离**：开关只读目标工程的 `config/skill_execution.yaml`；轨迹只写目标工程的 `hs_dev_docs/_06_dev_process/_05_skill_trace/sessions/`；不读、不写其他工程与全局目录（`~/.hs-dev-skill/`）。
- **缺省关闭**：无配置文件即视为关闭；关闭时所有记录命令 no-op（R4）。
- **只读入口**：EXPLORE/READONLY 期间工程已开启 trace 时仍照常记录——trace 属本地可观测副作用，不视为任务/产物状态变更；未开启则不落盘。

## 1. 配置契约

`<工程根>/config/skill_execution.yaml`：

```yaml
version: "1.0"
description: 项目级 skill 执行配置
features:
  skill_trace: false   # Skill 执行轨迹（默认关闭）
```

- 管理命令：`python3 scripts/skill_trace.py enable|disable|status --root <工程根>`。
- 读写策略与 `governance_toggle` 一致：有 PyYAML 用 YAML 解析，无则逐行兜底；写出固定模板。
- 初始化：`init_hs_dev_docs.py` 在目标工程缺省生成（`skill_trace: false`）。
- 无跨工程回退：`--root` 未显式指定时取当前目录，绝不回退到其他工程或演示目录。

## 2. 事件信封（Envelope）

每个事件一行 JSON（JSONL）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `v` | int | 是 | Schema 版本，当前 `1` |
| `event_id` | str | 是 | 会话内单调序号：`e_000001` 起，由记录器生成 |
| `session_id` | str | 是 | `s_YYYYmmdd_HHMMSS_xxxx`（xxxx=4 位十六进制随机），由 `start` 生成 |
| `ts` | str | 是 | UTC ISO-8601 秒精度 `YYYY-MM-DDTHH:MM:SSZ`，由记录器生成 |
| `event` | str | 是 | 事件类型（§3 枚举） |
| `data` | object | 是 | 类型专属载荷（§3） |
| `ref` | str | 视类型 | 关联引用；`task_link`/`decision`/`deviation` 必填（R3） |
| `truncated` | bool | 否 | 载荷截断标记（§5） |

- `ts` 与 `event_id` 由记录器生成、调用方不可伪造 → 保证 R1 有序与可校验。
- 未知附加字段忽略（前向兼容）；未知事件类型拒绝（exit 2）。

## 3. 事件类型与载荷（11 类）

| # | 类 | `event` | `data` 必填字段 | 取值约束 |
|---|---|---|---|---|
| 1 | 会话 | `session_start` | `host`、`cwd` | `host` 自由文本（如 cursor/codex/other） |
| 1 | 会话 | `session_end` | `reason` | `completed` / `aborted` / `handoff`（待验收/待决策/外部阻断按交接收束）/ `unknown` |
| 2 | 意图分级 | `intent_sizing` | `intent`、`change_size`、`work_mode`、`confirmed`、`source` | `change_size`∈{S,M,L}；`work_mode`∈{DESIGN,IMPLEMENT,READONLY} |
| 3 | 装载 | `skill_load` | `skill_id` | 子 Skill 目录名（如 hs-dev-discovery） |
| 4 | 路由 | `route_decision` | `intent`、`phase`、`process_skill`、`functional_skills` | `functional_skills` 数组（可空） |
| 5 | 阶段 | `phase_transition` | `from`、`to`、`status` | `status`∈{entered,waiting_acceptance,accepted,blocked,skipped} |
| 6 | 任务关联 | `task_link` | `task_id` | 可选 `plan_path`、`checkpoint_id`；`ref` 必填 |
| 7 | 关键动作 | `key_action` | `kind`、`summary`、`result` | `kind`∈{command,test,file,output,other}；`result`∈{ok,fail,partial,unknown} |
| 8 | 决策 | `decision` | `question`、`adopted` | `ref` 必填（指向 `_03_qa_log/` 记录或编号） |
| 9 | 纠偏 | `deviation` | `what_happened`、`correction` | `ref` 必填（触发事件 `event_id` 或文档路径） |
| 10 | 错误 | `error_retry` | `error`、`action`、`attempt` | `action`∈{retry,fallback,abort,ignored}；`attempt`≥1 |
| 11 | 耗时 | `timing` | `scope`、`duration_ms` | `duration_ms`≥0（scope 如 phase:3 / step:S3） |

> 记录克制原则：只记可观察事实与结构化摘要；不复制 process_log/qa_log 的正文（用 `ref` 引用）。

## 4. 时序与依赖约定（R1～R6）

一次会话的规范序列：

```text
session_start → (intent_sizing → skill_load → route_decision → phase_transition / task_link
                → key_action / decision / deviation / error_retry / timing)* → session_end
```

| 规则 | 约定 |
|---|---|
| **R1 追加与有序** | 轨迹文件 append-only；`ts` 单调不减、`event_id` 连续递增（由记录器保证） |
| **R2 会话归属** | 除 `session_start` 外所有事件必须携带有效 `session_id`，且对应会话文件已存在；否则拒绝（exit 2） |
| **R3 引用完整** | `task_link`/`decision`/`deviation` 必须携带非空 `ref`；目标不可解析不阻断写入，由 `validate` 标记为 unresolved（warning） |
| **R4 关闭即静默** | 未开启时所有写命令 no-op：exit 0、不报错、不创建目录/文件 |
| **R5 不阻断主流程** | 记录为 best-effort：写失败仅 stderr 告警一次，不得中断 Agent 主任务（R4/R5 是调用侧纪律，也是 CLI 语义） |
| **R6 隐私与体积** | 不记录对话/代码正文与机密；超限截断（§5） |

`ref` 解析约定：`task_link` → `task_id` 或工程内相对路径（如 `hs_dev_docs/_06_dev_process/_01_plan_log/<task_id>_plan.md`）；`decision` → `hs_dev_docs/_06_dev_process/_03_qa_log/...` 或 Q 编号；`deviation` → 既有 `event_id` 或文档路径。

## 5. 存储、隐私与截断

- 位置：`hs_dev_docs/_06_dev_process/_05_skill_trace/sessions/{session_id}.jsonl`（工程内）。
- 懒创建：仅在开启且 `start` 成功时创建目录与文件；UTF-8、一行一事件。
- 单写者假设：同一会话由同一 Agent 串行追加；不做并发锁（MVP）。
- 截断上限 `MAX_EVENT_BYTES = 8192`（含换行）：超限时 `data` 替换为
  `{"truncated": true, "original_bytes": <N>, "preview": <data 序列化前 4096 字符>}`，并在信封记 `"truncated": true`；重写后行必 ≤ 上限，保证可解析。
- 保留：手动清理 + 文档说明；无自动轮转/删除（MoSCoW 池）。
- `validate` 语义：对被截断事件（信封 `truncated: true`）跳过载荷字段检查并记 warning（不判定缺失字段）；其余事件按 §3 必填与枚举校验。
- 版本控制：建议在业务工程将 `hs_dev_docs/_06_dev_process/_05_skill_trace/` 视为本地运行数据（是否忽略由开发者自定，框架不强制）。

## 6. CLI 契约（`scripts/skill_trace.py`）

通用：`--root` 缺省 `.`；stdout 统一 JSON（`ensure_utf8_stdout`）；退出码 `0`=成功或关闭静默，`1`=运行失败（I/O 等），`2`=用法/校验错误。

| 子命令 | 参数 | 输出（stdout） | 退出码 |
|---|---|---|---|
| `status` | `[--root]` | `{ok, root, enabled, config_path}` | 0 |
| `enable` / `disable` | `[--root]` | `{ok, enabled, config_path}` | 0 |
| `start` | `[--root] [--host]` | `{ok, session_id, path}`；关闭时 `{ok, skipped:"trace_disabled"}` | 0 |
| `record` | `--session <id> --event <type> [--ref <r>] [--data <json>]` | `{ok, event_id, path}`；关闭时 `{ok, skipped:"trace_disabled"}` | 0 / 1 / 2 |
| `summary` | `[--session <id> \| --task <id> \| --since <iso>] [--root]` | `{ok, sessions:[...], counts:{...}, first_ts, last_ts, phases:[...], deviations:[...], errors:[...]}` | 0 / 1 |
| `query` | `[--session <id> \| --task <id>] [--event <type>] [--since <iso>] [--limit N]` | NDJSON：一行一事件（按时间序） | 0 / 1 |
| `validate` | `--session <id>` 或 `--file <path>` | `{ok, errors:[...], warnings:[...]}`（R1～R3 逐条） | 0 / 1 |

示例：

```bash
python3 scripts/skill_trace.py enable
python3 scripts/skill_trace.py start --host cursor          # → session_id
python3 scripts/skill_trace.py record --session s_x --event intent_sizing \
  --data '{"intent":"BUILD","change_size":"M","work_mode":"DESIGN","confirmed":true,"source":"O4"}'
python3 scripts/skill_trace.py summary --session s_x
python3 scripts/skill_trace.py query --task pay_process_001 --event deviation
python3 scripts/skill_trace.py validate --session s_x
```

## 7. 自报挂载点（Agent 何时记录）

| 时机 | 记录 |
|---|---|
| 会话开始且框架已接管 | `start`（host/cwd） |
| 会话结束/中止/按交接收束 | `session_end`（reason：`completed`/`aborted`/`handoff`/`unknown`） |
| O4 分级确认后 | `intent_sizing` |
| 装载子 Skill / 阶段路由 | `skill_load` / `route_decision` |
| 阶段流转（进入/待验收/通过/阻断） | `phase_transition` |
| 创建/更新任务计划、checkpoint | `task_link`（引用 plan/checkpoint，不复制内容） |
| 关键命令/测试/产出 | `key_action` |
| 开发者拍板 | `decision`（引用 QA 日志） |
| 纠偏/返工/用户纠正 | `deviation`（引用触发事件） |
| 错误与重试 | `error_retry` |
| 关键节点耗时 | `timing`（可选） |

- 装载与路由等事件只在开启时记录；关闭时按 R4 静默。
- 记录顺序遵循 §4 规范序列；跨阶段继续沿用同一 `session_id`，跨会话任务复盘时用 `--task` 过滤拼接。

## 8. 扩展点与兼容

- Hook 适配器（工具调用级自动采集）：后续迭代扩展点，须保持 §2 信封兼容；框架本体不依赖宿主事件。
- 索引/门禁联动、聚合统计、可视化 UI、token 用量采集：MoSCoW 池，本期不实现。
- Schema 演进：新增事件类型或必填字段必须提升 `v` 或保持旧字段兼容；查询与校验以 `v` 分派。
