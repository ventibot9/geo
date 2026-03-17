# GEO Platform - Monitor 引用监控服务详细规范

## 文档信息
- **版本**: v1.0.0
- **模块**: Citation Monitor Service
- **日期**: 2026-03-17
- **维护者**: GEO Platform Team

---

## 1. 模块职责

### 1.1 核心功能
1. **AI 引擎查询**
   - ChatGPT (OpenAI API)
   - Claude (Anthropic API)
   - 文心一言 (搜索方式)

2. **引用数据提取**
   - 关键词匹配
   - 置信度计算 (0-1)

3. **定期监控**
   - 每 6 小时执行一次
   - 多引擎并发查询

4. **统计分析**
   - 趋势分析
   - 热门关键词排行
   - 引用增长率计算

---

## 2. AI 引擎查询接口

### 2.1 引擎基类
```python
from abc import ABC, abstractmethod

class BaseAIEngine(ABC):
    """AI 引擎查询基类"""

    @abstractmethod
    async def query(self, keywords: list, query_template: str) -> dict:
        """查询 AI 引擎"""
        pass

    @abstractmethod
    def extract_citations(self, response: str, keywords: list) -> dict:
        """提取引用数据"""
        pass
```

### 2.2 ChatGPT 引擎
```python
class ChatGPTEngine(BaseAIEngine):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)

    async def query(self, keywords: list, query_template: str) -> dict:
        """查询 ChatGPT"""
        # 构建查询
        query = query_template.format(keyword=", ".join(keywords))

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个搜索引擎，帮助用户查找信息。请客观、简洁地回答。"
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        return {
            'engine': 'chatgpt',
            'query': query,
            'response': response.choices[0].message.content,
            'tokens_used': response.usage.total_tokens
        }

    def extract_citations(self, response: str, keywords: list) -> dict:
        """提取引用数据"""
        response_lower = response.lower()

        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)

        # 计算置信度
        confidence = self._calculate_confidence(found_keywords, len(keywords))

        return {
            'engine': 'chatgpt',
            'found_keywords': found_keywords,
            'found_count': len(found_keywords),
            'total_keywords': len(keywords),
            'confidence': confidence
        }

    def _calculate_confidence(self, found: list, total: int) -> float:
        """计算置信度"""
        if total == 0:
            return 0.0

        base_score = 0.5 if len(found) >= 1 else 0.0
        count_bonus = min(len(found) * 0.1, 0.3)  # 最多加 0.3
        category_bonus = 0.2 if len(found) > 1 else 0.0

        return min(base_score + count_bonus + category_bonus, 1.0)
```

### 2.3 Claude 引擎
```python
class ClaudeEngine(BaseAIEngine):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def query(self, keywords: list, query_template: str) -> dict:
        """查询 Claude"""
        query = query_template.format(keyword=", ".join(keywords))

        message = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )

        return {
            'engine': 'claude',
            'query': query,
            'response': message.content[0].text,
            'tokens_used': message.usage.input_tokens + message.usage.output_tokens
        }

    def extract_citations(self, response: str, keywords: list) -> dict:
        """提取引用数据"""
        response_lower = response.lower()

        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)

        confidence = self._calculate_confidence(found_keywords, len(keywords))

        return {
            'engine': 'claude',
            'found_keywords': found_keywords,
            'found_count': len(found_keywords),
            'total_keywords': len(keywords),
            'confidence': confidence
        }
```

### 2.4 文心一言引擎
```python
import aiohttp
from bs4 import BeautifulSoup

class ErnieEngine(BaseAIEngine):
    def __init__(self):
        self.base_url = "https://www.baidu.com/s"

    async def query(self, keywords: list, query_template: str) -> dict:
        """查询文心一言 (搜索方式)"""
        query = query_template.format(keyword=" ".join(keywords))

        params = {
            'wd': query,
            'rn': 50  # 获取 50 条结果
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                html = await response.text()

        return {
            'engine': 'wenxin',
            'query': query,
            'response': html,
            'tokens_used': 0
        }

    def extract_citations(self, response: str, keywords: list) -> dict:
        """提取引用数据"""
        soup = BeautifulSoup(response, 'lxml')
        search_results = soup.find_all('div', class_='result')

        found_keywords = []
        for result in search_results:
            text = result.get_text().lower()
            for keyword in keywords:
                if keyword.lower() in text:
                    found_keywords.append(keyword)
                    break  # 每个结果只统计一次

        confidence = self._calculate_confidence(found_keywords, len(keywords))

        return {
            'engine': 'wenxin',
            'found_keywords': found_keywords,
            'found_count': len(found_keywords),
            'total_keywords': len(keywords),
            'confidence': confidence
        }
```

---

## 3. 定时任务调度

### 3.1 APScheduler 配置
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job(
    CronTrigger.from_crontab('0 */6 * * *'),  # 每 6 小时
    id='monitor_job'
)
async def monitor_task():
    """定时监控任务"""
    logger.info("开始引用监控任务")

    # 获取所有活跃企业
    enterprises = await get_active_enterprises()

    for enterprise in enterprises:
        # 获取企业关键词
        keywords = await get_enterprise_keywords(enterprise['id'])

        # 多引擎并发查询
        engines = [
            ChatGPTEngine(openai_key),
            ClaudeEngine(anthropic_key),
            ErnieEngine()
        ]

        results = await asyncio.gather(*[
            engine.query(keywords, "{keyword}")
            for engine in engines
        ])

        # 提取引用数据
        for engine, result in zip(engines, results):
            citations = engine.extract_citations(result['response'], keywords)

            # 存储到数据库
            await save_citation_data(
                enterprise_id=enterprise['id'],
                engine=citations['engine'],
                keywords=keywords,
                citations=citations
            )

    logger.info("引用监控任务完成")
