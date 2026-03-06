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

# UserManager alias for backward compatibility
UserManager = UserService

# Re-export ProgressTracker from progress module for convenience
from progress import ProgressTracker

# Simple DataVisualizer stub for demo compatibility
class DataVisualizer:
    """Simple data visualizer for demo purposes"""
    
    def generate_radar_chart(self, data: dict, output_format: str = "svg") -> str:
        """Generate a simple radar chart representation"""
        # Return a simple SVG representation
        max_val = max(data.values()) if data else 5
        points = []
        labels = list(data.keys())
        n = len(labels)
        
        import math
        for i, (label, value) in enumerate(data.items()):
            angle = 2 * math.pi * i / n - math.pi / 2
            r = (value / max_val) * 100
            x = 150 + r * math.cos(angle)
            y = 150 + r * math.sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
        
        return f'''<svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg">
  <polygon points="{" ".join(points)}" fill="rgba(66,133,244,0.3)" stroke="#4285f4" stroke-width="2"/>
  <text x="150" y="20" text-anchor="middle" font-size="14">能力雷达图</text>
</svg>'''

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
    "UserManager",  # Alias for backward compatibility
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
    # Re-exported from progress
    "ProgressTracker",
    # Visualizer
    "DataVisualizer",
]
