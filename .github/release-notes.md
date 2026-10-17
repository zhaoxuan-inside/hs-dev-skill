产品开发主路由 Skill：10 个过程子 Skill、6 个功能子 Skill，以及共享详规、脚本和模板。

本版新增与改进：

- 完善主入口触发条件及项目入口约定，减少开发任务绕过 Skill 的情况。
- 每个实际阶段提交验收时，完整展示文档名称、绝对路径、版本和状态。
- 引入变化感知装载：未变化的内容复用，发生变化后只重新读取需要的范围。
- 将 9 组大规则拆成 41 个业务分册，两组大模板拆为 9 个片段；检索直达当前主题。
- 提供完整包更新、需求基线与派生失效检查、执行观测及分级优化工具。

验证：174 项单元测试、3 项示例测试及严格一致性检查通过。发行 ZIP 仅包含 Skill 本体、说明、模板、示例及测试，不包含项目过程记录、恢复快照或会话轨迹。

## 安装

```bash
npx skills add zhaoxuan-inside/hs-dev-skill --skill hs-dev-skill
```

也可下载完整 ZIP 并解压，将整个 `hs-dev-skill` 目录安装至 Agent 的技能目录。子 Skill 依赖主包共享资源，不要单独复制子目录。

要求 Python >= 3.8。安装后在完整包目录运行：

```bash
python scripts/skill_router.py check
```

Linux/macOS 可用 `python3`，Windows 可用 `py -3`。`SHA256SUMS` 提供发行 ZIP 的 SHA-256 校验和。
