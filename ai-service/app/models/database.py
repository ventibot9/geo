from sqlalchemy import Column, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class RewriteRecordDB(Base):
    """改写记录数据库模型"""
    __tablename__ = "rewrite_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original = Column(Text, nullable=False)
    rewritten = Column(Text, nullable=False)
    model_provider = Column(String, nullable=False)
    model = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    quality_score = Column(Float, nullable=True)
    quality_details = Column(JSON, nullable=True)
