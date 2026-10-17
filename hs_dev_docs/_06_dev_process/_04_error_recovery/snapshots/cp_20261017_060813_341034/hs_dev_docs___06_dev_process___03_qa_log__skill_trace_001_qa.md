# Q&A 决策日志（skill_trace_001）

> 审讯 / 开场确认 / 变更裁定的一切问答与拍板记录，供跨会话回溯与返工溯源。每轮追加，不覆盖旧记录。

## 会话 / 阶段

- **日期**：2026-10-17
- **任务**：`skill_trace_001` Skill 执行轨迹（trace）能力（change_size=`M`）
- **work_mode**：`DESIGN`
- **阶段**：0 产品

## 问题与答复

### Q0. 开场对齐 O1～O4（确认）

- **题域**：产品语义 / 范围 / 分级
- **题干**：O1 复述（新增项目级隔离的 Skill 执行 trace，开启后记录全流程供复盘优化；反目标：不改 `observability_telemetry`、不做跨工程聚合、不重写 process_log、不承诺超自报范畴的捕获）；O2 空白清单 7 项；O3 约束（Python 标准库 / 三端 / 门禁与测试无损）；O4 分级建议
- **开发者答复**：确认，继续
- **采纳决策**：intent=`BUILD`；change_size=`M`；work_mode=`DESIGN`
- **关联落盘**：`hs_dev_docs/_06_dev_process/_01_plan_log/skill_trace_001_plan.md`

### Q1. 采集机制与「完整」边界

- **题域**：产品语义 / 范围裁剪
- **题干**：A 自报式语义事件基线 / B 宿主 Hook 工具调用级 / C 分期
- **开发者答复**：自报式，但需要讲清楚执行的顺序和依赖关系，避免混乱。
- **采纳决策**：采用自报式（Agent 按规则写 trace 事件）；本期不含工具调用级明细；必须提供明确的「事件执行顺序与依赖约定」（时序 + 依赖规则），保证自报一致、可复盘。Hook 适配器仅留扩展点文档。
- **关联落盘**：PRD（待写）事件时序与依赖约定章节

### Q2. 开关形态（项目隔离）

- **题域**：对外契约 / 配置
- **题干**：A governance.yaml 新增键 / B 独立配置 / C 环境变量
- **开发者答复**：新增一个项目级别的 skill 执行配置
- **采纳决策**：独立新建「项目级 skill 执行配置」承载 trace 开关，不耦合 `governance.yaml`；缺省关闭；配置文件名、结构与读写通道在设计阶段定稿。
- **关联落盘**：PRD（待写）配置契约章节

### Q3. 事件分母

- **题域**：产品语义
- **开发者答复**：A 全量语义事件
- **采纳决策**：记录 11 类语义事件（会话开始/结束、意图分级、skill 装载、路由决策、阶段流转、任务/checkpoint 关联、关键动作、拍板决策、纠偏返工、错误重试、耗时）；不含工具调用级明细。
- **关联落盘**：PRD（待写）事件目录

### Q4. 日志载体

- **题域**：持久化
- **开发者答复**：A 按会话 JSONL
- **采纳决策**：`hs_dev_docs/_06_dev_process/_05_skill_trace/sessions/{session_id}.jsonl`；JSONL 追加、UTF-8；保留=手动清理 + 文档说明（不自动删除）。
- **关联落盘**：PRD（待写）存储契约

### Q5. 消费方式

- **题域**：范围
- **开发者答复**：A 最小查询 CLI
- **采纳决策**：提供 `scripts/skill_trace.py` 最小查询（`summary` / `query`，支持 `--task/--session/--event/--since`）+ 原始 JSONL；索引集成列为后续迭代。
- **关联落盘**：PRD（待写）；CLI 子命令在设计阶段定稿

### Q6. 真实案例与验收样本

