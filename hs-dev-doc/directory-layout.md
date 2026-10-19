# 目录布局与维护

## 职责

- 安装根的 SKILL.md 是主入口，README.md 是使用说明。
- hs-dev-doc/ 保存本 Skill 的设计、演进和验证资料。
- hs-dev-skill/references/ 保存场景入口、活动、知识库、Schema、模板与协议。
- hs-dev-skill/scripts/ 保存工具入口、hs_dev/ 实现包、tests/ 和 Python 打包配置。
- 原 agents/openai.yaml 保留为 host-adapters/openai.yaml 示例，核心运行不需要 agents/。

目标工程的 hs-dev-skill/ 是运行数据目录，与安装根内部的程序目录含义不同。目录迁移不更改目标工程运行数据格式，也不自动迁移已有工程或已安装旧包。

## 命令

在安装根执行：

```bash
python3 hs-dev-skill/scripts/hs_dev.py --version
python3 hs-dev-skill/scripts/build_docs.py --check
python3 -m unittest discover -s hs-dev-skill/scripts/tests -v
```

如需构建 Python 包，在 hs-dev-skill/scripts/ 下使用 pyproject.toml。Python 包仅提供工具程序；Agent 安装仍需包含 SKILL.md 和参考资料的完整 Skill 包。

安装更新使用完整包根。包校验、connect 生成的命令、构建器及测试均使用新目录。完整包更新必须保留内部 hs-dev-skill/，不能将其当作目标工程运行数据排除。

## 迁移验证

- 新目录下 75 项自动化测试通过，包含完整包首次安装、重复更新、异地启动和 connect 入口验证。
- 活动资产生成器的 --check 校验通过。
- 全部 Markdown 本地文件链接和 Python 语法检查通过。
- 修正 connect 写入宿主指令后未发布索引的问题，确保生成指令后工作区可通过一致性检查。
