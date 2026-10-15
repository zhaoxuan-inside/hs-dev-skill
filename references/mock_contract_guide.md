# Mock 规范与契约测试指南

## 1. 核心架构与隔离原则

```text
    ┌───────────────────────────────────────────────┐
    │  hs_dev_docs/_04_engineering_contract/_03_mock_contract/   │
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

创建契约和 Profile 时可分别从 [`mock_contract.json`](../resources/templates/mock/mock_contract.json) 与 [`test_profile.yaml`](../resources/templates/mock/test_profile.yaml) 起草，再按实际协议和测试框架补齐字段。

```yaml
profile: order_create_timeout_profile
description: 模拟下游库存服务超时场景
dataset: order_create_base
scenario: order_create_timeout
error_inject: downstream_timeout
delay_inject: slow_stock_service
contract_ref: hs_dev_docs/_04_engineering_contract/_03_mock_contract/order_create.json
```

---

## 3. Mock 数据集与测试数据集（DDT）的边界协同

为防止出现“将外部 Mock 数据与领域测试数据集混为一谈”或“在端到端测试中全链路 Mock 导致假绿”的失真问题，严格执行以下隔离标准：

### 3.1 职责正交分离
| 维度 | Mock 数据集 (`mock/_02_mock_data`) | 测试数据集 (`test/_08_test_data`) |
|---|---|---|
| **核心定位** | 外部不可控环境与网络替身（Fake Environment） | 本系统业务规则断言与用例输入（Domain Specification） |
| **生效边界** | 仅挂载在 Adapter / 外部 RPC / HTTP 调用外部 | 驱动领域服务、方法单元、状态机或控制器测试 |
| **典型内容** | 下游服务的 200/404/500 Response Payload、延迟注入 | 业务场景输入参数（Inputs）与业务期望结果（Expectations） |

### 3.2 数据驱动测试（DDT）断言规约
- 允许在 `test/_08_test_data` 中声明测试用例的 `input` 与期望结果；
- **禁止全量绝对相等比对（Anti-Pattern: `assert actual == expected`）**：由于真实业务往往包含动态 UUID、时间戳（`createdAt`）、Token 与乱序数组，全量相等会导致极其脆弱的假红；
- **强制采用复合断言**：通过 Schema Match 校验协议契约，并提取核心领域字段（如状态码、金额、状态机状态）进行精准断言。

### 3.3 双轨制 E2E 验证原则
1. **日常开发快跑轨（Mock Profile）**：允许单测、契约测与本地极速冒烟通过 `mock/_06_test_profile` 打桩运行，提供秒级反馈；
2. **阶段 6 交付门禁轨（Sandbox / Testcontainers）**：提交与交付前，严禁全链路全量 Mock！必须保留至少一条连通真实数据库容器（如 Testcontainers 启动真实 PostgreSQL）或第三方沙箱（Sandbox）的真实链路，杜绝同义反复的假 E2E 幻觉。

