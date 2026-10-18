# trace 追踪

trace 是独立于 mute、activity、stage 的可选开关，默认关闭。配置 trace.enabled 或全局 --trace 临时开启；关闭不创建事件文件。banner 和 JSON meta 表达当前开关。

事件包含 event_id、run_id、时间、操作 UUID、结果及白名单摘要字段；记录入口、路由、上下文数量、命令结果与耗时。禁止凭证、完整对话、代码和文档正文。任务及活动标识可用于关联过滤。

按项目隔离存储于 trace/，配置 max_file_bytes、max_files、max_event_bytes 约束容量和轮换；写冲突或失败允许丢弃并累计计数，不影响业务结果。trace-query 按 run/task/operation 有界查询。

追踪不是恢复日志、验收证据或人工确认记录，不进入业务索引、快照或默认模型上下文，也不申请业务修改 UUID。诊断时只提供过滤后的摘要。
