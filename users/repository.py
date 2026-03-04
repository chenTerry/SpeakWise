"""
Repository Layer

提供数据访问层的 CRUD 操作：
- UserRepository: 用户数据操作
- SessionRepository: 会话数据操作
- ProgressRepository: 进度数据操作

Design Principles:
- Repository Pattern 封装数据访问
- 类型注解完整
- 异常处理清晰
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .tables import UserTable, UserProfileTable, SessionTable, ProgressTable


class RepositoryError(Exception):
    """Repository 层异常基类"""
    pass


class NotFoundError(RepositoryError):
    """记录未找到异常"""
    pass


class DuplicateError(RepositoryError):
    """重复记录异常"""
    pass


# =============================================================================
# User Repository
# =============================================================================

class UserRepository:
    """
    用户数据仓库
    
    提供用户相关的 CRUD 操作
    """
    
    def __init__(self, session: Session):
        """
        初始化用户仓库
        
        Args:
            session: SQLAlchemy Session
        """
        self.session = session
    
    def create(self, username: str, password_hash: str, salt: str,
               email: Optional[str] = None, display_name: Optional[str] = None) -> UserTable:
        """
        创建新用户
        
        Args:
            username: 用户名
            password_hash: 密码哈希
            salt: 盐值
            email: 邮箱（可选）
            display_name: 显示名称（可选）
            
        Returns:
            创建的 UserTable 对象
            
        Raises:
            DuplicateError: 用户名已存在
        """
        try:
            user = UserTable(
                username=username,
                password_hash=password_hash,
                salt=salt,
                email=email,
                display_name=display_name,
                role="user",
                status="active"
            )
            self.session.add(user)
            self.session.flush()  # 获取 ID
            
            # 创建默认画像
            profile = UserProfileTable(user_id=user.id)
            self.session.add(profile)
            
            return user
            
        except IntegrityError as e:
            if "username" in str(e.orig):
                raise DuplicateError(f"Username '{username}' already exists")
            raise RepositoryError(f"Database error: {e}")
    
    def get_by_id(self, user_id: int) -> Optional[UserTable]:
        """
        根据 ID 获取用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            UserTable 对象，不存在则返回 None
        """
        return self.session.get(UserTable, user_id)
    
    def get_by_username(self, username: str) -> Optional[UserTable]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            UserTable 对象，不存在则返回 None
        """
        stmt = select(UserTable).where(UserTable.username == username)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def get_by_email(self, email: str) -> Optional[UserTable]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            UserTable 对象，不存在则返回 None
        """
        stmt = select(UserTable).where(UserTable.email == email)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def update(self, user_id: int, **kwargs) -> Optional[UserTable]:
        """
        更新用户信息
        
        Args:
            user_id: 用户 ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的 UserTable 对象，不存在则返回 None
        """
        user = self.get_by_id(user_id)
        if user is None:
            return None
        
        # 更新允许的字段
        allowed_fields = {"email", "display_name", "role", "status", "last_login"}
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        # 更新 updated_at
        user.updated_at = datetime.utcnow()
        
        return user
    
    def update_last_login(self, user_id: int) -> bool:
        """
        更新最后登录时间
        
        Args:
            user_id: 用户 ID
            
        Returns:
            是否成功更新
        """
        return self.update(user_id, last_login=datetime.utcnow()) is not None
    
    def delete(self, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            是否成功删除
        """
        user = self.get_by_id(user_id)
        if user is None:
            return False
        
        self.session.delete(user)
        return True
    
    def list_users(self, limit: int = 100, offset: int = 0,
                   status: Optional[str] = None) -> List[UserTable]:
        """
        获取用户列表
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            status: 状态过滤（可选）
            
        Returns:
            UserTable 对象列表
        """
        stmt = select(UserTable)
        
        if status:
            stmt = stmt.where(UserTable.status == status)
        
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
    
    def count(self, status: Optional[str] = None) -> int:
        """
        统计用户数量
        
        Args:
            status: 状态过滤（可选）
            
        Returns:
            用户数量
        """
        stmt = select(func.count(UserTable.id))
        
        if status:
            stmt = stmt.where(UserTable.status == status)
        
        return self.session.execute(stmt).scalar() or 0


