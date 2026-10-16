# hs-dev-skill 全局共享区

跨项目偏好与技术学习目录，**Windows / Linux / macOS** 三端共用。

## 路径

| 平台 | 位置 |
|---|---|
| 解析规则 | `Path.home() / ".hs-dev-skill"` |
| Linux / macOS | `$HOME/.hs-dev-skill/` |
| Windows (cmd) | `%USERPROFILE%\.hs-dev-skill\` |
| Windows (PowerShell) | `$env:USERPROFILE\.hs-dev-skill\` |

## 内容

| 文件/目录 | 用途 |
|---|---|
| `preferences.yaml` | 同一类事情的用户处理偏好（权威源；可含 `tags`） |
| `tech_learning/` | 新技术学习笔记（每条一条索引记录） |
| `tag_synonyms.yaml` | 技术 → 特性标签同义词（如 Nginx ↔ 反向代理） |
| `global_index.sqlite` | 可重建查询缓存（勿手改） |
| `learn_and_prefer.md` | 学习/偏好/GitHub 对标协议副本 |

## 标签怎么写

每条笔记必须有特性标签，用「能力」描述技术，便于检索：

```markdown
- **标签**：`后端`, `组件`, `反向代理`, `正向代理`, `WEB服务器`
```

例：找「反向代理」方案时不必先想起 Nginx：

```bash
python scripts/global_index_db.py search --tag 反向代理
python scripts/global_index_db.py suggest-tags --path tech_learning/nginx_notes.md
python scripts/global_index_db.py rebuild   # 写/改笔记或偏好后
```

## 初始化

在 Skill 仓库根目录执行（任选当前平台可用的解释器）：

```bash
python scripts/init_hs_global.py
python scripts/init_hs_global.py
py -3 scripts/init_hs_global.py
```

查看解析结果：`python scripts/hs_paths.py`
