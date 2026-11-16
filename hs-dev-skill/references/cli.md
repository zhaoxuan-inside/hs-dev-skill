# 执行接口与输入

需要时按本页准备当前一步的输入，不预先填写所有活动。命令入口：

```sh
python3 <Skill根>/scripts/hs-dev.py --root <实际工程根> <command>
```

命令输出 JSON；拒绝或未就绪时退出码为 2，具体原因在 stderr。成功运行某条命令不等于活动完成。`@文件.json`读取真实 JSON 文件；下列示例是结构说明，须替换为本次实际内容和程序返回的 ID、摘要，不能登记为真实证据。

## 初始化和定位

`init` 只创建全新格式，不覆盖已有 `hs-dev/`。默认 `confirm`，每个具体方案需要登记实际已有授权；这不是要求再向用户询问一次。已有开放配置可通过 `init --record @policy.json` 固定：

```json
{"policy":{"mode":"bounded","allow":["src","hs-dev/project","hs-dev/deliveries","hs-dev/execution/evidence"],"source":{"path":"已有授权快照.md","digest":"该快照的实际sha256"}}}
```

`mode` 为 `confirm`、`bounded` 或 `read-only`。非默认配置必须有初始化前真实存在的授权/设置快照及摘要。`bounded` 仅对允许路径内、明确声明可逆的本地方案免重复授权；外部或不可逆作用仍需要具体决定。策略不能经手改状态扩大。

```sh
python3 <Skill根>/scripts/hs-dev.py --root <工程根> status
python3 <Skill根>/scripts/hs-dev.py --root <工程根> reindex
python3 <Skill根>/scripts/hs-dev.py --root <工程根> locate --query '当前规则或真实路径' --limit 5
python3 <Skill根>/scripts/hs-dev.py --root <工程根> read --path <返回路径> --start <起行> --end <末行> --digest <source_digest>
```

索引过期需显式重建；查询不会替用户重建或猜相似身份。先取定位卡片，再按摘要读取必要正文。`locate --query source:已登记ID`定位普通内容；`source-get --id ID`只取该来源状态，`evidence-read --path hs-dev/execution/evidence/... --digest 实际摘要`读取指定执行证据。普通 `read` 不读取执行控制。

## 来源

`source-add --record @source.json` 登记已实际取得的快照，不执行网络抓取，也不证明发言者身份。快照必须存在，假设可登记但不能用作事实、确认或授权。

```json
{"id":"稳定来源ID","kind":"document","path":"实际快照相对路径.md","version":"已核实的具体版本","observed_at":"实际UTC采集时间","scope":"与本次交付一致的范围文本","claim_type":"requirement"}
```

- `kind`：`document|code|user|private|official|primary|execution`。
- `claim_type`：`fact|requirement|decision|hypothesis`。用户回答要求 `kind=user`，授权还要求 `claim_type=decision`。
- 不存在版本概念时用 `version:{"not_applicable_reason":"具体原因"}`。不能用 latest、unknown 或猜测版本。
- 公开/私域外部来源必须给出 `valid_until`；网络来源须有无凭证的实际 `url`，外部来源须有 `publisher`、`quality_reason`。有效期是复核期限，不保证远端未更新。
- `scope` 为本次交付的原样文本，或经核实适用全项目的 `project`。不能用全项目范围掩盖局部适用性。
- 同 ID 更新保留旧记录；即使正文相同，版本/适用范围等元数据变化也会使旧判断失效。

## 交付、追问和就绪

`start --title 实际标题 --activity G1 --scope 实际范围` 返回交付 ID。下文 `D` 指该返回值，不是字面字符串。

`template --activity G1` 返回进入条件和本活动输出契约；`--output G1.O1`只取具体输出。进入条件只是能开始，不代表完成。输出另有逐项达成判据。

```sh
python3 <Skill根>/scripts/hs-dev.py --root <工程根> question D --id q1 --question '需要负责人的具体问题' --reason '不同答案的影响' --options @options.json --recommendation '有依据的建议及代价'
python3 <Skill根>/scripts/hs-dev.py --root <工程根> answer D q1 --source 实际用户来源ID --understanding '对回答的具体理解'
python3 <Skill根>/scripts/hs-dev.py --root <工程根> reflect D q1 --source 依据ID --scenario '用于挑战回答的反例' --outcome supported --reason '反例检验的结果和边界'
```

`options`为字符串数组，可省略。先实际询问再记录回答，`outcome=reopen` 保持相关工作受阻。修改回答会清除旧反思；旧沟通进入历史，当前摘要保留现行理解。独立角色讨论使用实际委派工具，保存真实分析与交叉质疑证据；程序不会凭角色名称制造讨论。

