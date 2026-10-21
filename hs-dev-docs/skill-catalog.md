# Skill 职责目录

依据 `hs-dev-skill/skill-packages.json`与各源入口核对：1 个总控、10 个过程、18 个领域、3 个支撑，共 32 个 Skill。下表是导航摘要，具体执行清单以链接目标为准。

总控：[hs-dev-skill](../hs-dev-skill/SKILL.md)，负责诉求判断、过程选择、专业加载及共享执行边界。

## 过程 Skill

| Skill | 职责摘要 |
|---|---|
| [hs-dev-acceptance](../hs-dev-skill/skills/hs-dev-acceptance/SKILL.md) | 核对指定交付范围的材料与证据；保留真实确认来源。 |
| [hs-dev-continuity](../hs-dev-skill/skills/hs-dev-continuity/SKILL.md) | 恢复已有任务或评估变化影响；从任务绑定状态恢复最小工作集。 |
| [hs-dev-debugging](../hs-dev-skill/skills/hs-dev-debugging/SKILL.md) | 定位已观察到的异常并修复；按根因扩大上下文。 |
| [hs-dev-design](../hs-dev-skill/skills/hs-dev-design/SKILL.md) | 解决指定技术决定；按影响选择质量、架构或工程契约资料。 |
| [hs-dev-discovery](../hs-dev-skill/skills/hs-dev-discovery/SKILL.md) | 明确问题、范围和产品行为；根据缺失的产品决定选择活动。 |
| [hs-dev-exploration](../hs-dev-skill/skills/hs-dev-exploration/SKILL.md) | 解释指定代码、架构或设计；不默认加载开发活动资料。 |
| [hs-dev-implementation](../hs-dev-skill/skills/hs-dev-implementation/SKILL.md) | 实现已明确任务；以当前切片约束和证据限制上下文。 |
| [hs-dev-planning](../hs-dev-skill/skills/hs-dev-planning/SKILL.md) | 把已明确设计转为可执行任务；只读取当前规划缺口。 |
| [hs-dev-refactoring](../hs-dev-skill/skills/hs-dev-refactoring/SKILL.md) | 保持可观察行为调整结构；以行为保护和变更边界限制读取。 |
| [hs-dev-reverse](../hs-dev-skill/skills/hs-dev-reverse/SKILL.md) | 从指定代码范围重建可证实的工程知识；按调查对象选择资料。 |

## 领域 Skill

