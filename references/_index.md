# references 索引（禁止整目录通读）

用本表按需打开**一份**文件；已读过的本会话不重复读。争议百科才查 `spec_v2_4.md` 对应节。

不确定场景时先检索（勿通读目录）：

```bash
python scripts/skill_ref_index.py search --q "幂等" --limit 5
python scripts/skill_ref_index.py search --scenario UI --limit 5
# 索引缺失时：python scripts/skill_ref_index.py rebuild
```

| 场景 | 打开 |
|------|------|
| **动手前：装载门闩（反合理化 × Token）** | `load_latch.md` |
| **任何需求第一步：变更分级 S/M/L** | `right_sizing.md` |
| **审讯式 DESIGN 对齐 / grilling** | `grill_orchestration.md` |
| 设计多问 / 实现少问 / 跳过收紧 / work_mode | `confidence_decision.md` |
| **继续任务 / plan_log / change_log / 非 git 回退** | `process_continuity.md` |
| **产品设计规范（设计语言 + 产品功能）** | `product_design.md` |
| **产品原型 / 多态线框（无位图）** | `product_prototype.md` |
| **产品分阶段规划与 MVP 裁剪（人机交互对齐）** | `product_roadmap.md` |
| 任务状态合法迁移 | `task_state_machine.md` |
| **测试方法（一等公民）/ TDD / seam** | `testing.md` |
| 提交前门禁 / 九级测试分层 | `quality_gates.md` |
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
| **版本号控制与单源防漂移 / SemVer / 发布 Tag** | `version_control.md` |
| 学习笔记 / 偏好 / GitHub 对标 | `learn_and_prefer.md` |
| Win/Linux/macOS 路径与解释器 | `cross_platform.md` |
