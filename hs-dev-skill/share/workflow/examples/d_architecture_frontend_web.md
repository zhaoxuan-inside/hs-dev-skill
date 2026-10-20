# D 架构设计范例：Web 离线草稿

> 虚构案例；共用产品行为和接口契约见 [D 共用架构](d_architecture_common.md)。实现验证见 [G Web 实现](../../../skills/hs-dev-implementation/SKILL.md)。

## D4 Web 框架边界

页面组件管理输入、保存状态和冲突选择；草稿仓库封装项目选定的浏览器持久化方式；跨标签页协调位于应用层。同步协调器依赖仓库和 API 客户端，组件不自行重试。浏览器支持范围、私密浏览行为和存储配额以项目目标为准，不在架构中假设。

平台行为和运行验证见 [G Web 实现范例](../../../skills/hs-dev-implementation/SKILL.md)。
