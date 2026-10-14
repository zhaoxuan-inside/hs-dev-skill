# 方法类型分类与契约画像指南 (Method Archetypes & Contract Profile)

**何时读**：
- 阶段 3 详细规格设计（编写/更新 `hs_dev_docs/_06_method_design/`）；
- 阶段 4 上下文装配（Context Pack 中按方法画像物化切片）；
- 阶段 5 编码与测试实现（依据方法属性收窄上下文、定向跑测、维护修改历史）；
- 检索命令：`python scripts/skill_ref_index.py search --scenario 方法设计` 或 `search --q 方法类型`

---

## 1. 核心思想：“文档定义代码”与 VibeCoding 效能引擎

在传统开发中，方法元数据分散在人类脑海或冗长代码注释中，导致 AI 在 VibeCoding 模式下频繁面临两大痛点：
1. **上下文膨胀与幻觉**：AI 为修改一个方法，被迫阅读数千行上下游源码，大量消耗 Token 且容易丢失约束。
2. **测试盲目与效率低下**：AI 无法感知改动的真实影响半径，要么无脑跑全量测试耗时数分钟，要么漏测高危分支。

**“文档定义代码”（Specification Drives Code）原则**：
- **代码保持纯粹**：源码实现专注于逻辑本身，不充斥冗余元数据注释；
- **文档作为单一天理源**：方法的设计属性、代码物理定位（行号与行数）、改动敏感度、依赖拓扑与历史修改原理全部沉淀在 `hs_dev_docs/_06_method_design/` 中；
- **精准投喂与秒级闭环**：AI 通过检索文档获取切片，毫秒级读取目标代码行段，执行定点测试，并反向更新文档历史记录。

---

## 2. 七大方法标准类型 (The 7 Method Archetypes)

本 Skill 将系统中所有方法抽象为 7 类原子模型，每一类具有截然不同的依赖约束、敏感度与测试策略：

| 类型代号 | 类型名称 | 核心职责 | 默认敏感度 | 副作用与外部依赖 | 推荐测试层级 |
|---|---|---|---|---|---|
| **`TRANSFORM`** | 数据填充与转换 | DTO/VO 互转、Schema 校验清洗、字段组装映射 | `LOW` | **无副作用**（纯内存映射，无 I/O） | 单元测试 (`UNIT`) |
| **`ALGO`** | 通用计算与算法 | 核心计价、哈希加解密、排序检索、数值统计公式 | `MEDIUM` ~ `CRITICAL` | **严格纯函数**（无 I/O，无全局状态修改） | 单元测试 (`UNIT`) |
| **`GUARD`** | 校验守卫与权限策略 | 越权检查、角色鉴权判定、业务前置规则断言拦截 | `HIGH` ~ `CRITICAL` | **高危拦截**（返回布尔或抛出拒绝异常） | 单元测试 / 契约测试 (`UNIT`/`CONTRACT`) |
| **`STATE`** | 状态机驱动变迁 | 生命周期流转驱动、合法变迁断言、Reducer | `CRITICAL` | **核心资产**（无外部 I/O，操作内存聚合根状态） | 状态矩阵单测 (`UNIT`) |
| **`ORCHESTRATE`** | 业务逻辑编排 | 顶层用例流程组装、串联调度各子方法、Controller/Service | `HIGH` | **胶水层**（无底层复杂运算，调度外部 I/O 与领域层） | 集成/用例测试 (`INTEGRATION`) |
| **`ADAPTER`** | 外部 I/O 适配 | DB CRUD、三方 HTTP API、Redis/MQ 读写、文件系统包装 | `MEDIUM` | **有外部副作用**（需承受网络波动与异常重试） | Mock 契约测试 (`CONTRACT`) |
| **`PRESENT`** | 展现与格式化 | 币种/时间友好显示、日志脱敏掩码、CLI/UI 视图组装 | `LOW` | **边缘展现**（格式化输出，出错不破坏核心数据） | 单元测试 (`UNIT`) |

---

## 3. 方法属性机制（七维画像）

在 `hs_dev_docs/_06_method_design/` 中，每个登记的方法均具备以下标准化属性：

