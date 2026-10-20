---
name: hs-dev-frontend-android
description: Android 界面的系统导航、布局、权限和系统入口规则，按主题加载。
license: MIT
---

# Android 前端特性

与 [前端基础](../hs-dev-frontend-base/SKILL.md)配合。应用壳、生命周期和导航架构由[Android 客户端框架](../hs-dev-framework-client-android/SKILL.md)负责；本入口只路由界面专属细节。

只读取命中本次目标的端侧资料；通用要求和验证方式见前端 Base，不重复加载。

| 当前涉及的特性 | 专有资料 |
|---|---|
| 返回行为、系统栏、方向、屏幕尺寸和折叠设备 | [navigation layout](references/navigation-layout.md) |
| 运行时授权、通知、深链接、分享或系统选择器 | [permissions system entry](references/permissions-system-entry.md) |

当前平台资料用于补充平台行为；不要因为项目目标平台明确就加载表中全部资料。

执行前从工程核实相关 UI 技术栈及版本、SDK 配置、系统和设备支持范围，再选择专题中的适用检查；涉及平台机制时核对对应版本的官方契约，不默认改换技术栈。产品行为缺失时返回当前过程，不擅自增加权限、入口或交互。

已选检查项记录 `对象／依据／状态／证据／未决项`，状态为“通过、未通过、不适用、未验证”，并说明不适用理由、失败影响或未验证条件。证据包含操作、预期与实际结果、设备/系统版本及相关 UI 技术栈。静态审阅、截图和实际交互结果分别说明，纯设计计划不标记运行通过。框架问题与 Android 框架技能共享证据，不重复验证或代替人工确认。