```

### 3.2 报告生成任务
```python
@scheduler.scheduled_job(
    CronTrigger.from_crontab('0 0 * * *'),  # 每天凌晨
    id='report_job'
)
async def generate_daily_report():
    """生成日报"""
    logger.info("开始生成日报")

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 聚合数据
    report = await generate_daily_aggregation(yesterday)

    # 保存报告
    await save_report(report)

    # 发送通知 (可选)
    await send_report_notification(report)

    logger.info(f"日报生成完成: {yesterday}")
```

---

## 4. 数据聚合与统计

### 4.1 趋势分析
```python
async def analyze_trends(enterprise_id: str, period: int = 30) -> dict:
    """分析引用趋势"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period)

    # 查询引用数据
    citations = await db.citation_data.find_many({
        'enterprise_id': enterprise_id,
        'date': {
            '$gte': start_date,
            '$lte': end_date
        }
    })

    # 按日期分组
    daily_data = {}
    for citation in citations:
        date_str = citation['date'].strftime('%Y-%m-%d')
        if date_str not in daily_data:
            daily_data[date_str] = []
        daily_data[date_str].append(citation)

    # 计算每日引用数
    trend = []
    for date_str, data in daily_data.items():
        total = sum(d['count'] for d in data)
        trend.append({
            'date': date_str,
            'count': total,
            'avg_confidence': sum(d['confidence'] for d in data) / len(data)
        })

    # 计算增长率
    if len(trend) >= 2:
        recent_avg = sum(t[-7:]['count'] for t in trend) / 7
        previous_avg = sum(t[-14:-7]['count'] for t in trend) / 7
        growth_rate = ((recent_avg - previous_avg) / previous_avg) * 100
    else:
        growth_rate = 0

    return {
        'period_days': period,
        'trend': trend,
        'avg_daily': sum(t['count'] for t in trend) / len(trend),
        'growth_rate': round(growth_rate, 2)
    }
```

### 4.2 热门关键词排行
```python
async def analyze_top_keywords(enterprise_id: str, limit: int = 10) -> list:
    """分析热门关键词"""
    # 聚合关键词统计数据
    pipeline = [
        {
            '$match': {'enterprise_id': enterprise_id},
            '$group': {
                '_id': '$keyword',
                'total': {'$sum': '$count'},
                'avg_confidence': {'$avg': '$confidence'},
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'total': -1},
            '$limit': limit
        }
    ]

    results = await db.citation_stats.aggregate(pipeline)

    # 计算趋势
    top_keywords = []
    for result in results:
        # 查询最近 7 天的数据
        recent_data = await db.citation_stats.find({
            'keyword': result['_id'],
            'date': {'$gte': datetime.now() - timedelta(days=7)}
        })

        if len(recent_data) > 0:
            recent_count = sum(d['count'] for d in recent_data)
            trend = 'up' if recent_count > result['total'] else 'down'
        else:
            trend = 'stable'

        top_keywords.append({
            'rank': len(top_keywords) + 1,
            'keyword': result['_id'],
            'total_count': result['total'],
            'avg_confidence': round(result['avg_confidence'], 2),
            'trend': trend
        })

    return top_keywords
```

---

## 5. 数据模型

### 5.1 CitationRecord (引用记录)
```python
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime

class CitationRecord(Base):
    __tablename__ = 'citation_records'

    id = Column(String, primary_key=True)
    engine_name = Column(String, nullable=False)  # chatgpt, claude, wenxin
    query_text = Column(String, nullable=False)
    keyword_found = Column(String)  # JSON 数组
    citation_count = Column(Integer, default=0)
    confidence_score = Column(Float)  # 0-1
    timestamp = Column(DateTime, default=datetime.utcnow)
```

### 5.2 EngineConfig (引擎配置)
```python
class EngineConfig(Base):
    __tablename__ = 'engine_configs'

    engine_name = Column(String, primary_key=True)
    enabled = Column(Boolean, default=True)
    api_endpoint = Column(String)
    model_name = Column(String)
    api_key = Column(String)  # 加密存储
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    last_used = Column(DateTime)
```

### 5.3 KeywordStats (关键词统计)
```python
class KeywordStats(Base):
    __tablename__ = 'keyword_stats'

    id = Column(String, primary_key=True)
    keyword = Column(String, nullable=False)
    category = Column(String)
    engine_name = Column(String, nullable=False)
    total_citations = Column(Integer, default=0)
    exposure_count = Column(Integer, default=0)  # AI 引擎曝光次数
    avg_confidence = Column(Float)
    date = Column(DateTime, nullable=False)  # 统计日期 (精确到天)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

**文档版本**: v1.0.0
**最后更新**: 2026-03-17
**下次审查**: 2026-04-17