1. **所属层次与模块**：自上而下的定位锚点（如 `领域核心层 / billing 模块`）。
2. **代码精准定位与符号锚点（Symbol Anchor 抗脆弱）**：
   - 标明文件相对路径与目标符号名称（如 `ClassName.method_name`）；
   - **动态求值行号（抗脆弱机制）**：严禁硬依赖脆弱的死行号。系统借助 AST（通过 `doc_index_db symbol-slice --name <symbol>`）动态解析当前最新物理行段（如 `L45-L62`），格式化、增加注释、调整 import 绝不失效；
   - 物理行号仅作为辅助快照缓存，在代码演进时由 AST 自动对齐自愈。
   > **VibeCoding 收益**：AI 借助符号锚点与动态行号毫秒级单屏命中目标代码，无需全量通读，Token 节省达 90%。
3. **方法类型 (`archetype`)**：7 大标准类型之一。
4. **模式协同集群关联 (`patternCluster`)**：【核心防破坏与精准指针】
   - 标明所选设计模式（`Strategy` / `Chain of Resp.` / `State` / `Builder` / `Adapter` / `Facade` 等）；
   - 指向所属模式集群档案文件路径及在集群中的角色（如 `Role: ConcreteStrategy`、`Contract: IPricingStrategy`）；
   - **直指防破坏护栏锚点**（如 `#4-vibecoding-防破坏红线`）；
   - > **精准切片收益**：AI 处理该方法时，通过单向指针只读取关联的 15 行护栏切片，**绝对禁止全量扫描或通读整份庞大的设计模式文档库**，实现极致 Token 控制与架构防腐。
5. **改动敏感度与理由 (`sensitivity`)**：
   - `LOW` / `MEDIUM` / `HIGH` / `CRITICAL`（属于模式集群核心参与者的方法强制为 `HIGH` 或 `CRITICAL`）；
   - **独立拆行给出敏感理由**：向 AI 明确阐述破坏后果（如资损、安全越权、设计模式被破坏）。
6. **副作用类型与具体副作用 (`sideEffect`)**：
   - 类型：`NONE`（严格纯函数）/ `IN_MEMORY`（仅改内存状态）/ `EXTERNAL_IO`（涉及外部 I/O）。
   - **独立拆行给出具体表现**：明确是否有网络请求、DB 写入、入参浅拷贝污染等。
7. **指导测试范围与执行策略 (`testScope`)**：
   - 明确测试文件路径、测试级别（`UNIT` / `CONTRACT` / `INTEGRATION` / `E2E`）；
   - 明确覆盖约束与**精确跑测命令**（如 `npm test -- path/to/test.ts` 或 `pytest tests/test_algo.py`）；
   - **硬性禁止跑全量无关测试**。

---

## 4. 以本方法为中心的局部依赖拓扑图 (Ego Dependency Graph)

每个方法档案必须内嵌以该方法为中心（★）的 Mermaid 局部依赖图：
- **上游调用方 (Callers)**：明确标出谁在调度它，以及调用方的类型；
- **下游被调方 (Callees)**：明确标出它依赖谁，以及被调方的类型；
- **隔离禁令**：
  - `ALGO` 与 `TRANSFORM` **绝对禁止调用 `ADAPTER`**（计算不得混入 I/O）；
  - `GUARD` 只能由 `ORCHESTRATE` 调度，或在领域聚合根入口处拦截；
  - `ADAPTER` 仅做协议翻译与网络包装，不得包含业务编排。

---

## 5. 三段式历史修改记录 (Structured Changelog)

历史记录禁止简略为一句话。每次修改必须包含以下三段：
1. **需求背景**：对应的需求/任务（Task ID）与业务目标；
2. **修改原因**：为什么需要修改此处代码，原逻辑有何缺陷或不足；
3. **技术原理**：底层实现的变更机制与设计考量（防止后续迭代中被其他 AI 误当冗余代码删除）。

---

## 6. 防方法爆炸与查重选型优先机制 (Method Discovery & Anti-Explosion Gate)

在 AI 辅助编程（VibeCoding）中，大模型自回归生成的本能往往是**“无脑新建函数”**而不是“选择/复用已有方法”，导致项目中充斥着大量功能重合的影子函数（如 `formatDate2`、`parseMobileUtil`、`checkUserHelper`），造成灾难性的**方法爆炸（Method Explosion）**。

若试图将全库已有函数直接塞入 Prompt，又会引发严重的 **Prompt 膨胀与上下文稀释（Attention Dilution）**。

本 Skill 确立**“写前检索、查重优于新建、单一天理源派生轻量索引”**的抗爆炸防护体系：