| Skill | 职责摘要 |
|---|---|
| [hs-dev-backend](../hs-dev-skill/skills/hs-dev-backend/SKILL.md) | 在已确定的工程任务中处理后端数据、接口、业务逻辑、运行状态和外部依赖；遵循当前过程及其范围。 |
| [hs-dev-framework-backend](../hs-dev-skill/skills/hs-dev-framework-backend/SKILL.md) | 设计服务端应用的技术框架、模块分层、依赖方向和运行边界；不替代业务契约设计。 |
| [hs-dev-framework-client-android](../hs-dev-skill/skills/hs-dev-framework-client-android/SKILL.md) | Android 客户端框架特性，处理应用组件、进程生命周期、状态恢复、系统能力和构建边界。 |
| [hs-dev-framework-client-base](../hs-dev-skill/skills/hs-dev-framework-client-base/SKILL.md) | 提供移动和桌面客户端框架设计的共通原则；按目标操作系统加载对应平台特性。 |
| [hs-dev-framework-client-ios](../hs-dev-skill/skills/hs-dev-framework-client-ios/SKILL.md) | iOS 客户端框架特性，处理应用/Scene 生命周期、状态恢复、系统服务适配和构建边界。 |
| [hs-dev-framework-client-linux](../hs-dev-skill/skills/hs-dev-framework-client-linux/SKILL.md) | Linux 客户端框架特性，处理桌面环境兼容、显示协议、系统服务集成和软件分发边界。 |
| [hs-dev-framework-client-windows](../hs-dev-skill/skills/hs-dev-framework-client-windows/SKILL.md) | Windows 客户端框架特性，处理窗口/进程模型、系统集成、配置和打包更新边界。 |
| [hs-dev-framework-frontend](../hs-dev-skill/skills/hs-dev-framework-frontend/SKILL.md) | 设计浏览器前端应用的技术框架、模块结构、路由、状态与运行边界；不负责产品交互定义。 |
| [hs-dev-frontend-android](../hs-dev-skill/skills/hs-dev-frontend-android/SKILL.md) | Android 界面的系统导航、布局、权限和系统入口规则，按主题加载。 |
| [hs-dev-frontend-base](../hs-dev-skill/skills/hs-dev-frontend-base/SKILL.md) | 提供 Web、移动端和桌面端界面工作的共通要求；按实际目标端加载对应平台 Skill。 |
| [hs-dev-frontend-ios](../hs-dev-skill/skills/hs-dev-frontend-ios/SKILL.md) | iOS 界面的导航、安全区、系统授权和系统集成规则，按主题加载。 |
| [hs-dev-frontend-linux](../hs-dev-skill/skills/hs-dev-frontend-linux/SKILL.md) | Linux 桌面界面的环境、显示协议、输入、系统门户和辅助功能规则，按主题加载。 |
| [hs-dev-frontend-mac](../hs-dev-skill/skills/hs-dev-frontend-mac/SKILL.md) | macOS 界面的窗口/文档、菜单快捷键、系统授权和辅助功能规则，按主题加载。 |
| [hs-dev-frontend-web](../hs-dev-skill/skills/hs-dev-frontend-web/SKILL.md) | Web 端按需加载的浏览器交互与运行环境规则。 |
| [hs-dev-frontend-windows](../hs-dev-skill/skills/hs-dev-frontend-windows/SKILL.md) | Windows 桌面界面的窗口、输入、系统集成和辅助功能规则，按主题加载。 |
| [hs-dev-governance](../hs-dev-skill/skills/hs-dev-governance/SKILL.md) | 检查和维护术语、产物登记、覆盖关系、索引一致性及已启用的工程约束；沿用当前活动范围，不自动引入基础设施或代替验收。 |
| [hs-dev-product](../hs-dev-skill/skills/hs-dev-product/SKILL.md) | 分析产品价值、定位、功能、行为、交互和跨功能旅程，核验约定范围内的完整性；沿用当前过程，不替代工程设计或人工确认。 |
| [hs-dev-testing](../hs-dev-skill/skills/hs-dev-testing/SKILL.md) | 设计和执行与当前任务匹配的行为、契约、集成、回归及质量检查，分析失败并交付可追溯证据；不代替产品验收或扩大修复范围。 |

## 支撑 Skill

| Skill | 职责摘要 |
|---|---|
| [hs-dev-recovery](../hs-dev-skill/skills/hs-dev-recovery/SKILL.md) | 统一快照、changelog、冲突保护、完整恢复和保留清理。 |
| [hs-dev-trace](../hs-dev-skill/skills/hs-dev-trace/SKILL.md) | 按配置记录本项目摘要事件，best effort且默认关闭。 |
| [hs-dev-update](../hs-dev-skill/skills/hs-dev-update/SKILL.md) | 明确授权后安装当前完整包，校验、替换、失败恢复。 |

## 协作边界

- 过程负责活动选择、依赖和推进；领域入口提供专业方法，不单独扩大授权。
- 后端业务契约由 backend 负责；模块、依赖和运行模型由 framework-backend 负责。
- 界面共性由 frontend-base 负责，平台入口只补差异；Web 应用结构由 framework-frontend 负责。
- 移动与桌面框架使用 framework-client-base，再追加实际平台入口；当前无独立 macOS 框架入口，macOS 使用 Base。
- continuity 恢复任务上下文；recovery 处理文件快照和操作恢复，两者完成条件不同。
- testing 提供验证证据，acceptance 对指定范围核验；governance 核查登记和一致性，均不代签人工确认。