# =============================================================================
# Session Repository
# =============================================================================

class SessionRepository:
    """
    会话数据仓库
    
    提供会话相关的 CRUD 操作
    """
    
    def __init__(self, session: Session):
        """
        初始化会话仓库
        
        Args:
            session: SQLAlchemy Session
        """
        self.session = session
    
    def create(self, user_id: int, scene_type: str,
               scene_id: Optional[str] = None, title: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None) -> SessionTable:
        """
        创建新会话
        
        Args:
            user_id: 用户 ID
            scene_type: 场景类型
            scene_id: 场景 ID（可选）
            title: 会话标题（可选）
            metadata: 元数据（可选）
            
        Returns:
            创建的 SessionTable 对象
        """
        session_record = SessionTable(
            user_id=user_id,
            scene_type=scene_type,
            scene_id=scene_id,
            title=title,
            status="active",
            metadata=metadata
        )
        self.session.add(session_record)
        return session_record
    
    def get_by_id(self, session_id: int) -> Optional[SessionTable]:
        """
        根据 ID 获取会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            SessionTable 对象，不存在则返回 None
        """
        return self.session.get(SessionTable, session_id)
    
    def get_by_user(self, user_id: int, limit: int = 50,
                    offset: int = 0, status: Optional[str] = None) -> List[SessionTable]:
        """
        获取用户的会话列表
        
        Args:
            user_id: 用户 ID
            limit: 返回数量限制
            offset: 偏移量
            status: 状态过滤（可选）
            
        Returns:
            SessionTable 对象列表
        """
        stmt = select(SessionTable).where(SessionTable.user_id == user_id)
        
        if status:
            stmt = stmt.where(SessionTable.status == status)
        
        stmt = stmt.order_by(SessionTable.started_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        
        return list(self.session.execute(stmt).scalars().all())
    
    def update(self, session_id: int, **kwargs) -> Optional[SessionTable]:
        """
        更新会话信息
        
        Args:
            session_id: 会话 ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的 SessionTable 对象，不存在则返回 None
        """
        session_record = self.get_by_id(session_id)
        if session_record is None:
            return None
        
        # 更新允许的字段
        allowed_fields = {"status", "title", "metadata", "dialogue_history",
                         "evaluation_result", "ended_at", "duration_seconds"}
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(session_record, field):
                setattr(session_record, field, value)
        
        # 更新 updated_at
        session_record.updated_at = datetime.utcnow()
        
        return session_record
    
    def complete_session(self, session_id: int,
                         evaluation_result: Optional[str] = None,
                         dialogue_history: Optional[str] = None) -> Optional[SessionTable]:
        """
        完成会话
        
        Args:
            session_id: 会话 ID
            evaluation_result: 评估结果 JSON（可选）
            dialogue_history: 对话历史 JSON（可选）
            
        Returns:
            更新后的 SessionTable 对象
        """
        session_record = self.get_by_id(session_id)
        if session_record is None:
            return None
        
        # 计算持续时间
        if session_record.started_at:
            duration = datetime.utcnow() - session_record.started_at
            session_record.duration_seconds = int(duration.total_seconds())
        
        # 更新字段
        session_record.status = "completed"
        session_record.ended_at = datetime.utcnow()
        
        if evaluation_result:
            session_record.evaluation_result = evaluation_result
        if dialogue_history:
            session_record.dialogue_history = dialogue_history
        
        session_record.updated_at = datetime.utcnow()
        
        return session_record
    
    def delete(self, session_id: int) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否成功删除
        """
        session_record = self.get_by_id(session_id)
        if session_record is None:
            return False
        
        self.session.delete(session_record)
        return True
    
    def count_by_user(self, user_id: int, status: Optional[str] = None) -> int:
        """
        统计用户的会话数量
        
        Args:
            user_id: 用户 ID
            status: 状态过滤（可选）
            
        Returns:
            会话数量
        """
        stmt = select(func.count(SessionTable.id)).where(SessionTable.user_id == user_id)
        
        if status:
            stmt = stmt.where(SessionTable.status == status)
        
        return self.session.execute(stmt).scalar() or 0
    
    def get_recent_sessions(self, user_id: int, days: int = 30,
                           limit: int = 10) -> List[SessionTable]:
        """
        获取用户最近的会话
        
        Args:
            user_id: 用户 ID
            days: 天数限制
            limit: 返回数量限制
            
        Returns:
            SessionTable 对象列表
        """
        cutoff_date = datetime.utcnow()
        
        stmt = (
            select(SessionTable)
            .where(SessionTable.user_id == user_id)
            .where(SessionTable.started_at >= cutoff_date)
            .order_by(SessionTable.started_at.desc())
            .limit(limit)
        )
        
        return list(self.session.execute(stmt).scalars().all())


# =============================================================================
# Progress Repository
# =============================================================================

class ProgressRepository:
    """
    进度数据仓库
    
    提供进度相关的 CRUD 操作
    """
    
    def __init__(self, session: Session):
        """
        初始化进度仓库
        
        Args:
            session: SQLAlchemy Session
        """
        self.session = session
    
    def create_or_get(self, user_id: int) -> ProgressTable:
        """
        创建或获取进度记录
        
        Args:
            user_id: 用户 ID
            
        Returns:
            ProgressTable 对象
        """
        progress = self.get_by_user_id(user_id)
        
        if progress is None:
            progress = ProgressTable(user_id=user_id)
            self.session.add(progress)
        
        return progress
    
    def get_by_user_id(self, user_id: int) -> Optional[ProgressTable]:
        """
        根据用户 ID 获取进度
        
        Args:
            user_id: 用户 ID
            
        Returns:
            ProgressTable 对象，不存在则返回 None
        """
        return self.session.get(ProgressTable, user_id)
    
    def update(self, user_id: int, **kwargs) -> Optional[ProgressTable]:
        """
        更新进度信息
        
        Args:
            user_id: 用户 ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的 ProgressTable 对象，不存在则返回 None
        """
        progress = self.get_by_user_id(user_id)
        if progress is None:
            return None
        
        # 更新允许的字段
        allowed_fields = {
            "total_sessions", "completed_sessions", "total_duration_seconds",
            "avg_score", "dimension_scores", "improvement_rate",
            "streak_days", "last_session_at"
        }
        
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(progress, field):
                setattr(progress, field, value)
        
        # 更新 updated_at
        progress.updated_at = datetime.utcnow()
        
        return progress
    
    def increment_sessions(self, user_id: int, duration_seconds: int = 0,
                          score: float = 0.0) -> Optional[ProgressTable]:
        """
        增加会话计数
        
        Args:
            user_id: 用户 ID
            duration_seconds: 会话时长（秒）
            score: 会话分数
            
        Returns:
            更新后的 ProgressTable 对象
        """
        progress = self.create_or_get(user_id)
        
        progress.total_sessions += 1
        progress.completed_sessions += 1
        progress.total_duration_seconds += duration_seconds
        
        # 更新平均分
        total_score = progress.avg_score * (progress.total_sessions - 1) + score
        progress.avg_score = total_score / progress.total_sessions
        
        # 更新最后会话时间
        progress.last_session_at = datetime.utcnow()
        progress.updated_at = datetime.utcnow()
        
        return progress
    
    def update_dimension_scores(self, user_id: int,
                                dimension_scores: Dict[str, float]) -> Optional[ProgressTable]:
        """
        更新七维度分数
        
        Args:
            user_id: 用户 ID
            dimension_scores: 七维度分数字典
            
        Returns:
            更新后的 ProgressTable 对象
        """
        progress = self.get_by_user_id(user_id)
        if progress is None:
            return None
        
        # 合并分数（简单平均）
        existing_scores = progress.dimension_scores or {}
        
        for dim, score in dimension_scores.items():
            if dim in existing_scores:
                # 计算移动平均
                existing_scores[dim] = (existing_scores[dim] + score) / 2
            else:
                existing_scores[dim] = score
        
        progress.dimension_scores = existing_scores
        progress.updated_at = datetime.utcnow()
        
        return progress