### 6.1 单一天理源（SSOT）与派生轻量索引
- **严禁双重维护文档**：`hs_dev_docs/_06_method_design/` 是全仓方法契约的**单一天理源**，不需要也不允许额外人工维护第二份方法清单；
- **自动化物化索引（Materialized Cache）**：`scripts/doc_index_db.py` 会自动扫描解析 `_06_method_design/*.md` 中的方法名、分类画像（archetype）、核心功能描述与物理代码坐标，物化为本地 SQLite `methods` 表；
- **NLP / 意图极速召回**：在写任何辅助方法前，Agent 执行 `python scripts/doc_index_db.py method-search --q "<业务意图>"`，仅消耗几十 Token 即可获得 Top-3 候选画像。

### 6.2 编码前的四步决策漏斗 (The 4-Step Decision Funnel)
Agent 在产生“我需要一个函数来实现 X”的念头时，**绝对禁止直接落笔写代码**，必须遵循以下漏斗：

```text
[新需求 / 业务意图]
        │
        ▼
[1. 意图检索 (Search)] ──调用 doc_index_db.py method-search --q "业务意图"
        │
        ▼
[2. 画像决策 (Decision)]
  ├── A. 完全匹配 (100%) ───────► 直接 import 复用，严禁新建
  ├── B. 高度相似 (≥80%) ──────► 扩展入参（Options/可选参数），严禁造影子函数
  ├── C. 单处使用且极微小 (≤3行) ─► 遵循深模块哲学，就地内联 (Inline)，严禁浅抽取
  └── D. 确认全新通用领域逻辑 ──► 获准新建；必须先在 _06_method_design 登记画像
        │
        ▼
[3. 极窄切片 (Narrow Slice)] ──按画像结果使用 view_file 读取目标 15~30 行代码
        │
        ▼
[4. 实施变更与定点跑测] ──执行专属测试命令，绿灯后同步回写文档
```

### 6.3 抗爆炸三大防线原则
1. **写前必搜（Search Before Create）**：未经 `method-search` 检索直接创建公共函数属于严重违纪。
2. **扩展优于重造（Extend over Duplicate）**：现有方法入参若不支持某些新格式，采用可扩展配置对象（如 `options` 或可选参数）进行平滑扩展，保持向后兼容，杜绝 `methodV2`。
3. **三次原则与深模块（Rule of Three & Deep Modules）**：
   - 1 处使用：直接内联在调用处（Private/Local）；
   - 2 处使用：容忍少量复制，不急于抽象；
   - 3 处以上使用：且属于跨用例核心逻辑，才抽为公共方法并建档。

---

## 7. 面向 VibeCoding 的执行守则（降低 Token 与极速反馈）

AI Agent 在承接修改任务时，必须严格执行以下工作流：

```text
[1. 意图检索与选型] ──执行 doc_index_db.py method-search 召回候选；确定复用/扩展/新建
        │
[2. 读文档画像]     ──从 _06_method_design 提取「物理定位行号 + 跑测命令」
        │
[3. 极窄上下文]     ──仅 view_file 目标行段（15~30行）及对应单测；严禁加载全量调用链源码
        │
[4. 实施精准变更]   ──按方法类型与规范修改或扩展逻辑
        │
[5. 定点跑测]       ──执行文档指定的专属测试命令；严禁全量跑测；绿灯后结束
        │
[6. 同步回写]       ──更新文档中的代码行号定位与三段式历史修改记录
```

---

## 8. 前端工程化落地与实战映射 (Frontend Architecture Mapping)

前端开发是 VibeCoding 中“逻辑与样式混杂、组件爆炸、单测最难落地”的重灾区。将 7 大方法规范严格映射到现代前端（React / Vue / Svelte）中，能彻底斩断“大组件”对 Token 的消耗：

