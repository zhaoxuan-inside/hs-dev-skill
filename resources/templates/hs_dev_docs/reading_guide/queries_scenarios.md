## 3. 其他 Agent 极速索引与检索操作手册 (Agent Query Playbook)

当任何协同 Agent（如 Claude、GPT-4o、DeepSeek、Gemini 或其他 IDE 插件）介入本项目时，**严禁使用全量递归搜索或大段通读**。必须通过标准库支持的跨平台 CLI 专属命令进行毫秒级切片召回：

### 3.1 检索矩阵速查
| 检索场景 | 目标内容 | 推荐 CLI 指令 | 预期返回 |
|---|---|---|---|
| **查业务功能/需求** | PRD 契约、特性描述 | `python scripts/doc_index_db.py --root . feature-search --q "支付"` | 匹配特性 ID、标题、摘要及文件路径 |
| **查交互页面/线框** | 页面拓扑、线框规范 | `python scripts/doc_index_db.py --root . page-search --q "结算台"` | 页面路由、布局结构与线框图切片 |
| **查架构模式/集群** | 设计模式、防破坏护栏 | `python scripts/doc_index_db.py --root . pattern-search --q "Strategy"` | 协同方法列表、单向指针与安全护栏 |
| **查数据表/DDL** | 字段定义、表结构约束 | `python scripts/doc_index_db.py --root . schema-search --q "orders"` | 字段字典、索引设计与 DDL 迁移路径 |
| **查方法依赖拓扑** | 爆炸半径、调用时序 | `python scripts/doc_index_db.py --root . dep-graph --symbol "OrderService.create"` | 上游调用者（爆炸半径）与下游依赖 Mermaid 图 |
| **写前意图防膨胀** | 查重防重复造轮子 | `python scripts/doc_index_db.py --root . method-search --q "计算税费"` | 重合度 ≥80% 强制复用已有方法画像 |
| **精准源码切片** | AST 符号物理实现 | `python scripts/doc_index_db.py --root . symbol-slice --name "OrderService"` | 类/函数的精确起止行号与纯净源码 |
| **查测试用例单跑** | 单元测试、执行命令 | `python scripts/doc_index_db.py --root . test-search --q "test_pay"` | 自动化测试单跑命令与测试说明 |
| **查变更过程账本** | 物理回退与断点快照 | `python scripts/doc_index_db.py --root . audit-search --since "2026-10-14"` | 时间段内的文件修改历史与快照哈希 |
| **语义向量混合搜索** | 跨自然语言/代码意图 | `python scripts/doc_index_db.py --root . embed-search --q "幂等更新"` | 相似度加权排序切片清单 |
| **文档局部切片** | 任意设计文档行段 | `python scripts/doc_index_db.py --root . slice --path "hs_dev_docs/..." --start 1 --end 40` | 指定文档的高信噪比片段，杜绝全篇灌入 |

---

## 4. 意图驱动的 Agent 推荐阅读路径 (Scenario Reading Pathways)

协同 Agent 在开始执行具体任务时，应根据当前意图（Intent）按序阅读文档：

```text
[BUILD (从零构建)]
  └─► _01_product_vision (产品愿景/DESIGN.md)
        └─► _02_feature_spec (PRD / vibe_spec / 原型)
              └─► _03_architecture_design (ADR / 架构蓝图)
                    └─► _04_engineering_contract (DB / API / 方法设计)
                          └─► _05_task_orchestration (编译装配 Context Pack) ──► 编码与单测

[EXPLORE (只读理解)]
  └─► _00_project_foundation/_05_doc_index (CLI 检索定位)
        └─► symbol-slice / dep-graph (局部符号切片与依赖图)
              └─► 结构化输出业务时序或架构图谱 (纯只读免交付)

[FIX (Bug修复)]
  └─► audit-search / dep-graph (排查近期变更与影响范围)
        └─► _04_engineering_contract/_04_method_design (查阅方法契约与边界画像)
              └─► 编写最小复现用例 RED ──► 精准修复 GREEN ──► 回归门禁

[REFACTOR (等价重构)]
  └─► dep-graph (评估下游被调方与爆炸半径)
        └─► pattern-search (确认设计模式防破坏约束)
              └─► 固化特性测试保护网 ──► 消除坏味道 ──► 零行为漂移验证

[RESUME (任务续做)]
  └─► _06_dev_process/_01_plan_log & _02_change_log (执行 process_log.py resume-scan)
        └─► _05_task_orchestration/_02_task_detail (恢复当前在制品断点) ──► 沿既有 Plan 继续
```

---
