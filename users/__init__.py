"""
AgentScope AI Interview - Users Module

用户管理模块提供：
- 用户数据模型 (User, UserProfile)
- 认证系统 (JWT tokens, session-based)
- 用户服务层 (业务逻辑封装)
- 数据库管理 (SQLite + SQLAlchemy)

版本：v0.6.0
"""

from .models import (
    UserResponse as User,
    UserProfileResponse as UserProfile,
    SessionResponse as SessionModel,
    UserCreate,
    UserInDB,
    SessionCreate,
    SessionInDB,
    ProgressMetrics,
    ProgressReport,
)
from .auth import AuthService, SessionManager
from .service import UserService
from .database import Database, get_db_session
from .tables import Base, UserTable, SessionTable, ProgressTable
from .repository import UserRepository, SessionRepository

__version__ = "0.6.0"

__all__ = [
    # Models
    "User",
    "UserProfile",
    "SessionModel",
    # Auth
    "AuthService",
    "SessionManager",
    # Service
    "UserService",
    # Database
    "Database",
    "get_db_session",
    # Tables
    "Base",
    "UserTable",
    "SessionTable",
    "ProgressTable",
    # Repository
    "UserRepository",
    "SessionRepository",
]
