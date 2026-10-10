# 领域规则库协议（本地高频 + 远程按需）

**何时读**：改 UI/API/架构且本地 craft 不够用、或要按社区规则名深挖时；每会话最多一次。

目标：本地只保留**高频必守**；范式选型 + 按档架构（ciembor / wshobson / FSD）、品牌 DESIGN.md、Vercel / Anthropic / Addy / anti-slop 等**远程 resolve + 切片**，避免把全文灌进上下文。

目录：[`resources/rule_sources.yaml`](../resources/rule_sources.yaml)  
CLI：`python scripts/rule_fetch.py`（见 §2）

---

## 1. 装载顺序（强制）

```text
1) 读本地 craft 一份：dev_paradigm /（若含 DDD）ddd_design / backend_arch / frontend_arch / design_md / frontend_craft / api_engineering（已读不重复）
2) 仍不够 → rule_fetch.py search --q <场景>
3) resolve --id <source> [--rule <单条名>]  （每任务最多 2 个 source id）
4) 优先 search 命中行段 / 单条 rule 文件；禁止整读远程 AGENTS / 百 KB README
```

网络失败：沿用本地 craft + 已缓存文件；可用 WebFetch 拉同一 raw URL，结果写入 `~/.hs-dev-skill/rule_cache/` 后继续。

---

## 2. CLI

```bash
python scripts/rule_fetch.py list
python scripts/rule_fetch.py search --q 幂等 --limit 5
python scripts/rule_fetch.py resolve --id local.dev.paradigm
python scripts/rule_fetch.py resolve --id local.ddd.design          # 仅 DDD 档
python scripts/rule_fetch.py resolve --id local.frontend.arch
python scripts/rule_fetch.py resolve --id local.backend.arch
python scripts/rule_fetch.py resolve --id wshobson.architecture-patterns
python scripts/rule_fetch.py resolve --id fsd.skill
python scripts/rule_fetch.py resolve --id muthub.c4designer
python scripts/rule_fetch.py resolve --id local.design.md
python scripts/rule_fetch.py resolve --id antislop.core
python scripts/rule_fetch.py search-cache --q waterfall --limit 8
```

| 命令 | 作用 |
|---|---|
| `list` | 目录摘要（无网络） |
| `search` | 按 tags/when/id 搜目录 |
| `resolve` | 确保本地可读：local 直接 path；remote 拉取/命中缓存；`github_tree` 须 `--rule` |
| `fetch` | 强制重新下载 |
| `search-cache` | 在已缓存正文里按行搜（降 Token） |

缓存根：`Path.home() / ".hs-dev-skill" / "rule_cache"`（可重建）。

---

## 3. 与 craft / Token / 门闩

- 本地 [`dev_paradigm.md`](dev_paradigm.md) / [`ddd_design.md`](ddd_design.md) / arch / craft / API = 高频子集，**不是**社区全文替代品。  
- 远程厚度靠本协议补齐；遵守 [`load_latch.md`](load_latch.md) L3 与 [`token_budget.md`](token_budget.md)「每次任务 ≤2 source」。  
- 实现期：按规则名 resolve 一条即可改代码；禁止「先把 Vercel 全库读进会话」。
