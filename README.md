# hs-dev-skill 0.0.2

将 Agent 作为开发者，用有效信息支持判断，用明确的产出契约和执行记录约束开发。从需求讨论到交付，所有阶段共享同一个工作循环。

入口：[主 Skill](hs-dev-skill/SKILL.md) · [阶段和活动](hs-dev-skill/references/activities.md) · [使用说明](hs-dev-skill/README.md) · [版本说明](release-notes.md) · [验证与边界](hs-dev-skill/references/verification.md)

## 组成

| 部分 | 内容 |
|---|---|
| Skill 入口 | 1 个主 Skill、9 个阶段子 Skill |
| 活动契约 | 38 个活动、114 个输出；每项包含具体问题、证据要求、可检查标准与异常处理 |
| 信息生产 | 固定模板组织内容，模型依据来源判断和总结；未知、假设、冲突分别保留 |
| 讨论机制 | 前期主动调查与独立角色交叉质疑，后期复用有效认识并处理新差异 |
| 执行控制 | 来源与评估绑定、计划授权、代码和文档锁定、验证、恢复、一致性提交后解锁 |
| 检索 | 当前文档与代码的可重建索引、有限定位卡片、版本摘要核验、关联入口 |

## 工程中的信息

```text
<工程>/
├── 业务代码与原生工程文件
└── hs-dev/
    ├── project/       # 当前有效的规则、契约与事实；包含内容和索引入口
    ├── deliveries/    # 每次变更的沟通、原因、决定与交付结果
    └── execution/     # 程序状态、索引、锁、快照、验证证据；不手改
```

项目规范与实现事实分开描述；不能为了迎合错误代码而改写需求。信息只保留一个有效正本，交付和执行记录引用来源和版本。

## 运行与验证

需要 Python 3.11+、SQLite FTS5；执行锁使用 POSIX `flock`。无第三方 Python 依赖。先查实际接口，初始化必须显式进行：

```sh
python3 hs-dev-skill/scripts/hs-dev.py --help
python3 hs-dev-skill/scripts/hs-dev.py template --activity A1
python3 hs-dev-skill/scripts/hs-dev.py --root /path/to/project init
```

在仓库根检查与构建：

```sh
python3 hs-dev-skill/scripts/check.py
PYTHONPATH=hs-dev-skill/scripts python3 -m unittest discover -s hs-dev-skill/tests -v
python3 hs-dev-skill/scripts/build.py --output /path/outside/source/packages
```

构建产生主 Skill 与九个可独立携带运行工具的阶段包、版本及摘要清单。将相应包中的同名目录安装到目标工具的 Skill 目录；仓库构建不等于已安装。

## 边界

本版本从零重建，不继承旧代码、命令或状态，不自动迁移旧工程。受管锁不能阻止外部编辑，因此每次写入和提交还会核对内容。一致性提交是本地交付记录，与 Git 提交、部署和发布分别处理。

来源登记不证明发言人身份，也不证明业务内容真实；程序检查支持开发者判断。实际需求讨论、来源采集、角色分析与业务接受需要真实执行，不能用模板或机器通过代替。
