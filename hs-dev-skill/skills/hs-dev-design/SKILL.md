---
name: hs-dev-design
description: 解决指定技术决定；按影响选择质量、架构或工程契约资料。
license: MIT
---

# 工程设计

先指出待决定的问题和受影响契约，再选表中的对应项；这些项是条件候选，不是 C～E 必做清单。依赖核验优先读取已绑定产物的相关章节，仅在结论缺失、失效或被本次修改影响时补充活动。比如调整已有接口错误返回，先选 E2；只有失败机制或用例也需改变时才加入 E4、E5，不展开技术选型和架构设计。

## 执行清单

- [ ] **确定设计基线**：明确本次待决定问题、预期结果、授权范围、有效产品契约、实际工程和受影响对象。区分约束、偏好、事实和假设；工程可查信息先核实，产品行为缺失或冲突返回负责过程，不自行补规则。只读评估不修改工程或登记新决定。
- [ ] **选择活动与专业能力**：按下表只选命中缺口的活动，复用已有有效结果；按实际边界调用框架、后端、前端、产品、测试或治理技能。过程组织依赖和决定，领域技能提供专业方法及证据；跨领域契约只维护一份有效定义，不重复设计。
- [ ] **形成技术决定**：先判断现状是否满足约束，必要时比较可行候选的运行、维护、迁移及退出成本。记录问题、依据、选定方案、取舍、适用条件、影响对象和未决项；不为展示完整性凭空增加候选、抽象或基础设施。涉及具体技术机制时核对实际版本与官方契约。
- [ ] **验证关键风险**：将决定关联到质量目标及验证方法；按需要做静态一致性核验或授权范围内的最小实验。记录环境、源版本、操作、预期与实际结果；验证计划、模拟结果和真实集成分别说明。可能推翻决定的关键未知尚未解决时，明确阻断或待验证条件，不宣称已具备实施条件。
- [ ] **同步受影响契约**：核对本次相关的数据、接口、方法、状态、配置和用例之间一致性。活动清单中的文档、环境和 Mock 要求先判适用，不因引用就固定新增阶段文档、六套环境或独立服务；不适用说明理由，不绕过项目明确要求。
- [ ] **交付与转交**：给出决定、契约位置、检查结果、证据、剩余风险及下一动作。当前范围内适用项已有明确结论、必要上游有效且关键猜测已处理后，按当前确认模式和诉求转入规划或实施；没有后续实施授权时止于设计交付，不自动展开后续活动。

## 验证与权限边界

设计任务不默认授权业务实现、生产资源变更、数据迁移、付费资源创建或部署发布。实验只回答当前技术问题，说明其代表范围及局限；需要额外授权或缺失条件时明确指出，继续不依赖该条件的工作。不把实验代码自动变成正式实现。

已选检查项使用“通过、未通过、不适用、未验证”，关联对象、依据和证据；不适用给理由，未验证说明条件，未通过说明影响。简单决定可直接回复或更新现有记录，不强制新建设计文档。专业自检不代签人工确认，准备度核验只在任务要求或实际缺口涉及 E9 时执行。

## 条件式资料选择

只读取命中条件的清单；每行独立判断，不按表格顺序全量加载。

| 当前缺口或动作 | 读取资料 |
|---|---|
| 缺少本次决策所需的可验证质量目标 | [C1 质量目标定义](../../share/workflow/c_quality_technical_decisions/c1_quality_attributes/checklist.md) |
| 存在待核实的技术限制或风险 | [C2 技术约束与风险](../../share/workflow/c_quality_technical_decisions/c2_constraints_risks/checklist.md) |
| 需要比较并选择技术或工程方法 | [C3 技术与方法决策](../../share/workflow/c_quality_technical_decisions/c3_technology_practice_selection/checklist.md) |
| 职责或数据所有权需要调整 | [D1 领域与职责划分](../../share/workflow/d_architecture/d1_domain_responsibilities/checklist.md) |
| 模块协作或调用关系需要调整 | [D2 结构与协作设计](../../share/workflow/d_architecture/d2_structure_collaboration/checklist.md) |
| 质量实现机制或演进策略需要调整 | [D3 质量与演进机制](../../share/workflow/d_architecture/d3_quality_evolution/checklist.md) |
| 框架约定或目录结构需要决定 | [D4 框架与目录约定](../../share/workflow/d_architecture/d4_framework_conventions/checklist.md) |
| 数据结构或约束变化 | [E1 数据契约设计](../../share/workflow/e_engineering_preparation/e1_data_contracts/checklist.md) |
| 接口输入、输出或错误返回变化 | [E2 接口契约设计](../../share/workflow/e_engineering_preparation/e2_interface_contracts/checklist.md) |
| 方法或组件职责需要细化 | [E3 方法与组件设计](../../share/workflow/e_engineering_preparation/e3_method_component_contracts/checklist.md) |
| 运行状态或失败处理变化 | [E4 运行与失败机制设计](../../share/workflow/e_engineering_preparation/e4_runtime_failure_design/checklist.md) |
| 需要设计验证用例 | [E5 测试用例构建](../../share/workflow/e_engineering_preparation/e5_test_cases/checklist.md) |
| 需要测试数据 | [E6 Mock数据构建](../../share/workflow/e_engineering_preparation/e6_mock_data/checklist.md) |
| 需要替代外部依赖 | [E7 Mock服务构建](../../share/workflow/e_engineering_preparation/e7_mock_services/checklist.md) |
| 配置项或配置来源变化 | [E8 配置体系构建](../../share/workflow/e_engineering_preparation/e8_configuration/checklist.md) |
| 请求核验实施准备是否完整 | [E9 工程准备度核验](../../share/workflow/e_engineering_preparation/e9_readiness_review/checklist.md) |

## 上下文边界

只读本任务命中的活动清单，并按目标定位代码与证据；不扩读相邻活动或整阶段资料。安全与范围遵循主入口；涉及写入时按需读取[执行协议](../../share/core/execution.md)，需要验收时读取[验收协议](../../share/core/acceptance.md)。
