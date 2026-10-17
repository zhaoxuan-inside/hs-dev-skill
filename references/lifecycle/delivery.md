# 阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)

**何时读**：处理阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 6：全层级门禁自检与交付归档 (Quality Gate & Closure)

### 1. 核心目标
执行严格的提交前质量门禁自检，保障零死代码、零破坏性迁移、零索引漂移。

### 2. 自检动作
1. **契约文档与过程账本闭环（Doc & Process Sync）**：核对阶段 5 编码中涉及的所有方法画像、接口契约、表结构变更已在 `_04_engineering_contract/` 中 100% 同步更新；在 `_06_dev_process/_01_plan_log` 标记所有步骤为 `done`，`_02_change_log` 记录最终快照 checkpoint。
2. **双层索引自愈与全局罗盘刷新（Self-Healing & Guide Refresh）**：
   ```bash
   python scripts/idx_manager.py rebuild
   python scripts/doc_index_db.py --root . rebuild
   python scripts/doc_index_db.py --root . generate-guide
   ```
   确保各子域 `.idx`、SQLite 倒排索引及根目录全局导航阅读说明 `hs_dev_docs/_00_docs_compass.md` 处于最新状态且哈希一致。
3. **运行全量测试与运行态走查（测试零报错绝对阻断门禁）**：`make test` 确保 **100% PASS**，**无任何失败、报错或异常用例**；若有任何报错，**绝对禁止将任务置为 COMPLETED，绝对禁止 Git Commit，绝对禁止向用户汇报交付或完工**！严禁出现“代码已交付但有测试报错稍后修”的严重违规，必须就地 Debug 修复直至全绿。前端工程结合 Chrome DevTools CDP 自动化排查，确保无未捕获 Console 报错与网络死锁，满足 WCAG a11y 对比度与 LCP/内存泄漏安全线。
4. **运行代码静态检测（零告警零错误门禁）**：语言对应 Linter（ESLint/Ruff/Flake8 等）与类型检查（TSC/Mypy）**必须达到 0 警告（0 Warning）且 0 错误（0 Error）**；任何 Warning 均视为阻断性质量缺陷必须就地消除，严禁带 Warning 提交代码。
5. **运行一致性与需求覆盖率门禁检查**：`python scripts/verify_consistency.py --root . --strict` 确保三文件、索引、V/U 脚本原子配对、目录卫生以及原子需求清单（`REQ-*`）100% 达成 `verified`（覆盖率硬阻断，严禁遗留未解决项交付）。
6. **运行死代码与孤儿方法扫描**：`python scripts/dead_code_scanner.py --root .`。
7. **流转任务状态并归档**：**仅当上述测试全绿、静态检测零告警零错误、一致性验证全部通过，且结构化验收记录已由开发者确认后**，方可执行 `python scripts/task_manager.py status --id {task_id} --set COMPLETED --acceptance-record <验收记录路径>`（命令检查记录、REQ 与严格一致性门禁后自动归档至 `_00_task_archive.idx`）。
8. **Git 规范提交**：按照 `<type>(<scope>): <subject>` 规范生成本地 Commit。**默认不** `git push`；**仅当用户明确要求推送**时代为执行并回报结果。
