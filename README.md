# hs-dev-skill 5.0.0.0

工程活动契约、精简上下文、逐内部活动验收与完整恢复。Python 3.11+，SQLite FTS5。只接受当前格式，无旧版兼容入口。

## 使用

保留完整安装包，直接执行：

```bash
python scripts/hs_dev.py --version
python scripts/hs_dev.py --root /your/project init
python scripts/hs_dev.py --root /your/project connect
python scripts/hs_dev.py --root /your/project status
```

`connect`显式追加AGENTS.md且保留原内容；追加后按正常修改验证和发布索引。自动触发依赖宿主加载Skill和项目指令，须新会话验证。不会自动修改其他项目或用户主目录。可用`python -m pip install -e .`安装`hs-dev`命令，资源入口仍需完整包。

除帮助、版本、参数用法提示和显式`acceptance --format markdown`外，命令输出JSON，失败非零退出码，`--root`在子命令前。JSON参数可用`@file.json`，验证命令使用argv数组，不执行shell字符串。

## 流程和模式

`status`先检查未完成任务和代码／文档／索引一致性；阻断时用户决定继续或回退。只读咨询、需求确认和继续不建新任务。分类结合信号、NLP和模型理由，不凭关键词授权修改。

```bash
python scripts/hs_dev.py --root /project classify '修复接口超时' --signals '{"test_failed":true}'
python scripts/hs_dev.py --root /project task-start '修复超时' --activities H1,E2,E4,G1,G2,G3,G4,H2,H3
python scripts/hs_dev.py --root /project task-continue TASK_ID
```

配置文件`config.json`依次位于主机`~/.hs-dev-skill/config/`、项目`hs-dev-skill/config/`、任务`hs-dev-skill/task/<id>/config/`。直接描述＞任务＞项目＞主机＞默认，`config`显示来源，未知键或无效值失败。唯一活动任务的配置自动传递到运行消费者；索引预算改变时，常驻服务要求重启后查询。

默认stage阶段人工；activity活动人工；mute模型验收，流程证据不省略。恢复决定及宿主权限不因mute免除。源版本、证据或清单变化使旧确认失效。

```bash
python scripts/hs_dev.py --root /project check TASK_ID G2 G2.1 PASS --evidence evidence.md
python scripts/hs_dev.py --root /project approve TASK_ID G --actor human --confirmation '真实来源与明确确认原文'
python scripts/hs_dev.py --root /project complete TASK_ID --checks @verification.json
```

人工清单及记录为Markdown，机器索引派生；CLI参数不能替代真实人工确认。A阶段仅宏观收集，B先完整功能提取再逐功能和整体设计，E构建契约／测试／Mock／配置，F安排优先级与分期。见[活动地图](workflow/README.md)。

各阶段、活动共用[统一验收服务](references/core/acceptance.md)。正常执行输出之外，以进度导航、材料卡片和结果摘要展示待审文档；检查证据及版本默认折叠。登记材料或检查证据自动进入清单；逐材料决定与范围最终确认分开保存。

```bash
python scripts/hs_dev.py --root /project acceptance-material TASK_ID G2 docs/design.md --title '交互方案' --focus '正常与异常反馈是否清楚'
python scripts/hs_dev.py --root /project acceptance TASK_ID --scope G --format markdown
python scripts/hs_dev.py --root /project acceptance TASK_ID --scope G
python scripts/hs_dev.py --root /project acceptance-decide TASK_ID G --materials MATERIAL_ID --decision pass --actor human --confirmation '用户：交互方案通过' --view-digest VIEW_DIGEST
```

宿主可将勾选或明确文字反馈映射成材料ID；CLI不猜测自然语言。未通过材料使用`reject`记录问题并沟通；决定后使用`defer`或`repair`，同时给出`--reason`和`--next-action`。暂缓仍是未通过，不能执行范围确认。修改后刷新视图再逐项确认。完整范围`approve`可一次确认尚待审阅材料，不能覆盖已有未通过、缺失或过期记录。

## 修改与恢复

`commit`接收JSON路径到UTF-8内容，null删除；二进制或外部编辑先snapshot，再显式continue后reconcile。不可直接改派生索引、运行状态或符号链接。

```bash
python scripts/hs_dev.py --root /project commit TASK_ID --activity G1 --changes @changes.json --checks @verification.json
python scripts/hs_dev.py --root /project rollback OPERATION_ID --decision rollback
python scripts/hs_dev.py --root /project reconcile --task TASK_ID --decision continue --checks @verification.json
python scripts/hs_dev.py --root /project task-rollback TASK_ID --decision rollback
```

快照＋changelog覆盖完整修改集合；普通操作回滚保护后续编辑，明确整体任务回退恢复整个基线。任务和快照超过48小时或超过最近5个清理，使用中恢复点暂缓；证据先归档，未完成任务留下阻断记录。任务入口及`retention`触发清理，无离线后台清理承诺。

## 检索与内存

属性、标签精确查询，FTS5中文词项和短语检索，关系查询及Python符号定位；无LIKE回退。history默认不搜，内容切片核验源摘要。

```bash
python scripts/hs_dev.py --root /project search --query '登录' --filters '{"tags":["http","mock"]}'
python scripts/hs_dev.py --root /project read hs_dev_docs/design.md --start 1 --end 40
python scripts/hs_dev.py --root /project context hs_dev_docs/design.md
python scripts/hs_dev.py --root /project serve
python scripts/hs_dev.py --root /project service-query '{"action":"search","query":"任务"}'
```

源属性：`<!-- hs: {"id":"API-001","activity":"E2","tags":["http","mock"],"status":"current"} -->`。关系relations数组指定source、target、kind。标签数组表示全部包含，`any`、`exclude`提供组合语义。

本地只读socket权限0600，串行请求有界。POSIX用RLIMIT_AS将整个服务地址空间限制在200MB以内；非POSIX严格常驻服务明确拒绝启动，可用有界CLI。预算覆盖常驻任务、SQLite、字节LRU和临时空间，不全量加载数据库或大型模型。

修订、摘要、代次校验缓存、索引、文档和代码；结构一致不能证明行为，必须另有实际验证。外部漂移阻断，不用重建冒充验收。
