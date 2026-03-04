"""
Database Module

提供数据库连接和会话管理：
- SQLite 数据库连接
- SQLAlchemy session 管理
- 数据库初始化

Design Principles:
- 使用 SQLite 简化部署
- Singleton 模式管理数据库连接
- 自动创建表结构
"""

import os
from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .tables import Base


class Database:
    """
    数据库管理类（Singleton）
    
    管理数据库连接和会话工厂
    
    Usage:
        db = Database.get_instance()
        db.initialize("sqlite:///users.db")
        
        with db.get_session() as session:
            # 使用 session
    """
    
    _instance: Optional["Database"] = None
    
    def __new__(cls) -> "Database":
        """Singleton 实例创建"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化数据库（仅调用一次）"""
        if self._initialized:
            return
        
        self.engine = None
        self.SessionLocal = None
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> "Database":
        """获取数据库实例"""
        return cls()
    
    def initialize(self, database_url: str) -> None:
        """
        初始化数据库连接
        
        Args:
            database_url: 数据库 URL
                - SQLite: "sqlite:///path/to/db.db"
                - SQLite (memory): "sqlite:///:memory:"
        """
        # 创建引擎
        if database_url.startswith("sqlite"):
            # SQLite 特殊配置
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False  # 设置为 True 以启用 SQL 日志
            )
        else:
            # 其他数据库（PostgreSQL, MySQL 等）
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,
                echo=False
            )
        
        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """
        获取数据库会话（上下文管理器）
        
        Usage:
            with db.get_session() as session:
                # 使用 session
                session.add(user)
                session.commit()
        
        Yields:
            SQLAlchemy Session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_direct(self) -> Session:
        """
        直接获取会话（需要手动管理生命周期）
        
        Returns:
            SQLAlchemy Session
        
        Note:
            使用此方法后必须手动调用 session.close()
            推荐使用 get_session() 上下文管理器
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        return self.SessionLocal()
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.SessionLocal = None
    
    def is_initialized(self) -> bool:
        """检查数据库是否已初始化"""
        return self.engine is not None


# =============================================================================
# Convenience Functions
# =============================================================================

def get_db_session() -> Session:
    """
    获取数据库会话（便捷函数）
    
    Returns:
        SQLAlchemy Session
    
    Note:
        使用前必须确保 Database 已初始化
    """
    db = Database.get_instance()
    return db.get_session_direct()


def init_database(database_url: Optional[str] = None) -> Database:
    """
    初始化数据库（便捷函数）
    
    Args:
        database_url: 数据库 URL，默认使用 SQLite 文件
        
    Returns:
        Database 实例
    """
    db = Database.get_instance()
    
    if database_url is None:
        # 默认使用项目目录下的 SQLite 文件
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "users.db"
        )
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        database_url = f"sqlite:///{db_path}"
    
    db.initialize(database_url)
    return db
