# 系统化调试与 Bug 修复指南（Systematic Debugging & Bug Fix）

**何时读**：接手缺陷修复、排查偶发异常、修补崩溃或回归 Bug 时；每会话最多一次。

---

## 1. 核心定位与铁律：假设驱动与先红后绿

Bug 修复绝非凭直觉“盲修乱试”，更禁止在未确认根因前胡乱添加兜底与补丁代码。  
核心铁律：
1. **科学假设驱动（Hypothesis-Driven RCA）**：一切定位必须基于可观测的日志、调用栈或代码切片提出确切假设；
2. **先红后绿（Reproduction Test First）**：**必须先写出可稳定触发 Bug 的自动化失败测试（RED），严禁在未见红前修改生产代码**；
3. **精准切片与零副作用（Minimal Blast Radius）**：遵从深模块与抗方法爆炸铁律，仅做必要最小修改使测试变绿（GREEN）；
4. **防退化门禁硬阻断（Regression Gating）**：修复后全量测试 100% 通过（0 报错），静态检测 0 告警，杜绝隐式引入新 Bug。

---

## 2. 调试修复四步闭环流

```text
[Step 1: 现象收集与假设] ──► [Step 2: 最小复现用例 RED] ──► [Step 3: 精准切片修复 GREEN] ──► [Step 4: 门禁与防退化]
   堆栈/切片/doc_index_db           编写自动化单测/集成测              深模块修复/意图查重             make test + 静态检测
```

### Step 1：现象收集与假设生成（Hypothesis Generation）
- **收集现场**：获取完整错误堆栈、输入入参、环境状态与期望行为；
- **切片定位与依赖探查**：强制使用 `doc_index_db` 专属索引指令定位现场，杜绝暴力盲搜：
  ```bash
  # 1. 查找涉事类与方法切片 (免读大文件)
  python scripts/doc_index_db.py symbol-slice --name "<涉事方法名>"
  # 2. 查局部微依赖图与爆炸半径 (分析 Callers 影响面与 Callees Mock 边界)
  python scripts/doc_index_db.py dep-graph --symbol "<涉事类名.方法名>"
  # 3. 检索该方法已有的测试用例与精准单跑指令
  python scripts/doc_index_db.py test-search --target "<涉事方法名>"
  # 4. 追溯该文件/方法近期的改动审计历史
  python scripts/doc_index_db.py audit-search --q "<涉事文件或方法>"
  ```
- **提出根因假设**：明确形式化假设：“在输入 X 且状态为 Y 时，由于逻辑 Z 未处理，导致产生错误 E”。

### Step 2：最小复现用例（Write Failing Test First - RED）
- 在对应的单元测试或集成测试文件中，构造能够稳定触发该缺陷的最小测试用例；
- 运行测试套件，**亲眼目睹该测试失败（RED），且报错原因与生产现场完全吻合**；
- 严禁假复现（测试因环境或断言语法失败，而非业务逻辑失败）。

### Step 3：精准切片修复（Make it GREEN）
- 依据 [`method_archetypes.md`](method_archetypes.md) 识别涉事方法的七分类与七维契约；
- 执行 `python scripts/doc_index_db.py method-search --q <业务意图>` 查重，严禁为了修 Bug 新增重复影子函数；
- 做最小必要改动，消除根因；
- 再次运行复现测试，确保其转为通过（GREEN）。

### Step 4：契约同步、索引自愈与防退化门禁（Contract Sync & Self-Healing Gating）
- **契约文档与方法画像同步**：若修复涉及方法内部逻辑、入参扩展或新增测试，同步更新 `_04_engineering_contract/_04_method_design/` 中的方法契约画像与精准单跑测试指令（若触及接口/表结构，同步更新对应契约）；
- **过程账本与快照留存**：修改前执行 `python scripts/process_log.py --root . checkpoint --id {task_id} --step {step_id} --summary "修复前快照" --paths {relative_path_1},{relative_path_2}` 留存快照，修复后更新日志与证据，在 `_06_dev_process/_01_plan_log` 标记对应断点步骤为 `done`；
- **双层索引自愈与罗盘刷新**：运行 `python scripts/idx_manager.py rebuild --root .` 与 `python scripts/doc_index_db.py --root . rebuild` 刷新 SQLite 索引与 SHA-256 Digest，并执行 `python scripts/doc_index_db.py --root . generate-guide` 保持 `hs_dev_docs/_00_docs_compass.md` 罗盘最新；
- **全量测试与防退化门禁**：运行全量测试套件（`make test`，确保 100% PASS 且 0 报错），静态检测（Linter / TypeChecker）0 告警 0 错误，执行 `python scripts/verify_consistency.py --root . --strict` 严格门禁验证；
- **本地归档提交**：门禁全绿后完成本地 Commit，严禁带病提交。

---

## 3. 分级规模决策（S / M / L）

| 级别 | 判定标准 | 流程要求 |
|---|---|---|
| **S** | 局部逻辑缺陷（如空指针、边界值越界、正则错位、文案错漏），不触碰 DB 表结构与公开 API 契约 | 轻量对齐 DoD $\to$ 编写复现单测（RED） $\to$ 精准修补（GREEN） $\to$ 单测+门禁通过 $\to$ Commit。 |
| **M** | 涉及状态机流转错误、补偿逻辑缺失、内部调用时序竞争，但不换技术栈与新增表 | 迷你阶段 0（记录缺陷根因与影响面） $\to$ 更新触达面设计 $\to$ 编写多场景回归测试套件 $\to$ 修复 $\to$ 全量门禁 $\to$ Commit。 |
| **L** | 架构级缺陷、严重数据不一致需要做数据订正与表迁移、破坏性契约更正 | 升级为 L 路径，走完阶段 0 方案评估至阶段 6 完整交付。 |
