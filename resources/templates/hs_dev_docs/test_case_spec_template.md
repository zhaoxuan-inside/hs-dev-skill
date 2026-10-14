# 测试用例规格说明书：{case_name}

- **用例标识 (Case ID)**：`{TC-XXX}`
- **用例名称**：{case_name}
- **关联业务特性 (Feature ID)**：`{FEAT-XXX}`
- **目标方法/符号 (Target Symbol)**：`{TargetClass.target_method}`
- **测试层级 (Test Layer)**：`UNIT` / `INTEGRATION` / `CONTRACT` / `E2E`
- **所属业务模块 (Module)**：`{module_name}`
- **测试代码文件 (Test File)**：`test/_01_method_test/{module}/test_{target}.py`
- **精确单跑指令 (Test Command)**：`pytest test/_01_method_test/{module}/test_{target}.py -k {test_method_name}`
- **DDT 数据集 (Dataset)**：`test/_08_test_data/{module}/{case_name}.json`

> [!NOTE]
> **质量优先 · 跑测精准**：
> 本规格书用于建立测试用例的物化索引，支持 `python3 scripts/doc_index_db.py test-search` 定向按需检索。
> 严禁无脑跑无关全量测试，依据精准单跑指令执行秒级闭环验证。

---

## 1. 测试用例意图与前置不变量 (Intent & Invariants)

- **业务意图**：{简述本用例验证的核心业务边界或异常分支}
- **前置不变量与初始上下文**：
  - 前置状态：{如：用户处于正常状态，余额充足}
  - 外部桩依赖 (Mock)：{声明外部 Mock Profile，仅在 contract/adapter 层引入，业务核心零 Mock 污染}

---

## 2. Gherkin 行为断言矩阵 (Given / When / Then)

```gherkin
Feature: {case_name}

  Scenario: 核心行为验证
    Given {初始前置条件与入参上下文}
    When 调用目标方法 {TargetClass.target_method}(args)
    Then 结果返回值满足业务断言，且领域不变量成立
```

---

## 3. 关联回归与缺陷记录 (Regression Trace)
- **关联 Task ID**：`{TASK-XXX}`
- **历史缺陷追踪**：{若为 Bug 修复回归用例，记录缺陷根因与防范原理}
