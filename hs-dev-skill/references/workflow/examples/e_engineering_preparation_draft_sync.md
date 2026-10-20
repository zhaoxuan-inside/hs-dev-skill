# E 工程准备范例：便笺离线草稿

> 虚构契约示例；总体边界见 [D 架构范例](d_architecture_common.md)。

## 数据与接口

```text
Draft { id, body, localRevision, serverRevision?, updatedAt,
        syncState: local_only | pending | synced | conflict | failed }
PUT /drafts/{id}: { body, baseServerRevision?, clientMutationId }
Success: { draftId, serverRevision, acceptedMutationId }
Conflict: { currentServerRevision, currentBody }
```

客户端推进本地版本，服务端确认服务端版本。相同 mutation ID 重试必须幂等；基础版本过期返回冲突；网络超时表示结果未知，可安全重试但不能丢弃草稿。

## 测试准备

覆盖本地写入/恢复、重复请求、过期版本并发写、存储失败、离线重试和冲突选择。替身测试只证明契约边界；数据库事务、真实系统生命周期及目标平台存储仍需集成环境验证。认证、数据保护和真实环境配置由项目补充。
