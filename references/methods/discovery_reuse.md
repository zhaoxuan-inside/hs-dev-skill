# 6. 防方法爆炸与查重选型优先机制 (Method Discovery & Anti-Explosion Gate)

**何时读**：处理6. 防方法爆炸与查重选型优先机制 (Method Discovery & Anti-Explosion Gate)时；先沿用[入口公共约束](../method_archetypes.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 6. 防方法爆炸与查重选型优先机制 (Method Discovery & Anti-Explosion Gate)

在 AI 辅助编程（VibeCoding）中，大模型自回归生成的本能往往是**“无脑新建函数”**而不是“选择/复用已有方法”，导致项目中充斥着大量功能重合的影子函数（如 `formatDate2`、`parseMobileUtil`、`checkUserHelper`），造成灾难性的**方法爆炸（Method Explosion）**。

若试图将全库已有函数直接塞入 Prompt，又会引发严重的 **Prompt 膨胀与上下文稀释（Attention Dilution）**。

本 Skill 确立**“写前检索、查重优于新建、单一天理源派生轻量索引”**的抗爆炸防护体系：

### 6.1 单一天理源（SSOT）与派生轻量索引
- **严禁双重维护文档**：`hs_dev_docs/_04_engineering_contract/_04_method_design/` 是全仓方法契约的**单一天理源**，不需要也不允许额外人工维护第二份方法清单；
- **自动化物化索引（Materialized Cache）**：`scripts/doc_index_db.py` 会自动扫描解析 `_04_engineering_contract/_04_method_design/*.md` 中的方法名、分类画像（archetype）、核心功能描述与物理代码坐标，物化为本地 SQLite `methods` 表；
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
  └── D. 确认全新通用领域逻辑 ──► 获准新建；必须先在 _04_engineering_contract/_04_method_design 登记画像
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
