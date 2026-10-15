# 完成度闭环（反假代码 / DoD 回收 / 禁止静默砍功能）

**何时读**：宣布「完成」前 / 阶段 6 / `COMPLETED` 流转前 / 写交付报告；每会话最多一次。
**要解决的问题**：门禁若只查文档不查代码，Agent 便可能以漂亮文档 + 假代码（占位注释、空桩、skip 测试、写死伪数据）过关，且砍掉的功能无人发现。本文把「做完」定义为**可机械验证的闭环**。

---

## 0. 三条铁律

1. **假代码零容忍**：黑名单（§1）任何一处命中 = 该切片未完成；`python scripts/fake_code_scanner.py --root .` 必须 0 命中（已内置于 `verify_consistency`）。
2. **DoD 逐条回收**：阶段 0 / 任务「验收标准」写下的每条 DoD，COMPLETED 前必须逐条映射到 seam 测试与证据（§2）；写了的 DoD 不允许凭空消失。
3. **未实现必须显式**：任何砍掉 / 简化 / 延后的功能必须进入「未实现清单」并**告知用户**（§3）；禁止静默砍功能。

---

## 1. 假代码黑名单（与 `fake_code_scanner.py` 类别同源）

| 类别 | 典型形态 | 合法替代 |
|---|---|---|
| 占位注释 | `TODO` `FIXME` `XXX` `HACK` `待实现` `未实现` | 直接实现；做不完 → `BLOCKED` + 未实现清单 |
| NotImplemented 桩 | `raise NotImplementedError`、`throw new Error("not implemented")`、`panic("not implemented")`、`NotImplementedException` | 实现真实逻辑 |
| 空桩函数体 | `pass` / `...` 独占函数体、仅 docstring 无实现 | 实现真实逻辑；真实 SPI/接口桩须行内 `hs-allow: <理由>` |
| 跳过/掏空测试 | `it.skip` `xit` `it.todo`、`@pytest.mark.skip`、`t.Skip`、`assert True` / 空断言 | 写真实断言或删除该用例；**门禁视 skip 为失败** |
| 业务代码 Mock 分支 | `if (isMock) …`、`useMock`、写死伪数据数组 | mock/ Sidecar + Test Profile（[`mock_contract_guide.md`](mock_contract_guide.md)） |
| 空 catch | `catch {}`、`except: pass` | 处理、记日志或重抛 |

- 扫描命令：`python scripts/fake_code_scanner.py --root .`（命中 exit 1；`--warn-only` 仅排障用，禁止当门禁结果）。
- **豁免纪律**：行内 `hs-allow: <理由>` 仅限真实 SPI/接口桩（插件点、协议/抽象定义、`@abstractmethod` 类），理由必填；用豁免掩盖未完成 = 违规。
- 合法不算假代码：测试夹具/`mock/` 目录内伪数据、`@overload`/`@abstractmethod`/`Protocol` 定义、显式捕获 `NotImplementedError` 的 fallback 控制。

---

## 2. DoD 逐条回收（映射表）

M/L：COMPLETED 前在 task detail「完成度审计」节落盘（`task_manager create` 已生成骨架）：

| DoD 项 | seam / 测试 | 证据（命令 + 结果） | 状态 |
|---|---|---|---|
| 逐条抄自验收标准 | 对应测试文件/用例 | `make test` → PASS 等 | ✅ |

- 全 ✅ 才可 `status --set COMPLETED --dod-audited`。
- 任何一条做不了 → 走 §3 范围裁剪；**不允许**标 ❌ 后照常 COMPLETED。
- **S**：不落盘，交付报告里 3 行核对（DoD 摘要 + 测试证据 + 扫描结果）。
- **L / 有 UI**：另做**功能覆盖对账**——PRD 功能点 ↔ 原型页 ↔ 实现文件/路由 ↔ 测试，逐行对账；缺一行即未完成。

---

## 3. 未实现清单与范围裁剪

- 砍 / 简化 / 延后任何 PRD 已冻结的功能 = 范围变更 → 触发询问闸门（[`confidence_decision.md`](confidence_decision.md)）：**先报告用户确认，再动代码**。
- 清单写入 task detail「未实现 / 简化清单」，为空写「无」；交付报告必须原样带出，不得省略。
- 实现期发现做不完（外部依赖 / 工作量超预期）→ `BLOCKED` 落盘 + 报告，不是留一堆占位符。

---

## 4. 交付报告模板（最终答复用户的消息必须含）

```text
1. 已实现：对照 DoD / 功能点逐条列出（含关键文件 / 路由）
2. 测试与门禁证据：make test / fake_code_scanner / verify_consistency 的命令与结果
3. 未实现与简化清单：显式列出（无则写「无」）
4. 自验方式：用户本地如何跑起来验证主路径
```

缺第 3 项 = 未按本协议交付。

---

## 5. 分档义务

| 档 | 完成前义务 |
|---|---|
| **S** | 扫描 0 命中；报告 3 行核对 |
| **M** | 扫描 0 命中 + DoD 映射表落盘 + 未实现清单显式 |
| **L** | M 义务 + 功能覆盖对账（PRD ↔ 原型 ↔ 实现 ↔ 测试）+ 交付报告四段齐 |

---

## 6. 与其他文件

- 提交前清单：[`quality_gates.md`](quality_gates.md) §2；测试方法：[`testing.md`](testing.md)；Mock 隔离：[`mock_contract_guide.md`](mock_contract_guide.md)；阶段 6 细则：[`spec_driven_lifecycle.md`](spec_driven_lifecycle.md)。
- 任务流转：`COMPLETED` 必须带 `--dod-audited`（[`task_state_machine.md`](task_state_machine.md)）；未过审计 → 回 `IN_PROGRESS` 或转 `BLOCKED`。
