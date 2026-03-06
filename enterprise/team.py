"""
Team Management - 团队管理

提供企业团队协作功能：
- Team: 团队模型
- TeamManager: 团队管理器
- TeamMember: 团队成员

Version: v0.9.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import json
import hashlib


class TeamRole(str, Enum):
    """团队角色"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class TeamStatus(str, Enum):
    """团队状态"""
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class TeamMember:
    """团队成员"""
    user_id: str
    team_id: str
    role: TeamRole = TeamRole.MEMBER
    joined_at: datetime = field(default_factory=datetime.utcnow)
    permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.role, str):
            self.role = TeamRole(self.role)

    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role in [TeamRole.OWNER, TeamRole.ADMIN]

    def has_permission(self, permission: str) -> bool:
        """检查是否有权限"""
        if self.is_admin:
            return True
        return permission in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "team_id": self.team_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "permissions": self.permissions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeamMember":
        """从字典创建"""
        if "joined_at" in data and isinstance(data["joined_at"], str):
            data["joined_at"] = datetime.fromisoformat(data["joined_at"])
        return cls(**data)


@dataclass
class Team:
    """团队模型"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str] = None
    status: TeamStatus = TeamStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    owner_id: Optional[str] = None
    member_count: int = 0
    max_members: int = 50
    settings: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = TeamStatus(self.status)

    @property
    def is_active(self) -> bool:
        """检查团队是否活跃"""
        return self.status == TeamStatus.ACTIVE

    @property
    def is_full(self) -> bool:
        """检查团队是否已满"""
        return self.member_count >= self.max_members

    @property
    def available_slots(self) -> int:
        """可用成员位置"""
        return max(0, self.max_members - self.member_count)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner_id": self.owner_id,
            "member_count": self.member_count,
            "max_members": self.max_members,
            "settings": self.settings,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Team":
        """从字典创建"""
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class TeamManager:
    """团队管理器"""

    def __init__(self, storage_path: str = "data/teams.json", db_path: Optional[str] = None):
        # Support both storage_path and db_path for compatibility
        if db_path:
            if db_path == ":memory:":
                self.storage_path = None  # In-memory mode
            else:
                self.storage_path = db_path
        else:
            self.storage_path = storage_path
        self._teams: Dict[str, Team] = {}
        self._members: Dict[str, Dict[str, TeamMember]] = {}  # team_id -> {user_id: member}
        self._load()

    def _load(self):
        """加载团队数据"""
        if not self.storage_path:
            return  # In-memory mode
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    teams_data = data.get("teams", [])
                    members_data = data.get("members", {})

                    for team_data in teams_data:
                        team = Team.from_dict(team_data)
                        self._teams[team.id] = team

                    for team_id, members in members_data.items():
                        self._members[team_id] = {
                            user_id: TeamMember.from_dict(m)
                            for user_id, m in members.items()
                        }
        except Exception:
            pass

    def _save(self):
        """保存团队数据"""
        if not self.storage_path:
            return  # In-memory mode
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "teams": [t.to_dict() for t in self._teams.values()],
            "members": {
                team_id: {uid: m.to_dict() for uid, m in members.items()}
                for team_id, members in self._members.items()
            },
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_team(
        self,
        tenant_id: str,
        name: str,
        description: Optional[str] = None,
        owner_id: Optional[str] = None,
        max_members: int = 50,
    ) -> Team:
        """创建团队"""
        team_id = self._generate_id(tenant_id, name)

        team = Team(
            id=team_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            owner_id=owner_id,
            max_members=max_members,
        )

        self._teams[team_id] = team

        # 添加所有者为团队成员
        if owner_id:
            member = TeamMember(
                user_id=owner_id,
                team_id=team_id,
                role=TeamRole.OWNER,
            )
            if team_id not in self._members:
                self._members[team_id] = {}
            self._members[team_id][owner_id] = member
            team.member_count = 1

        self._save()
        return team

    def get_team(self, team_id: str) -> Optional[Team]:
        """获取团队"""
        return self._teams.get(team_id)

    def update_team(self, team_id: str, **kwargs) -> Optional[Team]:
        """更新团队"""
        team = self._teams.get(team_id)
        if not team:
            return None

        for key, value in kwargs.items():
            if hasattr(team, key):
                setattr(team, key, value)

        team.updated_at = datetime.utcnow()
        self._save()
        return team

    def delete_team(self, team_id: str) -> bool:
        """删除团队"""
        if team_id in self._teams:
            del self._teams[team_id]
            self._members.pop(team_id, None)
            self._save()
            return True
        return False

    def list_teams(
        self,
        tenant_id: Optional[str] = None,
        status: Optional[TeamStatus] = None,
    ) -> List[Team]:
        """列出团队"""
        teams = list(self._teams.values())
        if tenant_id:
            teams = [t for t in teams if t.tenant_id == tenant_id]
        if status:
            teams = [t for t in teams if t.status == status]
        return teams

    def add_member(
        self,
        team_id: str,
        user_id: str,
        role: TeamRole = TeamRole.MEMBER,
        permissions: Optional[List[str]] = None,
    ) -> Optional[TeamMember]:
        """添加成员"""
        team = self._teams.get(team_id)
        if not team or not team.is_active:
            return None

        if team.is_full:
            return None

        if team_id not in self._members:
            self._members[team_id] = {}

        # 检查是否已是成员
        if user_id in self._members[team_id]:
            return self._members[team_id][user_id]

        member = TeamMember(
            user_id=user_id,
            team_id=team_id,
            role=role,
            permissions=permissions or [],
        )

        self._members[team_id][user_id] = member
        team.member_count = len(self._members[team_id])
        self._save()
        return member

    def remove_member(self, team_id: str, user_id: str) -> bool:
        """移除成员"""
        if team_id not in self._members:
            return False

        if user_id in self._members[team_id]:
            del self._members[team_id][user_id]
            team = self._teams.get(team_id)
            if team:
                team.member_count = len(self._members[team_id])
            self._save()
            return True
        return False

    def get_member(self, team_id: str, user_id: str) -> Optional[TeamMember]:
        """获取成员"""
        if team_id not in self._members:
            return None
        return self._members[team_id].get(user_id)

    def list_members(self, team_id: str) -> List[TeamMember]:
        """列出成员"""
        if team_id not in self._members:
            return []
        return list(self._members[team_id].values())

    def get_team_size(self, team_id: str) -> int:
        """获取团队成员数量"""
        if team_id not in self._members:
            return 0
        return len(self._members[team_id])

    def update_member_role(
        self,
        team_id: str,
        user_id: str,
        new_role: TeamRole,
    ) -> Optional[TeamMember]:
        """更新成员角色"""
        member = self.get_member(team_id, user_id)
        if not member:
            return None

        member.role = new_role
        self._save()
        return member

    def get_user_teams(self, user_id: str) -> List[Team]:
        """获取用户所属团队"""
        user_team_ids = [
            team_id
            for team_id, members in self._members.items()
            if user_id in members
        ]
        return [
            team for team_id, team in self._teams.items()
            if team_id in user_team_ids
        ]

    def get_statistics(self, tenant_id: str) -> Dict[str, Any]:
        """获取团队统计"""
        teams = self.list_teams(tenant_id=tenant_id)
        total_members = sum(t.member_count for t in teams)

        return {
            "total_teams": len(teams),
            "active_teams": len([t for t in teams if t.is_active]),
            "archived_teams": len([t for t in teams if t.status == TeamStatus.ARCHIVED]),
            "total_members": total_members,
            "avg_team_size": total_members / len(teams) if teams else 0,
            "largest_team": max((t.member_count for t in teams), default=0),
        }

    def _generate_id(self, tenant_id: str, name: str) -> str:
        """生成团队 ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{tenant_id}{name}{timestamp}"
        return f"team_{hashlib.md5(content.encode()).hexdigest()[:12]}"
