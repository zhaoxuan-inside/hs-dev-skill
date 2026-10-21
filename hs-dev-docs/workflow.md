# 活动与交付

依据 [workflow.json](../hs-dev-skill/scripts/hs_dev/data/workflow.json)整理当前活动。阶段提供导航，活动组织工作，清单中的内部检查项是验收单元；上游表示活动依赖，不要求重复执行已有效完成的活动。

当前共有 8 个阶段、36 个活动、108 个检查项。

## A 产品构想与宏观信息收集

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [A1 问题、愿景与价值](../hs-dev-skill/share/workflow/a_product_intent/a1_problem_vision_value/activity-guide.md) | 无固定上游 | [检查清单](../hs-dev-skill/share/workflow/a_product_intent/a1_problem_vision_value/checklist.md)；目标用户、情境、问题及来源，区分事实与假设；价值主张、愿景与成功预期，附未决项和确认来源 |
| [A2 定位与产品调性](../hs-dev-skill/share/workflow/a_product_intent/a2_positioning_product_character/activity-guide.md) | A1 | [检查清单](../hs-dev-skill/share/workflow/a_product_intent/a2_positioning_product_character/checklist.md)；有来源及时间的替代方案观察、推断和未知；定位与调性原则、适用场景、取舍及未决项 |
| [A3 核心能力与业务边界](../hs-dev-skill/share/workflow/a_product_intent/a3_capabilities_business_boundary/activity-guide.md) | A1, A2 | [检查清单](../hs-dev-skill/share/workflow/a_product_intent/a3_capabilities_business_boundary/checklist.md)；关联问题和价值的宏观能力及责任边界；外部依赖、已知限制、假设和未决项及其影响 |

## B 功能体系与产品行为设计

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [B1 完整功能提取](../hs-dev-skill/share/workflow/b_product_design/b1_feature_inventory/activity-guide.md) | A3 | [检查清单](../hs-dev-skill/share/workflow/b_product_design/b1_feature_inventory/checklist.md)；有稳定定位、来源、角色及范围状态的功能基线；能力覆盖、通用能力适用性、关键待定项及下游影响 |
| [B2 逐功能行为设计](../hs-dev-skill/share/workflow/b_product_design/b2_feature_behavior/activity-guide.md) | B1 | [检查清单](../hs-dev-skill/share/workflow/b_product_design/b2_feature_behavior/checklist.md)；关联功能标识的行为契约、规则及适用状态转换；正常与适用异常场景、可观察结果、未决项及影响 |
| [B3 逐功能交互设计](../hs-dev-skill/share/workflow/b_product_design/b3_feature_interaction/activity-guide.md) | B2, A2 | [检查清单](../hs-dev-skill/share/workflow/b_product_design/b3_feature_interaction/checklist.md)；关联功能和行为的入口、操作、展示及反馈流程；适用交互状态、可演练材料、检查证据和未决项 |
| [B4 整体结构与功能关联](../hs-dev-skill/share/workflow/b_product_design/b4_structure_connections/activity-guide.md) | B2, B3 | [检查清单](../hs-dev-skill/share/workflow/b_product_design/b4_structure_connections/checklist.md)；本次功能到结构/入口的映射及跨功能关系；代表角色旅程的演练证据、冲突及未决影响 |
| [B5 产品完整性验证](../hs-dev-skill/share/workflow/b_product_design/b5_product_completeness/activity-guide.md) | B1, B4 | [检查清单](../hs-dev-skill/share/workflow/b_product_design/b5_product_completeness/checklist.md)；逐项覆盖与跨功能一致性结论及证据引用；整体核验状态、有效确认、阻断和后续动作 |

## C 质量约束与技术决策

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [C1 质量目标定义](../hs-dev-skill/share/workflow/c_quality_technical_decisions/c1_quality_attributes/activity-guide.md) | A3, B2 | [检查清单](../hs-dev-skill/share/workflow/c_quality_technical_decisions/c1_quality_attributes/checklist.md)；适用质量场景、目标及判断标准；目标权衡、验证条件/方法、未知与阻断 |
| [C2 技术约束与风险](../hs-dev-skill/share/workflow/c_quality_technical_decisions/c2_constraints_risks/activity-guide.md) | C1 | [检查清单](../hs-dev-skill/share/workflow/c_quality_technical_decisions/c2_constraints_risks/checklist.md)；带来源及适用条件的技术约束和风险判断；关键未知的核验结果、剩余风险处置和阻断条件 |
| [C3 技术与方法决策](../hs-dev-skill/share/workflow/c_quality_technical_decisions/c3_technology_practice_selection/activity-guide.md) | C2 | [检查清单](../hs-dev-skill/share/workflow/c_quality_technical_decisions/c3_technology_practice_selection/checklist.md)；沿用或选定技术/方法的决定、依据和适用范围；版本、取舍、变更影响、剩余风险及后续条件 |

