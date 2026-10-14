# 子特性需求与功能规格说明书 (Feature PRD)：{feature_name}

- **特性ID (Feature ID)**：`{FEAT-XXX}`
- **特性名称**：{feature_name}
- **所属模块**：{module_name}
- **优先级**：P0 / P1 / P2
- **状态**：active / draft / frozen
- **宏观品味宪章继承**：`Inherits: /DESIGN.md`（严禁在此重新定义全站调性、色彩或字体规范）
- **上级总览索引**：`_02_product_design/overview_prd.md`
- **关联界面原型**：`_03_product_figma/{feature_name}_prototype.md`
- **面向 VibeCoding 契约**：`_02_product_design/features/{feature_name}_vibe_spec.md`

> [!NOTE]
> **微观施工图定位**：本子规格书专注于单一业务功能的微观执行契约，控制在 100~250 行内。
> 严禁侵入数据库 DDL、六元组代码签名或单测覆盖率指标。

---

## 1. 特性洞察与核心价值界定 (Framing & Discovery)

- **现状与摩擦 (Status Quo)**：{用户当前没有本特性时如何应对？最耗时的摩擦点在哪？}
- **用户雇佣任务 (JTBD)**：`When` {特定触发情境}，`I want to` {完成的核心动作}，`so I can` {达成可感知的核心价值}。
- **惊喜时刻 (Aha Moment)**：{进入 30 秒或 3 步内，哪个瞬间让用户体验到十倍提升？}
- **冷启动体验 (FTUE)**：{首次进入且无数据时，如何通过模板/示例引导在 1 分钟内完成首操？}

---

## 2. 交互形态比选与取舍 (Approaches & Trade-offs)

| 评估维度 | 方案 A（推荐采纳） | 方案 B（备选弃用） | 取舍理由 (Trade-off Rationale) |
|---|---|---|---|
| **交互形态** | {方案 A 简述，如侧滑抽屉} | {方案 B 简述，如弹窗/跳转} | 保持主列表上下文连贯，渐进式披露 |

---

## 3. 详细字段与业务规则约束矩阵 (Specifications & Constraints)

| 字段/参数名 | 披露层级 | 类型 | 必填 | 校验规则与边界极端值 | 默认值与微文案提示 |
|---|---|---|---|---|---|
| `{field_1}` | 首屏必填 | 字符串 | 是 | 长度 2-30 字符，防 SQL 注入与 XSS | 请输入真实有效的... |
| `{field_2}` | 渐进折叠 | 数字 | 否 | 正整数，范围 1~999 | 默认 1 |

### 业务分支规则矩阵
1. **分支 1（常规成功）**：{业务处理规则描述}
2. **分支 2（临界或受限）**：{规则描述及原位提示}

---

## 4. 行为驱动产品验收标准 (Functional DoD)

采用 Gherkin 语法，覆盖主成功流、校验拦截流与异常恢复流：

```gherkin
Feature: {feature_name}

  Scenario: 正常触发并完成核心动作 (Happy Path)
    Given 用户已完成前置鉴权且处于正常状态
    When 用户在界面填入有效参数并点击具象主按钮
    Then 界面在 200ms 内展示即时反馈，并流转至目标状态

  Scenario: 参数校验失败原位拦截 (Validation)
    Given 用户输入了超出边界的无效参数
    When 用户触发提交
    Then 界面原位红框高亮错误字段，显示具体修复提示，且保留用户已填内容
```
