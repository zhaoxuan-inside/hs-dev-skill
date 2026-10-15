# 测试方法（一等公民 · 质量优先）

**何时读**：进入 IMPLEMENT / 阶段 5；写或改业务逻辑、API、六元组；定 seam 与验收；门禁失败；每会话最多一次。  
**分工**：本文 = **测什么、怎么测、与分级挂钩**；层级目录与覆盖率表 → [`quality_gates.md`](quality_gates.md)；可测形状 → [`deep_modules.md`](deep_modules.md)；契约夹具 → [`mock_contract_guide.md`](mock_contract_guide.md)。

测试用例规格可使用 [`test_case_spec_template.md`](../resources/templates/hs_dev_docs/test_case_spec_template.md)；根据项目的实际测试框架调整模板中的路径和单跑命令。

---

## 0. 质量铁律（高于速度与「看起来做完」）

1. **质量大于一切**：可演示但无测试证明的行为，不算完成。  
2. **分步的正确 → 最终的正确**：每一垂直切片（一个行为）红→绿→重构通过后，再开下一片；禁止横切片「先堆全测再写全码」导致测不对行为。  
3. **用测试提高正确性**：测试是规格与回归网，不是事后补丁；接口（seam）即测试面。  
4. **无确认的 seam 不写测**：先与用户/冻结设计对齐「在哪测、测什么行为」。  
5. **测试报错绝对阻断交付（Zero Failing Test Gate）**：全套测试只要有 **≥1 个失败/报错/超时**，**绝对禁止**将任务置为 `COMPLETED`，**绝对禁止**执行 `git commit`，**绝对禁止向用户报告交付**！严禁向用户汇报“已完成，但有若干测试未通过/稍后修复”。只要测试未绿，唯一合法动作是就地进入 Debug 修复循环（定位 Seam -> 修复实现/校准测试 -> 重测），直至 100% PASS。若遇外部不可抗力（如不可逆第三方服务中断）必须设为 `status --set BLOCKED` 并详述阻断上下文，严禁假装完工。  
6. **静态检测零告警零错误（Zero Warnings, Zero Errors）**：交付前代码静态检查（Linter / TypeChecker / 死代码扫描 / 门禁验证）必须 **0 Warning 且 0 Error**。任何 Warning 均视为阻断性质量缺陷，必须在提交前彻底消除，严禁带 Warning 交付代码。

---

## 1. 好测试的标准

| 要 | 不要 |
|----|------|
| 行为规格：「用户可用有效购物车结账」 | 绑定私有函数名/内部结构 |
| 经**公共接口（seam）**观察 | 为测而测，反射撬开实现 |
| 重构后仍绿（测行为不测形状） | 镜像实现逐步断言 |
| 失败信息指向规格缺口 | 只 assert true / 空测 |

---

## 2. Seam 先确认（强制）

**Seam** = 可替换行为、可观察结果的公共边界（见 [`deep_modules.md`](deep_modules.md)）。

编码前落盘（brief / context_pack / 任务详情一行表即可）：

| Seam | 观察什么 | 抓住什么 | 抓不住什么 |
|------|----------|----------|------------|
| 例：HTTP 契约 | 状态码+字段 | 对外行为 | 域内不变量细节 |
| 例：领域方法六元组 | output/metrics/evolution | 规则与补偿 | UI 文案 |

- **S**：≥1 个 seam（通常方法或单端点）  
- **M**：触达面每个对外行为 ≥1 seam  
- **L**：主路径 e2e + 核心方法 + 契约；补偿/降级 seam 必测  

未确认 seam → 禁止开始红灯循环（可先 DESIGN 迷你审讯问清）。

---

## 3. 垂直切片 TDD（默认实现节奏）

```text
确认 seam → 写一个失败测试（红）→ 最小实现（绿）→ 重构（保持绿）→ 下一行为
```

1. **一次一片**：一个用户/系统可感知行为，不是一层全测完。  
2. **依赖注入**：接受依赖，不在被测模块内 `new` 外部 SDK（Adapter 在 seam 外）。  
3. **Mock 隔离**：业务零污染；Profile 在 `mock/`，见 mock_contract_guide。  
4. **六元组**：`method` / `compensate` / `fallback` 分支在方法测中显式覆盖（补偿/降级 **100%**）。  
5. **回归**：修 bug 先加失败测再修（与 systematic debugging 同精神）。

---

## 4. 与 change_size / 门禁

| 档 | 最低测试义务 |
|----|----------------|
| **S** | 触达行为 ≥1 自动化测；或证明纯文案/无逻辑且 DoD 不含行为变更 |
| **M** | 触达方法/API 单测或契约测绿；相关回归不破 |
| **L** | 阶段 5 全套：方法测 + 契约 + 主路径；阶段 6 `make test` 全绿 |

---

## 4b. 方法类型属性驱动的精准测试矩阵 (Method Archetype Driven Scope)

在 VibeCoding 实现期，为防止 AI 无脑全量跑测（耗费大量 Token 与时间）或漏测关键风险，**必须依照 `_04_engineering_contract/_04_method_design/` 中声明的方法属性精确收窄测试范围**（详见 [`method_archetypes.md`](method_archetypes.md)）：

