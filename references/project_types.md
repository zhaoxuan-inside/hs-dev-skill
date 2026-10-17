# 项目类型与清单组织规范（Project Types & Checklist Structure）

**何时读**：阶段 0 分级后确定项目类型时；编写任意步骤的工作清单/验收清单/产出文档时；类型判定模糊或跨类型组合时；每会话最多一次。

**分工**：分级与意图 → [`right_sizing.md`](right_sizing.md) / [`intent_routing_and_gates.md`](intent_routing_and_gates.md)；阶段细则（三件套落点）→ [`spec_driven_lifecycle.md`](spec_driven_lifecycle.md)。

---

## 0. 三件套与清单组织规范（核心原则）

**每个开发步骤 = 三件套**：

| # | 组件 | 作用 | 不达标怎么办 |
|---|---|---|---|
| 1 | **工作清单** | 记录本步骤"要做什么"（原子动作） | — |
| 2 | **验收清单** | 记录"做到什么程度才达标"（逐条可查） | **继续问答或继续开发**，禁止带病进入下一步 |
| 3 | **产出文档** | 本步骤交付物（路径清单） | 缺即未完成 |

**清单组织规范（树状 · 原子叶子）**：
- 三个清单统一用**树状层级**组织；
- **叶子 = 原子独立项**：一项只含一个可判定内容，**禁止合并**（如"幂等/补偿/fallback 100% 覆盖"必须拆成三个叶子）；
- **父节点仅做分组**，不承担判定；判定只发生在叶子；
- 每个叶子必须**可独立验证**（机器可查，或人工可查）。

**通用性**：工作清单与验收清单**按项目类型参数化**——基础清单（全类型通用）+ 类型专属清单（各类型差异）；单个项目只做"套用 + 裁剪 + 记录差异"，不从零定制。

---

## 1. 项目类型判定（P1 ~ P6）

| 类型 | 定义 | 触发条件 | 代码收敛位置 |
|---|---|---|---|
| **P1 纯后端服务** | 无 UI，仅提供服务端能力（API/消息/批处理/微服务） | 无 `frontend/`、无 `apps/*` | `backend/`（微服务 `services/`） |
| **P2 Web 应用** | 含响应式浏览器前端 + 后端 | 存在前端页面且浏览器内运行 | `backend/` + `frontend/`（或单工程） |
| **P3 桌面客户端** | 桌面应用（本地窗口 + 打包分发） | 存在桌面窗口应用 | `apps/desktop/` |
| **P4 移动客户端** | 移动 App / H5 / 小程序（触控优先） | 存在移动端分发 | `apps/mobile/`（可细分 `ios/`、`android/`） |
| **P5 全端组合** | 多端并存，共享契约 | **≥2 端并存** | `apps/*` + `packages/` |
| **P6 纯库/包/CLI 工具** | 无部署，被外部引用 | 交付物是包/SDK/CLI，非可部署服务 | `packages/` 或独立仓库 |

---

## 2. 组合规则

1. **P5 全端** = P1 ∪ P2 ∪ P3 ∪ P4 各端专属验收**全量叠加** + P5 专属（共享契约层 + 跨端一致性）；叠加按"类型卡整体并入"，不写合并检查项。
2. **P6 带 demo**：库内含可运行 demo 页面 → **叠加 P2**（demo 走 Web 验收）。
3. **多类型叠加**：验收清单 = 基础清单 + 各类型专属清单**并集**；叶子仍保持原子独立。
4. **类型变更**：实现中发现类型判定变化（如新增端）→ 回切 DESIGN，重判类型并重跑受影响验收，禁止静默沿用旧类型。

---

## 3. 类型卡片

<!-- HS_SECTION_INDEX -->

**按业务装载**：正文已拆成独立文件。先沿用本页公共约束，只打开当前业务/阶段需要的分册；不要顺序读全套。分册独立进行变化检查；迁移后旧的行号/摘要须重新定位，已有签收不得自动迁移。

### P1 纯后端服务

正文见 [project_types/backend.md](project_types/backend.md)。

### P2 Web 应用

正文见 [project_types/web.md](project_types/web.md)。

### P3 桌面客户端

正文见 [project_types/desktop.md](project_types/desktop.md)。

### P4 移动客户端

正文见 [project_types/mobile.md](project_types/mobile.md)。

### P5 全端组合

正文见 [project_types/multi_platform.md](project_types/multi_platform.md)。

### P6 纯库/包/CLI 工具

正文见 [project_types/library_cli.md](project_types/library_cli.md)。

## 4. 类型 × 阶段 影响速查

正文见 [project_types/stage_matrix.md](project_types/stage_matrix.md)。

## 5. 反模式

正文见 [project_types/stage_matrix.md](project_types/stage_matrix.md)。
