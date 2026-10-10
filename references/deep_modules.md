# 深模块词汇（日常设计 / 重构对话）

**何时读**：阶段 2 架构；定模块接口与 seam；重构「改不动 / Agent 到处改」；配合测试可测性；每会话最多一次。  
**分工**：范式阶梯 → [`dev_paradigm.md`](dev_paradigm.md)；后端分层 → [`backend_arch.md`](backend_arch.md)；测试面 → [`testing.md`](testing.md)。DDD 限界上下文≠本文 seam（见下）。

溯源：John Ousterhout《A Philosophy of Software Design》深度思想 + 社区 codebase-design 操作词汇（本地点火，禁止整仓通读外部 Skill）。

---

## 1. 强制词汇（对话与 ADR 里用这些词）

| 词 | 含义 | 避免混用 |
|----|------|----------|
| **Module（模块）** | 有接口与实现的任意尺度：函数 / 类 / 包 / 用例切片 | 勿笼统说 component/service |
| **Interface（接口）** | 调用方正确使用须知的一切：签名、不变量、顺序、错误模式、配置与性能特征 | 不止 TypeScript `interface` |
| **Implementation（实现）** | 模块内部代码 | 与 Adapter 角色区分 |
| **Depth（深度）** | 单位接口学习成本可换取的行为量；深 = 小接口后藏大行为 | 勿用「实现行数/接口行数」刷深度 |
| **Seam（缝）** | 可不改此处而替换行为的位置；接口安放点（Feathers） | 勿与 DDD **Bounded Context** 混称 boundary |
| **Adapter（适配器）** | 在 seam 上满足接口的具体物（Postgres repo、内存 fake、HTTP 客户端封装） | 描述角色，不描述内部大小 |
| **Leverage（杠杆）** | 深度给调用方：一处实现，N 处调用与 M 处测试受益 |
| **Locality（局部性）** | 深度给维护者：改/修/验集中一处 |

**深模块**：小接口 + 厚实现。  
**浅模块**：接口几乎与实现一样复杂（透传）→ 优先加深或删除。

```text
深:  [ 小 Interface ]     浅:  [     很大 Interface     ]
     [               ]         [ 很薄 Implementation ]
     [ 厚 Implementation ]
```

---

## 2. 设计原则（落地提问）

1. **深度是接口属性**：内部可再拆小块与内部 seam；它们不必暴露给调用方。  
2. **删除测试（deletion test）**：想象删掉该模块——复杂度消失 → 多半是透传；复杂度散到 N 个调用方 → 它在赚深度。  
3. **接口即测试面**：调用方与测试走同一 seam；若总想测穿接口 → 模块形状可能错了。  
4. **一个 Adapter = 假想缝；两个 Adapter = 真缝**：没有第二实现（如内存 fake / 第二支付渠道）时，禁止为「架构好看」空加端口。  
5. **接受依赖、返回结果**：便于测试；副作用集中在明确 Adapter。

设计接口时连问：能否更少方法？更简参数？能否把更多复杂度藏进实现？

---

## 3. 与本 Skill 范式 / 分层的挂钩

| 场景 | 用法 |
|------|------|
| 选 B2/B3 | 用例模块对外小接口；Infra 为 Adapter |
| 选 B4+ DDD | BC 是战略边界；**seam** 仍用于可测与替换点，两套词并存勿混 |
| 前端 Feature | Feature 公共入口是 seam；禁止 features 互相深挖内部 |
| 六元组方法 | 方法签名 + 不变量 = Interface；compensate/fallback 属同一模块深度 |
| 阶段 2 ADR | 用「深/浅、seam、Adapter」写清为何这里切开 |

`change_size=S`：不新写架构文，但改接口时仍用本词汇自检是否在造浅模块。

---

## 4. 日常重构对话（轻量 improve）

发现 Agent 散改多文件、测不动、重复逻辑时：

```text
1) 指出浅模块 / 过宽接口（热路径优先）
2) 提议 1～3 个加深候选（只列问题，先不写大方案）
3) 用户点名一个 → 用删除测试 +「设计两次」草图对比接口
4) 确认 seam 与测试面 → 再改代码（走 testing 红绿）
```

禁止：未对齐 seam 就 AFK 大重构；禁止用「微服务」伪装深度。

---

## 5. 反模式

| 禁止 | 改为 |
|------|------|
| 每个函数一个「端口」文件 | 真有 ≥2 Adapter 再抽 seam |
| 上帝 Service 五十个方法 | 按行为拆深模块 |
| 为测而把一切 public | 收窄 Interface，内测走内部 seam |
| 用 BC 文件夹假装深度 | 统一语言 + 不变量 + 小接口 |

远程加深（可选）：架构模式书规则 / Clean 分档 → `rule_fetch`；仍禁止通读外部整包 codebase-design。
