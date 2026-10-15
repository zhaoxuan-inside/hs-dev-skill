# 代码理解与架构探查指南（Code Exploration & Comprehension）

**何时读**：纯只读提问、代码逻辑理解、业务流向追溯、架构方案评估或排查困惑时；每会话最多一次。

---

## 1. 核心定位与原则：只读免交付、索引优先

当用户意图为**代码理解、逻辑咨询、架构答疑**时，本 Skill 必须快速响应，**严禁启动重型交付流水线**。  
核心原则：
1. **纯只读免交付（Read-Only & Zero Artifact Overhead）**：严禁创建任务三文件（`task_manager`）、严禁落盘 PRD、严禁强制运行 `verify_consistency` 或发起本地 Commit；
2. **索引加速与精准切片（Index-First Progressive Slicing）**：杜绝盲目大段读取代码，优先利用 `doc_index_db`、四级索引与 AST 符号表切片，守住 Token 预算；
3. **结构化认知交付（Structured Mental Model）**：回答不仅要解释代码，必须结合业务场景提炼**数据流向、状态机、时序图（Mermaid）或边界约束**。

---

## 2. 代码理解执行三步法

```text
[Step 1: 语义检索与切片定位] ──────► [Step 2: 局部依赖与调用链还原] ──────► [Step 3: 结构化解答与图谱输出]
     doc_index_db / 四级索引               追踪核心逻辑与数据流转                Mermaid / 状态机 / 边界解答
```

### Step 1：语义检索与切片定位（Progressive Slicing）
- 依据用户疑问关键词，优先运行工程索引（免整盘全量通读）：
  ```bash
  # 查找代码符号、类或函数
  python3 scripts/doc_index_db.py symbol-search --q "<疑问关键词>"
  # 直接提取符号代码切片（省 90% Token，自动按 AST 动态计算准确行号）
  python3 scripts/doc_index_db.py symbol-slice --name "<目标符号名>"
  # 若涉及需求或数据模式，查 feature-search 或 schema-search
  python3 scripts/doc_index_db.py feature-search --q "<业务意图>"
  ```
- 锁定目标文件后，使用局部切片读取（`symbol-slice` 或 `doc_index_db slice`），严禁大文件全量通读。

### Step 2：局部依赖与调用链还原（Call-Chain Trace）
- 直接使用方法依赖微图（Ego Graph）自动生成调用拓扑与爆炸半径：
  ```bash
  python3 scripts/doc_index_db.py dep-graph --symbol "<涉事类名.方法名>"
  ```
- 追溯核心方法的生命周期（直接复用生成的 Mermaid 关系）：
  - **入口（Callers）**：API 控制器、事件消费者或上游业务方；
  - **编排**：领域服务、深模块核心逻辑；
  - **出口（Callees）**：数据库持久化、外部 RPC 或下游子方法；
- 识别关键状态变化与防御性分支。

### Step 3：结构化解答与图谱输出（Structured Delivery）
- 输出给用户的解释应当包含：
  1. **直达结论**：用 1~2 句话直接回答用户的核心疑问；
  2. **时序或流转图**：采用 Mermaid 时序图（`sequenceDiagram`）或状态图（`stateDiagram-v2`）直观呈现运转机理；
  3. **关键代码切片与行号引用**：精准指向 `path#Lxx-Lyy`；
  4. **边界与潜在风险提醒**：若发现代码中存在隐患（如并发竞态、未捕获异常、性能瓶颈），主动做出工程提示。
- **完结退出**：解答完毕后即刻完成，不留垃圾文件，保持工作区绝对干净。
