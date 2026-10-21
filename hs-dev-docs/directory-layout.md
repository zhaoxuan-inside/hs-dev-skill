# 目录与维护

## 三种目录边界

| 场所 | 路径 | 用途 |
|---|---|---|
| 源码仓库 | `hs-dev-skill/SKILL.md` | 总控权威入口 |
| 源码仓库 | `hs-dev-skill/skills/<name>/` | 31 个子 Skill 及专属资料 |
| 源码仓库 | `hs-dev-skill/share/` | 共享协议、活动、索引、模板、Schema 与专题 |
| 源码仓库 | `hs-dev-skill/scripts/` | CLI、Python 实现、测试、文档与包构建器 |
| 源码仓库 | `hs-dev-docs/` | 本 Skill 的说明、分析与验证历史 |
| 构建结果 | `output/skills/<name>/` | 可独立安装的完整 Skill 包 |
| 目标工程 | `hs_dev_docs/` | 当前有效的需求、设计与契约 |
| 目标工程 | `hs-dev-skill/` | 配置、任务、索引、证据、恢复与追踪数据 |

源码路径不能直接当作目标工程运行目录。目标工程运行数据中，`config/` 保存配置，`state/` 保存工作区状态，`tasks/<task_id>/` 保存任务和活动记录，`index/` 保存派生索引，`recovery/` 保存恢复依据，`trace/` 保存可选摘要。实际生成文件以当前程序为准，不预建全部业务文档目录。

## 源与派生物

`hs-dev-skill/skill-packages.json`声明分类及打包策略。子 Skill 的权威入口位于 skills，共享规则在 share 单点维护；构建器复制所需引用闭包并改写安装包内链接。独立包具备本地资料，不等于运行时全部加载；跨 Skill 协作不自动成为安装依赖。

`share/` 的 `.idx` 用于逐层导航。活动文档和机器 catalog 由 `hs-dev-skill/scripts/build_docs.py`中的活动定义生成；编辑这些派生内容时先确认生成源，避免下次构建覆盖修改。该脚本构建的是共享活动资料，并不重建本 `hs-dev-docs/` 说明体系。

## 维护与检查

从仓库根运行：

```bash
python3 hs-dev-skill/scripts/hs_dev.py --version
python3 hs-dev-skill/scripts/build_docs.py --check
python3 hs-dev-skill/scripts/build_skill_packages.py
python3 -m unittest discover -s hs-dev-skill/scripts/tests -v
```

`--check` 核对已生成资料；不带它会写共享资料。包构建写入 `output/skills/`，不会安装到其他宿主。完整测试适用于运行时变更；纯文档调整优先检查本地链接、源覆盖、生成一致性和包引用。

安装后的 CLI 通常位于包根 `scripts/hs_dev.py`，源码仓库 CLI 位于 `hs-dev-skill/scripts/hs_dev.py`。命令参数以当前 `--help` 为准，更新通过 install 执行，不猜测 update 子命令。

## 文档演进规则

当前说明保留稳定入口；旧方案和旧验证移入 history，并明确日期、源版本和结论边界。新增或移除 Skill 同步核对 manifest、Skill 目录、加载矩阵及打包结果。来源清单保存内容摘要用于定位变化，不作为人工确认或运行通过证明。

可选宿主配置见 [host-adapters](host-adapters/README.md)。本次重建记录见[验证记录](implementation-verification.md)。
