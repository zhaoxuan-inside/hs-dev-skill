# G 实现集成范例：Android 草稿恢复

> 配套 [D Android 架构范例](d_architecture_frontend_android.md) 和 [E 工程契约](e_engineering_preparation_draft_sync.md)。

## 实现边界

稳定草稿 ID 跨导航和重建传递；页面状态放在可恢复的应用状态层，本地仓库独立于 Activity 生命周期。后台队列使用满足持久性、约束和取消语义的调度方式；不在 Activity 回调内执行唯一保存或同步。

## G2/G3 验证

验证系统返回、手势返回、配置变化、进程回收、网络约束变化、重试/取消、权限撤销和输入法操作。记录设备/API level、target SDK、厂商电源策略和真机/模拟器条件；单一设备结果不推广到全部 Android 设备。
