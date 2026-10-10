# 跨平台支持规范（Windows / Linux / macOS）

本 Skill 与配套脚本必须在 **Windows、Linux、macOS** 三端可用。Agent 写命令、落盘路径、跑门禁时遵循本文，禁止假设用户只在某一 OS 上开发。

---

## 1. 硬性约定

| 项 | 约定 |
|---|---|
| 脚本语言 | Python ≥ 3.8；业务脚本用 `pathlib`，禁止手写仅 POSIX 或仅 Windows 的路径拼接 |
| 全局共享区 | `Path.home() / ".hs-dev-skill"`（三端语义相同） |
| 文本编码 | UTF-8；新建/改写 Markdown、YAML、JSON、JSONL、源码均 UTF-8 |
| 换行 | 仓库内文本以 LF 为准（`.gitattributes` 可约束）；读写内容勿依赖 CRLF |
| 路径分隔 | 文档示例可用 `/`；代码用 `pathlib.Path`；展示 Windows 绝对路径时用该平台实际分隔符 |
| Make | 可选便利入口；**无 make 时必须可用等价 Python 命令**（Windows 常见） |

辅助模块：`scripts/hs_paths.py`（`global_root()`、`platform_id()`、路径展示）。

---

## 2. 全局目录三端写法

解析规则永远是：`pathlib.Path.home() / ".hs-dev-skill"`。

| 平台 | Shell 写法 | 典型解析结果 |
|---|---|---|
| Linux | `$HOME/.hs-dev-skill/` | `/home/<user>/.hs-dev-skill/` |
| macOS | `$HOME/.hs-dev-skill/` | `/Users/<user>/.hs-dev-skill/` |
| Windows (cmd) | `%USERPROFILE%\.hs-dev-skill\` | `C:\Users\<user>\.hs-dev-skill\` |
| Windows (PowerShell) | `$env:USERPROFILE\.hs-dev-skill\` | 同上 |

文档中可用 `~/.hs-dev-skill/` 作简写，但 Agent **读写文件时必须解析为当前 OS 的绝对路径**（先 `Path.home()`），不要把字面量 `~/...` 传给不支持 tilde 展开的 API。

查看当前机解析：

```bash
python scripts/hs_paths.py
# 或
python3 scripts/hs_paths.py
# Windows 若仅有启动器：
py -3 scripts/hs_paths.py
```

---

## 3. Python 启动器（三端）

按顺序尝试，命中即用：

1. `python3`
2. `python`（且版本 ≥ 3.8）
3. Windows：`py -3`

文档命令统一写成：

```text
python scripts/<name>.py ...
```

并注明：Linux/macOS 可用 `python3`；Windows 可用 `py -3`。Makefile 中通过 `PYTHON` 变量覆盖（见根目录 `Makefile`）。

禁止在 Skill 正文里只写死 `python3` 而不给 Windows 替代；也禁止只写 `py -3`。

---

## 4. 常用命令对照

| 动作 | Linux / macOS | Windows (PowerShell) |
|---|---|---|
| 初始化全局区 | `python3 scripts/init_hs_global.py` | `py -3 scripts/init_hs_global.py` |
| 重建全局标签索引 | `python3 scripts/global_index_db.py rebuild` | `py -3 scripts/global_index_db.py rebuild` |
| 按特性标签搜笔记 | `python3 scripts/global_index_db.py search --tag 反向代理` | `py -3 scripts/global_index_db.py search --tag 反向代理` |
| 初始化项目文档 | `python3 scripts/init_hs_dev_docs.py --root .` | `py -3 scripts/init_hs_dev_docs.py --root .` |
| 重建文档索引库 | `python3 scripts/doc_index_db.py --root . rebuild` | `py -3 scripts/doc_index_db.py --root . rebuild` |
| 检索文档（降 Token） | `python3 scripts/doc_index_db.py --root . search --q kw` | `py -3 scripts/doc_index_db.py --root . search --q kw` |
| 跑测试 | `make test` 或 `python3 -m unittest discover -s tests -p "test_*.py"` | `py -3 -m unittest discover -s tests -p "test_*.py"` |
| 一致性门禁 | `python3 scripts/verify_consistency.py --root .` | `py -3 scripts/verify_consistency.py --root .` |
| Make（若已装） | `make init-global` / `make index-rebuild` | 同上（需 make；或直接跑 Python） |

---

## 5. Agent 行为要求

1. **探测 OS**：用 `scripts/hs_paths.py` 的平台标识或等价方式；命令与路径展示匹配当前 OS。
2. **落盘全局偏好/笔记**：始终写入 `Path.home() / ".hs-dev-skill"/...`，三端一致。
3. **Shell 工具**：Windows 优先 PowerShell/cmd 兼容写法；避免依赖仅 bash 才有的语法（如 `&&` 链在旧 PowerShell 可能失败时改用 `;` 或分开执行）。
4. **产品多端目录**：目标产品若含桌面端，继续使用仓库约定的 `windows/`、`linux/`、`mac/` 代码目录与对应选型/架构文档；与「Skill 自身跑在哪」分开。
5. **不把平台差异当成询问闸门事项**：路径、启动器、换行等属通用工程问题，高置信自定，不询问用户。
6. **Git 默认止于本地 commit**：三端均不主动 `git push`；仅当用户明确要求推送时代为执行。

---

## 6. 文档索引库（SQLite）三端约定

| 项 | 约定 |
|---|---|
| 引擎 | 标准库 `sqlite3`（勿依赖仅 Linux 的扩展二进制） |
| FTS | 优先 FTS5；不可用或中文查询时 `LIKE` 回退，保证三端可搜 |
| 路径 | `Path(workspace) / "hs_dev_docs/_00_project/_18_doc_index/doc_index.sqlite"` |
| 输出 | CLI 打印 JSON；内部 path 使用 POSIX 相对路径（`as_posix()`），避免 `\` 污染提示词 |
| 编码 | UTF-8；Windows 控制台经 `hs_paths.ensure_utf8_stdout()` 尽量不乱码 |

语义向量扩展（可选）必须同样走 `pathlib` + 可重建缓存，且不能阻断无 GPU/无网络环境的 FTS/LIKE 主路径。

---

## 7. 验收清单（Skill 可移植性）

- [ ] `init_hs_global.py` 在 Win/Linux/macOS 均能创建全局目录  
- [ ] `preferences.yaml` / `tech_learning/` 路径仅通过 `Path.home()` 解析  
- [ ] `doc_index_db.py rebuild/search/slice` 在三端可用（仅标准库）  
- [ ] `global_index_db.py rebuild/search --tag` 在三端可用（索引 `Path.home()/.hs-dev-skill`）  
- [ ] 无 GNU make 时，全部门禁仍可通过 `python`/`python3`/`py -3` 执行  
- [ ] 文档同时给出 Unix 与 Windows 示例，或使用「`python` + 启动器说明」统一写法  
