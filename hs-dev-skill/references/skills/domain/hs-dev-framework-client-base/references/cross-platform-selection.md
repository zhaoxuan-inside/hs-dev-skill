# 跨端框架选型参考

仅在新项目选择跨端框架、评估迁移，或现有方案无法满足目标平台时读取。维护现有项目时沿用其技术栈，不因本参考中的候选名称触发选型或迁移。

## 候选类别

以下是用于建立候选集的例子，不是排名、完整清单或最新技术认证。候选必须覆盖本项目的目标平台和系统版本；查阅其官方文档核实支持状态、能力边界、发布与维护情况。

| 类别 | 可评估候选示例 | 主要需要验证的边界 |
|---|---|---|
| 多平台 UI 与应用 | Flutter、React Native、.NET MAUI | 目标平台与插件覆盖、平台原生能力接入、UI 一致性、团队语言与调试经验 |
| 共享业务逻辑、保留原生 UI | Kotlin Multiplatform 等 | 可共享代码范围、各端 UI 维护成本、平台互操作与构建链 |
| 桌面跨平台 | Qt、Electron、Tauri、Flutter | 安装包体积、系统集成、运行时依赖、目标桌面环境及分发方式 |
| 平台原生 | 各平台官方工具链 | 原生体验与系统能力、每端实现和维护成本 |

候选类别可能交叉；同一产品也可以按模块混合方案。不要为了“代码复用率”牺牲系统能力、无障碍、性能或可维护性。

## 决策步骤

1. 列出必须支持的平台、最低系统版本、设备能力、分发渠道、离线要求及团队已有技能。
2. 先排除官方支持范围不满足硬约束的候选，再对剩余方案验证关键插件、原生扩展能力、构建与发布链路。
3. 用一个有代表性的端到端垂直切片验证风险最高的能力，例如权限、后台任务、深链接、文件访问或桌面系统集成。
4. 对比初始开发、平台专属代码、升级跟进、测试矩阵和长期维护成本；记录取舍、未验证项、核验日期及官方来源。
5. 若没有候选在硬约束和维护成本上胜出，保留各端原生实现或混合架构，不强求统一框架。

## 官方核验入口示例

这些链接是核验入口而非时效保证。每次实际选型应打开官方当前文档，确认页面所述版本和目标平台：

- [Flutter supported platforms](https://docs.flutter.dev/reference/supported-platforms)
- [React Native environment setup](https://reactnative.dev/docs/set-up-your-environment)
- [.NET MAUI supported platforms](https://learn.microsoft.com/dotnet/maui/supported-platforms)
- [Kotlin Multiplatform](https://kotlinlang.org/multiplatform/)
- [Qt for desktop](https://doc.qt.io/qt-6/desktop.html)
- [Electron documentation](https://www.electronjs.org/docs/latest/)
- [Tauri documentation](https://tauri.app/start/)
