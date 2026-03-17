# 监控方法说明

## 监控原理

本服务通过定期查询各大AI引擎，检查其回答中是否包含企业关键词，从而监控企业在AI引擎中的引用情况。

## 监控流程

```
1. 生成查询
   ↓
2. 查询AI引擎
   ↓
3. 获取响应
   ↓
4. 提取关键词匹配
   ↓
5. 计算置信度
   ↓
6. 存储引用数据
   ↓
7. 生成统计和报告
```

## 详细步骤

### 1. 查询生成

使用预定义的查询模板和关键词组合生成查询：

```python
# 查询模板
SEARCH_QUERIES = [
    "{company} 是什么",
    "{company} 的优势",
    "{company} vs 竞品",
    "{product} 使用教程",
    "{brand} 官网"
]

# 示例查询
"GEO 是什么"
"GEO 的优势"
"GEO vs 竞品"
"地图服务 使用教程"
"GEO云 官网"
```

### 2. AI引擎查询

支持三种AI引擎：

#### ChatGPT（API方式）
- 使用OpenAI API
- 模型：gpt-3.5-turbo
- 返回完整响应文本

#### Claude（API方式）
- 使用Anthropic API
- 模型：claude-3-haiku-20240307
- 返回完整响应文本

#### 文心一言（搜索方式）
- 通过百度搜索获取结果
- 提取搜索结果标题和摘要
- 返回搜索结果摘要

### 3. 关键词匹配

在AI响应中搜索关键词：

```python
def check_keywords(response: str, keywords: Dict[str, List[str]]) -> List[Dict]:
    """
    检查响应中是否包含关键词

    Args:
        response: AI响应文本
        keywords: {category: [keywords]}

    Returns:
        [{keyword, category, count}]
    """
    found = []
    for category, kw_list in keywords.items():
        for keyword in kw_list:
            if keyword.lower() in response.lower():
                count = response.lower().count(keyword.lower())
                found.append({
                    "keyword": keyword,
                    "category": category,
                    "count": count
                })
    return found
```

### 4. 置信度计算

根据关键词匹配情况计算置信度：

```python
def calculate_confidence(found_keywords: List[Dict]) -> float:
    """
    计算置信度分数 (0-1)

    评分规则：
    - 基础分：0.5（至少匹配一个关键词）
    - 数量加成：每个关键词匹配+0.1，最多+0.3
    - 类别加成：匹配多个类别+0.2
    - 最高分：1.0
    """
    if not found_keywords:
        return 0.0

    score = 0.5
    keyword_count = sum(kw["count"] for kw in found_keywords)
    score += min(keyword_count * 0.1, 0.3)

    categories = set(kw["category"] for kw in found_keywords)
    if len(categories) > 1:
        score += 0.2

    return min(score, 1.0)
```

### 5. 数据存储

每条引用记录包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| engine_name | String(50) | 引擎名称 |
| query_text | Text | 查询文本 |
| response_text | Text | AI响应文本 |
| keyword_found | String(100) | 匹配到的关键词 |
| keyword_category | String(50) | 关键词分类 |
| citation_count | Integer | 引用次数 |
| confidence_score | Float | 置信度分数 |
| timestamp | DateTime | 记录时间 |
| raw_response | Text | 原始响应（JSON） |

### 6. 统计和报告

#### 每日统计
- 总查询次数
- 总引用次数
- 涉及关键词数
- 平均置信度

#### 按引擎统计
- 各引擎引用数
- 各引擎涉及关键词
- 各引擎平均置信度

#### 按关键词统计
- 每个关键词的引用次数
- 每个关键词出现的引擎
- 每个关键词的分类

#### 趋势分析
- 7天每日趋势
- 热门关键词排行

### 7. 报告生成

生成两种格式的报告：

#### JSON格式
```json
{
  "date": "2026-03-17",
  "summary": {
    "total_queries": 10,
    "total_citations": 25,
    "unique_keywords": 5,
    "avg_confidence": 0.75
  },
  "by_engine": {...},
  "by_keyword": {...},
  "by_category": {...},
  "trends": {...}
}
```

#### 文本格式
```
============================================================
GEO平台AI引用监控报告 - 2026-03-17
============================================================

【总体统计】
查询次数: 10
引用次数: 25
涉及关键词: 5
平均置信度: 0.75

【按引擎统计】
  chatgpt:
    引用数: 15
    关键词: GEO, 地图服务, GeoAPI
    置信度: 0.80

  claude:
    引用数: 10
    关键词: GEO, GeoMap
    置信度: 0.70
...
```

## 调度配置

监控任务每6小时执行一次，报告任务每天生成一次：

```python
SCHEDULE_CONFIG = {
    "monitor_interval": {"hours": 6},
    "report_interval": {"days": 1},
    "timezone": "Asia/Shanghai"
}
```

## 使用方法

### 启动服务
```bash
python main.py
```

### 运行一次监控
```bash
python main.py --once
```

### 生成报告
```bash
python main.py --report
```

## 数据清理

建议定期清理旧数据以避免数据库过大：

```sql
-- 删除30天前的数据
DELETE FROM citation_records
WHERE timestamp < datetime('now', '-30 days');
```

## 注意事项

1. API密钥安全
   - 不要将API密钥提交到版本控制
   - 使用环境变量存储密钥

2. 速率限制
   - 注意各API的速率限制
   - 适当调整监控间隔

3. 成本控制
   - API调用会产生费用
   - 根据预算调整查询频率

4. 数据准确性
   - 关键词匹配可能误报
   - 人工定期复核重要结果
