# 技术选型与评估方案：{module_or_platform}

- **输入与产出基线**：{路径、版本/内容摘要}
- **TECH 验收记录**：{当前阶段记录路径、开发者确认范围及来源}
- **验收状态**：DRAFT

> 执行 Skill 的 references/engineering_acceptance.md 对应阶段；本文写完只代表可提交验收。

- **评估领域**：后端服务 / 前端架构 / 移动端 / 存储 / 中间件
- **评估日期**：{YYYY-MM-DD}
- **负责人**：{evaluator}
- **对应 ADR**：`hs_dev_docs/_00_project_foundation/_03_decision_record/ADR_001_{tech_name}.md`

---

## [VIBE_CONTRACT] 机器执行契约 (Machine-Actionable Decision)
<!-- 
  【专供 VibeCoding / AI 编码切片读取（顶部 [VIBE_CONTRACT] 至下一同级标题）】
  说明：本区块记录已锁定的唯一技术栈、明确版本号、依赖与硬性禁令。
  AI 编码切片（doc_index_db.py slice）优先读取本区块，禁止将下方落选方案写进代码！
-->
```yaml
tech_stack_lock:
  target_module: "{module_name}"
  selected_runtime: "{如：Go 1.22 / Node.js 20 LTS / Python 3.11}"
  framework: "{如：Gin v1.9 / Next.js 14 App Router / FastAPI 0.110}"
  storage_driver: "{如：pgx/v5 (PostgreSQL 16) / redis v7}"
  directory_root: "{如：backend/services/{module_name}}"
  package_manager: "{如：go mod / pnpm}"

hard_constraints:
  - "LOCKED: 数据库驱动统一使用 {Selected_Driver}，严禁引入未经批准的 ORM/库"
  - "LOCKED: 协议接口统一遵循 RESTful JSON + OpenAPI 3.0"
  - "FORBIDDEN: 严禁在实现中使用下方落选方案中所提及的被否决技术栈！"
```

---

## [HUMAN_RATIONALE] 多方案对比与决策背景 (Human Rationale & Alternatives)
<!-- 【面向人类评审与架构归档】：详细记录背景与多方案评估过程，说明为什么选 A 而弃用 B/C -->

### 1. 业务特征与技术诉求
- **业务特征**：高并发读 / 强事务写 / 多端跨平台 / 极速冷启动
- **核心约束**：吞吐量指标、资源占用预算、团队技术栈契合度

### 2. 备选技术方案对比矩阵

| 评估维度 | 方案 A: {Tech_A} (推荐采纳) | 方案 B: {Tech_B} (落选备选) | 方案 C: {Tech_C} (落选备选) |
|---|---|---|---|
| **性能与吞吐** | 高 (协程高并发) | 中等 (单线程事件循环) | 极高 (零开销抽象) |
| **内存与启动** | 极低 (~15MB) | 中 (~60MB) | 极低 (~5MB) |
| **团队熟练度** | 高 | 高 | 中 |
| **生态与库支持** | 丰富 | 极丰富 | 丰富 |
| **综合评分** | **9.2 / 10** | 8.0 / 10 | 8.5 / 10 |

### 3. 选型结论与决策理由
我们决定采纳 **方案 A: {Tech_A}**。核心理由如下：
1. ...
2. ...
