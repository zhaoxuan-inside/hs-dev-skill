# 阶段验收记录：{task_id} / {stage}

> 使用 Skill 的 references/stage_acceptance.md。工作 todolist 完成后提交验收，禁止预填 PASS 或代签。

- 验收记录 ID：{acceptance_id}
- 阶段：{0A需求理解 / 0B产品冻结 / 1 / 2 / 3 / 4 / 5 / 6}
- 验收状态：DRAFT
- 本次范围与 change_size：{范围} / {S/M/L}
- 规则版本：{Skill版本 + 清单文件版本或内容摘要}
- 编写者：{agent_or_author}
- 验收人/明确委托范围：{开发者；已有委托须引用记录}

## 1. 输入与产出基线

| 类型 | 文档/代码路径 | 版本或内容摘要 | 标题锚点/关联 ID | 当前是否有效 |
|---|---|---|---|---|
| 输入 | {path} | {revision} | {anchor / REQ-ID} | 待核对 |
| 产出 | {path} | {revision} | {anchor} | 待核对 |

## 2. 工作 todolist

### 提交文档清单（阶段完成时也须完整展示在回复中）

合并计划/DoD、当前 checklist、实际产出与证据引用，包含本验收记录；逐项核对，不用目录或“见报告”代替。沿用输入标记为已验收基线，应交未交项保留 MISSING。记录保留相对路径；提交回复展示经实际解析的绝对路径和最终摘要。

| 文档名 | 工程相对路径/外部绝对路径 | 版本/摘要 | 审阅范围/规则 ID | 状态 |
|---|---|---|---|---|
| {文件名} | {path；内联时附标题锚点} | {revision；本记录自身摘要见最终工具输出} | {范围} | SUBMITTED |

从当前阶段清单逐项生成，保留规则 ID；完成操作不代表验收通过。

- [ ] {规则ID}：{需完成的工作及预期产物}

## 3. 适用性与验收检查

复制当前阶段所有规则；无关项保留为 NA 并给出理由，禁止直接删除。检查内容及通过标准须具体到本项目。

| 规则 ID | 项目检查内容与通过标准 | 适用性/NA理由 | 证据路径、版本与锚点 | 核对方式及执行结果 | 候选结果 | 验收人结论/记录 |
|---|---|---|---|---|---|---|
| {ID} | {可判定的标准} | 待确定 | 待补充 | 待执行 | PENDING | 待验收 |

候选结果：PENDING / PASS / FAIL / NA。外部规范引用附来源 ID 与版本，不假造条款号。

## 4. 问题、反例与范围差异

| 问题 ID | 原规则/场景 | 反例或差异 | 理解偏差/需求变化/工程缺陷 | 是否阻断及理由 | 裁决/负责人/时点 | 关闭证据 |
|---|---|---|---|---|---|---|
| {issue_id} | {id} | {差异} | {分类} | 待判定 | 待处理 | 待补充 |

## 5. 运行证据（无运行项写 NA 及原因）

| 命令/演练场景 | 环境与时间 | 代码基线 | 退出码/观察结果 | 报告位置及关联规则 |
|---|---|---|---|---|
| {command_or_scenario} | {env/time} | {commit_or_digest} | 待执行 | 待补充 |

## 6. 提交与最终验收

- 适用项统计：{PASS数} / {适用总数}；PENDING：{数}；FAIL：{数}
- NA 项及认可记录：{列表，或无}
- 未关闭阻断问题：{列表，或经核对后写无}
- Agent 候选结论：待提交（只能建议，不能代替验收）
- 开发者结论：待验收（ACCEPTED / REJECTED）
- 确认范围：{阶段、规则ID、文档/原型版本；引用既有确认时标出覆盖范围}
- 确认原文、消息位置/时间或签名：待补充
- 下一阶段：待本阶段验收通过

## 7. 变更与失效记录

| 变更来源及版本差异 | 受影响规则/需求 | 受影响下游文档/Pack | INVALIDATED 时间 | 重验范围与新确认记录 |
|---|---|---|---|---|
| {change} | {ids} | {paths} | {time} | 待重验 |

## 8. CLI 完成门禁记录

将以下 JSON 更新为真实记录。验收未通过时保持 `SUBMITTED` 或 `REJECTED`；开发者确认后才填写 `ACCEPTED`。提交任务为 `COMPLETED` 时将本文件路径传给 `task_manager.py --acceptance-record`。

<!-- HS_ACCEPTANCE_GATE_V1
{
  "schema_version": 1,
  "task_id": "{task_id}",
  "acceptance_status": "SUBMITTED",
  "baseline": {"id": "{reviewed_baseline_id}", "version": "{version}", "sha256": "{source_sha256}"},
  "requirements": [
    {"id": "{REQ-ID}", "result": "PENDING", "evidence": ""}
  ],
  "artifacts": ["{registered_artifact_id}"],
  "developer_confirmation": {
    "decision": "PENDING",
    "reviewer": "",
    "confirmed_at": "",
    "source": "",
    "excerpt": ""
  },
  "verification": {
    "tests": [
      {"command": "{实际测试命令}", "exit_code": null, "evidence": "{工程内报告路径}", "sha256": "{报告摘要}"}
    ]
  },
  "checks": [
    {"rule_id": "{rule_id}", "result": "PENDING", "evidence": "", "reason": ""}
  ],
  "dod": [
    {"criterion": "{验收标准}", "result": "PENDING", "evidence": ""}
  ],
  "unimplemented": []
}
HS_ACCEPTANCE_GATE_V1 -->
