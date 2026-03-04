"""
User Data Models

定义用户相关的数据模型（Pydantic models），用于：
- 数据验证
- API 请求/响应
- 业务逻辑层数据传输

Design Principles:
- 使用 Pydantic v2 进行数据验证
- 分离创建模型和响应模型
- 包含完整的类型注解
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# =============================================================================
# User Models
# =============================================================================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱地址")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")


class UserCreate(UserBase):
    """创建用户请求模型"""
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")


class UserUpdate(BaseModel):
    """更新用户请求模型"""
    email: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    """用户响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="用户 ID")
    display_name: Optional[str] = Field(None, description="显示名称")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="用户状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")


class UserInDB(UserResponse):
    """数据库用户模型（包含敏感字段）"""
    password_hash: str = Field(..., description="密码哈希")
    salt: str = Field(..., description="密码盐值")


# =============================================================================
# User Profile Models
# =============================================================================

class UserProfileBase(BaseModel):
    """用户画像基础模型"""
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    avatar_url: Optional[str] = Field(None, description="头像 URL")
    timezone: str = Field(default="UTC", description="时区")
    language: str = Field(default="zh-CN", description="语言偏好")


class UserProfileCreate(UserProfileBase):
    """创建用户画像请求模型"""
    user_id: int = Field(..., description="关联用户 ID")


class UserProfileResponse(UserProfileBase):
    """用户画像响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="画像 ID")
    user_id: int = Field(..., description="关联用户 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# =============================================================================
# Session Models
# =============================================================================

class SessionStatus(str, Enum):
    """会话状态枚举"""
    ACTIVE = "active"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


class SessionBase(BaseModel):
    """会话基础模型"""
    scene_type: str = Field(..., description="场景类型")
    scene_id: Optional[str] = Field(None, description="场景 ID")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE, description="会话状态")


class SessionCreate(SessionBase):
    """创建会话请求模型"""
    user_id: int = Field(..., description="用户 ID")
    title: Optional[str] = Field(None, max_length=200, description="会话标题")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")


class SessionUpdate(BaseModel):
    """更新会话请求模型"""
    status: Optional[SessionStatus] = None
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionResponse(SessionBase):
    """会话响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="会话 ID")
    user_id: int = Field(..., description="用户 ID")
    title: Optional[str] = Field(None, description="会话标题")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    started_at: datetime = Field(..., description="开始时间")
    ended_at: Optional[datetime] = Field(None, description="结束时间")
    duration_seconds: Optional[int] = Field(None, description="持续时间（秒）")


class SessionInDB(SessionResponse):
    """数据库会话模型（包含完整字段）"""
    dialogue_history: Optional[str] = Field(None, description="对话历史 JSON")
    evaluation_result: Optional[str] = Field(None, description="评估结果 JSON")


# =============================================================================
# Progress Models
# =============================================================================

class ProgressMetrics(BaseModel):
    """进度指标模型"""
    total_sessions: int = Field(default=0, description="总会话数")
    completed_sessions: int = Field(default=0, description="完成会话数")
    total_duration_seconds: int = Field(default=0, description="总时长（秒）")
    avg_score: float = Field(default=0.0, description="平均分数")
    
    # 七维度评估分数
    dimension_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="七维度分数"
    )
    
    improvement_rate: float = Field(default=0.0, description="改进率（%）")
    streak_days: int = Field(default=0, description="连续练习天数")
    last_session_at: Optional[datetime] = Field(None, description="上次会话时间")


class ProgressTrendPoint(BaseModel):
    """进度趋势点"""
    date: datetime = Field(..., description="日期")
    score: float = Field(..., description="分数")
    session_count: int = Field(default=0, description="会话数")


class ProgressReport(BaseModel):
    """进度报告模型"""
    user_id: int = Field(..., description="用户 ID")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
    period_days: int = Field(default=30, description="统计周期（天）")
    
    metrics: ProgressMetrics = Field(..., description="进度指标")
    trend: List[ProgressTrendPoint] = Field(default_factory=list, description="趋势数据")
    strengths: List[str] = Field(default_factory=list, description="优势项")
    improvements: List[str] = Field(default_factory=list, description="改进建议")
