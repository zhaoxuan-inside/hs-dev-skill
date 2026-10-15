# 已有项目反向重建（Reverse Engineering）与规范接入指南

**何时读**：接手无 `hs_dev_docs` 的遗留/存量项目（Brownfield），或需要对已有代码进行架构还原、Schema 逆向与标准知识库重建时；每会话最多一次。

---

## 1. 核心目标与人机协同逆向哲学

已有存量项目往往存在文档缺失、隐式假设未记录、代码坏味道散落等问题。  
**纯自动化脚本只能逆向提取出“物理实现事实”（代码、表结构、路由），无法凭空推导系统的“业务第一因、领域边界、统一词典与隐式不变式”。**

反向重建的核心目标是：**在不破坏现有系统运行态的前提下，通过「代码资产静态逆向 + 开发者介入定界补齐」双阶段协同，逆向建立单一事实源与两级 7 大域文档体系，构建四级渐进索引与机器执行契约，使存量项目平滑具备本 Skill 的高质量研发与治理能力。**

### 逆向三原则
1. **代码即事实（Code as Ground Truth）**：以运行态代码与数据库 DDL/迁移文件为第一准绳，杜绝脑补设计；
2. **非侵入式探测（Non-Invasive Discovery）**：逆向分析阶段禁止改动业务代码，仅在 `hs_dev_docs/` 生成规范文档骨架与索引文件；
3. **开发者介入定界（Developer Intervention Required）**：涉及业务领域边界、术语歧义消解、产品愿景与不变式确认，必须由开发者介入拍板定界，严禁 Agent 单方面臆断。

---

## 2. 逆向重建三阶段标准流（代码逆向 + 开发者介入 + 索引体系编译）

```text
┌─────────────────────────────────┐      ┌──────────────────────────────────┐      ┌─────────────────────────────────┐
│   阶段一：代码资产静态逆向       │ ──►  │   阶段二：开发者介入定界补齐     │ ──►  │   阶段三：全景索引编译与纳管    │
│  (依赖扫描 / DB / API / 时序拓扑) │      │ (领域定界 / 统一词典 / 愿景与规则) │      │ (四级索引 / doc-guide / 门禁)   │
└─────────────────────────────────┘      └──────────────────────────────────┘      └─────────────────────────────────┘
```

### 阶段一：代码资产静态逆向提取（Agent 自动化）

0. **【前置】与现有团队/开发者对齐（防逆向方向返工）**：静态扫描**之前**，先与现有团队/开发者盘底既有约束（部署环境/合规/遗留依赖/不可动模块）、已知技术债与坑（绕过的校验、特殊魔改、手写 SQL）、既有术语黑话，并确认逆向的**优先域与验收口径**（可复用 [`opening_alignment.md`](opening_alignment.md) O1/O3 结构）。避免按错误理解全量逆向后才发现方向不对。

1. **代码库资产扫描与技术栈基线锁定**：
   - 运行工程检测，分析包依赖（如 `package.json`、`go.mod`、`requirements.txt`、`pom.xml`、`Cargo.toml`）；
   - 判定单体、分层微服务、还是 Monorepo（若包含多端，检查 `apps/` 与 `packages/` 结构）；
   - 在 `hs_dev_docs/_00_project_foundation/_03_decision_record/ADR_001_tech_stack_baseline.md` 固化当前技术栈基线，并在顶部置顶 `[VIBE_CONTRACT]` 契约块。

2. **数据库与存储实体（DB Schema 逆向）**：
   - 扫描 ORM 实体（TypeORM、Prisma、SQLAlchemy、GORM、Hibernate）或 `migrations/` 目录；
   - 将物理表结构与字段映射抽取至 `hs_dev_docs/_04_engineering_contract/_01_db_schema/`；
   - 记录核心表字段约束、主外键关系及枚举值，禁止遗漏 `created_at`/`updated_at` 命名风格差异。

3. **接口契约提取（API Interface 逆向）**：
   - 扫描路由注册中心（Controller、Router、gRPC Proto、GraphQL Schema）；
   - 按业务模块归类输出至 `hs_dev_docs/_04_engineering_contract/_02_interface_design/{module}/`；
   - 提炼 Request/Response 结构体、HTTP Method、状态码及鉴权要求。

