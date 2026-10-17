## 5. Agent 协同与防漂移治理铁律 (Guardrails & Anti-Drift Policy)

1. **统一语言与单一事实源 (Ubiquitous Language)**：
   所有业务实体、字段命名、事件名称必须与 [`_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml`](./_00_project_foundation/_02_dictionary/_02_project_word.dict.yaml) 保持绝对一致。严禁发明近义词或裸字符串。
2. **符号锚点防漂移 (Symbol Anchor)**：
   设计文档和任务包中绝对禁止硬编码绝对物理代码行号。必须使用 `Symbol Anchor`（如 `OrderService.createOrder#validation`），由底层的 AST 符号切片引擎动态求值行号。
3. **机器契约优先 (Machine Contract First)**：
   AI 编码与装配时，优先读取各文档顶部带有 `[VIBE_CONTRACT]` 标记的切片区块（顶部 [VIBE_CONTRACT] 至下一同级标题），杜绝下半部冗长的人类背景论证挤占 Token。
4. **索引自动同步机制 (Self-Healing Index)**：
   批量新增或更新设计文档后，必须执行以下指令保证权威 `.idx` 与 SQLite 缓存同步：
   ```bash
   python scripts/doc_index_db.py --root . rebuild
   ```
