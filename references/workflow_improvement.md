# 基线、执行观测与分级优化闭环

**何时读**：冻结需求、装配 Pack、实现前、完成门禁、流程复盘或修改 Skill 规则时。工具均仅使用 Python 标准库。

## 1. 优化强度

| 类别 | 判据 | 处理 |
|---|---|---|
| fatal 致命问题 | 已证实会造成漏需求交付、使用失效契约、丢失/伪造关键证据、破坏数据或越权执行 | 立即修复当前缺陷；阻断受影响交付；复现、修复、回归后才能放行，不等待重复案例 |
| habitual 习惯性问题 | 不破坏正确性，但反复造成无效追问、重复劳动、表达或操作偏差 | 先记案例；默认至少 3 个独立案例、3 个原始会话、观察跨度至少 7 天，有对照收益且无回归后，只形成小步更新候选 |
| advisory 其他问题 | 尚无证据的推测、偶发偏好、未影响交付的建议 | 提示、说明影响；不新增硬门禁，不自动改规则 |

致命性按影响与证据判断，不按出现次数判断。习惯性阈值是本版的保守初始策略，不代表已证明的最佳值；调整阈值同样要留下案例与评测。用户当场明确指令优先于历史偏好。修复当前工程问题不等于有权把个例提升成跨项目规则。

## 2. 需求基线与派生物

`scripts/baseline_gate.py --root <工程根>` 管理工程内 `hs_dev_docs/_06_dev_process/_07_baselines/registry.json`。这是版本化登记源；SQLite 索引仍只是缓存。每次写入采用临时文件替换；同一工程的登记操作串行执行。

冻结前，按返工影响从用户/成功结果、最小闭环、角色与归属、主路径、异常恢复、外部约束追问。已有确认直接引用；查得到的事实由 Agent 自查。问题要保留来源、关联 REQ、前置依赖、风险、答复、确认范围和关闭依据；高风险未知未关闭不能冻结。问题数量不能代替澄清质量。

建立专门的已确认范围文件，列出该范围全部稳定 REQ ID。工具核对显式需求集合等于该文件全部 REQ ID；`assignments` 将全部需求恰好分配给一个主责任务，防止任务自行缩小分母。协作任务引用主责需求，不重复归属。工具不能判断用户从未被记录的需求，Agent 仍须按 DISC/PROD 与原表达对账。

```bash
python scripts/baseline_gate.py --root PROJECT freeze --id scope-r1 --version 1 \
  --source scope.md --requirements '["REQ-A","REQ-B"]' \
  --assignments '{"task-a":["REQ-A"],"task-b":["REQ-B"]}' \
  --confirmation '{"source":"真实确认的消息位置","excerpt":"真实确认原文及范围"}'
python scripts/baseline_gate.py --root PROJECT derive --id design-r1 --path design.md --depends-on scope-r1
python scripts/baseline_gate.py --root PROJECT derive --id pack-r1 --path pack.md --depends-on design-r1
python scripts/baseline_gate.py --root PROJECT check
python scripts/baseline_gate.py --root PROJECT check --artifact pack-r1
python scripts/baseline_gate.py --root PROJECT invalidate
```

- `freeze` 保存源路径、SHA-256、版本、需求全集、任务归属和真实确认引用；ID 不可覆盖。确认用户需求范围不等于确认最终实现。
- `derive` 只允许依赖存在且有效的节点。登记设计、Pack、待验收代码/测试等产物；修改后重新登记新 ID，不能原地刷新旧摘要以维持签收。
- `check` 不改基线/验收状态，计算源摘要、文件存在性及依赖有效性；工程开启 trace 时可记录检查事实。文档和代码内容变化均保守失效，工具不判断语义等价。
- `invalidate` 显式落盘所有受影响派生节点的 INVALIDATED 状态；即使未执行此命令，动态检查也已拒绝失效节点。
- 实现前、续做、验收前执行 `check`；使用 Pack 时增加 `--artifact <当前ID>`，缺失基线或指定产物即失败。S 可登记任务内联契约，不强制生成空 Pack。发现失效即停止受影响工作，交 continuity 处理影响；其他独立工作可继续。
- 新确认后使用新基线/派生 ID。同一任务存在多个未被替代的范围基线时拒绝完成，不能挑选较小分母。旧节点可用 `supersede --id OLD --by NEW` 显式退出当前版本；替代节点须存在、有效、类型一致。先重建新链，再逐个替代旧链。历史记录保留，不能将旧签收迁移给新内容。
- 完成门禁必须绑定当前基线的 id/version/sha256、该任务完整 requirements 证据和已登记 artifacts。不存在、失效、错版本、缺行、重复行、额外行或证据缺失均阻断。测试运行证据还必须保存当前文件 SHA-256。
- 旧验收记录在新完成流转前必须补登记；不自动推断旧签收，不批量篡改历史档案。已归档旧任务无机器引用时，保留历史记录，不能宣称其已通过新门禁。

