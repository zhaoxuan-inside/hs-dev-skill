# 接口契约记录：Skill 执行轨迹（trace）

- **task_id**：`skill_trace_001`（change_size=M，work_mode=DESIGN）
- **阶段**：3 详细设计（触达面）
- **输入基线**：PRD v0.1（2026-10-17 冻结 APPROVED）；`references/skill_trace.md` v0.1（规范源）
- **状态**：SUBMITTED（待开发者验收）
- **编写者**：Agent；验收人：开发者

## 1. 契约清单（本次触达面）

| 契约 | 规范源 | 方言/载体 | 验证方式 |
|---|---|---|---|
| 事件信封与载荷 | `references/skill_trace.md` §2/§3 | JSON（JSONL 一行一事件） | JSON Schema 校验样例（实现阶段 `resources/templates/trace/trace_event.schema.json`） |
| CLI 行为 | §6 | 子命令 + JSON stdout + 退出码 | CLI 断言测试（stdout/退出码/文件副作用） |
| 配置读写 | §1 | YAML（可选 PyYAML，逐行兜底） | enable/disable/status 测试 + 兜底解析测试 |
| 存储与命名 | §5 | 路径/命名/懒创建/截断 | 路径断言 + 截断用例 |
| 时序与依赖 R1～R6 | §4 | validate 规则 | 依赖校验用例 |
| 集成（注册/初始化/挂载） | §4 变更清单 | 文件级变更 | `skill_router.py check` + `init` 断言 + 门禁 |

## 2. DETAIL 检查项（阶段 3 清单逐条）

| 规则 ID | 检查内容与通过标准 | 证据（路径/锚点） | 候选结果 |
|---|---|---|---|
| DETAIL-01 | 数据字段含义/类型/必填/枚举/上限/生命周期/访问模式明确；无 DB 变更 | `references/skill_trace.md` §2/§3/§5（信封表、载荷表、`MAX_EVENT_BYTES=8192`、懒创建、手动保留、追加写） | PASS |
| DETAIL-02 | 接口契约：操作/入参/Schema/错误/示例完整；方言固定 | §6 CLI 表（7 子命令、参数、stdout JSON、退出码 0/1/2、示例）；§1 配置模板；JSONL 行为 | PASS |
| DETAIL-03 | 方法行为：前置/后置/不变量/边界/副作用明确 | §2（ts/event_id 记录器生成）、§6 `start`/`record` 前置与副作用（追加一行、告警 only）、R1（append-only 不变量） | PASS |
| DETAIL-04 | 状态与失败语义：重复/失败/降级/幂等明确；无无限重试 | R4（关闭 no-op）、R5（失败降级告警，单次不重试）、exit 2 拒绝写入（缺会话/未知类型/坏 JSON）、§5 截断保解析、单写者假设 | PASS |
| DETAIL-05 | REQ/规则 ↔ 接口/数据 ↔ 场景 ↔ 测试一致 | 本记录 §3 映射表 | PASS |
| DETAIL-06 | 实现准备度：关键决定无需猜测；测试可区分正误 | 本记录 §4 变更清单 + §5 测试规格；对外行为待开发者确认 | PENDING（待签收） |

## 3. REQ ↔ 契约 ↔ 场景 ↔ 测试映射（DETAIL-05）

| REQ | 契约锚点 | Gherkin 场景（PRD §4.2） | 测试用例 | 演练 |
|---|---|---|---|---|
| REQ-TR-01 | skill_trace.md §1、§0（隔离） | 场景 1（A 开 B 不开） | T1、T2 | — |
| REQ-TR-02 | §2、§3、§5 | 场景 2（按序落盘） | T3 | demo 回放 |
| REQ-TR-03 | §4（R1～R3）、§6 `validate` | 场景 3（缺会话拒绝） | T4、T8 | — |
| REQ-TR-04 | §4（R4/R5） | 场景 4（关闭静默） | T5、T11 | — |
| REQ-TR-05 | §6 `summary`/`query` | 场景 5（复盘 demo 回放） | T7 | demo 回放 |
| REQ-TR-06 | §5（截断） | 场景 6（超长截断） | T6 | — |
| REQ-TR-07 | §1、§5（初始化） | —（由 T9 覆盖） | T9 | — |
| REQ-TR-08 | 门禁回归 | — | T10 | — |

