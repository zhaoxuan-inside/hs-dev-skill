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
| `preferences.yaml` | 同一类事情的用户处理偏好（权威源） |
| `tech_learning/` | 新技术学习笔记（跨项目复用） |
| `learn_and_prefer.md` | 学习/偏好/GitHub 对标协议副本 |

## 初始化

在 Skill 仓库根目录执行（任选当前平台可用的解释器）：

```bash
python scripts/init_hs_global.py
python3 scripts/init_hs_global.py
py -3 scripts/init_hs_global.py
```

查看解析结果：`python scripts/hs_paths.py`
