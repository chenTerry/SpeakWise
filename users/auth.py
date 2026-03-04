"""
Authentication Module

提供简单的 session-based 认证系统：
- JWT token 生成和验证
- Session 管理
- 密码哈希处理

Design Principles:
- 简单 session-based auth（演示用途）
- 使用 JWT 进行 token 管理
- 密码使用 bcrypt 哈希
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError


class AuthService:
    """
    认证服务类
    
    提供用户认证相关功能：
    - 密码哈希和验证
    - JWT token 生成和验证
    - Session 验证
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """
        初始化认证服务
        
        Args:
            secret_key: JWT 密钥
            algorithm: JWT 算法，默认 HS256
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry_hours = 24
    
    # =========================================================================
    # Password Hashing
    # =========================================================================
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        哈希密码
        
        Args:
            password: 原始密码
            salt: 可选盐值，不提供则自动生成
            
        Returns:
            (hashed_password, salt) 元组
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用 SHA-256 + salt 进行哈希
        salted_password = f"{salt}{password}{salt}"
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return hashed, salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        验证密码
        
        Args:
            password: 原始密码
            hashed_password: 存储的哈希值
            salt: 盐值
            
        Returns:
            密码是否匹配
        """
        computed_hash, _ = AuthService.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, hashed_password)
    
    # =========================================================================
    # JWT Token Management
    # =========================================================================
    
    def generate_token(self, user_id: int, username: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        生成 JWT token
        
        Args:
            user_id: 用户 ID
            username: 用户名
            extra_claims: 额外声明
            
        Returns:
            JWT token 字符串
        """
        now = datetime.utcnow()
        expiry = now + timedelta(hours=self.token_expiry_hours)
        
        payload = {
            "user_id": user_id,
            "username": username,
            "iat": now,
            "exp": expiry,
            "type": "access"
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证 JWT token
        
        Args:
            token: JWT token 字符串
            
        Returns:
            解析后的 payload，如果无效则返回 None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except InvalidTokenError:
            return None
        except Exception:
            return None
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        刷新 token
        
        Args:
            token: 当前 token
            
        Returns:
            新 token，如果原 token 无效则返回 None
        """
        payload = self.verify_token(token)
        if payload is None:
            return None
        
        # 生成新 token
        return self.generate_token(
            user_id=payload["user_id"],
            username=payload["username"]
        )


class SessionManager:
    """
    Session 管理器
    
    管理用户 session 状态（内存存储，演示用途）
    
    Production Note:
    实际生产环境应使用 Redis 或其他分布式缓存
    """
    
    def __init__(self):
        """初始化 session 管理器"""
        # Session 存储：{session_id: {user_id, username, created_at, last_active}}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        # User 到 Session 的映射：{user_id: session_id}
        self._user_sessions: Dict[int, str] = {}
        # Session 过期时间（小时）
        self.session_expiry_hours = 24
    
    def create_session(self, user_id: int, username: str) -> str:
        """
        创建新 session
        
        Args:
            user_id: 用户 ID
            username: 用户名
            
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        
        self._sessions[session_id] = {
            "user_id": user_id,
            "username": username,
            "created_at": now,
            "last_active": now
        }
        
        # 更新用户 session 映射
        self._user_sessions[user_id] = session_id
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取 session 信息
        
        Args:
            session_id: Session ID
            
        Returns:
            Session 信息字典，如果不存在则返回 None
        """
        session = self._sessions.get(session_id)
        
        if session is None:
            return None
        
        # 检查是否过期
        if self._is_session_expired(session):
            self.delete_session(session_id)
            return None
        
        # 更新最后活跃时间
        session["last_active"] = datetime.utcnow()
        return session
    
    def get_user_session(self, user_id: int) -> Optional[str]:
        """
        获取用户的 session ID
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Session ID，如果不存在则返回 None
        """
        session_id = self._user_sessions.get(user_id)
        
        if session_id is None:
            return None
        
        # 验证 session 是否仍然有效
        if session_id not in self._sessions:
            del self._user_sessions[user_id]
            return None
        
        return session_id
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除 session
        
        Args:
            session_id: Session ID
            
        Returns:
            是否成功删除
        """
        session = self._sessions.get(session_id)
        
        if session is None:
            return False
        
        # 清理用户 session 映射
        user_id = session["user_id"]
        if self._user_sessions.get(user_id) == session_id:
            del self._user_sessions[user_id]
        
        # 删除 session
        del self._sessions[session_id]
        return True
    
    def delete_user_sessions(self, user_id: int) -> int:
        """
        删除用户的所有 session
        
        Args:
            user_id: 用户 ID
            
        Returns:
            删除的 session 数量
        """
        session_id = self._user_sessions.get(user_id)
        
        if session_id is None:
            return 0
        
        self.delete_session(session_id)
        return 1
    
    def _is_session_expired(self, session: Dict[str, Any]) -> bool:
        """
        检查 session 是否过期
        
        Args:
            session: Session 信息字典
            
        Returns:
            是否过期
        """
        last_active = session["last_active"]
        expiry_time = last_active + timedelta(hours=self.session_expiry_hours)
        return datetime.utcnow() > expiry_time
    
    def cleanup_expired(self) -> int:
        """
        清理过期的 session
        
        Returns:
            清理的 session 数量
        """
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """
        获取活跃 session 数量
        
        Returns:
            活跃 session 数
        """
        return len(self._sessions)