## 4. 集成变更清单（实现阶段按此执行）

| # | 文件 | 变更 | 状态 |
|---|---|---|---|
| 1 | `scripts/skill_trace.py` | 新增：config/start/record/summary/query/validate 六类能力 | 待实现 |
| 2 | `resources/templates/trace/trace_event.schema.json` | 新增：事件信封与载荷 JSON Schema（draft-07） | 待实现 |
| 3 | `tests/test_skill_trace.py` | 新增：T1～T11 | 待实现 |
| 4 | `scripts/init_hs_dev_docs.py` | 缺省生成 `config/skill_execution.yaml`；新增目录 `_06_dev_process/_05_skill_trace/sessions` | 待实现 |
| 5 | `SKILL.md`（主路由） | “所有子 Skill 共同遵守”挂载 trace 自报一条（指向 `references/skill_trace.md`） | 待实现 |
| 6 | `README.md` | “51 份已登记详规”→ 52；新增功能小节（可选开启、项目隔离） | 待实现 |
| 7 | `references/skill_trace.md` | 已落盘（规范源） | 完成 |
| 8 | `references/_index.md` | 已新增索引行 | 完成 |
| 9 | `resources/skill_routes.json` | 已登记 `shared_references`（`skill_router check` = 16 skills / 52 refs） | 完成 |
| 10 | demo_project 回放 | 不新增脚本；按 PRD §7 记录命令与输出为验收证据 | 待执行 |

## 5. 测试规格（DETAIL-06）

| 用例 | 场景 | 断言要点 |
|---|---|---|
| T1 | 配置生命周期 | enable 后配置文件存在且 `skill_trace: true`；status 反映；disable 复原；缺文件=关闭 |
| T2 | 项目隔离 | 双 root：仅 A enable；A/B 各自记录 → 仅 A 出现 `sessions/*.jsonl`，B 零目录零文件 |
| T3 | 序列与有序性 | start→intent_sizing→…→session_end；首末类型正确；`event_id` 连续；`ts` 非降；行数匹配 |
| T4 | 依赖拒绝 | 缺 `--session`、未知事件、坏 JSON → exit 2 且文件行数不变 |
| T5 | 关闭静默 | 未开启时 `start`/`record` → exit 0 + `skipped=trace_disabled`；无目录无文件 |
| T6 | 截断 | 超长 `data` → 行 ≤8192 字节、`truncated=true`、JSON 可解析、`validate` 无错 |
| T7 | 查询复盘 | `summary` 计数/首末/阶段序列/偏差与错误清单正确；`query --event` 过滤、`--limit`、NDJSON 行序 |
| T8 | validate 规则 | 可用样例：缺 `session_end` 告警；`ref` 不可解析告警；人工篡改（乱序/断档/会话错配）报错 |
| T9 | 初始化集成 | `init_hs_dev_docs` 后配置文件存在且为 false、`_05_skill_trace/sessions` 目录存在 |
| T10 | 回归门禁 | `make test` 全绿；`verify_consistency --root . --demo --strict` 通过；`skill_router.py check` = 16/52 |
| T11 | 写失败降级 | 构造写失败（父路径被占用/移除）→ stderr 告警、exit 1、无异常栈；平台导致无法可靠构造时标 skip 并记录理由 |

## 6. 阶段 3 验收（内联）

- **验收状态**：SUBMITTED（待开发者）
- **适用项**：DETAIL-01～05 候选 PASS；DETAIL-06 待签收
- **阻断问题**：无
- **开发者结论**：待验收（ACCEPTED / REJECTED）
- **确认原文/时间**：待补充
