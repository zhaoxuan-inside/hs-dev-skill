# 上下文装载包 (Context Pack)：{task_name}

- **任务 ID**：`{task_id}`
- **生成时间**：`{timestamp}`
- **目标域**：`{domain_name}`
- **Token 预估**：`~{token_estimate}`

---

## 1. 业务目标与需求切片
{从需求文档 _01_product_design 中抽取的精准上下文}

---

## 2. 核心数据模型与表结构
{引用 _04_db_schema 中的相关字段与约束}

---

## 3. 接口与六元组方法签名
{引用 _05_interface_design 与 _06_method_design 中的关键签名}

---

## 4. 依赖调用链与外部契约
{引用 _07_call_chain 与 _13_mock_contract}

---

## 5. 质量与覆盖率门禁要求
- 单测分支覆盖率 ≥ 85%
- 补偿/降级分支 100% 覆盖
- 契约测试 100% 通过