| 方法类型 (`archetype`) | 敏感度 (`sensitivity`) | 强制测试范围 (`Test Scope`) | 上下文与跑测指令约束 |
|---|---|---|---|
| **`TRANSFORM`** / **`PRESENT`** | `LOW` | **纯单元测试 (`UNIT`)** | 仅加载该方法与单测；**严禁跑 E2E/集成测试** |
| **`ALGO`** | `MEDIUM` ~ `CRITICAL` | **算法单测 (`UNIT`)** | 覆盖边界值、零值与溢出断言；必须秒级执行 |
| **`GUARD`** | `HIGH` ~ `CRITICAL` | **守卫拦截单测 (`UNIT`)** | 双向覆盖：合法放行 + 非法越权拦截 100% 断言 |
| **`STATE`** | `CRITICAL` | **状态机矩阵测试 (`UNIT`)** | 全合法跃迁与非法跃迁拦截矩阵 100% 覆盖 |
| **`ADAPTER`** | `MEDIUM` | **Mock 契约测试 (`CONTRACT`)** | 校验 I/O 序列化与异常捕获；使用 Mock Profile，不连真实外部网络 |
| **`ORCHESTRATE`** | `HIGH` ~ `CRITICAL` | **用例集成测试 (`INTEGRATION`)** | Mock 外部 I/O；重点覆盖主流程与分支调度；触达六元组时 compensate/fallback 100% 覆盖 |

层级目录与覆盖率数字以 [`quality_gates.md`](quality_gates.md) 为准；**本文件管方法与节奏，那份管分层与清单**。

---

## 4c. 测试数据集与 Mock 的边界协同（DDT 与双轨制 E2E）

为彻底解决测试数据集（`_08_test_data`）与 Mock 数据集（`mock/_02_mock_data`）混淆重叠、以及“本地全 Mock 全绿但上线雪崩”的假 E2E 幻觉，确立以下设计规范：

### 1. 职责正交解耦（两类数据不混淆）
* **Mock 数据 (`mock/`) = 外部环境与网络替身（Fake Environment）**：
  * 仅用于模拟**外部不可控的第三方适配器（Adapter）边界**（HTTP 404/500、RPC 超时、下游网络抖动、错误注入）；
  * 由独立的 Mock Sidecar 驱动，**严禁业务逻辑被 Mock 分支污染**。
* **测试数据集 (`test/_08_test_data/`) = 本系统领域规则与断言意图（Domain Assertion）**：
  * 专用于驱动**本系统的业务计算、状态机和主流程**；
  * 声明用例输入参数、初始状态与业务预期结果。

### 2. 数据驱动测试（DDT）防脆弱断言铁律
在单测/集成测试中支持将输入与预期组织为结构化测试集（Data-Driven Testing / 表驱动测试），但必须严格遵守断言规则：
* **严禁全量刚性相等断言**：禁止使用 `assert actual == expected` 直接对比整个大型 JSON/对象，避免因动态生成的 `UUID`、自增 ID、`created_at` 时间戳、哈希签名、JSON Key 顺序差异产生“脆弱用例（Flaky Tests）”。
* **强制使用复合断言模式**：
  1. **Schema Match**：结构与字段类型契约匹配；
  2. **核心业务字段精确比对**：断言关键业务状态（如 `status == "PAID"`、`amount == 200`）；
  3. **领域不变量断言**：断言数据守恒与状态机约束。

### 3. 双轨制 E2E 原则（杜绝同义反复与假 E2E 幻觉）
* **开发快跑轨（Mock Profile 冒烟）**：
  * 本地实现期与日常开发中，允许通过 `mock/_06_test_profile/` 组装桩数据，秒级跑通 E2E 主链路，隔绝外部网络抖动；
* **门禁准出轨（真实容器 / 沙箱直连）**：
  * **阶段 6 交付门禁与发布前自检，严禁全链路全量 Mock！**
  * 必须具备直连**官方沙箱（Sandbox）**或通过 **Testcontainers** 启动真实轻量容器（如真实 PostgreSQL、真实 Redis）的验证通路，杜绝“我 Mock 了输入输出，所以断定系统正确”的同义反复自嗨。

---

提交前：全量测试 100% 绿 ∧ 静态检测 0 告警 0 错误 ∧ `verify_consistency` ∧（若适用）死代码扫描。测试有报错或静态检测有告警 → **绝对禁止 Commit，绝对禁止流转 COMPLETED 交付「先交再补」**。

---

## 5. 反模式

| 禁止 | 改为 |
|------|------|
| 先写完再「补单测」当仪式 | 红绿驱动每一片 |
| 测私有方法 / 巨型快照当唯一保障 | 测 seam 行为；快照仅辅助 UI |
| 为凑覆盖率测 getter | 测不变量与失败模式 |
| 实现期用测掩盖未冻产品语义 | 回切 DESIGN / grill |

---

## 6. 与审讯式 / 深模块

- DESIGN：审讯式问清 DoD 与验收 → 写成可测断言语言。  
- 架构：深模块 = 小接口后藏大行为 → **同一接口供调用方与测试使用**。  
- 模糊测法 → `skill_ref_index search --q 测试` 或本文件；远程专项可后续 `rule_fetch`，禁止开局通读外部 TDD 全书。
