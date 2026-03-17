"""
数据库模型定义
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CitationRecord(Base):
    """引用记录表"""
    __tablename__ = "citation_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    engine_name = Column(String(50), nullable=False, index=True)  # 引擎名称
    query_text = Column(Text, nullable=False)  # 查询文本
    response_text = Column(Text)  # AI响应文本
    keyword_found = Column(String(100))  # 匹配到的关键词
    keyword_category = Column(String(50))  # 关键词分类：企业名称/产品名称/品牌词
    citation_count = Column(Integer, default=0)  # 引用次数
    confidence_score = Column(Float, default=0.0)  # 置信度分数
    timestamp = Column(DateTime, default=datetime.now, index=True)  # 记录时间
    raw_response = Column(Text)  # 原始响应（JSON）

    def __repr__(self):
        return f"<CitationRecord(id={self.id}, engine={self.engine_name}, keyword={self.keyword_found})>"


class EngineConfig(Base):
    """引擎配置表"""
    __tablename__ = "engine_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    engine_name = Column(String(50), unique=True, nullable=False)  # 引擎名称
    enabled = Column(Boolean, default=True)  # 是否启用
    api_endpoint = Column(String(255))  # API端点
    model_name = Column(String(100))  # 模型名称
    rate_limit = Column(Integer, default=100)  # 速率限制（每小时）
    last_used = Column(DateTime)  # 最后使用时间
    success_count = Column(Integer, default=0)  # 成功次数
    failure_count = Column(Integer, default=0)  # 失败次数

    def __repr__(self):
        return f"<EngineConfig(name={self.engine_name}, enabled={self.enabled})>"


class KeywordStats(Base):
    """关键词统计表"""
    __tablename__ = "keyword_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False, index=True)  # 关键词
    category = Column(String(50), nullable=False)  # 分类
    engine_name = Column(String(50), nullable=False)  # 引擎名称
    total_citations = Column(Integer, default=0)  # 总引用次数
    date = Column(DateTime, default=datetime.now, index=True)  # 统计日期
    exposure_count = Column(Integer, default=0)  # 曝光次数（独立查询）
    avg_confidence = Column(Float, default=0.0)  # 平均置信度

    def __repr__(self):
        return f"<KeywordStats(keyword={self.keyword}, count={self.total_citations})>"


class MonitorTask(Base):
    """监控任务记录表"""
    __tablename__ = "monitor_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(100), nullable=False)  # 任务名称
    task_type = Column(String(50), nullable=False)  # 任务类型：monitor/report
    status = Column(String(20), nullable=False)  # 状态：running/completed/failed
    start_time = Column(DateTime, default=datetime.now)  # 开始时间
    end_time = Column(DateTime)  # 结束时间
    engines_queried = Column(Integer, default=0)  # 查询的引擎数
    queries_executed = Column(Integer, default=0)  # 执行的查询数
    citations_found = Column(Integer, default=0)  # 发现的引用数
    error_message = Column(Text)  # 错误信息

    def __repr__(self):
        return f"<MonitorTask(name={self.task_name}, status={self.status})>"