## D 架构与框架设计

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [D1 领域与职责划分](../hs-dev-skill/share/workflow/d_architecture/d1_domain_responsibilities/activity-guide.md) | B2, C3 | [检查清单](../hs-dev-skill/share/workflow/d_architecture/d1_domain_responsibilities/checklist.md)；一致的领域概念及本次职责、信息所有权映射；模块边界、公开契约原则、取舍及未决项 |
| [D2 结构与协作设计](../hs-dev-skill/share/workflow/d_architecture/d2_structure_collaboration/activity-guide.md) | D1 | [检查清单](../hs-dev-skill/share/workflow/d_architecture/d2_structure_collaboration/checklist.md)；受影响模块的依赖及协作契约边界；代表运行场景、适用部署关系、核验证据与未决项 |
| [D3 质量与演进机制](../hs-dev-skill/share/workflow/d_architecture/d3_quality_evolution/activity-guide.md) | C1, D2 | [检查清单](../hs-dev-skill/share/workflow/d_architecture/d3_quality_evolution/checklist.md)；质量目标到机制、责任位置和验证方法的映射；测试边界及适用演进/恢复方案、证据和未决项 |
| [D4 框架与目录约定](../hs-dev-skill/share/workflow/d_architecture/d4_framework_conventions/activity-guide.md) | D2, D3 | [检查清单](../hs-dev-skill/share/workflow/d_architecture/d4_framework_conventions/checklist.md)；适用框架、资源组织和依赖约定及依据；文档/机器契约单源规则、核验结果及未决项 |

## E 工程契约与验证环境构建

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [E1 数据契约设计](../hs-dev-skill/share/workflow/e_engineering_preparation/e1_data_contracts/activity-guide.md) | D1, D2 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e1_data_contracts/checklist.md)；本次数据对象、字段、关系和生命周期契约及权威来源；适用约束/访问/迁移方案、核验结果和未决风险 |
| [E2 接口契约设计](../hs-dev-skill/share/workflow/e_engineering_preparation/e2_interface_contracts/activity-guide.md) | B2, D2, E1 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e2_interface_contracts/checklist.md)；操作及输入/输出、错误、访问和副作用契约；权威契约、示例、验证依据及兼容/未决影响 |
| [E3 方法与组件设计](../hs-dev-skill/share/workflow/e_engineering_preparation/e3_method_component_contracts/activity-guide.md) | E2, D2 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e3_method_component_contracts/checklist.md)；关键方法/组件的职责和适用契约、依赖边界；复用/新增依据、实现及验证定位、未决项 |
| [E4 运行与失败机制设计](../hs-dev-skill/share/workflow/e_engineering_preparation/e4_runtime_failure_design/activity-guide.md) | D3, E2, E3 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e4_runtime_failure_design/checklist.md)；适用状态、时序、并发及资源/事务边界；失败结果、上限、一致性与恢复条件及验证依据 |
| [E5 测试用例构建](../hs-dev-skill/share/workflow/e_engineering_preparation/e5_test_cases/activity-guide.md) | B5, E1, E2, E3, E4 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e5_test_cases/checklist.md)；有来源、初态/输入、预期及断言的适用用例；执行入口与依赖、覆盖映射、实际结果或未验证条件 |
| [E6 Mock数据构建](../hs-dev-skill/share/workflow/e_engineering_preparation/e6_mock_data/activity-guide.md) | E5, E1 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e6_mock_data/checklist.md)；与适用场景关联的隔离测试数据或生成规则；装载/重置条件、验证结果、局限与未决项 |
| [E7 Mock服务构建](../hs-dev-skill/share/workflow/e_engineering_preparation/e7_mock_services/activity-guide.md) | E2, E5, E6 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e7_mock_services/checklist.md)；必要替代服务及其覆盖契约和场景控制方式；启动/隔离/清理与替换边界、验证证据及真实接入缺口 |
| [E8 配置体系构建](../hs-dev-skill/share/workflow/e_engineering_preparation/e8_configuration/activity-guide.md) | C3, D4, E7 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e8_configuration/checklist.md)；受影响配置的语义、来源、校验及生效契约；实际环境与资源隔离、凭据处理和验证结果 |
| [E9 工程准备度核验](../hs-dev-skill/share/workflow/e_engineering_preparation/e9_readiness_review/activity-guide.md) | E1, E2, E3, E4, E5, E6, E7, E8 | [检查清单](../hs-dev-skill/share/workflow/e_engineering_preparation/e9_readiness_review/checklist.md)；指定范围的准备度结论与逐项依据；阻断、未验证/不适用说明及负责活动和下一动作 |

