# 方法类型分类与契约画像指南 (Method Archetypes & Contract Profile)

**何时读**：
- 阶段 3 详细规格设计（编写/更新 `hs_dev_docs/_04_engineering_contract/_04_method_design/`）；
- 阶段 4 上下文装配（Context Pack 中按方法画像物化切片）；
- 阶段 5 编码与测试实现（依据方法属性收窄上下文、定向跑测、维护修改历史）；
- 检索命令：`python scripts/skill_ref_index.py search --scenario 方法设计` 或 `search --q 方法类型`

---

<!-- HS_SECTION_INDEX -->

**按业务装载**：正文已拆成独立文件。先沿用本页公共约束，只打开当前业务/阶段需要的分册；不要顺序读全套。分册独立进行变化检查；迁移后旧的行号/摘要须重新定位，已有签收不得自动迁移。

## 1. 核心思想：“文档定义代码”与 VibeCoding 效能引擎

正文见 [methods/profiles_dependencies.md](methods/profiles_dependencies.md)。

## 2. 七大方法标准类型 (The 7 Method Archetypes)

正文见 [methods/profiles_dependencies.md](methods/profiles_dependencies.md)。

## 3. 方法属性机制（七维画像）

正文见 [methods/profiles_dependencies.md](methods/profiles_dependencies.md)。

## 4. 以本方法为中心的局部依赖拓扑图 (Ego Dependency Graph)

正文见 [methods/profiles_dependencies.md](methods/profiles_dependencies.md)。

## 5. 三段式历史修改记录 (Structured Changelog)

正文见 [methods/profiles_dependencies.md](methods/profiles_dependencies.md)。

## 6. 防方法爆炸与查重选型优先机制 (Method Discovery & Anti-Explosion Gate)

正文见 [methods/discovery_reuse.md](methods/discovery_reuse.md)。

### 6.1 单一天理源（SSOT）与派生轻量索引

正文见 [methods/discovery_reuse.md](methods/discovery_reuse.md)。

### 6.2 编码前的四步决策漏斗 (The 4-Step Decision Funnel)

正文见 [methods/discovery_reuse.md](methods/discovery_reuse.md)。

### 6.3 抗爆炸三大防线原则

正文见 [methods/discovery_reuse.md](methods/discovery_reuse.md)。

## 7. 面向 VibeCoding 的执行守则（降低 Token 与极速反馈）

正文见 [methods/execution_frontend.md](methods/execution_frontend.md)。

## 8. 前端工程化落地与实战映射 (Frontend Architecture Mapping)

正文见 [methods/execution_frontend.md](methods/execution_frontend.md)。

### 前端 7 大分类职责与代码位置清单

正文见 [methods/execution_frontend.md](methods/execution_frontend.md)。

### 前端 VibeCoding 三大纪律：

正文见 [methods/execution_frontend.md](methods/execution_frontend.md)。

### 前端方法文档模板标准：

正文见 [methods/execution_frontend.md](methods/execution_frontend.md)。
