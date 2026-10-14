# API 工程细则（本地高频 · 按需加载）

**何时读**：阶段 3 写/改接口与 Mock 契约，或阶段 5 实现对外/模块边界 API 时；每会话最多一次。  
**分层**：本文 = **高频必守**；更深契约/幂等/Hyrum → [`rule_library.md`](rule_library.md) + `rule_fetch resolve --id addy.api-design`。

```bash
python scripts/rule_fetch.py search --q 幂等
python scripts/rule_fetch.py resolve --id local.api.core
python scripts/rule_fetch.py resolve --id addy.api-design
python scripts/rule_fetch.py search-cache --q Idempotency
```

---

## 1. 契约优先与命名规约

1. 先定输入/输出类型与错误形状，再写实现与 Mock JSON。
2. Input 与 Output 分离（Output 含服务端字段：`id`、时间戳等）。
3. 列表必须分页（`page`/`pageSize` 或 cursor + `pagination` 元数据）。
4. 扩展只加可选字段；禁止改类型/删字段而不走显式迁移/版本策略。
5. **词态矩阵与命名稳定**：
   - REST 路径用复数名词（`/orders`）；
   - 布尔字段用 `is/has/can`；
   - 变更枚举与状态用 `UPPER_SNAKE`（如 `CREATED`, `UPDATED`）；
   - **事件与 Webhook 主题**：统一使用**名词.过去分词**（`<entity>.<action_past_tense>`，如 `order.created`、`order.updated`），绝对禁止用动词原形（如 `order.update`）或时间戳（如 `updated_at`）作为事件名；
   - **时间戳字段**：统一采用 `created_at`、`updated_at`、`deleted_at`；
   - **Search-Before-Name 铁律**：新增接口字段、事件名或参数前，必须查阅代码库及 `_00_project/_02_project_word.dict.yaml`，严禁自创同义别名。

产品语义未冻（鉴权归属、计费字段等）→ `work_mode=DESIGN` 问清再写死公开契约。

---

## 2. 统一错误语义

全项目一种错误信封，禁止混用 throw/null/`{error}`：

```text
{ "error": { "code": "MACHINE_CODE", "message": "人类可读", "details"?: ... } }
```

| HTTP | 含义 |
|------|------|
| 400/422 | 校验或语义非法 |
| 401/403 | 未认证 / 无权限 |
| 404 | 资源不存在 |
| 409 | 冲突（版本、重复） |
| 500 | 内部错误（不泄露内部细节） |

第三方响应一律当不可信：校验形状后再用。

---

## 3. 边界校验

- **只在**系统边缘校验：HTTP/RPC 入口、表单提交、外部环境变量、外部服务响应。
- 内部同进程、已校验类型之间不重复校验。
- 校验失败返回稳定 `code`，便于客户端与契约测试。

---

## 4. 幂等（写接口）

接受 `Idempotency-Key` 就必须**兑现**：

| 规则 | 要点 |
|------|------|
| 键来源 | 客户端或业务不可变意图 ID；禁止每次重试新 UUID/时间戳 |
| 原子占位 | 唯一约束一次插入抢主；禁止先 SELECT 再 INSERT |
| 载荷守卫 | 同 key 不同 body → 明确失败（如 422），禁止错配回放 |
| 进行中 | 预先选定 409 / 等待 / 202+查询；禁止第二请求当「卡住」再跑一遍 |
| 保留期 | TTL ≥ 最长重试链（含 DLQ 重放） |
| 未知结果 | 超时 ≠ 失败；先记意图再调外部，崩溃可对账 |

不可幂等的写操作必须在接口文档标明「不可安全重试」。深化：`addy.api-design` + `search-cache --q idempoten`。

---

## 5. Hyrum / 兼容

- 可观察行为都会被依赖：少泄露实现细节（排序、错误原文、耗时）。
- 优先「单一现行版本 + 加字段」；多版本并行成本高，需 ADR。
- 内部模块边界同样需要契约，避免隐式耦合。

---

## 6. 与本 Skill 产物对齐

| 产物 | 必须体现 |
|------|----------|
| `_05_interface_design/..._design.md` | 方法、路径、入出参、错误码表、是否幂等、分页 |
| `_13_mock_contract/*.json` | 与成功/失败形状一致 |
| 六元组 + 单测 | 校验失败、冲突、幂等重放、降级路径有覆盖 |

实现期命名/内部拆分细节：**少问**；公开契约与业务字段未决：**回切 DESIGN**。
