# hs-dev-skill 5.1.0.0 实施与验证记录

日期：2026-10-18。实现位于当前源码工程；自动验证结果不替代用户对使用体验及设计效果的验收。

## 已实现的模块与行为

| 范围 | 实现 |
|---|---|
| 工作区 | workspace.py 使用 SQLite 短事务申请 UUID 与 fence；同 UUID 写入互斥；任务和路径范围检查；读取凭据；显式完成、取消与撤销 |
| 状态 | 区分在途修改、验证、发布、回退、待恢复；旧凭据拒绝；外部漂移不自动纳入基线；恢复后核验再设安全 |
| 意图 | intent.py 分句提取行为、否定、只读约束及对象信号；候选评分；不足或冲突返回 NEEDS_MODEL；宿主提供最终意图与理由 |
| 任务 | 显式活动范围；类型化检查实例；task_store 与任务编排分离；当前任务摘要自动更新 |
| 依赖 | dependencies.py 绑定实际已验收产物；按 upstream 检查；确认绑定内容、证据及依赖，不绑定全局索引代次 |
| 验收 | confirmation.py 统一三种模式；人工材料全部通过且检查就绪时形成一次范围确认；日志不自动生成材料卡 |
| 上下文 | ContextProvider 优先必要约束、支持检索片段与当前任务、预算不足明确返回；同一读取会话共享核验；恢复数据隔离 |
| 分层 | 任务原文有界常驻；温数据正文 FTS；冷数据只索引标题及属性、按需读正文；集中存放索引；源未变化时复用发布修订 |
| trace | 与确认模式独立；入口、路由、状态、上下文、检查与确认事件；白名单字段；容量/时间清理与有界查询；失败不改变业务结果 |
| 输出 | banner、面向人的摘要与独立机器 meta/result；CLI 参数与应用编排分离 |
| 文档 | README 只描述和导航；单源生成活动清单；移除 36 份复述型 guide、36 份通用占位模板及 36 份重复活动 JSON |

## 工程产出与安装路径

Skill 程序保存在安装根的 hs-dev-skill/scripts/（入口与 hs_dev/ 实现包），不复制到目标工程。

目标工程使用 hs_dev_docs/ 保存当前有效文档，hs-dev-skill/ 保存运行数据：

```text
hs-dev-skill/
  config/config.json
  state/workspace.sqlite
  tasks/<task_id>/
    task.json
    config/config.json
    resolved_config.json
    plan.md
    current.md
    activities/<activity_id>/results.json
    evidence/
    acceptance/decisions.json
    acceptance/overview.md
  index/catalog.sqlite
  index/files.jsonl
  index/publication.json
  cache/
  recovery/
  trace/
```

decisions.json 是确认记录权威源，overview.md 是派生视图。任务结果只引用规则 ID 和摘要，不复制标准正文。业务设计目录按需建立。

## 验证证据

- `python -m unittest discover -s hs-dev-skill/scripts/tests -v`：31 项通过，包含 UUID/fence、并发所有权、同 UUID 写互斥、任务/路径范围、外部漂移、索引损坏、失败回退、整任务回退、实际依赖、三种模式、单次材料确认、上下文预算、冷热读取与 trace。
- `python hs-dev-skill/scripts/build_docs.py --check`：通过，生成源与已发布资产一致。
- skill-creator 的 `quick_validate.py .`：通过。
- `bundle.validate('.')`：通过，版本 5.1.0.0，108 个内部检查项，错误为空。
- Python AST 语法检查与 `git diff --check`：通过。
- 实际独立进程启动 Unix socket 服务：检索、热上下文均通过，socket 权限 0600；服务启用 200 MB 地址空间限制。

测试与服务运行均使用临时目标工程，未在源码工程初始化业务运行目录。

## 本机性能观察

同一解释器及机器，用修改前恢复副本与当前源码分别处理 200 个 Python 文件、30 份 Markdown。每个 Python 文件含 40 个简单函数，每份文档含 30 组标题与契约文字。初始化产生的目录和索引数量随各版本实际行为变化。

| 操作 | 修改前 | 当前 |
|---|---:|---:|
| 初始化 | 587.38 ms | 536.08 ms |
| 独立 Index 冷查询，3 次均值 | 153.62 ms | 21.08 ms |
| 同 Index 热查询，5 次均值 | 27.25 ms | 11.18 ms |
| 装配 6 份文档 | 293.33 ms | 28.56 ms |

该结果是一次本机合成样本观察，不代表所有工程的性能保证，也没有测量真实宿主会话的 token 节省率。

## 运行边界

- 意图分数属于未校准的轻量规则评分；模型兜底由宿主执行，没有偷偷加载本地模型或创建付费请求。
- CLI 无文件系统监听时通过枚举与摘要核验发现外部变化；UUID 管理受管流程，不能禁止其他程序直接编辑。
- 依赖当前按文件及实际输出摘要绑定，属于保守粒度；不宣称已实现任意符号级语义影响分析。
- trace 采用 best effort，有界存储不承担审计、验收或恢复权威。
- 旧运行格式明确拒绝自动读取或初始化覆盖；已有工程需显式安排迁移，不以重建丢弃其恢复数据。
