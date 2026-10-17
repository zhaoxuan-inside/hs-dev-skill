# 阶段 5：开发三同步实现 (Implementation & Three-Sync)

**何时读**：处理阶段 5：开发三同步实现 (Implementation & Three-Sync)时；先沿用[入口公共约束](../spec_driven_lifecycle.md)，只装载本业务分册。读取复用遵循[变化感知规则](../load_latch.md#5-变化感知与装载缓存统一重读规则)。

<!-- HS_SECTION_BODY -->
## 阶段 5：开发三同步实现 (Implementation & Three-Sync)

### 1. 核心目标
**质量优先**：以 [`testing.md`](../testing.md) 垂直切片 TDD + 六元组规范驱动编码，保证业务代码、设计文档、迁移脚本、测试用例的绝对一致性。分步红绿通过，最大可能保证最终正确。

### 2. 执行原则
1. **确认 seam**：落盘测面后再红灯（见 testing §2）；接口即测试面（见 [`deep_modules.md`](../deep_modules.md)）。
2. **Mock 先行与契约隔离**：在 `mock/_06_test_profile/` 配置测试集 Profile，业务代码零 Mock 污染。
3. **六元组业务逻辑**：在 `backend/` 或对应端实现 `method`、`method_compensate`、`method_fallback`。
4. **垂直切片 + 全覆盖**：一次一个行为红→绿→重构；`test/_01_method_test/` 核心域分支覆盖率 ≥ 85%，降级与补偿分支 100% 覆盖。
5. **实现期分叉**：新暴露的选择点同样适用置信度决策；产品空白回切 DESIGN（审讯式）；**实现期若需新增/改动 DB 设计 → 必须先经开发者决策，禁止自行落表**；触发询问则 `status --set BLOCKED`，禁止静默猜测业务特有规则。

---
