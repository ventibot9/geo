"""
定期监控任务
"""

from typing import List, Dict
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from config import SCHEDULE_CONFIG, ENGINES, SEARCH_QUERIES
from database import get_db
from database.models import MonitorTask, KeywordStats
from engines import ChatGPTEngine, ClaudeEngine, ErnieEngine
from scraper import CitationExtractor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitorScheduler:
    """监控调度器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone=SCHEDULE_CONFIG["timezone"])
        self.db = get_db()
        self.extractor = CitationExtractor()
        self.engines: List = []

        # 初始化引擎
        self._init_engines()

    def _init_engines(self):
        """初始化AI引擎"""
        if ENGINES["chatgpt"]["enabled"]:
            self.engines.append(ChatGPTEngine(ENGINES["chatgpt"]))

        if ENGINES["claude"]["enabled"]:
            self.engines.append(ClaudeEngine(ENGINES["claude"]))

        if ENGINES["ernie"]["enabled"]:
            self.engines.append(ErnieEngine(ENGINES["ernie"]))

        logger.info(f"Initialized {len(self.engines)} engines")

    def start(self):
        """启动调度器"""
        # 添加监控任务
        monitor_hours = SCHEDULE_CONFIG["monitor_interval"]["hours"]
        self.scheduler.add_job(
            self.run_monitor_task,
            trigger=IntervalTrigger(hours=monitor_hours),
            id="monitor_task",
            name="Monitor AI Engines",
            replace_existing=True
        )

        # 添加报告任务
        report_days = SCHEDULE_CONFIG["report_interval"]["days"]
        self.scheduler.add_job(
            self.run_report_task,
            trigger=IntervalTrigger(days=report_days),
            id="report_task",
            name="Generate Report",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def run_monitor_task(self):
        """执行监控任务"""
        logger.info("Starting monitor task...")

        # 创建任务记录
        task = MonitorTask(
            task_name="AI Engine Monitor",
            task_type="monitor",
            status="running"
        )

        with self.db.session() as session:
            session.add(task)
            session.flush()
            task_id = task.id

        try:
            engines_queried = 0
            queries_executed = 0
            citations_found = 0

            # 生成查询
            queries = self._generate_queries()

            # 执行监控
            for engine in self.engines:
                if not engine.is_available():
                    logger.warning(f"Engine {engine.get_name()} not available")
                    continue

                engines_queried += 1

                for query in queries:
                    queries_executed += 1

                    # 查询引擎
                    result = engine.query(query)

                    if result.success:
                        # 提取引用
                        citations = self.extractor.extract_from_response(
                            engine_name=engine.get_name(),
                            query_text=query,
                            response_text=result.response,
                            confidence_score=engine.calculate_confidence(
                                engine.check_keywords_in_response(
                                    result.response,
                                    self.extractor.keywords
                                )
                            )
                        )

                        # 保存到数据库
                        citations_found += len(citations)
                        for citation in citations:
                            db_record = self.extractor.to_db_record(citation)
                            session.add(db_record)

                        logger.info(
                            f"Query {engine.get_name()}: {query} -> {len(citations)} citations"
                        )
                    else:
                        logger.error(f"Query failed: {result.error_message}")

            session.commit()

            # 更新任务状态
            task.status = "completed"
            task.end_time = datetime.now()
            task.engines_queried = engines_queried
            task.queries_executed = queries_executed
            task.citations_found = citations_found
            session.commit()

            logger.info(
                f"Monitor task completed: {queries_executed} queries, "
                f"{citations_found} citations found"
            )

        except Exception as e:
            logger.error(f"Monitor task failed: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.end_time = datetime.now()
            session.commit()

    def run_report_task(self):
        """执行报告任务"""
        logger.info("Starting report task...")

        task = MonitorTask(
            task_name="Report Generator",
            task_type="report",
            status="running"
        )

        with self.db.session() as session:
            session.add(task)
            session.flush()
            task_id = task.id

        try:
            # 更新关键词统计
            self._update_keyword_stats(session)

            # 生成报告（简化版）
            self._generate_simple_report(session)

            task.status = "completed"
            task.end_time = datetime.now()
            session.commit()

            logger.info("Report task completed")

        except Exception as e:
            logger.error(f"Report task failed: {e}")
            task.status = "failed"
            task.error_message = str(e)
            task.end_time = datetime.now()
            session.commit()

    def _generate_queries(self) -> List[str]:
        """生成查询列表"""
        queries = []

        for query_template in SEARCH_QUERIES:
            # 从关键词中抽取示例
            for category, kw_list in self.extractor.keywords.items():
                if kw_list:
                    example_keyword = kw_list[0]
                    queries.append(query_template.format(
                        company=example_keyword,
                        product=example_keyword,
                        brand=example_keyword
                    ))
                    break  # 每个模板只用一个示例

            if len(queries) >= 10:  # 限制查询数量
                break

        return queries

    def _update_keyword_stats(self, session):
        """更新关键词统计"""
        from datetime import timedelta

        # 获取最近24小时的数据
        yesterday = datetime.now() - timedelta(days=1)

        # 按关键词分组统计
        stats = session.query(CitationRecord).filter(
            CitationRecord.timestamp >= yesterday
        ).all()

        # 聚合统计
        keyword_stats = {}
        for record in stats:
            key = (record.keyword_found, record.engine_name)
            if key not in keyword_stats:
                keyword_stats[key] = {
                    "total": 0,
                    "exposure": 0,
                    "confidence": 0.0,
                    "count": 0
                }
            keyword_stats[key]["total"] += record.citation_count
            keyword_stats[key]["exposure"] += 1
            keyword_stats[key]["confidence"] += record.confidence_score
            keyword_stats[key]["count"] += 1

        # 更新或插入统计记录
        for (keyword, engine_name), stats_data in keyword_stats.items():
            avg_confidence = stats_data["confidence"] / stats_data["count"]

            # 检查是否已有今天的记录
            existing = session.query(KeywordStats).filter(
                KeywordStats.keyword == keyword,
                KeywordStats.engine_name == engine_name,
                KeywordStats.date >= yesterday
            ).first()

            if existing:
                existing.total_citations += stats_data["total"]
                existing.exposure_count += stats_data["exposure"]
                existing.avg_confidence = avg_confidence
            else:
                new_stat = KeywordStats(
                    keyword=keyword,
                    category="",
                    engine_name=engine_name,
                    total_citations=stats_data["total"],
                    exposure_count=stats_data["exposure"],
                    avg_confidence=avg_confidence
                )
                session.add(new_stat)

        session.commit()
        logger.info("Keyword stats updated")

    def _generate_simple_report(self, session):
        """生成简单报告"""
        # 这里可以生成更详细的报告文件
        logger.info("Simple report generated")

    def trigger_now(self):
        """手动触发一次监控任务"""
        logger.info("Manual trigger: running monitor task")
        self.run_monitor_task()