4. **核心调用链与时序拓扑提取（Call-Chain 逆向）**：
   - 追踪核心端到端用例（Tracer Flow）的执行路径；
   - 产出 Mermaid 调用时序图至 `hs_dev_docs/_04_engineering_contract/_05_call_chain/`。

---

### 阶段二：开发者介入定界与文档体系补全（开发者协同核心）

自动提取的代码契约仅是物理骨架，**必须由开发者协同完成以下 4 项人工定界与补齐**：

1. **【开发者介入 1】业务领域与限界上下文定界（Bounded Contexts）**：
   - Agent 列出逆向扫描出的模块列表与调用依赖；
   - 开发者审定并划定清晰的领域边界（如核心域、支撑域、通用域），避免技术实现造成的混淆；
   - 成果沉淀至 `hs_dev_docs/_03_architecture_design/_01_system_architecture/`。

2. **【开发者介入 2】统一术语词典审定与裁定（Ubiquitous Language）**：
   - Agent 提取现有代码公共命名（实体名词、动词操作与状态字段）；
   - **开发者逐项核对并消除黑话、近义词与歧义**，严格确立 Command（动词原形）、Event（过去分词）、Attribute（时间戳 `_at`）词态矩阵；
   - 固化为全系统唯一事实源：`hs_dev_docs/_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml`。

3. **【开发者介入 3】产品愿景与宏观品味宪章补全（Vision & Taste）**：
   - 开发者阐述或确认系统的商业目标与业务第一因，沉淀至 `hs_dev_docs/_01_product_vision/`；
   - 若项目含 UI 前端，从既有代码提取公共调色板、CSS 变量并在根目录固化 `DESIGN.md`，归档至 `hs_dev_docs/_01_product_vision/_01_design_charter/`。

4. **【开发者介入 4】隐式业务规则与不变式补全（Business Invariants）**：
   - 将代码中散落的校验、硬编码分支与防御性断言提升为业务级不变式（Invariants）；
   - 补齐人类 PRD（`hs_dev_docs/_02_feature_spec/_01_human_prd/`）与机器契约（`hs_dev_docs/_02_feature_spec/_02_vibe_spec/`）。

---

### 阶段三：全景索引体系编译、阅读罗盘刷新与一致性纳管（系统收敛）

完成人机协同补齐后，必须执行标准自愈流水线，构建统一的文档索引大脑：

1. **四级索引生成**：为各功能子域生成权威 `.idx` 文件；
2. **SQLite 倒排索引编译**：
   ```bash
   python scripts/idx_manager.py rebuild
   python scripts/doc_index_db.py --root . rebuild
   ```
3. **全局文档阅读罗盘生成**：
   ```bash
   python scripts/doc_index_db.py --root . generate-guide
   # 或运行 make doc-guide
   ```
   自动生成置顶 `[VIBE_CONTRACT]` 机器索引契约与 7 大域直接索引相对链接表的 `hs_dev_docs/README.md`。
4. **一致性门禁严格核验**：
   ```bash
   python scripts/verify_consistency.py --root . --strict
   ```
   确保代码、契约与 `.idx` 零漂移。门禁通过后，存量项目正式纳管，具备执行后续 BUILD / FIX / REFACTOR 的全量能力。

---

## 3. 分级规模与产出边界

| 规模 | 适用场景 | 逆向与补齐范围 | 开发者介入重点 |
|---|---|---|---|
| **S** | 单模块/局部接口接入规范 | 仅逆向涉及的单表、单个 API 接口及该方法调用链，生成局部切片。 | 确认接口语义与该方法的命名术语。 |
| **M** | 独立子系统/功能域重建 | 逆向完整业务子域（如支付域），建立该域专属的 DB/API/调用链与三级索引。 | 划定子域边界、裁定子域术语词典、确认子域业务规则。 |
| **L** | 全量工程纳入治理 | 全项目扫描、提取完整四要素、建立项目词典、全局根索引与 `doc_index.sqlite`。 | 全局领域定界、词典全量裁定、确立 `DESIGN.md`、签署纳管冻结。 |
