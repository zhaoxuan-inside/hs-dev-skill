# 技术学习、偏好记忆与 GitHub 对标协议

本协议与 [置信度决策](confidence_decision.md) 配套：通过**学新技术、记用户偏好、对标高星成熟方案**，提高 **IMPLEMENT 期**自主决策置信度，**降低实现期询问频率**并改善落地质量。  
注意：**不能**用本协议替代 DESIGN 期对产品语义的多问澄清；领域厚规则优先走 [rule_library](rule_library.md) / `rule_fetch`，学习笔记用于偏好与选型沉淀。

适用于：新建项目、优化旧项目、引入新技术、UI/交互描述模糊、选型与架构分叉。  
配合生命周期：**产品需求冻结前不做选型结论**；学习/对标用于抬高置信，不能替代未闭合的产品决策。

---

## 0. 全局共享根目录（强制 · Windows / Linux / macOS）

偏好账本与技术学习笔记必须落在**用户主目录下的全局目录**，供所有项目共用，**禁止**写进某个项目的 `hs_dev_docs/`（项目内只引用结论到 ADR/选型，不存权威偏好）。

**唯一解析规则**：`pathlib.Path.home() / ".hs-dev-skill"`（三端相同）。跨平台路径与命令细则见 [cross_platform.md](cross_platform.md)。

| 平台 | Shell 写法 |
|---|---|
| Linux | `$HOME/.hs-dev-skill/` |
| macOS | `$HOME/.hs-dev-skill/` |
| Windows (cmd) | `%USERPROFILE%\.hs-dev-skill\` |
| Windows (PowerShell) | `$env:USERPROFILE\.hs-dev-skill\` |
| 代码 | `Path.home() / ".hs-dev-skill"` |

目录结构（`~` 仅为简写，读写须解析为绝对路径）：

```text
~/.hs-dev-skill/
├── README.md
├── learn_and_prefer.md
├── preferences.yaml
├── tag_synonyms.yaml          # 技术 → 特性标签同义词（可扩展）
├── global_index.sqlite        # 可重建查询缓存（勿手改；默认不提交）
└── tech_learning/
    └── {tech_slug}_notes.md   # 每条笔记含「标签」元数据