- **题域**：需求取证
- **题干**：A 本会话 dogfooding + demo_project 回放 / B 仅 demo 回放 / C 其他真实工程
- **开发者答复**：A 本会话 + demo 回放
- **采纳决策**：首用案例 =（a）本次 trace 能力开发会话本身（从 discovery 起全过程可回放）；（b）demo_project 上的一段标准 BUILD 流程回放作为可复现验收样本。
- **关联落盘**：PRD §1 案例与 §7 验收演练

### Q7. 项目级 skill 执行配置形态

- **题域**：对外契约 / 配置
- **题干**：A `config/skill_execution.yaml`（version + features.skill_trace）/ B `config/skill_trace.yaml` / C 自定义
- **开发者答复**：A
- **采纳决策**：新建 `config/skill_execution.yaml`；`features.skill_trace` 缺省 `false`；`scripts/skill_trace.py enable|disable|status` 读写；`init_hs_dev_docs.py` 初始化时缺省生成。
- **关联落盘**：PRD §3.1 配置契约

### Q8. MVP 范围裁定（CEO 质疑式裁剪）

- **题域**：范围裁剪
- **题干**：本期做 5 项 / 裁剪 6 项，请拍板
- **开发者答复**：A 按此清单
- **采纳决策**：MVP = ①项目级配置+开关 CLI；②自报式事件记录（JSONL 按会话）；③事件时序与依赖约定（详规 + 路由层挂载）；④最小查询 CLI；⑤测试/文档/模板。裁剪（登记 MoSCoW 池，不写详细规格）：①Hook 适配器实现；②doc_index 索引与门禁联动；③自动清理/轮转/压缩；④多工程聚合统计；⑤可视化 UI；⑥token 用量采集。胃口：单任务内小步交付。
- **关联落盘**：PRD §6 MVP 范围

### Q9. 阶段 0 验收与冻结签署

- **题域**：阶段验收
- **题干**：阶段 0 验收结论 + 冻结单 A 节业务语义签收与冻结结论
- **开发者答复**：ACCEPTED + APPROVED
- **采纳决策**：阶段 0 验收 ACCEPTED；冻结单 APPROVED；进入阶段 1～3 触达面设计（M 路径：跳过选型/架构新建，仅补 trace 触达契约）
- **关联落盘**：`hs_dev_docs/_06_dev_process/skill_trace_001_phase0_acceptance.md`、`hs_dev_docs/_06_dev_process/skill_trace_001_freeze_signoff.md`

### Q10. 阶段 3 触达面设计验收

- **题域**：阶段验收
- **题干**：阶段 3 设计提交（skill_trace 详规 + 路由注册 + 索引行 + 接口契约记录；DETAIL-01～06 证据、集成清单 10 项、测试规格 T1～T11）验收结论
- **开发者答复**：ACCEPTED
- **采纳决策**：阶段 3 设计契约冻结；进入 S2 计划（实施计划与 DoD 见接口契约记录 §7）；后续门禁与最终签收在 S4
- **关联落盘**：`references/skill_trace.md`、`hs_dev_docs/_04_engineering_contract/_02_interface_design/skill_trace/interface_contract.md`（§6 验收 + §7 实施计划）；checkpoint `cp_20261017_055446_114913`

### Q11. 阶段 4～6 最终验收（S4）

- **题域**：阶段验收
- **题干**：任务/实现/交付阶段验收（TASK-01～05、IMPL-01～06、DELIV-01～05 共 16 项候选 PASS；附全量测试 128 绿、strict 门禁绿、router 16/52、demo_project 回放零告警证据）
- **开发者答复**：ACCEPTED
- **采纳决策**：阶段 4～6 验收通过；任务 `skill_trace_001` 完成；提交仓库变更待开发者另行授权
- **关联落盘**：`hs_dev_docs/_06_dev_process/skill_trace_001_final_acceptance.md`（ACCEPTED + 门禁 JSON）；checkpoint `cp_20261017_060714_314015`

---

## 变更请求登记（CR）

| CR 编号 | 变更描述 | 影响面 | 返工代价 | 开发者裁定 | 落盘 |
|---|---|---|---|---|---|
| （暂无） | | | | | |
