# 架构决策记录 (ADR)：{ADR_TITLE}

- **编号**：ADR-{NUMBER}
- **状态**：PROPOSED / ACCEPTED / DEPRECATED / SUPERSEDED
- **日期**：{YYYY-MM-DD}
- **作者**：{AUTHOR}

---

## [VIBE_CONTRACT] 架构决策契约 (Machine-Actionable Decision)
<!-- 
  【专供 VibeCoding / AI 编码切片读取（顶部 [VIBE_CONTRACT] 至下一同级标题）】
  说明：本区块记录本 ADR 锁定的不可变决策、生效范围与硬编码禁令。
  AI 编码时只需装载本区块，绝不可使用下方已否决方案！
-->
```yaml
adr_decision_contract:
  adr_id: "ADR-{NUMBER}"
  status: "ACCEPTED"
  scope: "{如：后端全域 / 订单微服务 / 前端组件层}"
  locked_decision: "{一句话明确最终锁定的架构方案，如：采用 PostgreSQL 行级乐观锁实现幂等}"

guardrails:
  - "MUST: 所有状态迁移必须检查 version 字段单调递增"
  - "FORBIDDEN: 严禁采用分布式软锁或内存锁绕过数据库行锁约束"
```

---

## [HUMAN_RATIONALE] 决策背景与多方案论证 (Human Rationale & Options)
<!-- 【面向人类评审与架构审计】：记录为什么做此决策以及备选方案分析 -->

### 1. 背景与问题阐述 (Context)
{详细描述当前面临的技术挑战、业务需求或架构瓶颈}

### 2. 备选方案权衡 (Options Considered)

| 方案 | 优势 (Pros) | 劣势 (Cons) | 成本与风险 |
|---|---|---|---|
| **方案 A：{Name} (最终采纳)** | 性能高、数据强一致 | 需维护版本字段 | 低 |
| **方案 B：{Name} (已否决)** | 无需加列 | 极端高并发下可能出现击穿 | 高 |

### 3. 决策结果与详细理由 (Decision & Rationale)
我们决定采纳 **方案 A**，主要原因为：
1. ...
2. ...

### 4. 影响与后续行动 (Consequences)
- **正面影响**：...
- **负面影响与技术债**：...
- **后续待办**：...
