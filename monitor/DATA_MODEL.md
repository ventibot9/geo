# 数据模型设计

## 数据库架构

本服务使用SQLite数据库，包含4张核心表。

## ER图

```
+----------------+         +---------------------+
| EngineConfig   |         | CitationRecord     |
+----------------+         +---------------------+
| id (PK)        |<--------| engine_name (FK)    |
| engine_name    |         | id (PK)             |
| enabled        |         | query_text          |
| api_endpoint   |         | response_text       |
| model_name     |         | keyword_found       |
| rate_limit     |         | keyword_category    |
| last_used      |         | citation_count      |
| success_count  |         | confidence_score    |
| failure_count  |         | timestamp           |
+----------------+         | raw_response        |
                            +---------------------+
                                     |
                                     v
                            +---------------------+
                            | KeywordStats        |
                            +---------------------+
                            | id (PK)             |
                            | keyword             |
                            | category            |
                            | engine_name         |
                            | total_citations     |
                            | date                |
                            | exposure_count      |
                            | avg_confidence      |
                            +---------------------+

+----------------+
| MonitorTask    |
+----------------+
| id (PK)        |
| task_name      |
| task_type      |
| status         |
| start_time     |
| end_time       |
| engines_queried|
| queries_executed|
| citations_found|
| error_message  |
+----------------+
```

## 表结构详解

### 1. CitationRecord（引用记录表）

存储每次查询中发现的企业关键词引用记录。

| 字段名 | 类型 | 约束 | 索引 | 说明 |
|--------|------|------|------|------|
| id | Integer | PK | - | 主键，自增 |
| engine_name | String(50) | NOT NULL | INDEX | 引擎名称（chatgpt/claude/ernie） |
| query_text | Text | NOT NULL | - | 查询文本 |
| response_text | Text | NULL | - | AI响应文本（可能很长） |
| keyword_found | String(100) | NULL | - | 匹配到的关键词 |
| keyword_category | String(50) | NULL | - | 关键词分类 |
| citation_count | Integer | DEFAULT 0 | - | 该关键词在响应中出现次数 |
| confidence_score | Float | DEFAULT 0.0 | - | 置信度分数 (0-1) |
| timestamp | DateTime | DEFAULT NOW | INDEX | 记录时间 |
| raw_response | Text | NULL | - | 原始响应JSON（用于调试） |

**索引设计：**
- `idx_engine_name`: engine_name - 加速按引擎查询
- `idx_timestamp`: timestamp - 加速时间范围查询

**用途：**
- 记录每次查询中发现的关键词引用
- 支持按时间、引擎、关键词查询
- 用于生成统计报告

**示例数据：**
```json
{
  "id": 1,
  "engine_name": "chatgpt",
  "query_text": "GEO 是什么",
  "response_text": "GEO是一款专业的地理信息平台...",
  "keyword_found": "GEO",
  "keyword_category": "企业名称",
  "citation_count": 3,
  "confidence_score": 0.8,
  "timestamp": "2026-03-17 10:30:00",
  "raw_response": null
}
```

---

### 2. EngineConfig（引擎配置表）

存储AI引擎的配置和统计信息。

| 字段名 | 类型 | 约束 | 索引 | 说明 |
|--------|------|------|------|------|
| id | Integer | PK | - | 主键，自增 |
| engine_name | String(50) | UNIQUE, NOT NULL | - | 引擎名称 |
| enabled | Boolean | DEFAULT TRUE | - | 是否启用 |
| api_endpoint | String(255) | NULL | - | API端点URL |
| model_name | String(100) | NULL | - | 使用的模型名称 |
| rate_limit | Integer | DEFAULT 100 | - | 速率限制（次/小时） |
| last_used | DateTime | NULL | - | 最后使用时间 |
| success_count | Integer | DEFAULT 0 | - | 成功次数 |
| failure_count | Integer | DEFAULT 0 | - | 失败次数 |

**用途：**
- 管理AI引擎配置
- 统计引擎使用情况
- 控制引擎开关

**示例数据：**
```json
{
  "id": 1,
  "engine_name": "chatgpt",
  "enabled": true,
  "api_endpoint": "https://api.openai.com/v1",
  "model_name": "gpt-3.5-turbo",
  "rate_limit": 100,
  "last_used": "2026-03-17 10:30:00",
  "success_count": 150,
  "failure_count": 5
}
```

---

### 3. KeywordStats（关键词统计表）

存储关键词的每日统计信息，用于趋势分析。

| 字段名 | 类型 | 约束 | 索引 | 说明 |
|--------|------|------|------|------|
| id | Integer | PK | - | 主键，自增 |
| keyword | String(100) | NOT NULL | INDEX | 关键词 |
| category | String(50) | NOT NULL | - | 关键词分类 |
| engine_name | String(50) | NOT NULL | - | 引擎名称 |
| total_citations | Integer | DEFAULT 0 | - | 总引用次数 |
| date | DateTime | DEFAULT NOW | INDEX | 统计日期 |
| exposure_count | Integer | DEFAULT 0 | - | 曝光次数（独立查询数） |
| avg_confidence | Float | DEFAULT 0.0 | - | 平均置信度 |

