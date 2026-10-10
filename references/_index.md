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
| **任何需求第一步：变更分级 S/M/L** | `right_sizing.md` |
| 询问是否该问用户 / 自主推进 | `confidence_decision.md` |
| 满配阶段细则 0～6 | `spec_driven_lifecycle.md`（可只读当前阶段节） |
| UI/组件/页面实现或详设 | `frontend_craft.md` |
| API/契约/Mock/幂等 | `api_engineering.md` |
| 六元组签名与衍生方法 | `six_tuple_runtime.md` |
| Token / SQLite / context_pack | `token_budget.md` |
| 四级 JSONL 路由 | `four_level_routing.md` |
| 任务状态机 | `task_state_machine.md` |
| Mock Profile | `mock_contract_guide.md` |
| 提交前门禁 | `quality_gates.md` |
| 学习笔记 / 偏好 / GitHub 对标 | `learn_and_prefer.md` |
| Win/Linux/macOS 路径与解释器 | `cross_platform.md` |
