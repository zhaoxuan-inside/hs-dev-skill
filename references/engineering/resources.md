# 工程资源

代码src、配置config、测试tests、Mock数据mock/data、Mock服务mock/services分别管理。运行参数配置化，业务状态和协议值用常量枚举，凭证注入。不机械配置正常语法初值。

外部服务按真实HTTP等协议建立独立Mock，客户端只配置地址。未知契约明确标记，模拟不能代替真实集成。环境dev/dev.mock/test/test.mock/sandbox/online显式选择，默认→环境→Mock覆盖→注入，预发正式禁用Mock。

表结构Markdown表格包括字段类型空值默认约束语义；接口包括输入输出错误访问；方法包括前后置、不变量、副作用和依赖。调用用Mermaid，实际接口方法任务逐对象关联测试及证据。
