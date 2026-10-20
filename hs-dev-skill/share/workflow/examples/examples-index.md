# Workflow 阶段范例

本组范例按 A–H 阶段展示同一个虚构“便笺”产品（离线草稿与同步）的产物如何保持一致：产品行为定义用户可见规则，框架设计确定平台职责和边界，任务拆分引用这些决定，开发与验证按同一契约执行。文件名以阶段代码开头，平台专项明确标注平台和阶段。

所有内容均为教学用假设，不是本仓库产品需求、技术决定或已执行证据。真实任务需重新核对需求、代码、目标平台和运行条件；不得把示例里的通过结果复制为实际验证结论。

## 共用阶段范例

按实际工作阶段读取，不需要从头加载全套。

| 阶段 | 范例文件 | 展示内容 |
|---|---|---|
| A 产品构想 | [a_product_intent_draft_sync.md](a_product_intent_draft_sync.md) | 问题、目标、范围和排除项 |
| B 产品设计 | [b_product_design_draft_sync.md](b_product_design_draft_sync.md) | 用户行为、交互状态和验收条件 |
| C 质量与技术决策 | [c_quality_decisions_draft_sync.md](c_quality_decisions_draft_sync.md) | 质量目标、约束和待决风险 |
| D 架构设计 | [d_architecture_common.md](d_architecture_common.md) | 共用契约、责任边界及平台选择 |
| E 工程准备 | [e_engineering_preparation_draft_sync.md](e_engineering_preparation_draft_sync.md) | 数据/API/失败/测试契约 |
| F 交付规划 | [f_delivery_planning_draft_sync.md](f_delivery_planning_draft_sync.md) | 切片、依赖和任务完成证据 |
| G 实现集成 | 按下表平台专项 | 实现边界、验证场景及证据记录 |
| H 交付反馈 | [h_delivery_feedback_draft_sync.md](h_delivery_feedback_draft_sync.md) | 覆盖、未验证项、验收与交接 |

## D/G 平台专项范例

每个平台在 D 阶段给出职责和框架边界，在 G 阶段引用同一决定，展示实现与验证如何落实。选择目标平台对应的两份文件；后端按同样方式配对。

| 平台 | D 架构设计 | G 实现集成 | 对应技能 |
|---|---|---|
| Web | [d_architecture_frontend_web.md](d_architecture_frontend_web.md) | [g_implementation_frontend_web.md](../../../skills/hs-dev-implementation/SKILL.md) | [前端 Web](../../../skills/hs-dev-frontend-web/SKILL.md)、[Web 框架](../../../skills/hs-dev-framework-frontend/SKILL.md) |
| Windows | [d_architecture_frontend_windows.md](d_architecture_frontend_windows.md) | [g_implementation_frontend_windows.md](../../../skills/hs-dev-implementation/SKILL.md) | [前端 Windows](../../../skills/hs-dev-frontend-windows/SKILL.md)、[Windows 框架](../../../skills/hs-dev-framework-client-windows/SKILL.md) |
| macOS | [d_architecture_frontend_mac.md](d_architecture_frontend_mac.md) | [g_implementation_frontend_mac.md](../../../skills/hs-dev-implementation/SKILL.md) | [前端 macOS](../../../skills/hs-dev-frontend-mac/SKILL.md)、[客户端框架基础](../../../skills/hs-dev-framework-client-base/SKILL.md) |
| Linux | [d_architecture_frontend_linux.md](d_architecture_frontend_linux.md) | [g_implementation_frontend_linux.md](../../../skills/hs-dev-implementation/SKILL.md) | [前端 Linux](../../../skills/hs-dev-frontend-linux/SKILL.md)、[Linux 框架](../../../skills/hs-dev-framework-client-linux/SKILL.md) |
| iOS | [d_architecture_frontend_ios.md](d_architecture_frontend_ios.md) | [g_implementation_frontend_ios.md](../../../skills/hs-dev-implementation/SKILL.md) | [前端 iOS](../../../skills/hs-dev-frontend-ios/SKILL.md)、[iOS 框架](../../../skills/hs-dev-framework-client-ios/SKILL.md) |
| Android | [d_architecture_frontend_android.md](d_architecture_frontend_android.md) | [g_implementation_frontend_android.md](../../../skills/hs-dev-implementation/SKILL.md) | [前端 Android](../../../skills/hs-dev-frontend-android/SKILL.md)、[Android 框架](../../../skills/hs-dev-framework-client-android/SKILL.md) |
| 后端 | [d_architecture_backend.md](d_architecture_backend.md) | [g_implementation_backend.md](../../../skills/hs-dev-implementation/SKILL.md) | [后端开发](../../../skills/hs-dev-backend/SKILL.md)、[后端框架](../../../skills/hs-dev-framework-backend/SKILL.md) |

共用活动不为每个平台复制：需求、范围、质量目标、数据/API 契约、交付切片和交接分别引用对应 A/B/C/E/F/H 阶段范例。仅在平台行为改变用户体验、状态所有权或验证条件时，才选择对应端范例。跨端任务需要同时核对客户端与后端契约。

## 和 workflow 的对应

| 工作内容 | 参考 workflow 活动 |
|---|---|---|---|
| 问题、范围、行为和交互 | A1–A3、B1–B5 |
| 质量、约束、架构和平台框架 | C1–C3、D1–D4 |
| 数据、接口、方法、失败、测试与就绪 | E1–E9 |
| 切片、任务、上下文与恢复准备 | F1–F4 |
| 实现、验证、集成和提交 | G1–G4 |
| 覆盖、交付验证、验收与交接 | H1–H4 |

活动清单仍以对应 workflow 文件为准；本组范例展示如何填写和串联产物，不替代活动准入、人工确认、验收或恢复协议。所有名称、约束和结果均为教学假设；实际任务必须以当前项目和真实验证证据替换。
