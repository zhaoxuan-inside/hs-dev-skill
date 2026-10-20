---
name: hs-dev-frontend-ios
description: iOS 界面的导航、安全区、系统授权和系统集成规则，按主题加载。
license: MIT
---

# iOS 前端特性

与 [前端基础](../hs-dev-frontend-base/SKILL.md)配合。应用结构、Scene 生命周期和本地状态架构由[iOS 客户端框架](../hs-dev-framework-client-ios/SKILL.md)负责；本入口只路由界面专属细节。

只读取命中本次目标的端侧资料；通用要求和验证方式见前端 Base，不重复加载。

| 当前涉及的特性 | 专有资料 |
|---|---|
| 导航栈、手势、安全区、窗口与方向适配 | [navigation layout](references/navigation-layout.md) |
| 系统授权、VoiceOver、动态字体、通用链接或系统面板 | [system services accessibility](references/system-services-accessibility.md) |

当前平台资料用于补充平台行为；不要因为项目目标平台明确就加载表中全部资料。

先从工程核实相关 UI 技术栈及版本、部署目标、设备与窗口支持范围，再选择专题条目；涉及系统机制时核对对应版本的官方契约，不默认替换 SwiftUI/UIKit 或跨平台方案。沿用 Base 的任务、授权及产品契约，缺失行为交由当前过程决定，不擅自增加授权、入口或窗口能力。

沿用 Base 的逐项状态与证据格式，补充设备/系统版本、相关 UI 技术栈、初始状态、操作及预期与实际结果。截图、静态审阅、模拟器与真机结果分别说明覆盖范围，未执行计划标记未验证。应用/Scene 生命周期与恢复问题和 iOS 框架技能共享证据，不以界面检查代替框架验证或人工确认。
