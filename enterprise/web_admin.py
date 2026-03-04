"""
Web Admin Interface - Web 管理界面

提供企业 Web 管理后台：
- WebAdminApp: Web 管理应用
- AdminRouter: 管理路由

Version: v0.9.0
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class WebAdminApp:
    """Web 管理应用"""

    def __init__(
        self,
        tenant_manager=None,
        team_manager=None,
        sso_integration=None,
        report_generator=None,
    ):
        self.tenant_manager = tenant_manager
        self.team_manager = team_manager
        self.sso_integration = sso_integration
        self.report_generator = report_generator
        self.routes: Dict[str, callable] = {}
        self._register_routes()

    def _register_routes(self):
        """注册路由"""
        # Dashboard
        self.routes["GET /"] = self.dashboard
        self.routes["GET /api/stats"] = self.get_stats

        # Tenants
        self.routes["GET /api/tenants"] = self.list_tenants
        self.routes["POST /api/tenants"] = self.create_tenant
        self.routes["GET /api/tenants/{id}"] = self.get_tenant
        self.routes["PUT /api/tenants/{id}"] = self.update_tenant
        self.routes["DELETE /api/tenants/{id}"] = self.delete_tenant

        # Teams
        self.routes["GET /api/teams"] = self.list_teams
        self.routes["POST /api/teams"] = self.create_team
        self.routes["GET /api/teams/{id}"] = self.get_team
        self.routes["DELETE /api/teams/{id}"] = self.delete_team

        # SSO
        self.routes["GET /api/sso/config"] = self.get_sso_config
        self.routes["POST /api/sso/config"] = self.configure_sso
        self.routes["DELETE /api/sso/config"] = self.disable_sso

        # Reports
        self.routes["GET /api/reports"] = self.list_reports
        self.routes["POST /api/reports"] = self.generate_report
        self.routes["GET /api/reports/{id}"] = self.get_report
        self.routes["GET /api/reports/{id}/export"] = self.export_report

        # Users
        self.routes["POST /api/users/import"] = self.import_users
        self.routes["GET /api/users/export"] = self.export_users

    async def dashboard(self, request) -> Dict[str, Any]:
        """管理仪表盘"""
        stats = self._get_dashboard_stats()
        return {
            "success": True,
            "data": {
                "stats": stats,
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    async def get_stats(self, request) -> Dict[str, Any]:
        """获取统计数据"""
        stats = self._get_dashboard_stats()
        return {"success": True, "data": stats}

    async def list_tenants(self, request) -> Dict[str, Any]:
        """列出租户"""
        if not self.tenant_manager:
            return {"success": False, "error": "Tenant manager not available"}

        query = request.get("query", {})
        tenants = self.tenant_manager.list_tenants(
            status=query.get("status"),
            plan=query.get("plan"),
        )

        return {
            "success": True,
            "data": {
                "tenants": [t.to_dict() for t in tenants],
                "total": len(tenants),
            },
        }

    async def create_tenant(self, request) -> Dict[str, Any]:
        """创建租户"""
        if not self.tenant_manager:
            return {"success": False, "error": "Tenant manager not available"}

        data = request.get("data", {})
        tenant = self.tenant_manager.create_tenant(
            name=data.get("name", "New Tenant"),
            plan=data.get("plan", "trial"),
            contact_email=data.get("contact_email"),
            trial_days=data.get("trial_days", 30),
        )

        return {
            "success": True,
            "data": {"tenant": tenant.to_dict()},
            "message": f"Tenant '{tenant.name}' created successfully",
        }

    async def get_tenant(self, request, id: str) -> Dict[str, Any]:
        """获取租户"""
        if not self.tenant_manager:
            return {"success": False, "error": "Tenant manager not available"}

        tenant = self.tenant_manager.get_tenant(id)
        if not tenant:
            return {"success": False, "error": "Tenant not found"}

        return {"success": True, "data": {"tenant": tenant.to_dict()}}

    async def update_tenant(self, request, id: str) -> Dict[str, Any]:
        """更新租户"""
        if not self.tenant_manager:
            return {"success": False, "error": "Tenant manager not available"}

        data = request.get("data", {})
        tenant = self.tenant_manager.update_tenant(id, **data)

        if not tenant:
            return {"success": False, "error": "Tenant not found"}

        return {
            "success": True,
            "data": {"tenant": tenant.to_dict()},
            "message": "Tenant updated successfully",
        }

    async def delete_tenant(self, request, id: str) -> Dict[str, Any]:
        """删除租户"""
        if not self.tenant_manager:
            return {"success": False, "error": "Tenant manager not available"}

        success = self.tenant_manager.delete_tenant(id)
        if not success:
            return {"success": False, "error": "Tenant not found"}

        return {"success": True, "message": "Tenant deleted successfully"}

    async def list_teams(self, request) -> Dict[str, Any]:
        """列出团队"""
        if not self.team_manager:
            return {"success": False, "error": "Team manager not available"}

        query = request.get("query", {})
        teams = self.team_manager.list_teams(
            tenant_id=query.get("tenant_id"),
            status=query.get("status"),
        )

        return {
            "success": True,
            "data": {
                "teams": [t.to_dict() for t in teams],
                "total": len(teams),
            },
        }

    async def create_team(self, request) -> Dict[str, Any]:
        """创建团队"""
        if not self.team_manager:
            return {"success": False, "error": "Team manager not available"}

        data = request.get("data", {})
        team = self.team_manager.create_team(
            tenant_id=data.get("tenant_id"),
            name=data.get("name", "New Team"),
            description=data.get("description"),
            owner_id=data.get("owner_id"),
        )

        return {
            "success": True,
            "data": {"team": team.to_dict()},
            "message": f"Team '{team.name}' created successfully",
        }

    async def get_team(self, request, id: str) -> Dict[str, Any]:
        """获取团队"""
        if not self.team_manager:
            return {"success": False, "error": "Team manager not available"}

        team = self.team_manager.get_team(id)
        if not team:
            return {"success": False, "error": "Team not found"}

        return {"success": True, "data": {"team": team.to_dict()}}

    async def delete_team(self, request, id: str) -> Dict[str, Any]:
        """删除团队"""
        if not self.team_manager:
            return {"success": False, "error": "Team manager not available"}

        success = self.team_manager.delete_team(id)
        if not success:
            return {"success": False, "error": "Team not found"}

        return {"success": True, "message": "Team deleted successfully"}

    async def get_sso_config(self, request) -> Dict[str, Any]:
        """获取 SSO 配置"""
        if not self.sso_integration:
            return {"success": False, "error": "SSO integration not available"}

        tenant_id = request.get("tenant_id")
        if not tenant_id:
            return {"success": False, "error": "tenant_id required"}

        providers = {}
        for provider in ["oauth2", "saml", "ldap"]:
            config = self.sso_integration.get_config(tenant_id, provider)
            if config:
                providers[provider] = {
                    "enabled": config.get("enabled", False),
                    "config": {k: v for k, v in config.items() if k != "client_secret"},
                }

        return {"success": True, "data": {"providers": providers}}

    async def configure_sso(self, request) -> Dict[str, Any]:
        """配置 SSO"""
        if not self.sso_integration:
            return {"success": False, "error": "SSO integration not available"}

        data = request.get("data", {})
        tenant_id = data.get("tenant_id")
        provider = data.get("provider")
        config_data = data.get("config", {})

        if not tenant_id or not provider:
            return {"success": False, "error": "tenant_id and provider required"}

        # 简化实现：实际应该根据 provider 创建相应的配置对象
        success = True  # 实际应该调用相应的 configure_* 方法

        return {
            "success": success,
            "message": f"SSO configured for {provider}" if success else "Failed to configure SSO",
        }

    async def disable_sso(self, request) -> Dict[str, Any]:
        """禁用 SSO"""
        if not self.sso_integration:
            return {"success": False, "error": "SSO integration not available"}

        data = request.get("data", {})
        tenant_id = data.get("tenant_id")
        provider = data.get("provider")

        if not tenant_id or not provider:
            return {"success": False, "error": "tenant_id and provider required"}

        # 简化实现
        return {"success": True, "message": f"SSO disabled for {provider}"}

    async def list_reports(self, request) -> Dict[str, Any]:
        """列出报表"""
        if not self.report_generator:
            return {"success": False, "error": "Report generator not available"}

        query = request.get("query", {})
        reports = self.report_generator.list_reports(
            tenant_id=query.get("tenant_id"),
            report_type=query.get("report_type"),
            status=query.get("status"),
        )

        return {
            "success": True,
            "data": {
                "reports": [r.to_dict() for r in reports],
                "total": len(reports),
            },
        }

    async def generate_report(self, request) -> Dict[str, Any]:
        """生成报表"""
        if not self.report_generator:
            return {"success": False, "error": "Report generator not available"}

        data = request.get("data", {})
        report = self.report_generator.generate_report(
            report_type=data.get("report_type", "tenant_summary"),
            tenant_id=data.get("tenant_id"),
            title=data.get("title"),
            period_days=data.get("period_days", 30),
            filters=data.get("filters"),
            output_format=data.get("format", "json"),
        )

        return {
            "success": True,
            "data": {"report": report.to_dict()},
            "message": "Report generated successfully" if report.is_completed else "Report generation failed",
        }

    async def get_report(self, request, id: str) -> Dict[str, Any]:
        """获取报表"""
        if not self.report_generator:
            return {"success": False, "error": "Report generator not available"}

        report = self.report_generator.get_report(id)
        if not report:
            return {"success": False, "error": "Report not found"}

        return {"success": True, "data": {"report": report.to_dict()}}

    async def export_report(self, request, id: str) -> Dict[str, Any]:
        """导出报表"""
        if not self.report_generator:
            return {"success": False, "error": "Report generator not available"}

        query = request.get("query", {})
        format = query.get("format")

        file_path = self.report_generator.export_report(id, format)
        if not file_path:
            return {"success": False, "error": "Failed to export report"}

        return {
            "success": True,
            "data": {"file_path": file_path},
            "message": "Report exported successfully",
        }

    async def import_users(self, request) -> Dict[str, Any]:
        """导入用户"""
        # 简化实现
        return {"success": True, "message": "User import initiated"}

    async def export_users(self, request) -> Dict[str, Any]:
        """导出用户"""
        # 简化实现
        return {"success": True, "message": "User export initiated"}

    def _get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表盘统计"""
        stats = {
            "total_tenants": 0,
            "active_tenants": 0,
            "total_teams": 0,
            "total_users": 0,
        }

        if self.tenant_manager:
            tenant_stats = self.tenant_manager.get_statistics()
            stats["total_tenants"] = tenant_stats.get("total_tenants", 0)
            stats["active_tenants"] = tenant_stats.get("by_status", {}).get("active", 0)

        if self.team_manager:
            # 简化实现
            stats["total_teams"] = 0

        return stats

    def handle_request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """处理请求（同步版本）"""
        route_key = f"{method} {path}"
        handler = self.routes.get(route_key)

        if not handler:
            # 尝试匹配参数化路由
            for route, handler in self.routes.items():
                route_parts = route.split()
                if len(route_parts) == 2:
                    route_method, route_path = route_parts
                    if route_method == method:
                        # 简单参数匹配
                        path_parts = path.split("/")
                        route_parts_split = route_path.split("/")
                        if len(path_parts) == len(route_parts_split):
                            params = {}
                            match = True
                            for p, rp in zip(path_parts, route_parts_split):
                                if rp.startswith("{") and rp.endswith("}"):
                                    param_name = rp[1:-1]
                                    params[param_name] = p
                                elif p != rp:
                                    match = False
                                    break
                            if match:
                                return handler(data or {}, **params)

            return {"success": False, "error": f"Route not found: {route_key}"}

        return handler(data or {})