```mermaid
flowchart TD
    subgraph UI_Layer ["表现层 (Presentation - 无业务计算)"]
        PRESENT["PRESENT: Dumb组件 / JSX / Tailwind / 纯样式<br/>(敏感度: LOW, 纯渲染)"]
    end

    subgraph Flow_Layer ["流程编排与守卫 (Hooks / Router)"]
        ORCH["ORCHESTRATE: Custom Hooks / 容器组件 / Pinia Action<br/>(调度数据与生命周期)"]
        GUARD["GUARD: 路由守卫 / 按钮权限 / 操作条件断言<br/>(敏感度: HIGH, 单测100%)"]
    end

    subgraph Domain_Core ["纯领域核心 (Pure TypeScript - 0 DOM 依赖)"]
        TRANSFORM["TRANSFORM: DTO转ViewModel / 表单Payload组装<br/>(纯函数, 无副作用)"]
        ALGO["ALGO: 购物车折算 / 甘特图换算 / 复杂校验算法<br/>(纯函数, 毫秒级单测)"]
        STATE["STATE: Store Reducer / 状态机原子跃迁<br/>(内存状态, 状态矩阵单测)"]
    end

    subgraph Infra_Layer ["基础设施层 (I/O 隔离)"]
        ADAPTER["ADAPTER: Axios/Fetch API客户端 / Storage / WebSocket<br/>(Mock 隔离)"]
    end

    PRESENT --> ORCH
    ORCH --> GUARD
    ORCH --> TRANSFORM
    ORCH --> ALGO
    ORCH --> STATE
    ORCH --> ADAPTER
```

### 前端 7 大分类职责与代码位置清单

| 方法类型 | 前端真实角色与职责 | 推荐目录位置 | 依赖禁令与特征 | 跑测与测试策略 |
|---|---|---|---|---|
| **`PRESENT`** | 纯展示 Dumb 组件、格式化输出函数（如 `formatCurrency`） | `components/ui/`, `features/*/ui/` | **禁止包含复杂业务算式与 API I/O**；仅依赖 props | 快照或视觉审查；**不跑重型单测** |
| **`TRANSFORM`** | DTO ↔ ViewModel 互转、表单数据清洗与组装 | `features/*/model/mappers.ts` | **禁止异步、禁止修改入参**；纯内存数据塑形 | 纯单元测试 (`vitest` 毫秒级) |
| **`ALGO`** | 纯前端计算算法、本地折算、复杂排版换算、图表数据处理 | `utils/`, `features/*/model/calc.ts` | **严格纯函数，0 DOM 依赖，0 外部 I/O** | 纯单测，边界值与溢出断言 100% |
| **`GUARD`** | 路由前置守卫、按钮禁用判定、操作权限决策 | `guards/`, `features/*/model/policy.ts` | **只返回 boolean 或断言结果**；禁止执行业务修改 | 单测双向覆盖（放行 + 拦截） |
| **`STATE`** | 状态机驱动、Reducer、Pinia 原子 action 状态跃迁 | `stores/`, `features/*/model/state.ts` | **纯状态计算**；禁止在 reducer 内部触发网络请求 | 状态转移矩阵全用例单测 |
| **`ORCHESTRATE`** | 容器组件、Custom Hooks（如 `useOrderCheckout`） | `features/*/hooks/`, `features/*/views/` | **胶水层**；只串联上述纯函数与 Adapter，不自写算法 | 集成测试（Mock Adapter 接口） |
| **`ADAPTER`** | API Client 请求封装、LocalStorage/IndexedDB 包装 | `api/`, `services/`, `adapters/` | **禁止散落业务规则**；仅做协议转换、超时重试与异常封装 | Mock 契约测试，不发起真实外网请求 |

### 前端 VibeCoding 三大纪律：
1. **杜绝“几千行上帝组件”**：页面文件只保留 `ORCHESTRATE`（调用 hook）与 `PRESENT`（渲染标签）；业务算式强制下沉为 `ALGO`。
2. **改逻辑不读 JSX，改样式不读逻辑**：
   - 当需求为“调整折算规则”时，AI 查阅 `_06_method_design` 仅加载 `calc.ts`（L20-L45），**无需加载包含几百行 Tailwind 类名的 React 组件**，Token 节约 90%。
3. **0 DOM 依赖的高速单测**：
   - 核心业务纯函数（`ALGO` / `TRANSFORM` / `STATE` / `GUARD`）脱离浏览器 DOM 与 JSDOM 运行，`vitest run` 0.2 秒反馈，形成即时红绿闭环。

### 前端方法文档模板标准：
前端方法设计文档模板见 [`resources/templates/hs_dev_docs/frontend_method_design.md`](../resources/templates/hs_dev_docs/frontend_method_design.md)。前端核心方法必须落盘到 `hs_dev_docs/_06_method_design/_02_{feature}/_01_{method_name}_design.md`，明确标记 `0 DOM 依赖` 测试环境与具体行号范围。
