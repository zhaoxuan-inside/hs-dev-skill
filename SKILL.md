---
name: hs-dev-skill
description: >-
  Coordinate software development, design, fixes, refactoring, tests and project
  investigation through safe workspace access, signal-based intent and activity
  dependencies. 开发、设计、修复、重构、验收、续做和只读分析；排除无关问答。
license: MIT
metadata:
  author: hardstone
  version: "6.0.0.0"
  runtime: "Python >= 3.11, SQLite FTS5; install complete bundle"
---

# hs-dev-skill

第一项工程操作执行 `python <安装根>/hs-dev-skill/scripts/hs_dev.py --root <工程根> status`。修改或回退进行中等待；中断或漂移进入恢复，不读取混合版本。首次工程显式 init；不以重建索引代替验收。

开始逻辑任务时展示 `hs-dev-skill | 版本 | 场景 | 确认模式 | trace on/off`。宿主集成只展示一次；底层命令 JSON 通过 meta 标识来源。

## 当前目标与路径

读取[场景入口](hs-dev-skill/references/skills/README.md)中的一个过程 Skill，再按实际触达领域读取专业入口。仅加载[活动地图](hs-dev-skill/references/workflow/README.md)相关内容。

- 信号提取与意图决策分离；无信号、低置信度或冲突时，使用宿主模型通过 classify --model 返回意图及理由。权限与安全门禁独立执行。
- 新任务按实际影响明确选择活动，续做复用 task_id。上游可以来自本任务已完成结果或明确绑定的已验收产物，不强制重走 A～H。
- 咨询不建任务、不修改业务内容、不自动修复索引。协调状态读取与可选 trace 不等同业务修改。
- 内容通过 `context @request.json` 获取，选择器用 `required: true` 标明必要约束；先检查 status 与 coverage，再使用 body。恢复快照和恢复历史不提供给模型。

## 修改与确认

受管修改先取得 UUID 与操作代次。commit 自动申请；外部编辑先 operation-start 并 snapshot，后续携带 --operation/--fence 完成 reconcile 和 operation-finish。失联所有者撤销后仍需恢复核验，不能直接宣布安全。

代码提交统一核验活动及上游依赖。reconcile 必须指定 --activity，检查实际变更符合操作范围，登记活动输出并撤销旧确认；验证期间受管源文件发生变化时拒绝发布。commit 只接受源清单和快照可覆盖的路径。上述提交是受管文件发布，不自动创建 Git commit。

任务按清单工作、真实验证并记录证据；清单标准与任务结果分别保存。mute 模型确认、activity 活动人工、stage 阶段人工；trace 是独立追踪开关。统一确认展示范围、检查摘要、交付材料与问题，日志作为支撑证据。真实确认原文不得代签，暂缓不是通过。

后续活动消费有效上游结果。验收绑定清单、内容和实际依赖；无关修改或索引重建不撤销验收。恢复准备、修改、验证、发布与核验由应用模块协调，未验证版本不能对外标为安全。

正式代码、配置、测试、Mock 数据与服务分开；外部 Mock 遵循真实协议，通过地址配置替换。无魔法业务值，不因流程扩展业务需求。

详见[执行协议](hs-dev-skill/references/core/execution.md)、[验收协议](hs-dev-skill/references/core/acceptance.md)、[索引与上下文](hs-dev-skill/references/indexing/protocol.md)、[追踪](hs-dev-skill/references/support/trace.md)及[命令说明](README.md)。完整[目标设计](hs-dev-doc/skill-redesign.md)供体系审阅，不要求每次执行通读。
