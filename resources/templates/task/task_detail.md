# 任务详细设计与执行记录：{task_id}

- **任务名称**：`{task_title}`
- **change_size**：`{S|M|L}`
- **当前状态**：`{status}`
- **开始时间**：`{created_at}`
- **最后更新**：`{updated_at}`

---

## 1. 任务背景与目标
{详细描述该任务的业务价值与技术目标}

---

## 2. 关联设计文档清单
- **数据表设计**：`hs_dev_docs/_04_engineering_contract/_01_db_schema/...`
- **接口设计**：`hs_dev_docs/_04_engineering_contract/_02_interface_design/...`
- **方法设计**：`hs_dev_docs/_04_engineering_contract/_04_method_design/...`
- **调用链分析**：`hs_dev_docs/_04_engineering_contract/_05_call_chain/...`

---

## 2b. 需求追踪与覆盖矩阵 (Requirement Traceability Matrix)
> **验收硬阻断铁律**：任务标记为 COMPLETED 前，所有必需需求（REQ-*）必须达到 100% 验证覆盖率，禁止带未验证项交付。
> $\text{Coverage} = \frac{\text{已验证需求数}}{\text{全部必需需求数}} = 100\%$

| 需求ID | 对应功能/规则 | 对应方法/代码 Seam | 自动化测试用例 | 验收证据与断言 | 验证状态 |
|---|---|---|---|---|---|
| `REQ-001` | 主成功流处理 | `{method_name}` | `{test_file}::{test_case}` | 断言响应码 200 且数据行落盘 | `verified` |
| `REQ-002` | 边界拦截与原位提示 | `{method_name}` | `{test_file}::{test_validation}` | 拦截非法参数并断言特定异常码 | `verified` |

---

## 3. 执行步骤与进展 (Checklist)
<!-- 
  [步骤执行策略标注]
  - [idempotent: true|false]：标记操作是否具备幂等安全性
  - [side_effect: none|local|external]：标记副作用范围
  - [retry: N, backoff: exp|linear]：声明外部调用重试与退避策略
-->
- [ ] 1. 创建或更新 DB 迁移脚本（V/U 同步） `[idempotent: true]`
- [ ] 2. 编写/更新六元组核心方法与补偿/降级逻辑 `[side_effect: local]`
- [ ] 3. 更新 Mock 契约与 Test Profile `[idempotent: true]`
- [ ] 4. 编写全覆盖单元测试与契约测试（红绿垂直 TDD） `[side_effect: none]`
- [ ] 5. 执行构建与本地质量门禁验证（100% PASS 且 0 警告） `[side_effect: none]`

---

## 4. 涉及文件修改清单 (Diff Tracking)
```text
M backend/src/service/order_service.go
A hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations/V1.1.0__add_field.sql
A hs_dev_docs/_04_engineering_contract/_01_db_schema/_01_order/migrations/U1.1.0__add_field.sql
M test/_01_method_test/order_create_test.go
```

---

## 5. 验证与门禁记录
- 单测覆盖率：`{coverage}%`
- 契约比对结果：`PASS`
- E2E 冒烟测试：`PASS`
