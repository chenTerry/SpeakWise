"""
Tenant Management - 多租户管理

提供企业多租户架构支持：
- Tenant: 租户模型
- TenantManager: 租户管理器
- TenantConfig: 租户配置

Version: v0.9.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import json
import hashlib


class TenantStatus(str, Enum):
    """租户状态"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    TRIAL = "trial"


class TenantPlan(str, Enum):
    """租户计划"""
    FREE = "free"
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TenantConfig:
    """租户配置"""
    max_users: int = 100
    max_teams: int = 10
    max_sessions_per_month: int = 1000
    enable_sso: bool = False
    enable_custom_branding: bool = False
    enable_advanced_analytics: bool = False
    data_retention_days: int = 365
    allowed_scenes: List[str] = field(default_factory=lambda: ["interview", "meeting", "salon"])
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TenantStats:
    """租户统计信息"""
    tenant_id: str
    user_count: int = 0
    max_users: int = 100
    session_count: int = 0
    team_count: int = 0


@dataclass
class Tenant:
    """租户模型"""
    id: str
    name: str
    status: TenantStatus = TenantStatus.TRIAL
    plan: TenantPlan = TenantPlan.FREE
    config: TenantConfig = field(default_factory=TenantConfig)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.config, dict):
            self.config = TenantConfig(**self.config)
        if isinstance(self.status, str):
            self.status = TenantStatus(self.status)
        if isinstance(self.plan, str):
            self.plan = TenantPlan(self.plan)

    @property
    def is_active(self) -> bool:
        """检查租户是否活跃"""
        if self.status != TenantStatus.ACTIVE:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True

    @property
    def is_trial(self) -> bool:
        """检查是否在试用期"""
        return self.status == TenantStatus.TRIAL

    @property
    def days_remaining(self) -> Optional[int]:
        """计算剩余天数"""
        if self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return max(0, delta.days)
        return None

    def get_usage_limit(self, feature: str) -> int:
        """获取功能使用限制"""
        limits = {
            TenantPlan.FREE: {"users": 10, "teams": 2, "sessions": 100},
            TenantPlan.BASIC: {"users": 50, "teams": 5, "sessions": 500},
            TenantPlan.PROFESSIONAL: {"users": 200, "teams": 20, "sessions": 2000},
            TenantPlan.ENTERPRISE: {"users": -1, "teams": -1, "sessions": -1},  # -1 = unlimited
        }
        plan_limits = limits.get(self.plan, limits[TenantPlan.FREE])
        
        feature_map = {
            "users": "users",
            "teams": "teams",
            "sessions": "sessions",
        }
        
        limit_key = feature_map.get(feature)
        if limit_key:
            return plan_limits.get(limit_key, 0)
        return 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "plan": self.plan.value,
            "config": {
                "max_users": self.config.max_users,
                "max_teams": self.config.max_teams,
                "max_sessions_per_month": self.config.max_sessions_per_month,
                "enable_sso": self.config.enable_sso,
                "enable_custom_branding": self.config.enable_custom_branding,
                "enable_advanced_analytics": self.config.enable_advanced_analytics,
                "data_retention_days": self.config.data_retention_days,
                "allowed_scenes": self.config.allowed_scenes,
                "custom_settings": self.config.custom_settings,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "address": self.address,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tenant":
        """从字典创建"""
        config_data = data.pop("config", {})
        data["config"] = TenantConfig(**config_data) if config_data else TenantConfig()
        return cls(**data)


class TenantManager:
    """租户管理器"""

    def __init__(self, storage_path: str = "data/tenants.json", db_path: Optional[str] = None):
        # Support both storage_path and db_path for compatibility
        if db_path:
            if db_path == ":memory:":
                self.storage_path = None  # In-memory mode
            else:
                self.storage_path = db_path
        else:
            self.storage_path = storage_path
        self._tenants: Dict[str, Tenant] = {}
        self._load()

    def _load(self):
        """加载租户数据"""
        if not self.storage_path:
            return  # In-memory mode, no loading
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for tenant_data in data:
                        tenant = Tenant.from_dict(tenant_data)
                        self._tenants[tenant.id] = tenant
        except Exception:
            pass  # 如果加载失败，使用空字典

    def _save(self):
        """保存租户数据"""
        if not self.storage_path:
            return  # In-memory mode, no saving
        import os
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self._tenants.values()], f, indent=2, ensure_ascii=False)

    def create_tenant(
        self,
        name: str,
        plan: TenantPlan = TenantPlan.TRIAL,
        contact_email: Optional[str] = None,
        trial_days: int = 30,
        **kwargs,
    ) -> Tenant:
        """创建新租户"""
        tenant_id = self._generate_id(name)

        expires_at = None
        if plan == TenantPlan.TRIAL or trial_days > 0:
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=trial_days)

        # Handle plan as string for compatibility
        if isinstance(plan, str):
            plan_map = {
                "trial": TenantPlan.TRIAL,
                "free": TenantPlan.FREE,
                "basic": TenantPlan.BASIC,
                "starter": TenantPlan.BASIC,  # Alias for BASIC
                "professional": TenantPlan.PROFESSIONAL,
                "enterprise": TenantPlan.ENTERPRISE,
            }
            plan = plan_map.get(plan.lower(), TenantPlan.TRIAL)

        tenant = Tenant(
            id=tenant_id,
            name=name,
            status=TenantStatus.TRIAL if trial_days > 0 else TenantStatus.ACTIVE,
            plan=plan,
            contact_email=contact_email,
            expires_at=expires_at,
        )

        # Apply additional kwargs like max_users
        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
            elif hasattr(tenant.config, key):
                tenant.config.__dict__[key] = value

        self._tenants[tenant_id] = tenant
        self._save()
        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """获取租户"""
        return self._tenants.get(tenant_id)

    def get_tenant_stats(self, tenant_id: str) -> "TenantStats":
        """获取租户统计信息"""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")
        
        # Return a simple stats object
        return TenantStats(
            tenant_id=tenant_id,
            user_count=0,  # Would be calculated from actual data
            max_users=tenant.config.max_users,
            session_count=0,
            team_count=0,
        )

    def update_tenant(self, tenant_id: str, **kwargs) -> Optional[Tenant]:
        """更新租户"""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return None

        for key, value in kwargs.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)

        tenant.updated_at = datetime.utcnow()
        self._save()
        return tenant

    def delete_tenant(self, tenant_id: str) -> bool:
        """删除租户"""
        if tenant_id in self._tenants:
            del self._tenants[tenant_id]
            self._save()
            return True
        return False

    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        plan: Optional[TenantPlan] = None,
    ) -> List[Tenant]:
        """列出租户"""
        tenants = list(self._tenants.values())
        if status:
            tenants = [t for t in tenants if t.status == status]
        if plan:
            tenants = [t for t in tenants if t.plan == plan]
        return tenants

    def activate_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """激活租户"""
        return self.update_tenant(tenant_id, status=TenantStatus.ACTIVE)

    def suspend_tenant(self, tenant_id: str, reason: str = "") -> Optional[Tenant]:
        """暂停租户"""
        tenant = self.update_tenant(tenant_id, status=TenantStatus.SUSPENDED)
        if tenant:
            tenant.metadata["suspension_reason"] = reason
            self._save()
        return tenant

    def upgrade_plan(self, tenant_id: str, new_plan: TenantPlan) -> Optional[Tenant]:
        """升级租户计划"""
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            return None

        updates = {"plan": new_plan}
        if new_plan != TenantPlan.TRIAL:
            updates["status"] = TenantStatus.ACTIVE
            updates["expires_at"] = None

        return self.update_tenant(tenant_id, **updates)

    def _generate_id(self, name: str) -> str:
        """生成租户 ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{name}{timestamp}"
        return f"tenant_{hashlib.md5(content.encode()).hexdigest()[:12]}"

    def get_statistics(self) -> Dict[str, Any]:
        """获取租户统计"""
        tenants = list(self._tenants.values())
        return {
            "total_tenants": len(tenants),
            "by_status": {
                status.value: len([t for t in tenants if t.status == status])
                for status in TenantStatus
            },
            "by_plan": {
                plan.value: len([t for t in tenants if t.plan == plan])
                for plan in TenantPlan
            },
            "active_trials": len([t for t in tenants if t.is_trial]),
            "expiring_soon": len([t for t in tenants if t.days_remaining and t.days_remaining <= 7]),
        }
