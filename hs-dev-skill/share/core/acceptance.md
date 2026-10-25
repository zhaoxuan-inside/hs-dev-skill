# 验收与确认

活动规则来自唯一 catalog。任务 results.json 只保存 check_id、规则摘要、结果、证据、证据摘要及理由；Markdown 是展示。PASS 有有效证据，NA 有适用性理由，未通过项保持阻断。

任务按清单工作，结果与证据交验收计算；统一确认模块决定动作。mute 自动记录模型来源；activity 按活动人工确认；stage 按阶段人工确认。人工原文必须来自实际授权反馈。

主要材料由 acceptance-material 显式登记；日志保留为检查证据，不自动形成独立材料卡。视图包括当前范围、进度、材料与审阅重点，详情折叠。一次明确范围确认可覆盖已展示的待审材料；逐项全部通过且清单就绪时形成同一范围确认，不再追加一次相同询问。

反馈绑定稳定材料 ID 与 view_digest；未提及项不变。reject 记录原因，defer/repair 还记录下一动作；暂缓不等于通过或 NA，过期视图拒绝写入。支持 --format markdown 和结构化 JSON。

确认绑定当前清单结果、输出、实际依赖及证据摘要。下游正常修改和索引重建不撤销上游；被消费的契约或证据改变则相关确认失效。任务完成重新核对，不重复询问仍然有效的决定。

范围确认通过时自动晋升为项目级决策台账记录（`hs_dev_docs/foundation/decisions.jsonl`）：只增不改、逐条哈希链接，任务过期后决策仍然可追溯。记录保存决策 ID、范围、来源任务、确认原文、被否方案及绑定的文档单元修订；被绑定文档随后变化时该记录标记"内容已变化"，应复核或用 decision-supersede 补充推翻记录。关键设计决定（方案取舍、排除依据、边界裁决）用 decision-record 显式登记；项目文档只写当前结论并引用决策 ID，不重复叙述理由。任务完成前核对台账完整且未被篡改，缺失或损坏阻止完成。

行为蓝图登记（`hs_dev_docs/foundation/blueprint.json`）承载功能、行为场景与测试用例的机械对账：B1/B2 产出功能与场景登记，E5 用例以 case 条目绑定场景（evidence 指向真实测试文件，planned 状态不构成覆盖）。E9 准备度核验的检查记录前强制对账：登记缺失、为空或存在悬空引用、无场景功能、无用例场景即阻断；deferred 仅在给出理由时豁免且保持可见。含 E5/E9 活动的任务在完成时重新对账，防止登记在检查后被改坏。blueprint 命令随时输出对账报告与计数。

契约登记（`hs_dev_docs/foundation/contracts.json`）使机器契约成为权威：每条契约绑定 JSON Schema 或 OpenAPI 机器文件（data/interface 两类），登记的存在性、可解析性与结构（OpenAPI 需 openapi/paths/info.title，Schema 需 $schema 或 type 加 properties/items）在 E1/E2 检查记录前机械校验；文档元数据 relations 声明 derives 的目标必须是登记中的现行契约，Markdown 不得冒充未登记的权威。E9 与完成门禁同样复核。

对象图登记（`hs_dev_docs/foundation/object_graph.json`）自初始化起强制存在：缺失即工作区不可信（RECOVERY_REQUIRED），每个对象必须被关系覆盖或显式给出 not_applicable_reason，`required: false` 不再构成静默豁免；标记 changed 的 method/task 对象仍强制映射测试节点。

决策与代码的双向失效传播：决策记录除绑定文档单元外，自动收集其材料通过 describes 关系声明的代码文件（经对象图解析路径）并绑定其内容摘要——代码随后变更时，描述它的决策在 decision-list 中标记"内容已变化"，需复核或推翻。文档→任务的绑定失效（dependency-bind 单元修订）与代码→决策的失效（describes 修订）共同闭环。

契约内核链（`:::contract` 块）把行为与设计的机器权威嵌进文档：内核 JSON 非法、ID 重复在发布时阻断；`kernel` 命令对账 feature → behavior → case → contract → symbol 的 ID 链，悬空引用（未知功能/用例/实现单元/未登记契约）进入一致性门禁，与源漂移同级处理。行为内核必须绑定 covered_by 用例与 implemented_by 实现单元（或显式 unimplemented_reason）；实现新增/变更后由 G1.4 回填。E9 与 G4 的检查记录前、以及一切任务完成前强制复核内核链。

文档债队列（`doc-debt`）把"代码已变化、文档未同步"变成阻断性工作项：失效决策和行为内核的代码漂移逐条列出，未清偿债务阻断 E9、G4 与任务完成。豁免（`doc-debt-waive`）仅限人工、绑定当次债务摘要；摘要随漂移内容变化，旧豁免不覆盖新漂移；修复文档或以新决策锚定后债务自然消失。

验收（H3）以契约对照评审（R1）为必要前置：评审包由内核链与对象图从变更集推导，逐项核验实现与登记一致；偏离按缺陷或契约变更分流。对决策、契约或实现行为的分歧经 R2 登记——绑定对象 ID 与内容摘要，事实分歧以证据复核、取舍分歧升级为决策记录（含被否方案）、执行分歧移交负责活动；未决异议使相关验收保持阻断并在验收视图中可见。