**索引设计：**
- `idx_keyword`: keyword - 加速按关键词查询
- `idx_date`: date - 加速按日期查询

**用途：**
- 聚合关键词统计
- 支持趋势分析
- 生成热门关键词排行

**示例数据：**
```json
{
  "id": 1,
  "keyword": "GEO",
  "category": "企业名称",
  "engine_name": "chatgpt",
  "total_citations": 45,
  "date": "2026-03-17",
  "exposure_count": 15,
  "avg_confidence": 0.75
}
```

---

### 4. MonitorTask（监控任务记录表）

记录每次监控任务的执行情况。

| 字段名 | 类型 | 约束 | 索引 | 说明 |
|--------|------|------|------|------|
| id | Integer | PK | - | 主键，自增 |
| task_name | String(100) | NOT NULL | - | 任务名称 |
| task_type | String(50) | NOT NULL | - | 任务类型（monitor/report） |
| status | String(20) | NOT NULL | - | 状态（running/completed/failed） |
| start_time | DateTime | DEFAULT NOW | - | 开始时间 |
| end_time | DateTime | NULL | - | 结束时间 |
| engines_queried | Integer | DEFAULT 0 | - | 查询的引擎数 |
| queries_executed | Integer | DEFAULT 0 | - | 执行的查询数 |
| citations_found | Integer | DEFAULT 0 | - | 发现的引用数 |
| error_message | Text | NULL | - | 错误信息 |

**用途：**
- 跟踪任务执行历史
- 监控任务健康状态
- 审计日志

**示例数据：**
```json
{
  "id": 1,
  "task_name": "AI Engine Monitor",
  "task_type": "monitor",
  "status": "completed",
  "start_time": "2026-03-17 10:00:00",
  "end_time": "2026-03-17 10:05:30",
  "engines_queried": 3,
  "queries_executed": 15,
  "citations_found": 42,
  "error_message": null
}
```

---

## 数据关系

### 引用记录 → 引擎配置
- `CitationRecord.engine_name` → `EngineConfig.engine_name`
- 一对多：一个引擎可以有多条引用记录

### 引用记录 → 关键词统计
- 通过 `keyword` 和 `engine_name` 关联
- 统计表是引用记录的聚合

### 监控任务 → 引用记录
- 任务执行期间产生多条引用记录
- 任务中的 `citations_found` 统计记录数

## 数据增长预估

假设配置：
- 监控引擎：3个
- 每次查询数：5个
- 监控间隔：6小时/次
- 每条响应平均匹配：2-3个关键词

**每日数据增长：**
- 查询次数：3 × 5 × 4 = 60次/天
- 引用记录：60 × 3 = 180条/天
- 关键词统计：每个关键词每天1条，约15条/天
- 监控任务：5条/天（4次监控 + 1次报告）

**每月数据增长：**
- 引用记录：约5,400条
- 关键词统计：约450条
- 监控任务：约150条

## 数据清理策略

### 引用记录
- 保留期：30天
- 清理策略：每月清理30天前的数据

### 关键词统计
- 保留期：1年
- 清理策略：每年清理1年前的数据

### 监控任务
- 保留期：90天
- 清理策略：每季度清理90天前的数据

### 引擎配置
- 永久保留
- 定期更新统计数据

## 查询示例

### 查询最近7天的引用记录
```sql
SELECT * FROM citation_records
WHERE timestamp >= datetime('now', '-7 days')
ORDER BY timestamp DESC;
```

### 按引擎统计引用数
```sql
SELECT engine_name, COUNT(*) as total
FROM citation_records
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY engine_name;
```

### 查询热门关键词
```sql
SELECT keyword, SUM(citation_count) as total
FROM citation_records
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY keyword
ORDER BY total DESC
LIMIT 10;
```

### 查询任务执行历史
```sql
SELECT * FROM monitor_tasks
ORDER BY start_time DESC
LIMIT 20;
```

## 扩展性考虑

### 未来可能的扩展

1. **添加更多引擎**
   - 在 `EngineConfig` 中添加新记录
   - 代码中实现新的引擎类

2. **支持多语言**
   - 添加 `language` 字段
   - 区分不同语言的关键词

3. **支持自定义监控策略**
   - 添加 `MonitoringStrategy` 表
   - 配置不同关键词的监控频率

4. **支持实时通知**
   - 添加 `AlertRule` 表
   - 配置告警规则

5. **支持数据导出**
   - 添加 `ExportHistory` 表
   - 记录导出历史

### 性能优化

1. **分表策略**
   - 按月分表存储引用记录
   - 减少单表数据量

2. **缓存策略**
   - 缓存热门关键词统计
   - 减少实时计算

3. **读写分离**
   - 统计查询走只读副本
   - 写入操作走主库

4. **归档策略**
   - 旧数据归档到历史表
   - 主表只保留热数据
