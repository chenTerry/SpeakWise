"""
Enterprise Module - 企业版功能模块

v0.9: 企业版功能 (Enterprise Features)
- 多租户架构 (Multi-tenant Architecture)
- 团队协作 (Team Collaboration)
- 管理员仪表盘 (Admin Dashboard)
- 批量用户管理 (Bulk User Management)
- 企业报表 (Enterprise Reporting)
- SSO 单点登录 (Single Sign-On)

Version: v0.9.0
Author: AgentScope AI Interview Team
"""

from .tenant import Tenant, TenantManager, TenantConfig, TenantStatus, TenantPlan
from .team import Team, TeamManager, TeamMember, TeamRole, TeamStatus
from .collaboration import CollaborationSession, CollaborationManager, SessionType, SessionStatus
from .admin_dashboard import AdminDashboard, AdminStats
from .web_admin import WebAdminApp, AdminRouter
from .bulk_ops import BulkOperations, ImportResult
from .reports import EnterpriseReport, ReportGenerator, ReportType, ReportFormat
from .sso import SSOIntegration, OAuth2Config, SAMLConfig, SSOProvider, SSOStatus

__version__ = "0.9.0"
__author__ = "AgentScope AI Interview Team"

__all__ = [
    # Tenant Management
    "Tenant",
    "TenantManager",
    "TenantConfig",
    # Team Management
    "Team",
    "TeamManager",
    "TeamMember",
    # Collaboration
    "CollaborationSession",
    "CollaborationManager",
    # Admin Dashboard
    "AdminDashboard",
    "AdminStats",
    # Web Admin
    "WebAdminApp",
    "AdminRouter",
    # Bulk Operations
    "BulkOperations",
    "ImportResult",
    # Reports
    "EnterpriseReport",
    "ReportGenerator",
    # SSO
    "SSOIntegration",
    "OAuth2Config",
    "SAMLConfig",
]
