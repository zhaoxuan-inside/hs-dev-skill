# Skill 加载与引用资料路由

本文用于审查主控路由和发布包是否保持按需加载，不是每项工程任务都要读取的运行手册。实际执行以主控 Skill 和本轮选中的过程 Skill 为准。

## 两种不同的“加载”

- **上下文加载**：宿主先识别已安装 Skill 的名称和描述；主控选择一个过程，再按任务加载少量领域 Skill。Skill 的引用资料只在命中条件时读取。
- **发布包包含**：构建器把 Skill 可用的 Markdown 和其他资源放入安装包。文件随包发布不表示宿主会把它们全部加入当前对话。

主控 Skill 的入口文本约 4 KB；子 Skill 入口和引用资料随实际任务扩展。`references/` 中未被当前 Skill 指令要求或当前问题命中的文件保持未读。共享执行和验收协议属于独立子 Skill 的可用资源，不要求每次预读。

## 常见任务路由矩阵

下表中的主控 Skill 为每项任务共有；“必要入口”只包含本场景的最低过程/领域入口。“按需追加”必须由实际缺口触发。

| 请求场景 | 必要入口（除主控外） | 仅在这些条件下追加 | 活动与引用资料 |
|---|---|---|---|
| 只读解释代码或架构 | `hs-dev-exploration` | 用户要求重建经过核实的项目知识时改用 `hs-dev-reverse` | 只定位相关代码、文档和证据；不建任务、不加载活动清单 |
| 已观察到缺陷并要求诊断或修复 | `hs-dev-debugging` | 运行或选择验证时用 `hs-dev-testing`；证据显示需求/设计有缺口时转相应过程 | 只读相关 H1/E4/E5/G1/G2 清单；不加载整个 H 阶段 |
| 实现后端业务切片 | `hs-dev-implementation`、`hs-dev-backend` | 涉及框架/模块机制时加 `hs-dev-framework-backend`；执行测试时加 `hs-dev-testing`；相关配置治理时加 `hs-dev-governance` | G1 必要；G2/G3/G4 分别由验证、集成和受管发布动作触发 |
| 实现 Web 界面 | `hs-dev-implementation`、`hs-dev-frontend-base`、`hs-dev-frontend-web` | 涉及路由、渲染或应用级状态时加 `hs-dev-framework-frontend`；验证行为时加 `hs-dev-testing` | 只读相关浏览器交互或运行专题；不加载 Web 的全部参考资料 |
| 实现 Android/iOS/Windows/Linux/macOS 客户端界面 | `hs-dev-implementation`、`hs-dev-frontend-base`、对应的一个端侧 Skill | 应用生命周期或框架结构受影响时加 `hs-dev-framework-client-base` 与对应平台框架 Skill；验证时加 `hs-dev-testing` | 只读当前端和当前问题命中的专题；一个端的工作不加载其余平台入口 |
| 产品目标或用户场景尚未明确 | `hs-dev-discovery` | 具体产品行为已进入设计时加 `hs-dev-product`；技术设计应在产品输入有效后转 `hs-dev-design` | 只选择造成缺口的 A/B 活动，不从 A1 到 H4 全部展开 |
| 明确范围的交付验收 | `hs-dev-acceptance` | 需要补充独立测试证据时加 `hs-dev-testing`；发现代码缺陷时交回 debugging/implementation | 只核对本次验收范围、绑定材料和证据；不重做产生材料的过程 |

这是常见最小路由样例，不是硬编码工作流。目标项目已有有效结果时优先复用；跨阶段只按依赖和实际缺口追加入口。平台、框架、测试和治理能力均不得仅凭技术名词触发。

## 子 Skill 包的资料策略

独立发布包必须包含自身入口引用的资源，递归解析其 Markdown 引用；此外会包含 manifest 声明的必需共享协议。打包校验验证资源闭包和链接，但不会把整个包注入会话。共享资源的发布策略由 `hs-dev-skill/skill-packages.json` 中 `resource_policy` 与 `shared_resources` 共同声明。

公共约束的短摘要可以留在独立子 Skill 中，但完整操作规则以共享协议为准。摘要用于防止单独发布时越权或扩大范围，不应复制整份协议；多份摘要必须保持简短且语义一致。

## 审查要点

- 每个任务只选一个主过程；只有当前结果需要时才添加领域 Skill。
- 活动清单、框架专题和平台资料按命中条件逐项读取，不因目录结构完整而全量加载。
- 直接发布的子 Skill 仍具备自己的领域步骤；共享安全、执行和验收规则通过协议引用提供。
- 新增路由应同步更新主控规则、必要时更新本矩阵，并增加包构建测试；删除或合并路由时检查 manifest、技能目录和生成包三处的一致性。
