---
name: hs-dev-frontend-linux
description: Linux 桌面界面的环境、显示协议、输入、系统门户和辅助功能规则，按主题加载。
license: MIT
---

# Linux 前端特性

与 [前端基础](../hs-dev-frontend-base/SKILL.md)配合。应用运行和打包架构由[Linux 客户端框架](../hs-dev-framework-client-linux/SKILL.md)负责；本入口只路由界面专属细节。

只读取命中本次目标的端侧资料；通用要求和验证方式见前端 Base，不重复加载。

| 当前涉及的特性 | 专有资料 |
|---|---|
| 桌面环境、主题、X11/Wayland、缩放和窗口/输入行为 | [desktop display input](references/desktop-display-input.md) |
| 系统门户、辅助技术和分发包带来的界面差异 | [portals accessibility packaging](references/portals-accessibility-packaging.md) |

当前平台资料用于补充平台行为；不要因为项目目标平台明确就加载表中全部资料。

执行前核实相关工具包及版本、桌面环境、实际显示后端、缩放和目标分发方式；复用 Linux 框架专项已有且仍适用的基线。按本次目标和支持范围选择专题条目，涉及平台机制时核对对应版本的官方契约，不默认支持所有桌面组合或改换工具包。产品行为缺失时交回当前过程。

沿用 Base 的逐项状态和证据格式，记录发行版、桌面环境、会话协议与实际后端、相关版本、缩放、包格式及操作结果。区分宿主与沙箱、X11/Wayland/兼容层、截图与实际交互证据；虚拟显示或无图形环境不能证明真实桌面及读屏可用。未执行项标记未验证，和框架专项共享证据，不重复检查或代替人工确认。
