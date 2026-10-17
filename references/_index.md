# references 索引（禁止整目录通读）

先由主 Skill 选择过程/功能子 Skill；本表只用于命中详规，不替代子 Skill 路由。

用本表按需打开**一份**文件；已读过的本会话不重复读。争议百科才查 `spec_v2_4.md` 对应节。

不确定场景时先检索（勿通读目录）：

```bash
python scripts/skill_ref_index.py search --q "幂等" --limit 5
python scripts/skill_ref_index.py search --scenario UI --limit 5
# 索引缺失时：python scripts/skill_ref_index.py rebuild
```

| 场景 | 打开 |
|------|------|
| **子 Skill / 双轴分割 / 运行包 / 交接 / 独立调用** | `subskill_contract.md` |
| **阶段验收 / checklist / 通过证据 / 验收权限与失效** | `stage_acceptance.md` |
| **需求理解 / 预期对账 / 产品设计验收 DISC / PROD** | `product_acceptance.md` |
| **选型到交付验收 / TECH ARCH DETAIL TASK IMPL DELIV / Java P3C** | `engineering_acceptance.md` |
| **验收规范来源 / NASA / GOV.UK / arc42 / ISO 阅读范围** | `standards_basis.md` |
| **新需求第一步：开场确认（复述/假设/约束/分级建议）** | `opening_alignment.md` |
| **流程全景：意图路由 + 阶段门禁 + 回环（从各需求入口）** | `intent_routing_and_gates.md` |
| **项目类型 P1~P6 判定 / 三件套清单组织规范（树状原子叶子）** | `project_types.md` |
| **动手前：装载门闩（反合理化 × Token）** | `load_latch.md` |
| **任何需求第一步：变更分级 S/M/L（触 DB 变更 → 至少 M）** | `right_sizing.md` |
| **审讯式 DESIGN 对齐 / grilling（轮询不限次）** | `grill_orchestration.md` |
| 设计多问 / 实现少问 / 跳过收紧 / work_mode | `confidence_decision.md` |
| **继续任务 / plan_log / change_log / 非 git 回退** | `process_continuity.md` |
| **冻结后需求变更 / 变更请求单** | `requirement_change.md` |
| **产品设计规范（设计语言 + 产品功能 + 冻结签收）** | `product_design.md` |
| **产品原型 / 多态线框（无位图）** | `product_prototype.md` |
| **MVP 范围裁定（并入产品设计沟通）与分阶段规划** | `product_roadmap.md` |
| 任务状态合法迁移 | `task_state_machine.md` |
| **测试方法（一等公民）/ TDD / seam** | `testing.md` |
| **交付完成审计 / 需求与证据回收** | `completion_audit.md` |
| 提交前门禁 / 九级测试分层 | `quality_gates.md` |
| **多语言开发规范 / Linter 门禁矩阵 / 跨语言六元组** | `coding_standards.md` |
| **深模块 / seam / Adapter / 删除测试** | `deep_modules.md` |
| 满配阶段细则 0～6 | `spec_driven_lifecycle.md`（可只读当前阶段节） |
| **UI 默认审美（本地 Anthropic 蒸馏）** | `frontend_aesthetic.md` |
| UI 视觉方向 / DESIGN.md / 品牌对标 | `design_md.md` |
| UI 手艺高频（anti-slop / 动效 / a11y） | `frontend_craft.md` |
| **阶段 1～2：按规模/类型选开发范式（先于 DDD）** | `dev_paradigm.md` |
| DDD / 限界上下文（仅当范式选定含 DDD） | `ddd_design.md` |
| 后端分层 / 微服务 / Saga | `backend_arch.md` |
| 前端模块 / FSD / 与业务边界对齐 | `frontend_arch.md` |
| API 本地高频 | `api_engineering.md` |
| 领域规则远程按需（书规则 / FSD / wshobson…） | `rule_library.md` |
| 六元组签名与衍生方法 | `six_tuple_runtime.md` |
| **方法类型分类 / 契约画像 / 精准测试矩阵** | `method_archetypes.md` |
| **设计模式选型决策树 / 模式集群 / VibeCoding 防破坏** | `design_patterns.md` |
| Token / SQLite / context_pack | `token_budget.md` |
| 四级 JSONL 路由 | `four_level_routing.md` |
| Mock Profile | `mock_contract_guide.md` |
| **四段式版本控制 / 多级包区分 / 发布 Tag** | `version_control.md` |
| **工程附属机制与治理支撑 / 环境机密 / 供应链 / CI/CD / 探针 / 容灾 / 隐私** | `auxiliary_governance.md` |
| **反向重建：已有项目接入规范与知识库逆向** | `reverse_engineering.md` |
| **Bug 修复：系统化调试与测试驱动修补** | `systematic_debugging.md` |
| **代码重构：行为等价保护网与深模块演进** | `code_refactoring.md` |
| **代码理解：只读免交付检索与架构探查** | `code_exploration.md` |
| **项目文档阅读说明与跨 Agent 索引机制规范** | `doc_reading_guide.md` |
| 学习笔记 / 偏好 / GitHub 对标 | `learn_and_prefer.md` |
| Win/Linux/macOS 路径与解释器 | `cross_platform.md` |
| **各入口执行流程 / 计划-执行-证据-验收-交接** | `entry_workflows.md` |
| **Skill 执行轨迹（trace）：开关隔离 / 事件自报 / 时序依赖 / 查询复盘** | `skill_trace.md` |
