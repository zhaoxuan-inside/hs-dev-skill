---
name: hs-dev-backend
description: 在已确定的工程任务中处理后端数据、接口、业务逻辑、运行状态和外部依赖；遵循当前过程及其范围。
license: MIT
---

# 后端工程

## 职责范围

处理服务端的数据约束、接口语义、业务逻辑、运行状态、失败行为、配置和外部服务适配。主 Skill 选定当前过程和任务范围；本 Skill 提供后端专业判断，不决定产品规则，也不把设计任务变成实现任务。

- 后端模块分层、依赖方向、运行模型或框架选型交由 [backend framework 专业入口](../hs-dev-framework-backend/SKILL.md)处理；本 Skill 负责后端业务、数据、接口与方法契约。
- 页面、组件、客户端状态和交互反馈由 [frontend base 专业入口](../hs-dev-frontend-base/SKILL.md)与对应平台入口处理。接口约定与页面行为相接时，双方只处理各自边界，并共同核对契约。
- 业务目标、角色规则或对外可见行为尚未明确时，返回当前过程澄清；不能以数据库或 API 设计代替产品决定。

## 后端判断方法

围绕本次变更的入口和可观察结果追踪依赖，不从“后端通常需要什么”推导额外范围：

1. 找到目标接口、任务、事件或调用入口，并确认调用方、身份与授权上下文，以及成功和失败时对外可见的行为。
2. 沿调用链追踪数据读取和写入，明确字段约束、数据所有权、事务边界及持久化后的状态变化。检查重复请求、并发更新和部分失败是否会破坏不变量。
3. 明确接口或方法的输入、输出、错误语义和副作用。认证、授权、幂等、分页、重试等只在本场景适用时纳入；客户端需要的行为与服务端实际保证保持一致。
4. 对数据库、消息系统或第三方服务，区分本服务可保证的结果和外部边界的不确定性。定义超时、重试上限、去重或补偿方式及配置入口；不要让正式业务代码依赖测试替身。
5. 为本次约束选择最小充分的验证：契约检查覆盖接口语义，单元或组件测试覆盖规则，集成测试覆盖真实边界。Mock 只能证明约定的模拟行为，不能证明真实服务可用。

这些是分析维度，不要求每个任务都逐项展开。已有有效契约直接复用；只有证据显示契约缺失、失效或被本次变更影响时才补充设计。

## 按需读取后端资料

仅命中本次任务的问题时读取对应清单。设计、实现、调试或重构仍由当前过程规定，本表不触发额外活动。

| 当前问题 | 读取资料 |
|---|---|
| 数据字段、关系、约束、查询、索引或迁移 | [E1 数据契约](../../share/workflow/e_engineering_preparation/e1_data_contracts/checklist.md) |
| API 输入输出、授权、幂等、分页或错误语义 | [E2 接口契约](../../share/workflow/e_engineering_preparation/e2_interface_contracts/checklist.md) |
| 服务、方法或组件职责、签名、依赖及副作用 | [E3 方法与组件契约](../../share/workflow/e_engineering_preparation/e3_method_component_contracts/checklist.md) |
| 状态转换、事务、并发、超时、重试、中断或恢复 | [E4 运行与失败机制](../../share/workflow/e_engineering_preparation/e4_runtime_failure_design/checklist.md) |
| 需要构造或审查行为测试 | [E5 测试用例](../../share/workflow/e_engineering_preparation/e5_test_cases/checklist.md) |
| 测试需要隔离的模拟数据 | [E6 Mock 数据](../../share/workflow/e_engineering_preparation/e6_mock_data/checklist.md) |
| 外部依赖需要协议兼容的替代服务 | [E7 Mock 服务](../../share/workflow/e_engineering_preparation/e7_mock_services/checklist.md) |
| 配置项、环境差异、凭证注入或启动校验 | [E8 配置体系](../../share/workflow/e_engineering_preparation/e8_configuration/checklist.md) |

不要因为 E9 会汇总工程准备度就默认读取它；只有任务明确要求准备度审查时，才读取 [E9 清单](../../share/workflow/e_engineering_preparation/e9_readiness_review/checklist.md)。

## 产出

交付与当前过程相符的后端结果：必要时说明数据与接口契约、关键状态和失败语义、涉及的代码或配置位置，以及实际验证证据。未决假设标出影响和需要的决定；不重复加载或复制已确认的共同约束，不把模型自检写成人工确认。