验收 JSON 在原 `HS_ACCEPTANCE_GATE_V1` 区块中增加：

```json
{
  "baseline": {"id":"scope-r1","version":"1","sha256":"实际源摘要"},
  "requirements": [{"id":"REQ-A","result":"PASS","evidence":"reports/scenario-a.log"}],
  "artifacts": ["pack-r1","implementation-r1"],
  "verification": {"tests":[{"command":"实际命令","exit_code":0,"evidence":"reports/test.log","sha256":"实际报告摘要"}]}
}
```

证据路径必须位于工程内，拒绝绝对路径、目录穿越和指向工程外的符号链接。确认来源和证据内容真实性仍需人工与 Agent 诚信，摘要校验不等于可信签名或业务正确性证明。

## 3. 自动事实与复盘

`execution_observer.emit` 在项目 trace 开启时，为每次工具动作建立独立短会话，避免多个工具并发写同一 JSONL。自动采集任务创建/流转、完成门禁、checkpoint、基线检查；`skill_router route --project-root PROJECT` 可记录目标工程的路由事实，不传时仍只读。Agent 继续补充语义决策和纠偏。每条 `tool_result` 标记 producer/source，关闭时 no-op；采集失败只告警，不改变实际门禁结果。

验证命令通过 argv 数组运行，不用 shell；输出独占创建，拒绝覆盖已有证据：

```bash
python scripts/execution_observer.py --root PROJECT --task task-a --evidence reports/run-001.log -- python3 -m unittest discover
python scripts/workflow_report.py --root PROJECT --task task-a --format markdown
```

报告输出到 stdout，可由调用方保存。包含观测到的门禁尝试/失败数、验证次数/失败数/耗时、基线状态、按版本保存的需求分母、纠偏及轨迹完整性问题。分母不是验证覆盖率；缺失数据明确标注，不能把零事件解释成零问题。自报漏报率、首次验收率、等待时间、需求遗漏/返工率尚需完整阶段与原因记录，本版不虚构这些指标。

遥测不复制命令参数、对话或代码正文；执行输出可能包含机密，由调用方选择安全命令及输出环境。报告不启用业务系统运行时监控。

## 4. 规则评测与渐进更新

`scripts/skill_evolution.py --root PROJECT --input evaluations/change.json` 读取成对案例，核对来源、before/after 运行文件和回归报告的 SHA-256，比较失败数；JSON 运行文件必须包含同一 `case_id` 和 `failures`。原始会话/日期来自实际案例，禁止用重复运行伪造独立案例。

输入：`schema_version=1`、`rule_id`、`severity`、`cases[]`。每个案例包含 `case_id`、`session_id`、`observed_at`（YYYY-MM-DD）、`source:{path,sha256}`、`before/after:{failures,evidence,sha256}`、`regressions`、`regression_evidence:{path,sha256}`。回归报告包含实际 `command` 和 `regressions`；记录必须可追溯到原始日志，工具不能鉴别伪造的测量数据。

候选输出：fatal 的 FIX_NOW / REPAIR_REQUIRED，habitual 的 ACCUMULATE / GRADUAL_CANDIDATE，advisory 的 HINT_ONLY。任一案例新增失败不能被总体改善抵消。fatal 的立即修复不受观察周期约束；FIX_NOW 表示当前修复评测已无失败和回归，不代表自动发布。

采纳时记录根因、窄范围规则补丁、关联案例、兼容性、Skill 版本及回退方法；运行历史场景与全量回归。工具只建议，不自动修改/发布 Skill，不把偏好变成全局门禁。没有真实 before/after 证据时，只能记录候选或提示，不能声称已证明收益。
