# hs-dev-skill: 产品开发 Skill

> **文档驱动 + 变更分级（S/M/L）+ 六元组运行时 + Token 预算索引**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Spec Version](https://img.shields.io/badge/skill-v2.13-blue.svg)](SKILL.md)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](references/cross_platform.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

`hs-dev-skill` 是可安装到 Cursor / Claude Code 等 Agent 的**单体**产品开发技能包（Windows / Linux / macOS）。入口 [`SKILL.md`](SKILL.md) 保持薄装载；细则按场景索引打开。流程上先写 `change_size=S|M|L` 与 `work_mode=DESIGN|IMPLEMENT`（设计多问 / 实现少问），过装载门闩后再干活；领域规则本地高频 + `rule_fetch` 远程按需；配合产品冻结、SQLite 切片与 context_pack，平衡 Token 与反偷懒。

---

## 安装（生态分发）

根目录即为单个 Skill（含 `SKILL.md` / `scripts/` / `references/`），可用官方 skills CLI：

```bash
# 安装到当前项目（多 Agent 可选）
npx skills add zhaoxuan-inside/hs-dev-skill

# 全局安装
npx skills add zhaoxuan-inside/hs-dev-skill -g

# 仅浏览是否被发现
npx skills add zhaoxuan-inside/hs-dev-skill --list
```

手动（任选其一）：

```bash
git clone https://github.com/zhaoxuan-inside/hs-dev-skill.git
# Cursor 用户技能目录示例：
#   ln -s /path/to/hs-dev-skill ~/.cursor/skills/hs-dev-skill   # Linux/macOS
#   mklink /J %USERPROFILE%\.cursor\skills\hs-dev-skill C:\path\to\hs-dev-skill  # Windows（管理员/开发者模式）
```

装后首次建议：

```bash
python scripts/init_hs_global.py          # 或 py -3 / python3
python scripts/skill_ref_index.py rebuild # Skill 详规场景索引
```

依赖：`Python >= 3.8`（标准库 `sqlite3` + `pathlib`）。

---

## 核心特性

1. **变更分级（Right-Sizing）**：任意需求先写 `change_size=S|M|L`；S 快路径、M 补丁路径、L 满配。见 [right_sizing.md](references/right_sizing.md)。
2. **设计多问 / 实现少问**：`work_mode=DESIGN|IMPLEMENT`；设计树澄清可跳过，实现期四条件才问。见 [confidence_decision.md](references/confidence_decision.md)。
3. **装载门闩**：强制「分级 + 索引路由 + 1 份详规」，禁止跳过；也禁止整目录通读。见 [load_latch.md](references/load_latch.md)。
4. **产品需求冻结（M/L）**：PRD 完整/正确/无冲突后才选型或满配详设。
5. **Token 预算**：`skill_ref_index` + `doc_index_db` + `rule_fetch` 切片；禁止整树/远程规则包通读。见 [token_budget.md](references/token_budget.md)。
6. **领域规则库**：本地 [frontend_craft](references/frontend_craft.md) / [api_engineering](references/api_engineering.md) 高频；远程按需 [rule_library](references/rule_library.md) + `resources/rule_sources.yaml`。
7. **全局学习与偏好**：`~/.hs-dev-skill/` + `global_index_db.py`。
8. **六元组 + 任务三文件 + 迁移 V/U + Mock 契约隔离 + verify 门禁**。
9. **默认本地 Commit；明确要求才 push**。

---

## 快速命令

```bash
make paths          # 全局路径
make test
make verify
make skill-ref-rebuild
make skill-ref-search Q="幂等"
make rule-list
make rule-search Q="React"
make rule-resolve ID=vercel.react-rules RULE=async-parallel
make index-rebuild
make init-docs
make init-global
# Windows: make test PYTHON="py -3"
```

```bash
python scripts/hs_paths.py
python scripts/init_hs_global.py
python scripts/skill_ref_index.py search --q "幂等" --limit 5
python scripts/rule_fetch.py resolve --id local.frontend.core
python scripts/doc_index_db.py --root . search --q "订单 创建" --limit 8
python scripts/task_manager.py create --id order_create --title "创建交易订单" --change-size L --priority P0
python scripts/verify_consistency.py --root .
```

---

## 目录指引

| 路径 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | Agent 入口（薄）；铁律 + 路径图 + CLI |
| [references/_index.md](references/_index.md) | 详规场景表（禁止整目录通读） |
| [references/load_latch.md](references/load_latch.md) | **动手前装载门闩** |
| [references/right_sizing.md](references/right_sizing.md) | 变更分级 + work_mode |
| [references/confidence_decision.md](references/confidence_decision.md) | 设计多问 / 实现少问 |
| [references/frontend_craft.md](references/frontend_craft.md) / [api_engineering.md](references/api_engineering.md) | UI / API 本地高频 |
| [references/rule_library.md](references/rule_library.md) | 远程规则按需协议 |
| [resources/rule_sources.yaml](resources/rule_sources.yaml) | 规则源目录 |
| [references/token_budget.md](references/token_budget.md) | 装载纪律 |
| [references/spec_driven_lifecycle.md](references/spec_driven_lifecycle.md) | L 满配阶段细则 |
| [scripts/](scripts/) | CLI（索引 / 规则拉取 / 任务 / 门禁） |
| [resources/templates/](resources/templates/) | 文档与 Mock 脚手架 |
| [examples/order_service/](examples/order_service/) | 订单服务参考用例 |
