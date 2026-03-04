"""
Collaboration Tools - 协作工具

提供企业协作功能：
- CollaborationSession: 协作会话
- CollaborationManager: 协作会话管理器

Version: v0.9.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class SessionType(str, Enum):
    """会话类型"""
    PRACTICE = "practice"
    COMPETITION = "competition"
    TRAINING = "training"
    EVALUATION = "evaluation"


class SessionStatus(str, Enum):
    """会话状态"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CollaborationSession:
    """协作会话"""
    id: str
    team_id: str
    session_type: SessionType
    status: SessionStatus = SessionStatus.SCHEDULED
    name: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    participants: List[str] = field(default_factory=list)  # user_ids
    observers: List[str] = field(default_factory=list)  # user_ids
    scene: str = "interview"
    scene_config: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    recording_url: Optional[str] = None
    chat_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.session_type, str):
            self.session_type = SessionType(self.session_type)
        if isinstance(self.status, str):
            self.status = SessionStatus(self.status)

    @property
    def is_active(self) -> bool:
        """检查会话是否进行中"""
        return self.status == SessionStatus.IN_PROGRESS

    @property
    def is_completed(self) -> bool:
        """检查会话是否已完成"""
        return self.status == SessionStatus.COMPLETED

    @property
    def duration_minutes(self) -> Optional[int]:
        """计算会话时长（分钟）"""
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            return int(delta.total_seconds() / 60)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "team_id": self.team_id,
            "session_type": self.session_type.value,
            "status": self.status.value,
            "name": self.name,
            "description": self.description,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "participants": self.participants,
            "observers": self.observers,
            "scene": self.scene,
            "scene_config": self.scene_config,
            "results": self.results,
            "recording_url": self.recording_url,
            "chat_history": self.chat_history,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CollaborationSession":
        """从字典创建"""
        return cls(**data)


class CollaborationManager:
    """协作会话管理器"""

    def __init__(self, storage_path: str = "data/collaboration.json"):
        self.storage_path = storage_path
        self._sessions: Dict[str, CollaborationSession] = {}
        self._load()

    def _load(self):
        """加载协作数据"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for session_data in data:
                        session = CollaborationSession.from_dict(session_data)
                        self._sessions[session.id] = session
        except Exception:
            pass

    def _save(self):
        """保存协作数据"""
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self._sessions.values()], f, indent=2, ensure_ascii=False)

    def create_session(
        self,
        team_id: str,
        session_type: SessionType,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scene: str = "interview",
        participants: Optional[List[str]] = None,
        scheduled_at: Optional[datetime] = None,
    ) -> CollaborationSession:
        """创建协作会话"""
        import hashlib
        session_id = f"session_{hashlib.md5(f'{team_id}{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:12]}"

        session = CollaborationSession(
            id=session_id,
            team_id=team_id,
            session_type=session_type,
            name=name,
            description=description,
            scene=scene,
            participants=participants or [],
            scheduled_at=scheduled_at,
        )

        self._sessions[session_id] = session
        self._save()
        return session

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """获取会话"""
        return self._sessions.get(session_id)

    def update_session(self, session_id: str, **kwargs) -> Optional[CollaborationSession]:
        """更新会话"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        self._save()
        return session

    def start_session(self, session_id: str) -> Optional[CollaborationSession]:
        """开始会话"""
        return self.update_session(
            session_id,
            status=SessionStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
        )

    def end_session(
        self,
        session_id: str,
        results: Optional[Dict[str, Any]] = None,
    ) -> Optional[CollaborationSession]:
        """结束会话"""
        return self.update_session(
            session_id,
            status=SessionStatus.COMPLETED,
            ended_at=datetime.utcnow(),
            results=results or {},
        )

    def cancel_session(self, session_id: str, reason: str = "") -> Optional[CollaborationSession]:
        """取消会话"""
        session = self.update_session(
            session_id,
            status=SessionStatus.CANCELLED,
        )
        if session:
            session.metadata["cancellation_reason"] = reason
            self._save()
        return session

    def add_participant(self, session_id: str, user_id: str) -> bool:
        """添加参与者"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        if user_id not in session.participants:
            session.participants.append(user_id)
            self._save()
        return True

    def remove_participant(self, session_id: str, user_id: str) -> bool:
        """移除参与者"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        if user_id in session.participants:
            session.participants.remove(user_id)
            self._save()
        return True

    def add_observer(self, session_id: str, user_id: str) -> bool:
        """添加观察者"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        if user_id not in session.observers:
            session.observers.append(user_id)
            self._save()
        return True

    def add_chat_message(
        self,
        session_id: str,
        user_id: str,
        message: str,
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """添加聊天消息"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.chat_history.append({
            "user_id": user_id,
            "message": message,
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        })
        self._save()
        return True

    def list_sessions(
        self,
        team_id: Optional[str] = None,
        session_type: Optional[SessionType] = None,
        status: Optional[SessionStatus] = None,
    ) -> List[CollaborationSession]:
        """列出会话"""
        sessions = list(self._sessions.values())

        if team_id:
            sessions = [s for s in sessions if s.team_id == team_id]
        if session_type:
            sessions = [s for s in sessions if s.session_type == session_type]
        if status:
            sessions = [s for s in sessions if s.status == status]

        return sorted(sessions, key=lambda s: s.scheduled_at or datetime.min, reverse=True)

    def get_active_sessions(self, team_id: str) -> List[CollaborationSession]:
        """获取活跃会话"""
        return self.list_sessions(team_id=team_id, status=SessionStatus.IN_PROGRESS)

    def get_upcoming_sessions(self, team_id: str) -> List[CollaborationSession]:
        """获取即将开始的会话"""
        sessions = self.list_sessions(team_id=team_id, status=SessionStatus.SCHEDULED)
        now = datetime.utcnow()
        return [s for s in sessions if s.scheduled_at and s.scheduled_at > now]

    def get_statistics(self, team_id: str) -> Dict[str, Any]:
        """获取协作统计"""
        sessions = self.list_sessions(team_id=team_id)
        completed = [s for s in sessions if s.is_completed]
        active = [s for s in sessions if s.is_active]

        total_duration = sum(
            s.duration_minutes or 0
            for s in completed
        )

        return {
            "total_sessions": len(sessions),
            "completed_sessions": len(completed),
            "active_sessions": len(active),
            "cancelled_sessions": len([s for s in sessions if s.status == SessionStatus.CANCELLED]),
            "total_duration_minutes": total_duration,
            "avg_duration_minutes": total_duration / len(completed) if completed else 0,
            "total_participants": len(set(
                p for s in sessions
                for p in s.participants
            )),
        }