问题默认 `--blocking true`，旧状态缺少该字段时也保持阻断。补充问题可显式传 `--blocking false --affected-work '实际依赖答案的后续范围' --nonblocking-reason '当前活动为何不依赖答案'`；两个说明缺一不可。这只允许当前独立活动继续，不放行后续依赖范围；进入后续活动时仍须评估其前置条件。API 对应字段为 `blocking`、`affected_work`、`nonblocking_reason`。

用户明确否定前提或撤回问题时，用 `question-resolve D --record @resolution.json` 保留原问题并记录处置：

```json
{"question_id":"实际问题ID","outcome":"invalid-premise","reason":"用户否定了什么前提，为什么此问题不再适用","source_ids":["真实用户决定来源ID"]}
```

`outcome` 只允许 `invalid-premise|withdrawn`，来源必须为 `kind=user, claim_type=decision`，绑定当前有效版本。处置不等于回答或验收；来源变化需重核。重新 `answer` 会清除旧处置并要求新的反例复核。不能以等待超时、模型偏好或无依据的撤销来清除阻断。

`assess D --record @assessment.json`：

```json
{"understanding":"本次问题、规则和边界的具体理解","dialogue":{"mode":"reuse","summary":"为何已有有效认识足够，或本轮问答解决了什么","source_ids":["实际来源ID"]},"unknowns":[],"entries":[{"id":"所选模板返回的M项ID","status":"supported","judgment":"本项为何达到进入条件","source_ids":["实际来源ID"]}]}
```

每个 `minimum` 项恰好判断一次。`dialogue.mode=asked`要求实际回答和反思；`reuse`必须引用仍有效的认识，不能为凑提问数量重复问。未知记录为 `{issue,blocks:true或false,next_action}`；阻断未知未解决就不能规划依赖它的执行。`readiness D` 返回当前进入条件的判定及具体阻断。

`status/resume/advance` 返回历史未决的 `prior_questions`。存在这些问题时，`assess` 的记录必须另含同名数组，逐项填写 `{id,blocks,reason,next_action}`，说明它对当前活动的实际依赖；漏项或任一 `blocks:true` 不放行规划。未决问题每个后续活动都重新评估，不因曾声明补充问题而永久忽略。可以直接对历史未决问题使用 `answer/reflect`，或凭真实用户决定使用 `question-resolve`，原始问题归属保留。

## 方案、授权和锁

`plan D --record @plan.json`：

```json
{"paths":["src/actual.py","hs-dev/project/actual.md"],"steps":[{"id":"step-1","action":"具体动作及同步内容","paths":["src/actual.py","hs-dev/project/actual.md"],"expected":"可观察结果"}],"verifications":[{"id":"check-1","argv":["python3","真实检查入口.py"],"expected":"检查对象及真实通过判据"}],"recovery":{"strategy":"如何恢复本次自有修改","limitations":"不能恢复的外部作用与停止条件"},"risks":["具体风险及处理边界"],"effects":{"external":false,"irreversible":false,"local_reversible":true},"feasibility":{"status":"supported","judgment":"所需工具、输入和恢复条件为什么实际可用","source_ids":["依据ID"]},"source_ids":["依据ID"]}
```

路径必须为规范的精确文件路径，不能用目录、别名或执行控制。每条路径有步骤，验证命令不得用恒真空操作替代实际检查。计划绑定当前认识、来源和文件基线，变更后重新评估和规划。

`verifications` 为1至64项。每项可声明 `timeout_seconds`（整数1..300，省略为30），例如真实数据库检查 `{ "id":"database", "argv":["python3","tests/check_database.py"], "expected":"真实并发约束成立", "timeout_seconds":90 }`。全部声明时限合计不超过3600秒；整轮实际执行也有3600秒截止，各项仍受自身截止和4MB输出限制，进程清理可能有额外耗时。按实际生命周期和副作用选择预算，不以提高时限掩盖永久挂起或删除断言。

在默认策略下用 `authorize D --source 实际用户决定ID --plan-digest 返回的方案摘要` 登记已有的明确授权。必须核实真实授权覆盖该方案，不能从授权摘要反推用户已同意。

`lock D` 复核基线并保存前像。0.0.2 使用**单工程串行写锁**，代码和文档一起受管；其他交付可以调查，写入须等前一个释放。范围是精确路径，但本版不支持两个不相交范围并行写。它不能拦住外部编辑；程序每步重新比较实际内容。

## 修改、产出和验证

`apply D --changes @changes.json` 的输入为 `{ "精确已计划路径": "完整UTF-8新正文", "另一已计划路径": null }`；`null`为明确删除。单个修改不超过4MB，恢复前像总计不超过32MB。写入前记录恢复点，发现外部变化时拒绝覆盖。

