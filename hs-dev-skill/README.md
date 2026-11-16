# hs-dev-skill 0.0.2

面向 Agent 开发者的软件工程 Skill。它帮助开发者取得有效输入、参与充分讨论、按明确边界实施并用真实证据交付；程序承担索引、状态、锁、日志与一致性检查，模型承担有来源的理解和判断。

从 [SKILL.md](SKILL.md) 开始。当前问题决定选择哪个阶段，不要求每次重走完整流程。

| 要解决的问题 | 去哪里 |
|---|---|
| 真正的问题、价值和业务边界是什么 | [A 产品意图](skills/hs-dev-intent/SKILL.md) |
| 功能、用户操作和异常结果应怎样工作 | [B 产品设计](skills/hs-dev-product/SKILL.md) |
| 质量要求、技术限制和关键取舍是什么 | [C 质量与决定](skills/hs-dev-decisions/SKILL.md) |
| 职责、信息所有权和依赖如何划分 | [D 架构设计](skills/hs-dev-architecture/SKILL.md) |
| 当前范围需要哪些契约和验证条件 | [E 工程准备](skills/hs-dev-engineering/SKILL.md) |
| 如何形成可执行的小步交付 | [F 交付规划](skills/hs-dev-planning/SKILL.md) |
| 如何实现、修复、验证与集成 | [G 开发与验证](skills/hs-dev-development/SKILL.md) |
| 如何独立检查变更与处理分歧 | [R 技术评审](skills/hs-dev-review/SKILL.md) |
| 如何核实实际交付、接受与反馈 | [H 交付反馈](skills/hs-dev-delivery/SKILL.md) |

具体活动、最低字段、来源要求和失败处理由[活动目录](references/catalog.json)定义。共用方法只有三份：[工作循环](references/cycle.md)、[信息与依据](references/information.md)、[讨论与提问](references/questioning.md)。

## 一个交付的工作方式

先查证来源、理解并追问，明确最低标准后形成含验证和恢复的方案。核实实际配置与授权，复用已有授权；锁住相关代码和文档并复核基线，再小步修改、同步资料、实际验证和一致性提交，最后解锁。需求或契约出现缺口时回到负责阶段，不用代码现状反向改写要求。

前期对重要需求实际组织独立角色 Agent 分析与交叉质疑；后期复用有效认知，只问新差异。角色推断不当作真实用户证据，没有委派工具时明确降级。

## 信息在哪里

- `hs-dev/project/`：当前有效的项目认识、规则、契约与决定入口。
- `hs-dev/deliveries/`：本次范围、方案、完成标准、产物与交付说明。
- `hs-dev/execution/`：程序管理的索引、任务状态、锁、日志和执行证据。

代码仍在工程源目录。先定位再读取必要正文，项目规则只维护一份；交付与执行记录引用其版本，不复制出新的权威。模板不填写假事实，必要输入缺失、冲突、过期或未验证时说明具体影响及下一动作。

CLI 入口为 `python3 scripts/hs-dev.py --root <工程根> <command>`。先用 `--help` 查看程序实际支持的命令和输入；操作映射见[工作循环](references/cycle.md#程序接口与顺序)，实际 JSON 字段与限制见[执行接口](references/cli.md)。初始化须显式执行，旧格式不自动迁移。程序通过不等于业务判断已被证明，完成结论应限定于实际范围和证据。
