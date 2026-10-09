# Mock 规范与契约测试指南

## 1. 核心架构与隔离原则

```text
    ┌───────────────────────────────────────────────┐
    │  hs_dev_docs/_00_project/_13_mock_contract/   │
    │  (单一真理源契约库: JSON Schema / Protobuf)     │
    └───────┬───────────────────────────────┬───────┘
            │ 引用契约                      │ 协议断言
            ▼                               ▼
    ┌───────────────┐               ┌───────────────┐
    │ mock/ 服务层  │               │ test/ 契约测试│
    │ (独立 Sidecar)│               │ (_03_contract)│
    └───────────────┘               └───────────────┘
```

1. **业务代码零污染**：严禁在 `backend/`、`frontend/` 等业务代码中写入任何 Mock 分支判断（如 `if (isMock) ...`）或伪数据硬编码。
2. **Sidecar 独立部署**：Mock 模拟服务运行在独立的端口或容器中（由 `mock/_01_mock_server/` 提供）。
3. **数据与代码解耦**：
   - 数据集存放在 `mock/_02_mock_data/_01_dataset/`；
   - 覆盖数据存放在 `_02_override.json`；
   - 错误注入规则存放在 `mock/_04_error_inject/`；
   - 延迟注入规则存放在 `mock/_05_delay_inject/`。
4. **测试集组合（Test Profile）**：
   - 测试用例通过 `mock/_06_test_profile/{profile_name}.yaml` 组合具体的数据集、错误注入与延迟，代码无需任何改动。

---

## 2. Test Profile 示例

```yaml
profile: order_create_timeout_profile
description: 模拟下游库存服务超时场景
dataset: order_create_base
scenario: order_create_timeout
error_inject: downstream_timeout
delay_inject: slow_stock_service
contract_ref: hs_dev_docs/_00_project/_13_mock_contract/order_create.json
```
