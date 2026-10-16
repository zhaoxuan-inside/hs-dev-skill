# hs-dev-skill：AI 驱动文档，文档驱动代码

> 让开发过程看得见、留得住，让模型依据已确认的文档推进，而不是随意猜测。

[![Spec Version](https://img.shields.io/badge/skill-v4.0.1.0-blue.svg)](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/SKILL.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/LICENSE)

**[GitHub 源码](https://github.com/zhaoxuan-inside/hs-dev-skill) · [skills.sh 安装入口](https://skills.sh/zhaoxuan-inside/hs-dev-skill/hs-dev-skill) · [完整下载](https://github.com/zhaoxuan-inside/hs-dev-skill/releases)**

用 AI 写代码时，困难经常出现在代码之外：需求没对齐就开始实现，修一个 Bug 顺手改了架构，换个会话又丢了上下文，最后只得到一句“已经完成”，却看不到验证依据。

`hs-dev-skill` 的核心理念是：**AI 驱动文档，文档驱动代码。** AI 协助把想法整理为需求、设计、原型、契约与任务；开发者确认关键内容后，模型依据这些文档实现代码，并把变更与验证结果写回记录。文档随开发持续更新，成为下一步工作的依据。

## 核心优势：过程可视、过程持久、决策有据

### 可视化开发过程：看得见正在做什么

通过需求说明、流程图、架构图、界面原型、任务状态与验收清单，展示从想法到实现的推进过程。开发者可以检查模型如何理解需求、采用了什么设计、正在推进哪一步，以及哪些结果仍待验证或确认。

### 持久化开发过程：让上下文成为项目资产

需求、设计决定、任务计划、变更日志、快照和验收证据按需保存在项目文件中。中断、换会话或交接后，模型可以先读取已有记录，恢复已确认的范围与工作断点，再继续推进。

### 让模型有据可依：明确事实、假设与待确认项

实现前读取相关文档与契约；需求存在空白时，显式记录假设和待确认问题；修复缺陷时，依据复现与根因证据；交付时，对照需求和验收标准回收结果。把模型的推断与开发者已确认的决定分开，减少因猜测而产生的偏离。

这套约束贯穿整个循环：**AI 整理文档 → 开发者确认关键内容 → 文档指导实现 → 测试与验收核对 → 结果回写文档。**

## 它能帮你做什么？

- **从想法启动项目**：梳理真实场景、范围和验收标准，明确 MVP，再推进设计与实现。
- **在已有项目里增加功能**：沿用有效设计，只补本次触达的部分，保持需求、接口、代码和测试一致。
- **修复实际 Bug**：先复现，再定位根因、做最小修复，并补回归验证。
- **整理已有代码**：区分只读理解、存量项目纳管和保持行为的重构，按对应目标推进。
- **继续未完成的任务**：通过计划、变更记录和快照恢复断点，沿用已有决定。
- **核对是否真的做完**：把需求与实现、测试及验收证据逐项对账，显式记录未实现项。

## 几个值得关注的设计

### 按任务走流程，小改动也有短路径

技能区分从零开发、调试修复、重构、存量纳管、只读探索和任务续做六类意图，同时按 S / M / L 判断变更规模。

例如，修一个清晰的边界判断错误，可以走“复现 → 修复 → 相关测试”的短路径；涉及新业务、公开契约或系统边界的变化，再补充对应设计和确认。只读理解代码时，不应创建任务、修改文件或提交代码。

### 一个主入口，按需组合 16 个子 Skill

主路由协调 **10 个过程 Skill + 6 个功能 Skill**。

过程 Skill 负责当前工作怎么推进，覆盖需求发现、设计、规划、实现、验收、调试、重构、存量纳管、探索和续做。功能 Skill 提供产品、架构、前端、后端、测试和工程治理方面的规则。

例如，“支付接口偶发超时”会进入调试流程，再加载涉及的后端与测试规则。共享脚本、详规和模板只维护一份；装载时按当前阶段与触达面选择内容，控制无关上下文的进入。

### “完成”需要可复核的证据

仓库包含索引一致性、任务状态、需求覆盖与假代码扫描等检查工具，并提供结构化验收记录模板。

适用测试、扫描结果和验收结论需要分别记录。脚本通过可以支持判断，但不能替代真实业务验证或开发者确认。

### 需求、设计与实现之间有可追踪的连接

在需要的阶段，流程会维护 PRD、接口与方法契约、任务上下文，以及测试和变更记录。有 UI 的项目还包括设计语言与原型；无 UI 项目使用 API、CLI 或库契约等适用证据。

目标是让后续改动有依据、任务中断后能恢复、交付结果能核对。文档量随任务规模和影响面调整。

## 安装

通过 skills CLI 安装到当前项目：

```bash
npx skills add zhaoxuan-inside/hs-dev-skill --skill hs-dev-skill
```

全局安装：

```bash
npx skills add zhaoxuan-inside/hs-dev-skill --skill hs-dev-skill -g
```

也可以从 [GitHub Releases](https://github.com/zhaoxuan-inside/hs-dev-skill/releases) 下载完整 ZIP，或克隆仓库：

```bash
git clone https://github.com/zhaoxuan-inside/hs-dev-skill.git
```

**请保留完整主包。** 主入口依赖包内的 `skills/`、`scripts/`、`references/` 和 `resources/`，不要只复制一个 `SKILL.md` 或单独安装子目录。

使用支持 Agent Skills 的编程助手加载主入口。脚本要求 **Python ≥ 3.8**；skills CLI 安装方式需要可运行 `npx` 的 Node.js 环境。Windows、Linux 和 macOS 的使用约定见[跨平台说明](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/references/cross_platform.md)。

在安装包根目录运行一次完整性检查：

```bash
python scripts/skill_router.py check
```

Linux/macOS 可使用 `python3`，Windows 可使用 `py -3`。命令应能找到全部 16 个子 Skill 和 51 份已登记详规。

## 可以这样开始

安装并加载主 Skill 后，可以用自然语言描述任务，也可以显式指定 `hs-dev-skill`。

**从新需求开始：**

```text
使用 hs-dev-skill，帮我设计一个小团队的采购审批工具。
先确认核心场景、MVP 范围和验收标准，再推进需要的设计与实现。
```

**修复已有问题：**

```text
使用 hs-dev-skill，排查订单重复提交的问题。
先复现并定位根因，再做最小修复和回归验证。
```

**只读理解代码：**

```text
使用 hs-dev-skill，只读分析这个项目的登录鉴权流程。
给出入口、关键调用和证据位置，不修改文件。
```

**继续已有任务：**

```text
使用 hs-dev-skill，继续上次的支付接口任务。
先恢复计划、已确认的决定和断点，再推进剩余工作。
```

以上是使用示例；实际执行仍取决于任务输入、助手可用工具和已授予的权限。

## 项目里包含什么？

- [主 Skill 入口](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/SKILL.md)：路由规则、共享边界与资源定位。
- [过程与功能子 Skill](https://github.com/zhaoxuan-inside/hs-dev-skill/tree/main/skills)：各类任务的职责、输入、输出与执行规则。
- [详规索引](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/references/_index.md)：按场景查找产品、工程和测试规则。
- [脚本工具](https://github.com/zhaoxuan-inside/hs-dev-skill/tree/main/scripts)：文档索引、任务、过程日志、规则检索和一致性检查。
- [模板](https://github.com/zhaoxuan-inside/hs-dev-skill/tree/main/resources/templates)：产品、架构、契约、任务与验收记录模板。
- [示例](https://github.com/zhaoxuan-inside/hs-dev-skill/tree/main/examples/order_service)与[测试](https://github.com/zhaoxuan-inside/hs-dev-skill/tree/main/tests)：帮助理解工具行为和验证已有能力。

开发者可在仓库根目录运行：

```bash
make test
make verify
```

Windows 可使用 `make test PYTHON="py -3"`。没有 Make 时，可查看 [Makefile](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/Makefile) 中的 Python 等价命令。本仓库的 `make verify` 显式检查 Skill 包与示例工程；业务项目使用 `verify_consistency.py --root <工程根> --strict` 检查对应工程。

## 适合谁？

适合希望把 AI 编程用于持续迭代的独立开发者、小团队，以及需要维护既有系统的开发者。尤其适合需求、代码和验证结果需要一起维护的项目。

这是工作流、规则和辅助工具的组合，效果依赖助手的执行、可用环境和人工评审。它不承诺自动消除 Bug，也不会因为安装了 Skill 就获得额外的文件或服务访问权限。

## 交流与参与

项目采用 [MIT License](https://github.com/zhaoxuan-inside/hs-dev-skill/blob/main/LICENSE)。欢迎试用、提 Issue 或提交 PR。

如果在真实项目里遇到流程过重、路由不准确、工具报错或模板冲突，欢迎在 [GitHub Issues](https://github.com/zhaoxuan-inside/hs-dev-skill/issues) 描述任务场景、期望行为和实际结果。

需要转载介绍时，可以使用仓库中的 `README.forum.md` 论坛宣传短版。
