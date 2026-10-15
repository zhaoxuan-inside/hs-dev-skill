# Token 预算与渐进装载纪律（跨平台）

目标：在 **Windows / Linux / macOS** 上，用「查询 → 切片 → 物化 context_pack」替代整树阅读，降低上下文消耗，且不削弱产品冻结门禁与一致性。

权威源仍是 Markdown + JSONL `.idx`；**SQLite 仅为可重建查询缓存**。

---

## 1. 合法装载顺序（强制）

```text
1) 读主 SKILL.md 路由，选择一个过程子 Skill 与触达功能子 Skill；不加载无关入口
2) 装载门闩 load_latch L0～L2：开场确认（新需求）→ change_size+work_mode → skill_ref_index search 或 _index 一行 → 核心 1 份详规 + 阶段满配链附属（合计 ≤5 份）
3) 读 right_sizing.md（若尚未作为那 1 份打开）并写入分级（S 路径此后少读 lifecycle）
4) 按「路径/阶段 → references」表按需再开（已读不重复；仍遵守「同时打开详规宜少」）
5) UI/API 深化：rule_fetch search/resolve（每任务 ≤2 source id；github_tree 必须 --rule）
6) python scripts/doc_index_db.py search/get/slice 定位项目文档 path
7) 只 Read/slice 命中行段 → 物化 context_pack
8) 实现期默认只读 context_pack + 正在改的代码
```

禁止：

- 未过分级/门闩就加载满配 lifecycle 全文 + 多份 craft 文档
- 整读 `hs_dev_docs` 或某一功能域下全部 `.md`
- 整读大型 `.idx` 后手写改回（改索引走 `idx_manager`）
- context_pack 只写路径、实现时再打开全文设计
- 本会话已读过的 `references/*.md` 再读一遍
- 整目录通读 `references/`（用 `_index.md` 或 `skill_ref_index search`）
- 预拉 / 整读远程规则包（Vercel AGENTS.md 等）；只 resolve 命中 id / 单条 rule

---

## 2. 路径/阶段 → references 挂载表（按需，勿一次全读）

本表是子 Skill 内的详规路由，不是要求主 Skill 同时加载所有文件。入口与归属以 resources/skill_routes.json 为准。

| 当前 | 必读（每会话一次） | 可选 |
|---|---|---|
| **任何需求开始** | `load_latch.md`（极短）+ `right_sizing.md` | `_index.md` 或 `skill_ref_index search` |
| S 快路径 | （无需 lifecycle 全文） | `frontend_craft` / `api_engineering`（仅当改 UI/API） |
| 任意决策分叉 / 定 work_mode | `confidence_decision.md` | `learn_and_prefer.md` |
| M/L 阶段 0 | lifecycle 阶段 0 节 | `learn_and_prefer`（模糊 UI） |
| L 阶段 1 | lifecycle 阶段 1 | `learn_and_prefer` |
| L 阶段 2 | lifecycle 阶段 2 | — |
| M/L 阶段 3 | lifecycle 阶段 3；改方法时 `six_tuple_runtime` / `method_archetypes` | 本地 craft；深化用 `rule_library` + `rule_fetch` |
| 阶段 4 | 本文 + 必要时 `four_level_routing` | `task_state_machine` |
| 阶段 5 | （已读过的不重复） | craft / `rule_fetch resolve --rule …`（按触达） |
| 阶段 6 | `quality_gates.md` | — |
| 路径/命令 | `cross_platform.md` | — |
| 规格百科 | 仅争议时 `spec_v2_4.md` 对应节 | 禁止开局通读 |

`spec_v2_4.md` 体积大：**禁止**作为默认开局读物。S 会话若加载超过「right_sizing + 至多一份 craft + 必要代码」视为 Token 违规。远程规则每次任务最多 **2** 个 source id。

---

## 3. SQLite 底层真理与全维度索引（`doc_index_db.py`）

