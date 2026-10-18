---
name: hs-dev-skill
description: >-
  Handle software development: requirements, product and technical design,
  implementation, bug fixes, refactoring, tests, project investigation,
  acceptance and continuation. 开发、修复、重构、设计、测试、验收与续做先核验
  任务及代码、文档、索引、缓存一致性，再执行实际影响的活动。排除无关通用问答。
license: MIT
metadata:
  author: hardstone
  version: "5.0.0.0"
  runtime: "Python >= 3.11, SQLite FTS5; install complete bundle"
---

# 可恢复、可验证的开发活动

先读当前入口，再读一个场景入口及当前活动。[活动地图](workflow/README.md)组织A～H规则；历史过程和未触达领域不加载。

## 每次进入先检查

在目标工程执行`python <安装根>/scripts/hs_dev.py --root <工程根> status`。首次显式`init`；初始化或重建不等于验收。未完成、待验收、失败、回滚中任务或代码／文档／索引不一致时，展示范围与恢复点，让用户选择继续原任务或回退。解除阻断前不建新任务，mute亦不免除。继续、需求确认、补充和纯咨询不生成新任务ID。

## 识别与活动路径

确定性信号＋轻量NLP＋模型语义判断。显式指令、权限、否定和一致性门禁优先；模糊场景补充模型理由。`classify`返回入口、信号和是否需要模型补判，不自动执行。

| 场景 | 入口和边界 |
|---|---|
| 新产品／功能 | A宏观收集、B完整功能提取；A不安排优先级和分期 |
| 修复／重构 | H1阅读实际代码与行为基线，核验需求；仅重做受影响活动 |
| 设计 | 对应A～E，核验上游有效性，未知不靠猜测补全 |
| 续做／回退 | 连续性与恢复，复用task_id，恢复全部修改 |
| 只读分析 | exploration，不建任务、快照或PRD，不自动修改 |

[场景与领域入口](skills/README.md)只组织当前活动，不各自复制一套流水线。不强制A到H顺序；反馈进入受影响活动，不自动生成新任务。

## 执行与验收

新任务通过门禁后生成时间戳ID，配置直接描述＞任务＞项目＞主机。默认stage阶段人工；activity逐活动人工；mute模型验收且标明来源。所有模式执行完整适用清单和真实验证，不能代签人工确认。权限与外部授权独立于模式。

每个阶段与活动有README，活动有清单，内部活动是最小验收单元。当前目标、有效契约、代码片段、未决项和验收条件组成活跃工作集。人工产出优先Markdown表格、Mermaid；机器契约及配置使用JSON。

每次验收统一调用[验收服务](references/core/acceptance.md)，正常执行输出之外展示「进度导航＋材料卡片＋结果摘要」。材料列出链接、审阅重点及状态；宿主支持时勾选，否则按编号或名称回答。回答映射稳定材料ID并绑定视图版本，含糊回答先澄清，未提及项不变。不通过逐项沟通暂不处理或继续修复，记录原因和下一动作；暂缓不记通过，依赖范围保持阻断。材料或相关清单变化后重新验收。

修改前恢复准备，新任务／重大／大量修改先快照。登记→修改代码与文档→真实验证→发布索引→失效缓存→一致性核验→提交状态。缓存、索引文档、内容文档、代码绑定同一有效修订。中断与后续编辑冲突不能当成成功。

正式代码、配置、测试、Mock数据与服务分开；外部依赖按真实协议建立独立Mock，通过地址配置替换。业务与运行含义的魔法值使用命名常量、枚举或配置。5.0只支持当前契约，无旧格式读取或兼容入口。

## 工具

```bash
python scripts/hs_dev.py --root /project status
python scripts/hs_dev.py --root /project classify '重构任务执行器'
python scripts/hs_dev.py --root /project task-start '调整任务执行器' --activities H1,E3,G1,G2,G3,G4,H2,H3
python scripts/hs_dev.py --root /project search --query '恢复' --filters '{"tags":["recovery"]}'
```

主流程规则见[执行协议](references/core/execution.md)，命令与限制见[README](README.md)。`connect`显式安装项目入口约定，须新会话验证触发。宿主未加载Skill时，正文无法强制拦截；不承诺安装即可零漏触发，不自动修改其他项目或全局配置，不自动发布。
