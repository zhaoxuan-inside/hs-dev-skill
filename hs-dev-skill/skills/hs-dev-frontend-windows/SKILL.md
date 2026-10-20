---
name: hs-dev-frontend-windows
description: Windows 桌面界面的窗口、输入、系统集成和辅助功能规则，按主题加载。
license: MIT
---

# Windows 前端特性

与 [前端基础](../hs-dev-frontend-base/SKILL.md)配合。应用框架、窗口生命周期和进程结构由[Windows 客户端框架](../hs-dev-framework-client-windows/SKILL.md)负责；本入口只路由界面专属细节。

只读取命中本次目标的端侧资料；通用要求和验证方式见前端 Base，不重复加载。

| 当前涉及的特性 | 专有资料 |
|---|---|
| 窗口大小、键鼠/触控/触笔输入、焦点和系统外观 | [window input accessibility](references/window-input-accessibility.md) |
| 文件、剪贴板、通知、协议链接、关闭或更新体验 | [desktop integration](references/desktop-integration.md) |

当前平台资料用于补充平台行为；不要因为项目目标平台明确就加载表中全部资料。

先核实实际 UI 工具包及版本、Windows 支持范围、窗口与输入模型、显示设置和运行包环境，复用 Windows 框架专项已有基线。按本次任务选择专题，平台机制核对适用版本的官方契约；不默认改换技术栈或支持所有设备。产品行为缺失时返回当前过程。

沿用 Base 的逐项状态和证据格式，记录系统版本、工具包、窗口/显示条件、输入方式、用户权限、相关包环境以及操作与实际结果。截图不能证明焦点、输入或读屏可用；未执行项标记未验证。安装、签名、应用身份和更新机制与框架专项共享证据，本入口只检查用户体验，不代替框架验证或人工确认。
