# 多语言代码开发规范与静态检查门禁指南 (Multi-Language Coding Standards & Quality Gates)

**何时读**：
- 阶段 1 技术选型后确定语言与 Linter 规范；
- 阶段 3 详细设计中编写跨语言接口签名与异常体系；
- 阶段 5 编码与测试实现（编写 Go、Python、Rust、Java/Kotlin、TypeScript/Vue/React 等多语言代码）；
- 提交前排查消除 Linter 告警与代码坏味道；
- 检索命令：`python scripts/skill_ref_index.py search --scenario 开发规范` 或 `search --q 语言规范`

---

<!-- HS_SECTION_INDEX -->

**按业务装载**：正文已拆成独立文件。先沿用本页公共约束，只打开当前业务/阶段需要的分册；不要顺序读全套。分册独立进行变化检查；迁移后旧的行号/摘要须重新定位，已有签收不得自动迁移。

## 1. 核心理念：跨语言三层防护体系

正文见 [coding/core_quality.md](coding/core_quality.md)。

## 2. 多语言静态检测与 Linter 门禁矩阵表

正文见 [coding/core_quality.md](coding/core_quality.md)。

## 3. 跨语言零容忍代码坏味道清单 (Zero-Tolerance Code Smells)

正文见 [coding/core_quality.md](coding/core_quality.md)。

### 3.1 异常与错误处理 (Error Handling)

正文见 [coding/core_quality.md](coding/core_quality.md)。

### 3.2 并发、异步与资源生命周期 (Concurrency & Resources)

正文见 [coding/core_quality.md](coding/core_quality.md)。

### 3.3 安全与防注入 (Security by Default)

正文见 [coding/core_quality.md](coding/core_quality.md)。

### 3.4 命名统一性、词态矩阵与单一事实源 (Ubiquitous Language & Naming Invariants)

正文见 [coding/core_quality.md](coding/core_quality.md)。

### 3.5 方法爆炸与影子函数禁令 (Anti-Method Explosion & Shadow Functions)

正文见 [coding/core_quality.md](coding/core_quality.md)。

## 4. 六元组与方法分类在主流语言中的实现范式 (Polyglot Six-Tuple)

正文见 [coding/go.md](coding/go.md)。

### 4.1 Go 语言范式

正文见 [coding/go.md](coding/go.md)。

### 4.2 Python 语言范式

正文见 [coding/python.md](coding/python.md)。

### 4.3 TypeScript 范式

正文见 [coding/typescript_rules.md](coding/typescript_rules.md)。

## 5. 语言规则库的检索与动态装载

正文见 [coding/typescript_rules.md](coding/typescript_rules.md)。