| 项 | 约定 |
|---|---|
| 路径 | `hs_dev_docs/_00_project_foundation/_05_doc_index/doc_index.sqlite`（`pathlib`，三端） |
| 依赖 | 仅标准库 `sqlite3`；FTS5 优先，失败或中文查询回退 `LIKE` |
| 重建 | `python scripts/doc_index_db.py --root . rebuild` |
| 功能搜索 | `... feature-search --q <特性关键词>` → 定位 PRD 与功能 ID（免读 PRD 全文） |
| 原型搜索 | `... page-search --q <页面关键词>` → 定位线框图与路由（免读 UI 全文） |
| 模式搜索 | `... pattern-search --q <设计模式>` → 定位协同群与安全护栏（防破坏） |
| 数据搜索 | `... schema-search --q <表名>` → 定位字段摘要与迁移 DDL 脚本 |
| 依赖拓扑 | `... dep-graph --symbol <方法名>` → 输出局部微依赖图与爆炸半径 |
| 方法查重 | `... method-search --q <业务意图>` → 意图重合 ≥80% 强制复用（防方法爆炸） |
| 符号切片 | `... symbol-slice --name <方法/类名>` → 精准提取代码片段（省 90% Token） |
| 用例检索 | `... test-search --q <关键词>` → 瞬间返回单跑命令（如 `pytest ...`） |
| 审计检索 | `... audit-search --since <时间>` → 时间线与影响文件精准检索（免读 JSONL） |
| 文档检索 | `... search --q <kw> [--domain ...] [--limit 8]` → JSON（path + summary） |
| 切片阅读 | `... slice --path <rel> --start N --end M` → 行级 JSON |
| 同步 | 批量改文档/索引后 rebuild；`init_hs_dev_docs` 结束时自动 rebuild |
| Git | `*.sqlite` 默认不提交（可重建）；门禁缺失仅 warning |

语义检索（embedding / SemanticGrip 类）为**可选二级召回**：候选必须回落到 `path` + `digest`，不得替代结构化索引。


---

## 3b. 全局偏好 / 学习笔记索引（`global_index_db.py`）

| 项 | 约定 |
|---|---|
| 路径 | `Path.home()/.hs-dev-skill/global_index.sqlite` |
| 条目 | 每条 `tech_learning/*_notes.md` + 每条 `preferences.yaml` preference |
| 标签 | 显式标签 + `tag_synonyms.yaml` 展开 + 正文特性抽取（例：反向代理 → Nginx 组） |
| 建议 | `... suggest-tags --path tech_learning/xxx_notes.md` |
| 检索 | `search --tag 反向代理` / `search --q nginx` → 只打开命中 path |
| 重建 | 写笔记/改偏好/`init_hs_global` 后 `rebuild` |

禁止决策前整读 `preferences.yaml` 全文或 `tech_learning/` 目录；先索引再打开。

---

## 4. context_pack 物化门禁

进入阶段 5 前，当前任务的 `_00_context_pack.md` 应包含：

1. 需求/DoD 原文片段（非空）  
2. 相关 DB/接口/六元组签名原文片段  
3. 调用链或契约关键片段  
4. 本节「查询轨迹」中的 path 列表  

若仅有路径占位，Agent 必须先 `search`/`slice` 补齐再编码。

---

## 5. 三端命令

```bash
# Linux/macOS — Skill references 场景路由（勿通读 references/）
python3 scripts/skill_ref_index.py rebuild
python3 scripts/skill_ref_index.py search --q "幂等" --limit 5

# Linux/macOS — 领域规则（本地高频 + 远程单条）
python3 scripts/rule_fetch.py search --q React
python3 scripts/rule_fetch.py resolve --id vercel.react-rules --rule async-parallel

# Linux/macOS — 项目文档
python3 scripts/doc_index_db.py --root . rebuild
python3 scripts/doc_index_db.py --root . search --q "支付 补偿" --limit 8

# Linux/macOS — 全局偏好/学习笔记（标签加速）
python3 scripts/global_index_db.py rebuild
python3 scripts/global_index_db.py search --tag 反向代理

# Windows
py -3 scripts/skill_ref_index.py search --scenario UI
py -3 scripts/rule_fetch.py resolve --id local.api.core
py -3 scripts/doc_index_db.py --root . slice --path hs_dev_docs/_02_feature_spec/_01_human_prd/xxx_prd.md --start 1 --end 40
py -3 scripts/global_index_db.py search --q nginx --kind note
```

统一写法：`python scripts/...`，并按 [`cross_platform.md`](cross_platform.md) 选择启动器。  
Skill 索引缓存：`<skill_root>/.hs_cache/skill_ref.sqlite`（可重建，默认不提交）。  
远程规则缓存：`~/.hs-dev-skill/rule_cache/`（可重建）。

---

## 6. AST 符号骨架与命令行日志降噪（进阶省 Token）

1. **代码探索优先骨架化**：探索未知代码库或定位函数时，严禁直接 `view_file` 整读数百行大文件。必须先执行：
   ```bash
   python scripts/code_skeleton.py --path <file_or_dir>
   ```
   借助 AST 提取模块签名、类、方法及精确行号范围（实现 85%~95% Token 压缩），仅根据命中的精确行段按需切片查看。
2. **测试与命令日志降噪截断**：避免 `make test` 或构建工具打印数百行无关控制台输出污染上下文：
   ```bash
   python scripts/log_filter.py --cmd "make test"
   ```
   成功用例自动提炼为单行状态，失败用例仅提取核心错误帧与断言，消除 90%+ 噪音。

