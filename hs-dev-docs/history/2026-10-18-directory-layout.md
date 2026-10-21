> 历史资料：保留原始设计或验证结论，不代表当前版本状态。

# 目录布局与维护

## 职责

- hs-dev-skill/SKILL.md 和 hs-dev-skill/skills/ 保存总控与子 Skill 源码。
- 安装根的 SKILL.md 是主入口，README.md 是使用说明。
- hs-dev-docs/ 保存本 Skill 的设计、演进和验证资料。
- hs-dev-skill/share/ 保存场景入口、活动、知识库、Schema、模板与协议。
- hs-dev-skill/scripts/ 保存工具入口、hs_dev/ 实现包、tests/ 和 Python 打包配置。
- output/skills/ 保存可重建的总控与子 Skill 发布包。
- 原 agents/openai.yaml 保留为 host-adapters/openai.yaml 示例，核心运行不需要 agents/。

目标工程的 hs-dev-skill/ 是运行数据目录，与源码中的 hs-dev-skill/ 不同。发布安装应使用 output/skills 下生成的独立 Skill 包；源码仓库布局不是安装包布局。目录迁移不更改目标工程运行数据格式，也不自动迁移已有工程或已安装旧包。

## 命令

在源码仓库根执行：

```bash
python3 hs-dev-skill/scripts/hs_dev.py --version
python3 hs-dev-skill/scripts/build_docs.py --check
python3 -m unittest discover -s hs-dev-skill/scripts/tests -v
```

如需构建 Python 包，在 hs-dev-skill/scripts/ 下使用 pyproject.toml。Python 包仅提供工具程序；Agent 安装仍需包含 SKILL.md 和参考资料的完整 Skill 包。

从 output/skills/ 安装时，使用对应完整包根。安装后的 CLI 路径为 scripts/hs_dev.py；源码仓库中的 CLI 路径为 hs-dev-skill/scripts/hs_dev.py。包校验和更新逻辑兼容两种布局，不会把源码目录和目标工程运行数据混为一谈。

## 迁移验证

- 新目录下 75 项自动化测试通过，包含完整包首次安装、重复更新、异地启动和 connect 入口验证。
- 发布包构建校验通过；活动文档生成器的 --check 当前会报告 A1 活动指南与生成模板不一致，需单独同步生成规则或确认该手工扩展内容。
- 全部 Markdown 本地文件链接和 Python 语法检查通过。
- 修正 connect 写入宿主指令后未发布索引的问题，确保生成指令后工作区可通过一致性检查。
