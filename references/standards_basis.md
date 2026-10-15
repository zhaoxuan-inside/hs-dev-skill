# 阶段验收规范依据与转化边界

**何时读**：追溯验收规则来源、更新规范版本或需要更深领域规则时；日常执行直接读阶段清单，不要求联网重读所有原文。
**核对日期**：2026-10-15。以下是固定参考基线，不声明为最新版本，也不构成标准符合性认证。

## 1. 阅读范围与采用方式

本 Skill 的验收规则是针对 Agent 开发的原创项目规则。公开指南用于提取检查维度；只获取公开介绍的标准仅用于定位范围，不虚构条款号，不宣称已理解其付费全文。
外部标准不自动成为项目强制义务。先按规模/风险确定适用项；明确的用户指令、已确认业务约束及项目选定版本优先于通用示例。外部推荐与项目规则冲突时记录裁决。

| 来源 ID | 原始内容与阅读范围 | 本 Skill 的采用位置 |
|---|---|---|
| NASA-REQ | [NASA Appendix C](https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/)，阅读 C.1～C.4：用词、清晰度、完整性、一致性、追溯、正确性与可验证性 | DISC、PROD：拆分要求、显式假设、范围来源、可观察结果；不照搬航天工程全套流程 |
| GOV-NEEDS | [GOV.UK 用户需求指南](https://www.gov.uk/service-manual/user-research/start-by-learning-user-needs)，阅读用户、现状、证据、假设与持续验证部分 | DISC：先还原实际任务；缺少用户证据的推测须明确标记 |
| GOV-ALPHA | [GOV.UK Alpha 用户研究](https://www.gov.uk/service-manual/user-research/user-research-in-alpha)，阅读端到端服务与原型验证部分 | PROD：使用真实任务演练原型，记录差异；不能把截图认可等同业务验收 |
| ARC42 | [arc42 概览](https://arc42.org/overview/)与[检查清单建议](https://faq.arc42.org/questions/J-4/)，阅读十二个内容维度及按干系人需要裁剪的建议 | ARCH：上下文、结构、运行、部署、决策、质量和风险；不要求所有项目写满十二章 |
| P3C | [阿里 P3C 仓库](https://github.com/alibaba/p3c)及旧 GitBook 的[并发](https://github.com/alibaba/p3c/blob/master/p3c-gitbook/编程规约/并发处理.md)、[异常](https://github.com/alibaba/p3c/blob/master/p3c-gitbook/异常日志/异常处理.md)、[索引](https://github.com/alibaba/p3c/blob/master/p3c-gitbook/MySQL数据库/索引规约.md)、[单测](https://github.com/alibaba/p3c/blob/master/p3c-gitbook/单元测试.md)公开条目 | JAVA：线程/资源边界、错误处理、唯一性、测试；本次未逐条解析黄山版 PDF，不声称完整覆盖 |
| OAS | [OpenAPI 3.1.1](https://spec.openapis.org/oas/v3.1.1.html)，查阅结构、操作、参数、响应、Schema 和 Security 定义 | DETAIL：接口必须明确表达并校验；采用项目工具支持的方言，不能把语法正确当作业务正确 |
| ASVS | [OWASP ASVS 项目说明](https://owasp.org/projects/asvs)，阅读用途、版本化要求 ID 与机器可读格式说明 | ARCH/DELIV：安全检查须选定版本、条目和证据；本次未引入完整 ASVS 条目库，不能宣称 ASVS 全量通过 |

## 2. 仅作范围定位的标准

| 标准 | 官方公开范围 | 使用边界 |
|---|---|---|
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | 需求工程过程、信息项及其内容 | 支持需求工程的定位；具体 DISC/PROD 规则来自公开指南与项目设计，非逐条转录 |
| [ISO 9241-210:2019](https://committee.iso.org/standard/77520.html?browse=tc) | 交互系统以人为中心的设计 | 产品流程方向参考；没有据公开摘要生成详细强制条款 |
| [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) | 架构描述的结构与表达 | 约束文档关注点，不声称能由文档证明架构优劣 |
| [IEEE 1016-2009](https://standards.ieee.org/ieee/1016/4502/) | 软件设计描述 | 历史结构参考；不声称其为当前有效强制基线，采用前核对标准状态 |
| [ISO/IEC/IEEE 29119-3:2021](https://www.iso.org/standard/79429.html) | 测试文档模板 | 用于区分计划、规格、执行与结果；DELIV 的具体字段为本 Skill 自定 |
| [ISO/IEC 25010:2023](https://committee.iso.org/standard/78176.html) | 产品质量模型 | 提醒选择适用质量属性；具体阈值必须来自项目约束或测量，不从模型自动推导 |

## 3. 项目自定机制

阶段必须验收、开发者签收、证据绑定版本、来源变化后失效、任务覆盖对账和完成判定权限，均是本 Skill 为降低理解偏差与返工建立的机制；不归称任何外部标准原文。

每次更新记录来源版本/网页核对日期、实际阅读章节及受影响规则 ID。新增条款先写适用条件、可判定结果和证据，再接入清单；不能只增加“参考某标准”的链接。

阿里仓库明确提示旧 GitBook 与新版内容不一致；原目录 `alibaba.java-guide` 曾指向 formatter README，该页面不是完整开发手册。日常先用本地 JAVA 清单；需要完整阿里规约时读取所采用版本的原文，并按当前 JDK/框架裁剪。
