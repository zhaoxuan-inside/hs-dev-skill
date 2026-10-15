---
name: hs-dev-frontend
description: Design or implement UI, design tokens, responsive states, accessibility, and frontend module structure within the selected process and accepted product behavior.
license: MIT
---

# 界面、前端结构与交互实现

本 Skill 属于 hs-dev-skill 的功能轴。完整包共享 scripts、references 和 resources；[运行与交接协议](../../references/subskill_contract.md)定义路径、依赖及直接调用规则。

## 职责与边界

只处理界面与前端实现；产品业务流程归 product，系统边界归 architecture，公共 API 语义归 backend。

## 输入

当前过程/阶段、产品场景、目标终端、既有 DESIGN.md 与接口契约。

## 执行

1. 先继承已有设计语言；未定方向时提出具体参照，不能自行覆盖产品操作方式。
2. 设计阶段提供目标终端的界面结构、适用多态和交互原型；与产品场景和 Gherkin 对账。
3. 实现阶段按已验收组件/状态与接口完成代码，保护草稿、恢复路径及键盘访问。
4. 验证渲染、网络与控制台及适用 a11y/性能指标，将证据交 testing/当前过程。

## 输出与验收

按当前阶段输出原型、Tokens/组件结构或实际前端代码及运行证据。

遵循适用 PROD/DETAIL/IMPL/DELIV 项；无 UI 不加载；EXPLORE 下只解释，不生成页面或改代码。

## 按需读取

- [frontend_arch](../../references/frontend_arch.md)
- [frontend_aesthetic](../../references/frontend_aesthetic.md)
- [frontend_craft](../../references/frontend_craft.md)
- [design_md](../../references/design_md.md)
