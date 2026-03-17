"""
数据库连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path

from config import DATABASE_URL
from .models import Base


class Database:
    """数据库管理类"""

    def __init__(self, db_url: str = None):
        self.db_url = db_url or DATABASE_URL
        self.engine = None
        self.SessionLocal = None

    def initialize(self):
        """初始化数据库连接和表结构"""
        # 确保数据库目录存在
        db_path = Path(self.db_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建引擎
        self.engine = create_engine(
            self.db_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False} if "sqlite" in self.db_url else {}
        )

        # 创建Session工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # 创建所有表
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self) -> Session:
        """获取数据库会话的上下文管理器"""
        if self.SessionLocal is None:
            self.initialize()

        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def drop_all(self):
        """删除所有表（危险操作！）"""
        if self.engine:
            Base.metadata.drop_all(bind=self.engine)

    def reset(self):
        """重置数据库：删除所有表并重新创建"""
        self.drop_all()
        self.initialize()


# 全局数据库实例
_db_instance = None


def get_db() -> Database:
    """获取全局数据库实例（单例模式）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.initialize()
    return _db_instance
