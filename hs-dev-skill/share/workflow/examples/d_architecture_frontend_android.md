# D 架构设计范例：Android Activity 重建与后台限制

> 虚构案例；共用行为和服务端契约见 [D 共用架构](d_architecture_common.md)。实现验证见 [G Android 实现](../../../skills/hs-dev-implementation/SKILL.md)。

## 平台行为

- 草稿写入由应用数据层及时完成，不能只放在 Activity/Compose 临时状态或依赖 `onStop` 才保存。
- 系统返回、手势返回、旋转/配置变化和 Activity 重建都恢复同一草稿；用户导航离开与系统回收需按产品行为区分。
- 后台同步按任务约束、持久性、用户可见性和取消语义选择 Android 调度机制；重试可安全重复并保留本地内容。
- 权限仅在实际使用平台能力时请求；拒绝、撤销和目标版本行为均有降级路径。

## D4 框架边界

Activity/导航层传递稳定草稿 ID；ViewModel 或等价状态层管理页面状态；仓库和同步器独立于界面生命周期。后台任务接收幂等 mutation ID，进度或约束变化不会造成重复草稿。

返回/重建、后台约束、权限和输入体验验证见 [G Android 实现范例](../../../skills/hs-dev-implementation/SKILL.md)。
