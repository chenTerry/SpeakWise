"""
User Service Layer

用户服务层封装业务逻辑：
- 用户注册和登录
- 用户信息管理
- Session 管理

Design Principles:
- Service Layer Pattern
- 依赖注入 Repository
- 完整的错误处理
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from .models import (
    UserCreate, UserUpdate, UserResponse,
    SessionCreate, SessionResponse, SessionStatus,
    ProgressMetrics
)
from .auth import AuthService, SessionManager
from .repository import UserRepository, SessionRepository, ProgressRepository
from .database import Database


class UserServiceError(Exception):
    """用户服务异常基类"""
    pass


class AuthenticationError(UserServiceError):
    """认证错误"""
    pass


class UserNotFoundError(UserServiceError):
    """用户未找到"""
    pass


class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑：
    - 用户注册、登录、注销
    - 用户信息管理
    - Session 管理
    - 进度追踪集成
    """
    
    def __init__(self, db: Optional[Database] = None,
                 auth_service: Optional[AuthService] = None,
                 session_manager: Optional[SessionManager] = None):
        """
        初始化用户服务
        
        Args:
            db: 数据库实例（可选，默认使用单例）
            auth_service: 认证服务（可选）
            session_manager: Session 管理器（可选）
        """
        self.db = db or Database.get_instance()
        
        # 初始化认证服务
        if auth_service:
            self.auth_service = auth_service
        else:
            # 使用默认密钥（生产环境应从配置读取）
            self.auth_service = AuthService(secret_key="agentscope-secret-key-demo")
        
        # 初始化 Session 管理器
        self.session_manager = session_manager or SessionManager()
    
    # =========================================================================
    # User Registration & Authentication
    # =========================================================================
    
    def register(self, user_data: UserCreate) -> UserResponse:
        """
        注册新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            用户响应信息
            
        Raises:
            UserServiceError: 注册失败
        """
        with self.db.get_session() as session:
            user_repo = UserRepository(session)
            
            # 哈希密码
            password_hash, salt = self.auth_service.hash_password(user_data.password)
            
            # 创建用户
            try:
                user = user_repo.create(
                    username=user_data.username,
                    password_hash=password_hash,
                    salt=salt,
                    email=user_data.email,
                    display_name=user_data.display_name
                )
                session.commit()
                
                return UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    display_name=user.display_name,
                    role=user.role,
                    status=user.status,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                )
            except Exception as e:
                session.rollback()
                if "already exists" in str(e):
                    raise UserServiceError(f"Username '{user_data.username}' already exists")
                raise UserServiceError(f"Registration failed: {e}")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            包含 token 和 session_id 的字典
            
        Raises:
            AuthenticationError: 认证失败
        """
        with self.db.get_session() as session:
            user_repo = UserRepository(session)
            
            # 查找用户
            user = user_repo.get_by_username(username)
            
            if user is None:
                raise AuthenticationError("Invalid username or password")
            
            # 验证密码
            if not self.auth_service.verify_password(password, user.password_hash, user.salt):
                raise AuthenticationError("Invalid username or password")
            
            # 检查用户状态
            if user.status != "active":
                raise AuthenticationError(f"Account is {user.status}")
            
            # 更新最后登录时间
            user_repo.update_last_login(user.id)
            session.commit()
            
            # 生成 JWT token
            token = self.auth_service.generate_token(
                user_id=user.id,
                username=user.username
            )
            
            # 创建 Session
            session_id = self.session_manager.create_session(
                user_id=user.id,
                username=user.username
            )
            
            return {
                "token": token,
                "session_id": session_id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name
                }
            }
    
    def logout(self, session_id: str) -> bool:
        """
        用户登出
        
        Args:
            session_id: Session ID
            
        Returns:
            是否成功登出
        """
        return self.session_manager.delete_session(session_id)
    
    def verify_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        验证 Session
        
        Args:
            session_id: Session ID
            
        Returns:
            Session 信息，无效则返回 None
        """
        return self.session_manager.get_session(session_id)
    
    def get_user_by_session(self, session_id: str) -> Optional[UserResponse]:
        """
        根据 Session 获取用户信息
        
        Args:
            session_id: Session ID
            
        Returns:
            用户信息，无效则返回 None
        """
        session_info = self.session_manager.get_session(session_id)
        
        if session_info is None:
            return None
        
        with self.db.get_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(session_info["user_id"])
            
            if user is None:
                return None
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                role=user.role,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
    
    # =========================================================================
    # User Management
    # =========================================================================
    
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """
        获取用户信息
        
        Args:
            user_id: 用户 ID
            
        Returns:
            用户信息，不存在则返回 None
        """
        with self.db.get_session() as session:
            user_repo = UserRepository(session)
            user = user_repo.get_by_id(user_id)
            
            if user is None:
                return None
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                role=user.role,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
    
    def update_user(self, user_id: int, update_data: UserUpdate) -> Optional[UserResponse]:
        """
        更新用户信息
        
        Args:
            user_id: 用户 ID
            update_data: 更新数据
            
        Returns:
            更新后的用户信息，失败则返回 None
        """
        with self.db.get_session() as session:
            user_repo = UserRepository(session)
            
            user = user_repo.update(user_id, **update_data.model_dump(exclude_unset=True))
            
            if user is None:
                return None
            
            session.commit()
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                display_name=user.display_name,
                role=user.role,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login
            )
    
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            是否成功删除
        """
        with self.db.get_session() as session:
            user_repo = UserRepository(session)
            
            # 删除用户 Session
            self.session_manager.delete_user_sessions(user_id)
            
            # 删除用户
            success = user_repo.delete(user_id)
            
            if success:
                session.commit()
            
            return success
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    def create_session_record(self, session_data: SessionCreate) -> SessionResponse:
        """
        创建会话记录
        
        Args:
            session_data: 会话创建数据
            
        Returns:
            会话响应信息
        """
        with self.db.get_session() as session:
            session_repo = SessionRepository(session)
            
            session_record = session_repo.create(
                user_id=session_data.user_id,
                scene_type=session_data.scene_type,
                scene_id=session_data.scene_id,
                title=session_data.title,
                metadata=session_data.metadata
            )
            
            session.commit()
            
            return SessionResponse(
                id=session_record.id,
                user_id=session_record.user_id,
                scene_type=session_record.scene_type,
                scene_id=session_record.scene_id,
                title=session_record.title,
                status=session_record.status,
                metadata=session_record.metadata or {},
                started_at=session_record.started_at,
                ended_at=session_record.ended_at,
                duration_seconds=session_record.duration_seconds
            )
    
    def get_session_record(self, session_id: int) -> Optional[SessionResponse]:
        """
        获取会话记录
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话信息，不存在则返回 None
        """
        with self.db.get_session() as session:
            session_repo = SessionRepository(session)
            session_record = session_repo.get_by_id(session_id)
            
            if session_record is None:
                return None
            
            return SessionResponse(
                id=session_record.id,
                user_id=session_record.user_id,
                scene_type=session_record.scene_type,
                scene_id=session_record.scene_id,
                title=session_record.title,
                status=session_record.status,
                metadata=session_record.metadata or {},
                started_at=session_record.started_at,
                ended_at=session_record.ended_at,
                duration_seconds=session_record.duration_seconds
            )
    
    def get_user_sessions(self, user_id: int, limit: int = 50,
                         offset: int = 0, status: Optional[str] = None) -> List[SessionResponse]:
        """
        获取用户会话列表
        
        Args:
            user_id: 用户 ID
            limit: 返回数量限制
            offset: 偏移量
            status: 状态过滤（可选）
            
        Returns:
            会话列表
        """
        with self.db.get_session() as session:
            session_repo = SessionRepository(session)
            sessions = session_repo.get_by_user(user_id, limit, offset, status)
            
            return [
                SessionResponse(
                    id=s.id,
                    user_id=s.user_id,
                    scene_type=s.scene_type,
                    scene_id=s.scene_id,
                    title=s.title,
                    status=s.status,
                    metadata=s.metadata or {},
                    started_at=s.started_at,
                    ended_at=s.ended_at,
                    duration_seconds=s.duration_seconds
                )
                for s in sessions
            ]
    
    def complete_session(self, session_id: int,
                        evaluation_result: Optional[Dict[str, Any]] = None,
                        dialogue_history: Optional[Dict[str, Any]] = None) -> Optional[SessionResponse]:
        """
        完成会话
        
        Args:
            session_id: 会话 ID
            evaluation_result: 评估结果（可选）
            dialogue_history: 对话历史（可选）
            
        Returns:
            更新后的会话信息
        """
        import json
        
        with self.db.get_session() as session:
            session_repo = SessionRepository(session)
            
            session_record = session_repo.complete_session(
                session_id=session_id,
                evaluation_result=json.dumps(evaluation_result) if evaluation_result else None,
                dialogue_history=json.dumps(dialogue_history) if dialogue_history else None
            )
            
            if session_record is None:
                return None
            
            session.commit()
            
            return SessionResponse(
                id=session_record.id,
                user_id=session_record.user_id,
                scene_type=session_record.scene_type,
                scene_id=session_record.scene_id,
                title=session_record.title,
                status=session_record.status,
                metadata=session_record.metadata or {},
                started_at=session_record.started_at,
                ended_at=session_record.ended_at,
                duration_seconds=session_record.duration_seconds
            )
    
    # =========================================================================
    # Progress Integration
    # =========================================================================
    
    def get_user_progress(self, user_id: int) -> Optional[ProgressMetrics]:
        """
        获取用户进度指标
        
        Args:
            user_id: 用户 ID
            
        Returns:
            进度指标，不存在则返回 None
        """
        with self.db.get_session() as session:
            progress_repo = ProgressRepository(session)
            progress = progress_repo.get_by_user_id(user_id)
            
            if progress is None:
                return None
            
            return ProgressMetrics(
                total_sessions=progress.total_sessions,
                completed_sessions=progress.completed_sessions,
                total_duration_seconds=progress.total_duration_seconds,
                avg_score=progress.avg_score,
                dimension_scores=progress.dimension_scores or {},
                improvement_rate=progress.improvement_rate,
                streak_days=progress.streak_days,
                last_session_at=progress.last_session_at
            )
    
    def update_progress(self, user_id: int, session_id: int) -> Optional[ProgressMetrics]:
        """
        更新用户进度（会话完成后调用）
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            
        Returns:
            更新后的进度指标
        """
        with self.db.get_session() as session:
            session_repo = SessionRepository(session)
            progress_repo = ProgressRepository(session)
            
            # 获取会话信息
            session_record = session_repo.get_by_id(session_id)
            
            if session_record is None:
                return None
            
            # 更新进度
            duration = session_record.duration_seconds or 0
            
            # 从评估结果中提取分数
            score = 0.0
            if session_record.evaluation_result:
                import json
                try:
                    eval_result = json.loads(session_record.evaluation_result)
                    score = eval_result.get("overall_score", 0.0)
                except:
                    pass
            
            progress = progress_repo.increment_sessions(user_id, duration, score)
            session.commit()
            
            return ProgressMetrics(
                total_sessions=progress.total_sessions,
                completed_sessions=progress.completed_sessions,
                total_duration_seconds=progress.total_duration_seconds,
                avg_score=progress.avg_score,
                dimension_scores=progress.dimension_scores or {},
                improvement_rate=progress.improvement_rate,
                streak_days=progress.streak_days,
                last_session_at=progress.last_session_at
            )
