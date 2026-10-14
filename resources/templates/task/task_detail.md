# 任务详细设计与执行记录：{task_id}

- **任务名称**：`{task_title}`
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

## 3. 执行步骤与进展 (Checklist)
- [ ] 1. 创建或更新 DB 迁移脚本（V/U 同步）
- [ ] 2. 编写/更新六元组核心方法与补偿/降级逻辑
- [ ] 3. 更新 Mock 契约与 Test Profile
- [ ] 4. 编写全覆盖单元测试与契约测试
- [ ] 5. 执行构建与本地质量门禁验证

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
