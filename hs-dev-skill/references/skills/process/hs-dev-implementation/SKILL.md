---
name: hs-dev-implementation
description: 实现已明确任务；以当前切片约束和证据限制上下文。
license: MIT
---

# 实现与集成

先读取当前任务、受影响代码、必要契约及当前切片的通过标准；实现前明确怎样判断结果，具体测试执行与发布细节到需要时再读取。尚未执行的切片不加载正文。缺少某项契约时只补对应设计活动；不因进入 G 就加载 A～F，不因后续要集成就预读所有集成资料。

## 执行清单

- [ ] **核实实施基线**：确认当前切片目标、范围、适用标准、有效上游、相关代码与工程约定；遵循主入口检查工作区安全和受管写入条件。识别已有修改及归属，不覆盖用户工作。业务决定或契约缺失时仅补相应设计，不猜规则。
- [ ] **选择专业能力与验证**：按实际代码边界加载领域技能，与 testing 选择本次必要的行为、契约及回归检查；治理项仅按适用配置检查。实现前明确输入、预期和断言；有意义的新行为或缺陷回归按需要确认先失败，低影响修改不为凑数量新建测试。
- [ ] **小步实现与同步**：沿当前行为切片推进，复用符合意图和契约的已有实现，保持代码、配置、文档与契约一致。只做授权范围内的必要修改，不顺带改版、重构或换栈；发现独立异常按证据交由 debugging，产品或设计变化交回负责过程，不静默扩任务。
- [ ] **验证与增量集成**：先执行当前变化的针对性检查，再按受影响调用链验证必要集成及回归，复用 testing 的证据格式。明确真实资源与替身、未验证条件及失败影响；有未解释失败不能宣称完成，相关源再变动时复核受影响证据，不机械重跑无关检查。
- [ ] **发布受管变更**：按执行协议及适用 G4 条目检查操作归属、快照、修改登记、验证、索引及缓存一致性，发布前后核对源版本与证据。受管发布不等于 Git commit、push 或部署，不自动授权这些动作；不重复实现底层协议。G4 的“全部修改”只限本次操作归属，恢复前核验后续编辑冲突，不覆盖其他工作。
- [ ] **完成或交接**：核对当前任务适用标准、必要上游、实际产物和证据均有效，按当前模式处理确认后才标记完成。交付实际改动、验证、限制及下一动作，不以代码已写或命令成功替代结果。中断、漂移或恢复问题交由 continuity；未完成时保留具体阻断，不自动重启流程或发布应用。

## 输出要求

结果关联当前源版本，区分通过、未通过、不适用和未验证；不适用说明理由，未验证说明缺失条件。简单改动直接回复，不强制新增报告；沿用活动结果与专业证据，不另建竞争性清单。模型自检不代替人工验收。

## 条件式资料选择

只读取命中条件的清单；每行独立判断，不按表格顺序全量加载。

| 当前缺口或动作 | 读取资料 |
|---|---|
| 开始或继续当前切片的代码实现 | [G1 切片实现](../../../workflow/g_implementation_integration/g1_slice_implementation/checklist.md) |
| 验证当前切片的行为和契约 | [G2 切片验证](../../../workflow/g_implementation_integration/g2_slice_verification/checklist.md) |
| 与其他切片或模块存在集成边界 | [G3 增量集成](../../../workflow/g_implementation_integration/g3_incremental_integration/checklist.md) |
| 准备发布本次受管变更 | [G4 一致性提交](../../../workflow/g_implementation_integration/g4_consistent_commit/checklist.md) |

### 平台范例选择

多平台产品按已接受的交付切片逐端实现。全平台支持范围或平台矩阵不代表本轮要并行实现或加载所有端资料；先从当前任务/切片确认目标端，再只加载该端专业 Skill 和对应 G 阶段范例。没有目标端的共享层任务只读取共用契约与共享代码，不猜测平台。

| 当前切片目标 | 本轮范例 |
|---|---|
| Web 前端 | [G Web 实现](../../../workflow/examples/g_implementation_frontend_web.md) |
| Windows 前端 | [G Windows 实现](../../../workflow/examples/g_implementation_frontend_windows.md) |
| macOS 前端 | [G macOS 实现](../../../workflow/examples/g_implementation_frontend_mac.md) |
| Linux 前端 | [G Linux 实现](../../../workflow/examples/g_implementation_frontend_linux.md) |
| iOS 前端 | [G iOS 实现](../../../workflow/examples/g_implementation_frontend_ios.md) |
| Android 前端 | [G Android 实现](../../../workflow/examples/g_implementation_frontend_android.md) |
| 后端 | [G 后端实现](../../../workflow/examples/g_implementation_backend.md) |

只有当前切片包含或暴露了尚未解决的架构决定时，才追加读取对应 `d_architecture_*.md`；已接受的架构结论从任务/契约引用，不为实现重复加载其他端或整套 D 范例。端到端切片依实际涉及的客户端与服务端边界读取对应范例。

## 上下文边界

遵循[主入口](../../../../../SKILL.md)的安全与读取协议；已在上下文中的共同约束不重复加载。活动清单只定义标准，任务代码和产物另按对象定位。扩读前说明缺失的决定或证据及其影响；没有具体缺口时不读取相邻活动、阶段目录或整个 workflow。
