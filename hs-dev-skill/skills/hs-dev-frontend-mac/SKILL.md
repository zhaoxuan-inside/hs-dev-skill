---
name: hs-dev-frontend-mac
description: macOS 界面的窗口/文档、菜单快捷键、系统授权和辅助功能规则，按主题加载。
license: MIT
---

# macOS 前端特性

与 [前端基础](../hs-dev-frontend-base/SKILL.md)配合。应用结构和窗口生命周期由[客户端框架基础](../hs-dev-framework-client-base/SKILL.md)负责；本入口只路由 macOS 界面专属细节。

只读取命中本次目标的端侧资料；通用要求和验证方式见前端 Base，不重复加载。

| 当前涉及的特性 | 专有资料 |
|---|---|
| 窗口/文档、多窗口、菜单、快捷键和键盘操作 | [window document input](references/window-document-input.md) |
| 系统外观、VoiceOver、权限、沙箱或分发集成 | [system integration accessibility](references/system-integration-accessibility.md) |

当前平台资料用于补充平台行为；不要因为项目目标平台明确就加载表中全部资料。

先核实实际 UI 工具包及版本、macOS 部署目标、应用/文档模型、窗口支持和分发环境，复用框架 Base 已有基线。按本次任务选择专题；平台机制核对对应版本的官方契约，不把移动端机制直接套用于桌面。缺失产品行为返回当前过程，不默认增加窗口、权限或渠道。

沿用 Base 的逐项状态及证据格式，记录系统版本、工具包、窗口/文档和授权初始状态、相关系统设置、操作及实际结果。截图不能证明菜单、键盘或 VoiceOver 操作可用；无真实环境时标记未验证。沙箱、签名、公证和发布配置由框架 Base 与当前过程处理，本入口只检查相关用户体验并共享证据，不代替框架验证或人工确认。
