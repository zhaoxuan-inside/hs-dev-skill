# 语义上下文协议 v2

权威源文件保持唯一；语义索引是可重建派生数据。任务与验收引用 file 单元身份并绑定内容版本，索引重建本身不撤销业务确认。

## 请求

CLI：`python hs-dev-skill/scripts/hs_dev.py --root /project context @request.json`。
服务：`{"action":"context","request":{...}}`；不接受旧 paths/required 字段或旧 CLI 参数。

```json
{
  "goal": "定位创建用户的权限校验",
  "task_id": "可省略",
  "selectors": [
    {"path":"docs/api.md","scope":{"kind":"section","title":"权限"},"required":true},
    {"path":"src/users.py","scope":{"kind":"symbol","name":"UserService.create"}}
  ],
  "query": "创建用户 权限",
  "budget": {"max_output_bytes":48000,"max_output_tokens":0},
  "delivery":"full",
  "held":[]
}
```

scope 支持 file、section/title、symbol/name、lines/start/end；行号从 1 开始且两端包含。unit_id 选择器不能与 path/scope 混用。文件读取必须显式 scope=file，不再默认前 80 行。goal 是解释性目标，实际检索由 query 和 selectors 驱动，不进行额外模型调用。

## 数据组织

每个源具有 `file:<path>` 单元。Markdown 按标题层级建立父子章节，不按固定行数截断；围栏代码内标题不参与切分。章节默认 ID 来自路径与标题层级，可通过标题 `{#anchor}` 保持标题修改后的身份，或在章节内声明全局稳定身份：

```html
<!-- hs-unit: {"id":"api.user.auth","requires":["unit:security.roles"],"references":["unit:api.examples"]} -->
```

显式 ID 对应 `unit:api.user.auth`，跨文件唯一。重复标题与重复定义可以被索引，但按标题/符号选择时返回歧义候选；持久引用应使用显式 ID。章节原子交付；大章节应由作者划分有意义的子章节。

Python 使用 `symbol:<path>:<qualified_name>`，包含装饰器；同名方法通过类名区分，嵌套函数通过限定名区分。符号依赖文件前导上下文，方法还依赖类头。其他语言与配置目前按完整文件原子组织，可通过明确行区间读取；不声称支持其语法级符号解析。

unit_id 表示身份，unit_revision 对章节、符号和行区间表示规范化正文摘要（统一行分隔符，不含结尾换行），对全文和任务材料表示原始字节摘要；source_digest 表示权威原始字节摘要。父章节、全文和子单元可以范围重叠，交付时合并正文，不复制内容。file 内容版本由原始字节决定，二进制验收材料同样适用。

requires 为必要依赖，references 为可选参考。装配继承父单元的必要约束，不自动交付全部父正文；闭包检测循环、缺失和展开限制。查询顺序由 FTS 相关性决定，相同得分优先更小范围，再按身份排序。

## 返回与完整性

结果包含 schema_version=2、publication_id、units、coverage、missing、deferred、body 与 usage。units 记录身份、版本、来源、范围和选择理由；body 按路径与合并区间仅交付一份正文。

- complete：必要材料完整；可选材料可能因预算延迟，检查 deferred。
- needs_selection：显式定位存在歧义；检查 candidates 后重新指定。
- material_missing：显式材料或必要依赖缺失、循环、超出展开限制。
- insufficient_budget：必要集合无法整体装入；body 为空，返回所需成本。

missing/deferred 明细最多 8 项，coverage 保留总数。必要材料不截断、不自动摘要替代。版本变化或索引失配拒绝整个请求。只有 status=complete 才能作为完整上下文消费；上下文覆盖不代表业务验收通过。

## 预算

context 配置：max_output_bytes=48000、max_output_tokens=0、tokenizer=""、max_read_bytes=8000000、max_units=128、max_candidates=20、max_dependency_depth=8。请求只能收紧输出预算。输出字节最小 1024，最大 48000；读取总量与单文件大小均受限，同请求文件正文只解码一次，末尾另外复核摘要。

预算统计整个结果对象的紧凑 UTF-8 JSON，包括正文、引用、缺失项与 usage。CLI 外层 meta/result 封装及宿主消息格式属于传输开销，不计入结果预算。服务以相同紧凑格式发送结果；文本展示是供人阅读的呈现。

默认只执行字节硬限制；estimated_tokens 为 UTF-8 字节保守估算，tokens=null，token_limit_enforced=false。精确 tokenizer 可安装可选依赖 `.[tokens]`，配置 tokenizer=cl100k_base 或 o200k_base，并提前将官方 ranks 文件放入 TIKTOKEN_CACHE_DIR 对应缓存。请求期间不下载 tokenizer 数据。未配置 tokenizer 时 token 额度不执行，并明确标记。

使用 tokenizer 时 tokens 统计完整结果但将 tokens 自身设为 null，以避免自引用计数振荡；count_kind 明示此口径。硬限制另外计算最终含计数字段的真实序列化结果，不依赖估算。max_output_tokens=0 表示未启用 token 硬限制。

## 增量交付

调用方传入仍可见的 `held:[{"unit_id":"...","unit_revision":"..."}]` 并指定 delivery=delta。匹配单元标为 held、正文省略；新增和变化单元交付正文。full 忽略持有信息并完整交付选中内容。源校验不会因为正文省略而跳过。

新会话或上下文压缩后，调用方必须清空或重新核实持有清单；服务端不猜测模型记忆。未变化单元的位置可能移动，返回位置与 source_digest 始终来自当前发布。

## 不兼容切换

旧上下文参数、结果字段和 max_bytes 配置已删除。调用方必须同时更新。旧派生索引由 parser_revision=5 明确拒绝，源文件不变时通过显式 repair-index 重建。不要重建工程或删除任务、证据、恢复数据。

旧依赖记录必须使用原始确认依据显式重新绑定，系统不代签、不自动升级确认。dependency-bind 的第四个参数是 unit_id（例如 `file:contract.md`、`unit:contract.api`），验收材料也必须提供 `--unit-id`。两者均按所选单元的 unit_revision 失效，不受同文件其他章节修改影响；二进制文件使用 `file:<path>`，按原始字节摘要绑定。索引只保存可重建的语义单元，权威源摘要仅由 publication manifest 持有。
