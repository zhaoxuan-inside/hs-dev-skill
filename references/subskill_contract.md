# 子 Skill 运行、依赖与交接协议

**何时读**：首次组合子 Skill、直接调用子 Skill、安装校验或发生职责冲突时。

## 1. 两个轴的职责

- 主 Skill `hs-dev-skill`：识别意图、规模、阶段和触达领域，选择过程与功能 Skill，维持验收和交接边界。
- 过程轴 `skills/hs-dev-*/SKILL.md`：决定当前工作如何推进、需要哪些输入、何时提交验收、下一步交给谁。
- 功能轴 `skills/hs-dev-*/SKILL.md`：在给定过程内提供产品、架构、前端、后端、测试或治理的专业操作，不自行更换过程或宣布阶段通过。
- `resources/skill_routes.json`：唯一的机器路由与参考文档归属清单。主入口表格用于人工快速选择，增改路由同时更新清单与测试。

同一执行片段只设一个过程负责人。功能 Skill 可以提出其他领域的输入需求，交回主路由按需加载，不互相递归启动流程。加载 Skill 不等于启动子 Agent；是否委派遵守当前会话授权。

用户直接指定某个功能子 Skill 时，先沿用会话中已有的 intent、阶段、只读边界与确认；缺少过程上下文时只读取主路由对应行确定当前过程，不重跑无关生命周期。直接点名子 Skill 不等于授权修改代码或批准其产物。

## 2. 包结构与安装边界

这是一个主 Skill 携带子 Skill 的完整包。`skills/` 是真实带 frontmatter 的 Skill 入口；`references/` 为单份权威规则库，`scripts/` 和 `resources/` 为共享运行资源。此次拆分迁移职责和加载入口，不复制现有详规，也不改变旧脚本/模板路径。

安装必须保留主 Skill 根目录及其 `skills/`、`references/`、`scripts/`、`resources/`。不要单独复制一个子 Skill 文件夹后期待共享链接工作；子 Skill 当前是完整包的组成部分，不承诺脱离共享包独立安装。主路由显式读取本地子入口，因此宿主无需自动发现嵌套目录。

`HS_SKILL_ROOT` 表示安装包根，`PROJECT_ROOT` 表示目标工程根。它们可能完全不同：

```bash
# 以下路径替换为实际安装位置与工程位置
python3 /path/to/hs-dev-skill/scripts/skill_router.py check
python3 /path/to/hs-dev-skill/scripts/skill_router.py route --intent BUILD --phase 3 --domains backend
python3 /path/to/hs-dev-skill/scripts/doc_index_db.py --root /path/to/project search --q "订单"
```

从子 Skill 的 `SKILL.md` 向上两级可定位包根。文件中的相对链接相对该文件，工具路径相对包根，业务文件路径相对工程根；不要依赖当前 shell 正好位于包根。进入工程执行其测试时使用工程工作目录。Windows 可用 `python` 或 `py -3`。

## 3. 调用输入与返回

主路由向过程 Skill 交付：

| 字段 | 含义 |
|---|---|
| intent / change_size / work_mode | 已判定意图、规模和设计/实现/只读约束 |
| phase / checkpoint | 当前阶段及已有验收点，不能只凭用户说“开发”推定从阶段 0 重开 |
| scope / non_goals | 当前授权范围与不做范围 |
| input_baselines | 路径、版本/内容摘要、确认记录及有效性 |
| domains | 当前实际触达领域，可为空；不能为了凑矩阵加载全部功能 |
| open_issues / next_action | 未决项、阻断原因与本次预期输出 |

功能 Skill 接收同一上下文与具体专业问题，只返回本领域结果、证据及需要主路由裁决的问题。过程 Skill 返回：产出路径与版本、变更/测试证据、checklist 候选结果、有效/失效验收、未决项、建议下一阶段及实际加载的 Skill 名称。

验收状态遵循 [阶段验收协议](stage_acceptance.md)。调用成功和工作 todolist 完成不等于 ACCEPTED；模型不得代签。

## 4. 路由优先级与停点

1. 显式只读咨询锁定 EXPLORE/READONLY，后续功能 Skill 不能扩大权限。其他任务中的状态询问只简短回答并继续原任务，不重新路由成独立 EXPLORE。
2. 续做先交 continuity 恢复已有阶段和确认，恢复前不得自行选择 BUILD 阶段。
3. 变更事件交 continuity 做影响分析；验收事件交 acceptance。事件是当前意图的子过程，不替换原目标。
4. FIX/REFACTOR/REVERSE 按专门过程执行；BUILD 根据实际阶段 0～6 选择过程。S/M 跳过未触达阶段，保留沿用基线。
5. 专业领域由触达面决定。BUILD 0 默认 product，1/2 默认 architecture，3 默认 backend，6 默认 testing；这些只是路由建议，无 UI、无 DB 等场景应按实际范围显式选择/排除，不自动增加工作。

提交验收、询问缺失决策或等待外部条件时保留交接记录，已有确认按范围复用。收到用户新信息只更新相关节点，不重做已验收且未失效的阶段。

## 5. 路由工具能力边界

`skill_router.py route` 只根据显式 intent/phase/domains/event 输出入口路径；不会解析业务语义、读取项目状态、执行子 Skill 或判定验收通过。BUILD 没有当前阶段时拒绝猜测。RESUME 返回“需恢复”后，由 Agent 从日志取得实际阶段，再调用相应路由。

`check` 校验入口存在性、名称、路由目标及参考文档唯一归属；不能证明模型执行正确。`skill_ref_index.py search` 可检索子入口与详规，`rule_fetch.py` 原有接口继续保留。

## 6. 维护不变量

- 每份详规只有一个维护归属，跨 Skill 链接复用；共有编排文档明确标为 shared。
- 专业规则变化改相应功能 Skill/详规，过程变化改过程 Skill/详规；只修改主入口不足以完成子 Skill 变更。
- 子 Skill 缺失时报告缺失路径与完整包安装方法，不假称已调用，也不退化为一口气读取整个 references。
- 新增入口必须有清晰触发/排除、输入、执行、输出与验收；不能只有“见另一份文件”的空壳。
- 参考文档中的历史阶段链是展开说明；实际分派以主路由和当前验收为准，不能在子 Skill 内再次递归执行整条链。