## F 交付规划与执行准备

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [F1 交付切片规划](../hs-dev-skill/share/workflow/f_delivery_planning/f1_delivery_slices/activity-guide.md) | B5, C3, E9 | [检查清单](../hs-dev-skill/share/workflow/f_delivery_planning/f1_delivery_slices/checklist.md)；需求到切片的范围映射、依赖及顺序依据；切片可验证结果、完成/恢复条件及待决影响 |
| [F2 任务详细设计](../hs-dev-skill/share/workflow/f_delivery_planning/f2_task_details/activity-guide.md) | F1 | [检查清单](../hs-dev-skill/share/workflow/f_delivery_planning/f2_task_details/checklist.md)；当前任务目标、范围、输入和影响对象及执行检查；可判断完成条件、验证方式、依赖/恢复及就绪状态 |
| [F3 上下文装配](../hs-dev-skill/share/workflow/f_delivery_planning/f3_context_assembly/activity-guide.md) | F2 | [检查清单](../hs-dev-skill/share/workflow/f_delivery_planning/f3_context_assembly/checklist.md)；按上下文协议核验的当前最小必要工作集；来源/版本/覆盖及预算结果、缺失/延迟项和下一动作 |
| [F4 恢复准备](../hs-dev-skill/share/workflow/f_delivery_planning/f4_recovery_preparation/activity-guide.md) | F3 | [检查清单](../hs-dev-skill/share/workflow/f_delivery_planning/f4_recovery_preparation/checklist.md)；本次适用恢复覆盖、依据有效性和操作归属结论；冲突/不可恢复限制、保留保护及缺失条件和下一动作 |

## G 实现、测试与增量集成

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [G1 切片实现](../hs-dev-skill/share/workflow/g_implementation_integration/g1_slice_implementation/activity-guide.md) | F4 | [检查清单](../hs-dev-skill/share/workflow/g_implementation_integration/g1_slice_implementation/checklist.md)；符合当前任务契约的实际切片修改及对象集合；同步的必要资料、针对性检查证据与待验证/未决项 |
| [G2 切片验证](../hs-dev-skill/share/workflow/g_implementation_integration/g2_slice_verification/activity-guide.md) | G1, E5 | [检查清单](../hs-dev-skill/share/workflow/g_implementation_integration/g2_slice_verification/checklist.md)；当前切片行为及工程检查的实际结果与证据；失败分类、覆盖局限、未验证项及下一动作 |
| [G3 增量集成](../hs-dev-skill/share/workflow/g_implementation_integration/g3_incremental_integration/activity-guide.md) | G2 | [检查清单](../hs-dev-skill/share/workflow/g_implementation_integration/g3_incremental_integration/checklist.md)；本次集成及代表端到端路径的实际结果；受影响回归、真实/替身覆盖及缺失条件与风险 |
| [G4 一致性提交](../hs-dev-skill/share/workflow/g_implementation_integration/g4_consistent_commit/activity-guide.md) | G3 | [检查清单](../hs-dev-skill/share/workflow/g_implementation_integration/g4_consistent_commit/checklist.md)；核验一致的受管修订及操作/活动登记结果；证据/确认有效性、中断状态或未解决阻断 |

## H 交付、验收与反馈

| 活动 | 必要上游 | 输出定位 |
|---|---|---|
| [H1 完整性对账与现状核验](../hs-dev-skill/share/workflow/h_delivery_feedback/h1_coverage_review/activity-guide.md) | 无固定上游 | [检查清单](../hs-dev-skill/share/workflow/h_delivery_feedback/h1_coverage_review/checklist.md)；有来源的现状与约定差异、覆盖及一致性结论；遗漏/冲突/失效及未验证项、影响和下一动作 |
| [H2 交付与恢复验证](../hs-dev-skill/share/workflow/h_delivery_feedback/h2_delivery_recovery_verification/activity-guide.md) | G4 | [检查清单](../hs-dev-skill/share/workflow/h_delivery_feedback/h2_delivery_recovery_verification/checklist.md)；实际交付路径及适用恢复检查结果；产物版本、环境、覆盖局限和阻断/下一动作 |
| [H3 验收](../hs-dev-skill/share/workflow/h_delivery_feedback/h3_developer_acceptance/activity-guide.md) | H1, H2 | [检查清单](../hs-dev-skill/share/workflow/h_delivery_feedback/h3_developer_acceptance/checklist.md)；与当前材料和模式绑定的验收结果及确认记录；完成状态或拒绝/暂缓/修复项、阻断及下一动作 |
| [H4 反馈与后续](../hs-dev-skill/share/workflow/h_delivery_feedback/h4_feedback_handoff/activity-guide.md) | H3 | [检查清单](../hs-dev-skill/share/workflow/h_delivery_feedback/h4_feedback_handoff/checklist.md)；有来源及影响的反馈分类和负责过程/活动；最小续做上下文、下一动作、阻断及完成状态说明 |

## 使用与交付

先识别当前目标和已有有效产物，再由过程入口选择命中的活动。缺少上游时定位必要材料，不能把依赖图当作全文加载要求。H1 无固定上游，仍需明确本次核对的范围与材料。

产物可以更新已有文档或直接答复，不强制为每个活动新建文档。受管任务的清单结果、证据和确认分别记录；文档存在不代表检查通过。具体结果要求见[验收协议](../hs-dev-skill/share/core/acceptance.md)。
