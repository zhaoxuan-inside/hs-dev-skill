# hs-dev-skill 5.1.0.0

以安全版本、活动依赖和有效证据协调软件开发的 Skill。Python 3.11+，SQLite FTS5，无第三方运行依赖。安装需保留完整包；Skill 程序与目标工程运行数据分开。

## 使用

```bash
python /skill/scripts/hs_dev.py --root /project init
python /skill/scripts/hs_dev.py --root /project status
python /skill/scripts/hs_dev.py --root /project classify '修复接口超时'
python /skill/scripts/hs_dev.py --root /project task-start '修复超时' --activities H1,E2,G1,G2
```

输出默认人类摘要并带 banner；全局 `--output json` 返回 meta 与 result，stdout 不混入展示文字。全局参数放在子命令前；JSON 参数支持 @file。真实验证命令必须使用 argv 数组。省略活动范围会拒绝创建，不铺开所有活动。

classify 返回 NEEDS_MODEL 时，由宿主结合 signals、candidates 和当前目标判断，再传 `--model '{"intent":"FIX","reason":"当前请求针对已复现的接口故障"}'`。置信评分是未校准启发式分数，不是概率。

## 修改与恢复

commit 自动申请 UUID、保存恢复点、执行验证并发布。已有工程外部编辑使用：

```bash
python /skill/scripts/hs_dev.py --root /project --output json operation-start
# 保存返回的 operation_id 与 fence；编辑前建立恢复点
python /skill/scripts/hs_dev.py --root /project --operation UUID --fence 1 snapshot --task TASK_ID
# 在该操作范围内编辑文件
python /skill/scripts/hs_dev.py --root /project --operation UUID --fence 1 reconcile --task TASK_ID --decision continue --checks @checks.json
python /skill/scripts/hs_dev.py --root /project --operation UUID --fence 1 operation-finish
```

`operation-status` 查看安全状态，`operation-revoke --reason ...` 只撤销已退出的持有者，保持待恢复。`rollback OPERATION_ID --decision rollback` 恢复单次操作；task-rollback 显式恢复整个任务。repair-index 只修复源基线未变的索引，查询不会自动重建。

## 依赖与确认

本任务未执行的必要上游，通过 `dependency-bind TASK_ID CONSUMER PRODUCER path --actor human --confirmation '实际确认原文'` 引用有效产物。活动执行按依赖检查，不按列表位置强制串行。

check 记录检查项及证据；acceptance-material 登记需要审阅的交付材料；acceptance 展示统一视图；approve 确认活动或阶段。逐材料决定全部通过且清单就绪时完成同一范围确认，不额外要求重复交互。日志不自动变成主要材料卡。

## 上下文与追踪

`context --task TASK_ID --query '接口' --required hs_dev_docs/api.md` 装配当前任务和必要片段。热数据有界常驻，温数据正文进入 FTS，冷数据使用 `<!-- hs: {"tier":"cold"} -->` 标记后按磁盘读取。恢复数据排除检索。

trace 默认关闭，全局 --trace 临时开启，也可配置 trace.enabled。`trace-query --task-id TASK_ID` 返回有界摘要事件；trace 不影响确认模式、恢复或业务结果。

## 路径与配置

工程产出为 hs_dev_docs/（有效文档）和 hs-dev-skill/（config、state、tasks、index、cache、recovery、trace）。目录按实际需要创建。Skill 源码在安装根 src/hs_dev/，不复制到目标工程。

配置优先级：直接参数＞任务＞项目＞主机＞默认；主机 ~/.hs-dev-skill/config/config.json，项目 hs-dev-skill/config/config.json，任务 hs-dev-skill/tasks/<id>/config/config.json。唯一活动任务自动供运行消费者使用；索引预算改变后常驻服务须重启。旧运行格式明确拒绝，不自动迁移或丢弃恢复信息。

## 验证

```bash
python -m unittest discover -s tests -v
python scripts/hs_dev.py --root /project --output json verify
```

活动目录见[地图](workflow/README.md)，模块及数据契约见[整体设计](docs/skill-redesign.md)。
