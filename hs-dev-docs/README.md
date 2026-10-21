# hs-dev-skill 文档体系

本体系依据仓库内 **v6.0.0.0** 源文件重建，调查日期为 2026-10-21。覆盖总控和全部 31 个子 Skill，并关联共享活动、协议及工具入口。这里记录当前结构及使用边界；执行规则以源 Skill 和共享协议为准。

| 阅读目标 | 文档 |
|---|---|
| 理解定位、能力与授权边界 | [产品与能力](product-overview.md) |
| 查找全部 Skill 的职责和源入口 | [Skill 目录](skill-catalog.md) |
| 判断如何进入过程、按需加载平台能力 | [加载与路由](skill-loading.md) |
| 查询 A～H 活动、输入输出与依赖 | [活动与交付](workflow.md) |
| 理解模块协作、修改、上下文和验收 | [体系与运行机制](skill-redesign.md) |
| 区分源码、安装包和目标工程 | [目录与维护](directory-layout.md) |
| 查看本次检查、范围和局限 | [验证记录](implementation-verification.md) |
| 复核源文件内容版本 | [来源清单](source-baseline.json) |
| 查询历史演进 | [历史资料](history/README.md) |
| 使用可选宿主示例 | [宿主适配](host-adapters/README.md) |

入门安装与示例见[仓库 README](../README.md)。本文档目录 `hs-dev-docs/` 与目标工程当前知识目录 `hs_dev_docs/` 用途不同。

维护顺序：先修改权威 Skill、共享协议或程序，再更新受影响说明和来源清单，执行适用检查。文档导航不构成上下文必读清单；不要把整套文档默认装入日常任务。
