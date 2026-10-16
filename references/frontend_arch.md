# 前端架构方案清单（本地高频 · 指导设计）

**何时读**：[`dev_paradigm.md`](dev_paradigm.md) 选定前端阶之后；划模块；与后端边界对齐；每会话最多一次。  
**分工**：本文 = **前端结构与依赖**；范式总表 → `dev_paradigm`；深模块/seam → [`deep_modules.md`](deep_modules.md)；默认审美 → [`frontend_aesthetic.md`](frontend_aesthetic.md)；DESIGN.md → [`design_md.md`](design_md.md)；手艺 → [`frontend_craft.md`](frontend_craft.md)；DDD 档边界 → [`ddd_design.md`](ddd_design.md)。

```bash
python scripts/rule_fetch.py resolve --id local.frontend.arch
python scripts/rule_fetch.py resolve --id fsd.skill                 # Feature-Sliced Design
python scripts/rule_fetch.py resolve --id local.dev.paradigm
```

**溯源**：[feature-sliced/skills](https://github.com/feature-sliced/skills)（FSD）· [feature-sliced/documentation](https://github.com/feature-sliced/documentation) · 本 Skill 范式表。

---

## 1. 先选方案（分档）

| 档 | 信号 | 方案 |
|----|------|------|
| T0 | 单页/落地/营销站 | 按页面目录即可；跟 `DESIGN.md` + `frontend_craft` |
| T1 | 中小型产品、上下文少 | **按业务能力的 feature 模块**（推荐默认） |
| T2 | 多团队/多域/长期演进 | **Feature-Sliced Design (FSD)** 或严格 Clean FE |

不确定 → **T1**。禁止小项目上全套 FSD 仪式。

---

## 2. 与后端边界对齐（强制原则）

1. **一后端模块（或 BC）↔ 一前端 feature（或 FSD slice 组）**；跨边界数据经 API/BFF，不共享后端实体形状。  
2. **页面是用例入口**，不是「组件垃圾桶」；容器拉数、展示组件无业务规则。  
3. **视图模型 ≠ 后端模型**：DTO → UI state；禁止把领域/表 JSON 铺满全局 store。  
4. **词典**：路由/类型名跟项目词典；展示文案可口语化。  
5. 视觉身份仍以项目根 `DESIGN.md` 为准。  
6. 未选 DDD 时用「业务模块」对齐即可，勿伪造限界上下文目录。

---

## 3. 方案 A：按 BC 的 Feature 模块（默认）与七大方法映射

遵循 [`method_archetypes.md`](method_archetypes.md) 规范，将前端逻辑细分收敛至 7 类方法，杜绝大组件与逻辑耦合：

```text
src/
  app/                 # 壳：路由、provider、鉴权门闩
  features/
    order/             # ← 业务特征域
      api/             # ADAPTER: 外部 API Client 请求与网络封装
      model/
        calc.ts        # ALGO: 纯前端折算、运费计算（0 DOM 依赖纯函数）
        mappers.ts     # TRANSFORM: DTO ↔ ViewModel 互转、Payload 组装
        policy.ts      # GUARD: 权限策略、按钮/操作可执行性判定
        state.ts       # STATE: 本地状态机跃迁、Reducer
      hooks/
        useOrder.ts    # ORCHESTRATE: 业务流程编排 Hook（调度上述纯函数与 API）
      ui/
        OrderCard.tsx  # PRESENT: Dumb 组件、纯展示、Tailwind 样式
    payment/
  shared/              # 真共享 UI kit (PRESENT) / 通用工具 (ALGO)（无具体业务规则）
```

| 禁令 | 改为 |
|------|------|
| 在 JSX 组件内部写复杂折算/计费/校验算式 | 抽离至 `model/calc.ts` (`ALGO`)，单测 100% 覆盖 |
| 在 UI 组件内直接 `fetch` / `axios` | 经 `api/` (`ADAPTER`) 请求，组件或 Hook 仅消费返回值 |
| `features/order` import `features/payment` 内部 model | 经 API/事件或 `shared` 的纯展示类型 |
| 全局 store 塞所有域 | 域内状态 + 服务端缓存（Query/SWR） |
| shared 塞业务 if/else | 下沉到对应 feature |

---

## 4. 方案 B：Feature-Sliced Design（T2）

层（依赖只向下）：`app → pages → widgets → features → entities → shared`。

| 层 | 职责 |
|----|------|
| app | 提供者、路由、初始化 |
| pages | 组合，少逻辑 |
| widgets | 大块 UI 组合 |
| features | 用户场景（下单、支付） |
| entities | 业务实体的前端表示（非后端聚合泄漏） |
| shared | UI kit、lib、api 客户端骨架 |

深化：`resolve --id fsd.skill`（按需 `search-cache`），勿整篇灌进上下文。官方文档：[feature-sliced.design](https://feature-sliced.design/)。

---

## 5. BFF / 聚合视图

- 一屏要拼多 BC：优先 **BFF 或后端查询侧组合**，前端少编排多域写操作。  
- 写操作仍打到拥有该聚合的上下文 API（幂等/错误码见 `api_engineering`）。

---

## 6. 交付自检

- [ ] feature 边界能对照架构文中的 BC 表  
- [ ] 无跨 feature 偷引内部模块  
- [ ] 无「后端 Entity 直出」当 UI 状态  
- [ ] 档位与产品规模匹配；有 `DESIGN.md` 时视觉不另起炉灶  
- [ ] 关键路径 loading/empty/error 齐（`frontend_craft`）