```

- **首次使用 / 目录缺失**：`python scripts/init_hs_global.py`（Linux/macOS 可用 `python3`；Windows 可用 `py -3`）。
- **Agent 每次决策前**：优先用全局索引检索，再打开命中文件——**禁止**整目录通读 `tech_learning/`。
- 打印当前机路径：`python scripts/hs_paths.py`。

### 0.1 全局标签索引（降 Token）

| 项 | 约定 |
|---|---|
| CLI | `python scripts/global_index_db.py`（`--global-root` 可覆盖，默认 `Path.home()/.hs-dev-skill`） |
| 重建 | `... rebuild`（写/改笔记或偏好后必须执行；`init_hs_global` 结束时自动 rebuild） |
| 按标签搜 | `... search --tag 反向代理`（同义词展开，如命中 Nginx 笔记） |
| 按关键词 | `... search --q nginx` 或 `--q 缓存` |
| 列标签 | `... tags` |
| 标签来源 | ① 笔记显式 `- **标签**：...` ② `tag_synonyms.yaml` 按 slug 展开 ③ 正文/标题特性词自动抽取 ④ 偏好项 `tags` |
| 建议标签 | `... suggest-tags --path <note.md>`（写出前可预览） |

**写笔记纪律**：每条学习笔记必须填写特性标签（例：Nginx → `后端`, `组件`, `反向代理`, `正向代理`, `WEB服务器`），使「用能力找技术」而不必先想准技术名。新概念可追加到 `tag_synonyms.yaml`。rebuild 时即使用户漏写标签，也会尝试从正文抽取同义词表中的特性词并展开。

---

## 1. 强制时机

在阶段 0 对齐之后、阶段 1 选型与阶段 2/3 设计之前（以及实现期遇到新技术时），Agent 必须自检：

| 触发条件 | 必须动作 |
|---|---|
| 栈中出现本会话尚未掌握、或全局学习笔记中不存在/过期的技术 | **技术学习**（§2）并写入 `~/.hs-dev-skill/tech_learning/` |
| 用户对某类问题给出过明确选择或纠偏 | **偏好记账**（§3）写入全局 `preferences.yaml`，同类优先复用 |
| 新技术 / UI / 交互 / 视觉 等描述模糊，或缺少可执行规格 | **GitHub 高星对标**（§4）；UI 视觉优先 [design_md](design_md.md) + awesome-design-md |
| 优化旧项目且触及陌生模块或新依赖 | 先学再改：读代码 + 学依赖 + 查全局偏好账本 |

禁止：对新技术「凭印象硬写」；禁止在未读全局偏好账本时反复询问同类问题；禁止在模糊 UI/新技术需求上无对标凭空臆造。

---

## 2. 技术学习（New Tech Learning）

### 2.1 学习目标（够用即可，禁止百科式堆砌）

1. 核心概念与适用边界  
2. 官方推荐的最小可行用法  
3. 常见集成方式（目录、依赖、错误处理、可观测）  
4. 常见坑与反模式  
5. 测试策略  

笔记中可附「当前项目适配要点」，但笔记本体放在全局，供后续项目复用。

### 2.2 信息源优先级

1. 官方文档 / RFC / 语言标准  
2. 全局已有学习笔记与偏好  
3. 当前项目代码与 ADR  
4. GitHub 高星成熟项目（§4）  
5. 权威博客或发布说明（注明日期与版本）

### 2.3 落盘位置

`~/.hs-dev-skill/tech_learning/{tech_slug}_notes.md`  
模板：`resources/templates/hs_global/tech_learning_notes.md`

落盘时**必须**填写 `- **标签**：...`（特性标签，非仅技术名）。  
落盘后：`python scripts/global_index_db.py rebuild`。  
决策检索：`python scripts/global_index_db.py search --tag <特性>` 或 `--q <技术名>`，只打开返回的 `abs_path`。

学习完成后重估置信度；仍满足询问闸门四条件再问，否则自主推进。

---

## 3. 用户偏好记忆（Preference Memory）

### 3.1 目标

把用户对**同一类事情**的处理方式沉淀为**跨项目**可复用规则 → 少问、更贴习惯。

### 3.2 「同一类事情」粒度示例

- UI：信息密度、动效、卡片、色调、文案语气  
- API：错误码、分页、幂等、版本策略  
- 数据：软删、审计字段、迁移节奏  
- 工程：测试深度、日志、提交粒度、是否引入新中间件  
- 产品：默认降级、是否先做 MVP  

### 3.3 落盘位置

`~/.hs-dev-skill/preferences.yaml`（权威源）  
模板：`resources/templates/hs_global/preferences.yaml`

决策前：全局偏好命中 → 视为资料已提及（询问闸门条件 C 不成立），**不得再问同类问题**（除非用户当场改口，并回写全局账本）。

项目内 `_01_dev_rule/`、ADR 仅表达**本项目特例**；与全局偏好冲突时见 §3.5。

### 3.4 记账触发（必须落盘，禁止只留在对话里）

更新全局 `preferences.yaml`（增量 Edit，注明 `updated_at` 与 `source`）：

1. 用户在询问闸门中做出选择  
2. 用户主动纠偏（「以后都按 X」或等价）  
3. 连续两次以上对同类点相同倾向  
4. 从 GitHub 对标中高置信采纳、且可跨项目复用的风格  

字段建议：`category`、`preference`、`rationale`、`source`、`examples`、`updated_at`、`tags`。

### 3.5 冲突裁决

1. 用户当场明确指令  
2. **全局** `~/.hs-dev-skill/preferences.yaml`  
3. 当前项目明确 ADR / `_01_dev_rule`（仅约束本项目）  
4. Skill 通用规范与高星对标结论  
5. Agent 习惯（最低，禁止）

---

## 4. GitHub 高星对标（Fuzzy → Mature Solutions）

### 4.1 何时必须检索

新技术落地、UI/UX、缺少先例的架构拼装等描述模糊时，**优先**检索 GitHub 高 Star、仍维护的成熟项目，再设计。对标后置信拉开则**不询问**。

### 4.2 检索与筛选

1. 关键词：技术名 + 场景  
2. Stars 高、近期维护、文档/示例完整、许可证可接受  
3. 至少对比 **2** 个候选（或旗舰 + 官方示例）  
4. **学模式，不整仓抄袭**；遵守许可证  
5. 手段：`gh search repos`、WebSearch（`site:github.com`）等  

### 4.3 落盘与引用

- **可复用模式 / 技术要点** → 全局 `tech_learning/` 与必要时 `preferences.yaml`  
- **本项目选型结论** → 项目 `_02_tech_select/`、ADR、PRD（引用全局笔记路径与对标仓库）  

---

## 5. 与置信度决策的衔接

0. `python scripts/global_index_db.py search --tag/--q ...`（或等价打开命中项）；偏好命中则按偏好做，不询问  
1. 新技术或模糊 UI/技术 → §2 / §4，读写全局 `tech_learning/`（先索引后切片，禁止整树读）  
2. 重估置信度  
3. 再套用询问闸门四条件  

目标态：**跨项目复用偏好与学习成果，问得更少，依据更硬，检索更便宜**。
