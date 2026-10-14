# 已有项目反向重建（Reverse Engineering）与规范接入指南

**何时读**：接手无 `hs_dev_docs` 的遗留/存量项目（Brownfield），或需要对已有代码进行架构还原、Schema 逆向与标准知识库重建时；每会话最多一次。

---

## 1. 核心目标与逆向三原则

已有存量项目往往存在文档缺失、隐式依赖多、代码坏味道散落等问题。反向重建的核心目标是：**在不破坏现有系统运行态的前提下，逆向提取单一事实源，建立四级渐进索引与机器执行契约，使存量项目平滑具备本 Skill 的高质量研发与治理能力。**

### 逆向三原则
1. **代码即事实（Code as Ground Truth）**：以运行态代码与数据库 DDL/迁移文件为第一准绳，杜绝脑补设计；
2. **非侵入式探测（Non-Invasive Discovery）**：逆向分析阶段禁止改动业务代码，仅生成 `hs_dev_docs/` 与索引文件；
3. **分层提取与逐步收敛**：从全局拓扑（根） $\to$ 数据实体与表（DB） $\to$ 接口边界（API） $\to$ 核心调用链与方法契约逐步提取。

---

## 2. 逆向重建四步流水线

```text
[Step 1: 代码库资产扫描] ──► [Step 2: 核心要素提取] ──► [Step 3: 文档体系与词典物化] ──► [Step 4: 四级索引重建与对齐]
      目录拓扑/技术栈              DB / API / 模块边界           hs_dev_docs/ 规范骨架               doc_index_db 编译
```

### Step 1：代码库资产扫描与技术栈锁定
- 运行工程检测，分析包依赖（如 `package.json`、`go.mod`、`requirements.txt`、`pom.xml`、`Cargo.toml`）；
- 判定单体、分层微服务、还是 Monorepo（若包含多端，检查 `apps/` 与 `packages/` 结构）；
- 在 `hs_dev_docs/_00_project/_05_decision_record/ADR_001_tech_stack_baseline.md` 固化当前技术栈基线，并在顶部置顶 `[VIBE_CONTRACT]` 契约块。

### Step 2：核心要素提取（四要素反向映射）

#### 2.1 数据库与存储实体（DB Schema 逆向）
- 扫描 ORM 实体（TypeORM、Prisma、SQLAlchemy、GORM、Hibernate）或 `migrations/` 目录；
- 将物理表结构与字段映射抽取至 `hs_dev_docs/_04_db_schema/`；
- 记录核心表字段约束、主外键关系及枚举值，禁止遗漏 `created_at`/`updated_at` 命名风格差异。

#### 2.2 接口契约提取（API Interface 逆向）
- 扫描路由注册中心（Controller、Router、gRPC Proto、GraphQL Schema）；
- 按业务模块归类输出至 `hs_dev_docs/_05_interface_design/{module}/`；
- 提炼 Request/Response 结构体、HTTP Method、状态码及鉴权要求。

#### 2.3 领域边界与调用链提取（Architecture & Call-Chain 逆向）
- 确定业务领域划分（如 auth、user、order、payment 等）；
- 追踪核心用例（Tracer Flow）的执行路径，产出 Mermaid 调用时序图至 `hs_dev_docs/_07_call_chain/`。

### Step 3：项目统一词典与宏观品味固化
- 扫描现有公共命名，提取实体名词、动词与状态态，生成 `_02_project_word.dict.yaml`，统一词态矩阵（Command 动词原形 / Event 过去分词 / Attribute 时间戳）；
- 若项目包含 UI，提取公共调色板、CSS 变量或 Tailwind 配置，在根目录沉淀基础版 `DESIGN.md`。

### Step 4：四级索引重建与门禁对齐
- 生成各功能域 `.idx` 文件；
- 运行重建命令对齐 SQLite 缓存：
  ```bash
  python3 scripts/idx_manager.py rebuild
  python3 scripts/doc_index_db.py --root . rebuild
  ```
- 运行门禁校验：`python3 scripts/verify_consistency.py --root .` 确保零漂移。

---

## 3. 分级规模与产出边界

| 规模 | 适用场景 | 逆向提取范围 |
|---|---|---|
| **S** | 单模块/单接口接入规范 | 仅逆向涉及的单表、单个 API 接口及该方法调用链，生成局部切片。 |
| **M** | 独立子系统/功能域重建 | 逆向完整业务子域（如支付域），建立该域专属的 DB/API/调用链与三级索引。 |
| **L** | 全量工程纳入治理 | 全项目扫描、提取完整四要素、建立项目词典、全局根索引与 `doc_index.sqlite`。 |