已完成锁、授权、源和路径检查后，完全相同字节的写入或删除已不存在文件属于 no-op：`changed` 只列真实变化，不清除有效验证。混合批次的真实变化仍使旧验证失效；不能用同字节请求绕过外部漂移或来源过期。

原子替换保留已有文件的 POSIX mode；新加锁的恢复前像同时保存 mode，回退被删文件时还原。内容摘要不检测权限等元数据漂移，旧前像没有 mode 时无法恢复已删除文件的原权限；其他元数据和外部作用见[生产开发边界](production-readiness.md#执行工具的适用边界)。

`produce D --record @output.json` 按契约渲染并维护稳定章节：

```json
{"id":"G1.O1","scope":"交付范围原样文本","path":"已计划且归属正确的路径.md","answers":[{"id":"契约返回的Q项ID","answer":"针对本问题的具体答案","status":"supported","source_ids":["依据ID"]}],"acceptance":[{"id":"契约返回的A项ID","status":"supported","judgment":"逐项标准如何达成的具体判断","source_ids":["依据ID"]}],"limitations":"结论实际适用的范围及未证明内容"}
```

所有 Q 和 A 项各出现一次。状态为 `supported|unknown|conflict|not-applicable`；非 supported 还需具体 `reason` 与 `next_action`。未知、冲突可以记录，不能提交为完成；不适用也要真实证据和理由。

项目产物通常在 `project/`，交付产物在 `deliveries/D/`，执行产物在 `execution/evidence/D/`。代码、SQL、协议等原生项目产物继续放原工程位置，用 `record-output D --record @output.json`，同样填写判断，另给 `format:"artifact"`、`artifact_digest:"实际文件sha256"`；程序核对原文件，不把说明章节写入代码。

本次自有代码变更后的旧来源只可支持明确标记 `basis:"baseline"` 的前像判断；描述当前实现应登记新的实际来源。模型不能用旧实现证据证明新实现正确。

`run D`实际运行全部获授权的计划检查；`--checks @checks.json`仅可显式选择同一完整命令集合，不可替换命令或放宽时限。执行始终使用计划绑定的预算，旧计划省略时仍为30秒。日志在执行证据中，结果含实际耗时、时限、退出码与摘要；超时124、输出超限125、启动失败127均不算通过。命令不通过 shell；这不是隔离沙箱，必须先评估真实副作用。检查不能修改源或控制文件；失败、超限和篡改均不能提交。

控制输出较大时用 `--compact`，例如 `python3 scripts/hs-dev.py --root /path/to/project --compact run D`。它只压缩 `run/resume/status/plan/lock` 的终端投影，保留各项退出码、日志路径/摘要和完整记录入口；失败仍以非零退出。原来源清单、问答、计划和验证证据完整保存在工程内，去掉此选项可读取全部响应。简洁输出不是新的验证或改变提交条件。

主命令退出0但同一进程组仍有残留时记失败126；结束时清理该进程组，避免后台继续写入后才消费旧验证。独立 session、容器及远端任务仍须由检查入口自行清理，不能从进程组清理推导所有外部作用已终止。

退出码0只证明命令执行成功，开发者还须核对断言、覆盖和实际输出。禁止零测试、错误环境、Mock成功或修改预期后冒充原目标通过。产物变更后旧验证失效，完成全部同步后再运行最终检查。

## 提交、解锁和恢复

`submit D`检查全部产出、当前验证和来源，生成带摘要的本地一致性提交记录；随后 `unlock D`。这不是 Git 提交、部署或发布。提交后发生的新编辑会在解锁时标明，原记录只证明提交当时的版本，不覆盖新变化。

返回的 `task_complete:false` 表示只完成当前活动，未建立主任务完成结论；解锁后对照用户目标继续剩余已授权工作，不能把这个响应当作停止执行的理由。

`advance D --activity 下一活动ID` 复用同一交付并保留前序成果；只在已提交或已回退且解锁后使用。回退后可以重试同一活动。`story.md`为程序维护的当前沟通与成果入口，旧摘要在 `history/`，默认不作为现行认识检索。

中断先 `resume D`，继续原交付；写入和取得锁/释放锁都有可核验的恢复记录。`rollback D`只恢复仍为本次所有的修改，不覆盖后来编辑。外部修改导致冲突时，保留原内容并核实归属；需要放弃本次修改且保留后来内容，可用：

```json
{"preserve":["实际冲突且本次触及的路径"],"reason":"为何明确保留后来的编辑","source_ids":["覆盖该处置的实际用户决定ID"]}
```

通过 `rollback D --record @preserve.json` 登记此处置，随后解锁。它不会回滚外部系统或声称保留的编辑已经验证。不要手改执行状态、偷锁、清证据或另建同义交付绕过阻断。
