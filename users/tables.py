"""
SQLAlchemy Table Definitions

定义数据库表结构：
- users: 用户表
- user_profiles: 用户画像表
- sessions: 会话记录表
- progress_data: 进度数据表

Design Principles:
- 使用 SQLAlchemy ORM
- 包含完整的索引和外键约束
- 支持软删除和时间戳
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy.sql import func


# 创建基类
Base = declarative_base()


# =============================================================================
# User Tables
# =============================================================================

class UserTable(Base):
    """
    用户表
    
    存储用户基本信息和认证数据
    """
    __tablename__ = "users"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 认证数据
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    salt: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # 角色和状态
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 关系
    profile = relationship("UserProfileTable", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("SessionTable", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("ProgressTable", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("ix_users_status", "status"),
        Index("ix_users_created_at", "created_at"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', status='{self.status}')>"


class UserProfileTable(Base):
    """
    用户画像表
    
    存储用户扩展信息和偏好设置
    """
    __tablename__ = "user_profiles"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # 画像信息
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # 偏好设置
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="zh-CN", nullable=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # 关系
    user = relationship("UserTable", back_populates="profile")
    
    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


# =============================================================================
# Session Tables
# =============================================================================

class SessionTable(Base):
    """
    会话记录表
    
    存储用户对话会话的完整记录
    """
    __tablename__ = "sessions"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # 会话信息
    scene_type: Mapped[str] = mapped_column(String(100), nullable=False)
    scene_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    
    # 对话数据
    dialogue_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 字符串
    evaluation_result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON 字符串

    # 额外数据
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 时间信息
    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # 关系
    user = relationship("UserTable", back_populates="sessions")
    
    # 索引
    __table_args__ = (
        Index("ix_sessions_user_status", "user_id", "status"),
        Index("ix_sessions_started_at", "started_at"),
        Index("ix_sessions_scene_type", "scene_type"),
    )
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


# =============================================================================
# Progress Tables
# =============================================================================

class ProgressTable(Base):
    """
    进度数据表
    
    存储用户进度指标和评估分数
    """
    __tablename__ = "progress_data"
    
    # 主键
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # 外键
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # 基础指标
    total_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # 七维度评估分数（JSON 存储）
    dimension_scores: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # 趋势数据
    improvement_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    streak_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 时间信息
    last_session_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # 关系
    user = relationship("UserTable", back_populates="progress")
    
    # 索引
    __table_args__ = (
        Index("ix_progress_updated_at", "updated_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Progress(id={self.id}, user_id={self.user_id}, avg_score={self.avg_score})>"
