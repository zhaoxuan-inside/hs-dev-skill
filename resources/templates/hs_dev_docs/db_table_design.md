# 数据表设计文档：{table_name}

## 1. 表基础信息
- **表名**：`{table_name}`
- **说明**：{表业务含义}
- **所属模块**：`{model_name}`
- **主键策略**：Snowflake / UUID / Auto-Increment

---

## 2. 字段定义

| 字段名 | 类型 | 长度/精度 | 允许空 | 默认值 | 约束 / 索引 | 说明 |
|---|---|---|---|---|---|---|
| `id` | BIGINT / VARCHAR | 64 | 否 | 无 | PRIMARY KEY | 主键 ID |
| `created_at` | TIMESTAMP | - | 否 | CURRENT_TIMESTAMP | - | 创建时间 (UTC) |
| `updated_at` | TIMESTAMP | - | 否 | CURRENT_TIMESTAMP | - | 更新时间 (UTC) |
| `description`| VARCHAR | 255 | 是 | '' | - | 业务描述与备注 (禁止使用 desc) |
| `is_del` | BIGINT | - | 否 | 0 | INDEX(is_del, id) | 软删除标记 (0:未删, >0:删除时间戳) |
| `version` | INT | - | 否 | 1 | - | 乐观锁版本号 |
| `{business_col}` | ... | ... | ... | ... | ... | 业务字段 |

---

## 3. 索引清单
- `PRIMARY KEY (id)`
- `UK_{table_name}_{business_key} (is_del, {business_key})`：唯一键包含 `is_del` 以兼容软删除。
- `IDX_{table_name}_created_at (created_at)`

---

## 4. 迁移脚本映射 (Atomic V/U Sync)

| 版本号 | 脚本类型 | 脚本文件路径 | 描述 |
|---|---|---|---|
| `V1.0.0` | 前向迁移 (Forward) | `migrations/V1.0.0__init_{table_name}.sql` | 初始化 {table_name} 表结构 |
| `U1.0.0` | 回滚脚本 (Undo) | `migrations/U1.0.0__init_{table_name}.sql` | DROP TABLE {table_name} |
