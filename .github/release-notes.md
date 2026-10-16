产品开发主路由 Skill：10 个过程子 Skill、6 个功能子 Skill，以及共享详规、脚本和模板。

本版包含全流程审计修复：索引摘要重建、显式校验目标、假代码门禁、无 UI 项目与 S/M/L 分级适用性、API/Mock 错误契约及文档命令与模板对齐。

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