class AdminRouter:
    """管理路由器（FastAPI 集成）"""

    def __init__(self, web_admin_app: WebAdminApp):
        self.web_admin = web_admin_app
        self.router = None
        self._setup_router()

    def _setup_router(self):
        """设置路由器"""
        try:
            from fastapi import APIRouter
            self.router = APIRouter(prefix="/admin", tags=["admin"])
            self._register_fastapi_routes()
        except ImportError:
            pass

    def _register_fastapi_routes(self):
        """注册 FastAPI 路由"""
        if not self.router:
            return

        from fastapi import Request

        @self.router.get("/")
        async def dashboard():
            return await self.web_admin.dashboard({})

        @self.router.get("/stats")
        async def get_stats():
            return await self.web_admin.get_stats({})

        @self.router.get("/tenants")
        async def list_tenants(status: str = None, plan: str = None):
            return await self.web_admin.list_tenants({"query": {"status": status, "plan": plan}})

        @self.router.post("/tenants")
        async def create_tenant(request: Request):
            data = await request.json()
            return await self.web_admin.create_tenant({"data": data})

        @self.router.get("/tenants/{tenant_id}")
        async def get_tenant(tenant_id: str):
            return await self.web_admin.get_tenant({}, id=tenant_id)

        @self.router.put("/tenants/{tenant_id}")
        async def update_tenant(tenant_id: str, request: Request):
            data = await request.json()
            return await self.web_admin.update_tenant({"data": data}, id=tenant_id)

        @self.router.delete("/tenants/{tenant_id}")
        async def delete_tenant(tenant_id: str):
            return await self.web_admin.delete_tenant({}, id=tenant_id)

        @self.router.get("/teams")
        async def list_teams(tenant_id: str = None, status: str = None):
            return await self.web_admin.list_teams({"query": {"tenant_id": tenant_id, "status": status}})

        @self.router.post("/teams")
        async def create_team(request: Request):
            data = await request.json()
            return await self.web_admin.create_team({"data": data})

        @self.router.get("/teams/{team_id}")
        async def get_team(team_id: str):
            return await self.web_admin.get_team({}, id=team_id)

        @self.router.delete("/teams/{team_id}")
        async def delete_team(team_id: str):
            return await self.web_admin.delete_team({}, id=team_id)

        @self.router.get("/reports")
        async def list_reports(tenant_id: str = None, report_type: str = None, status: str = None):
            return await self.web_admin.list_reports({"query": {"tenant_id": tenant_id, "report_type": report_type, "status": status}})

        @self.router.post("/reports")
        async def generate_report(request: Request):
            data = await request.json()
            return await self.web_admin.generate_report({"data": data})

        @self.router.get("/reports/{report_id}")
        async def get_report(report_id: str):
            return await self.web_admin.get_report({}, id=report_id)

        @self.router.get("/reports/{report_id}/export")
        async def export_report(report_id: str, format: str = "json"):
            return await self.web_admin.export_report({"query": {"format": format}}, id=report_id)

    def get_router(self):
        """获取路由器"""
        return self.router
