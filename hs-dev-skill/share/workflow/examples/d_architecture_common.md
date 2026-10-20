# D 架构设计范例：便笺离线草稿

> 虚构案例。产品范围和行为见 [A 产品构想](a_product_intent_draft_sync.md)、[B 产品设计](b_product_design_draft_sync.md) 与 [C 质量决策](c_quality_decisions_draft_sync.md)；数据/API 契约在 [E 工程准备](e_engineering_preparation_draft_sync.md)展开。

## D1 领域与职责

| 责任 | 归属 | 边界 |
|---|---|---|
| 编辑状态与平台交互 | 各客户端 UI | 调用客户端草稿服务，不直接拼接同步请求 |
| 本地草稿仓库 | 客户端数据层 | 通过平台存储适配器读写，管理本地版本和待同步状态 |
| 同步协调器 | 客户端应用层 | 管理重试、幂等键和冲突状态，不覆盖用户选择 |
| 草稿 API 与持久化 | 后端 | 校验版本并原子写入；冲突返回当前版本，不隐式合并 |

## D2 协作结构

```text
UI -> DraftService -> LocalDraftRepository
                  -> SyncCoordinator -> DraftAPI -> DraftRepository
```

UI 的保存提示来自本地仓库状态；同步成功以服务端确认响应为准。网络超时不能证明服务端未写入，客户端重试沿用同一 `clientMutationId`。客户端保存与服务端同步解耦，离线编辑不依赖网络可用。

## D3/D4 共用约束与平台边界

- 本地已确认保存的内容应支持应用重启后恢复；具体时限由项目质量目标决定。
- 同步请求可安全重试，冲突时保留本地与服务端版本供用户选择。
- 客户端平台差异放在 UI、存储和系统能力适配层，不改变共用草稿和同步契约。
- 不预设数据库、客户端框架或部署拓扑；沿用仓库事实并记录实际选择。

平台专项见本目录中 `d_architecture_frontend_<platform>.md` 和 `d_architecture_backend.md`。实现与验证应配对阅读对应 `g_implementation_*.md`；本阶段设计本身不构成实现或验收证据。
