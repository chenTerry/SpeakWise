"""
Admin Dashboard - 管理员仪表盘

提供企业管理员 CLI 界面：
- AdminDashboard: 管理员仪表盘
- AdminStats: 管理统计

Version: v0.9.0
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

if TYPE_CHECKING:
    from .tenant import TenantManager, Tenant
    from .team import TeamManager


@dataclass
class AdminStats:
    """管理统计"""
    total_tenants: int = 0
    active_tenants: int = 0
    total_teams: int = 0
    total_users: int = 0
    total_sessions: int = 0
    sessions_today: int = 0
    sessions_this_week: int = 0
    revenue_mtd: float = 0.0
    revenue_ytd: float = 0.0
    expiring_trials: int = 0
    system_health: str = "healthy"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_tenants": self.total_tenants,
            "active_tenants": self.active_tenants,
            "total_teams": self.total_teams,
            "total_users": self.total_users,
            "total_sessions": self.total_sessions,
            "sessions_today": self.sessions_today,
            "sessions_this_week": self.sessions_this_week,
            "revenue_mtd": self.revenue_mtd,
            "revenue_ytd": self.revenue_ytd,
            "expiring_trials": self.expiring_trials,
            "system_health": self.system_health,
        }


class AdminDashboard:
    """管理员仪表盘"""

    def __init__(
        self,
        tenant_manager: Optional["TenantManager"] = None,
        team_manager: Optional["TeamManager"] = None,
    ):
        # Create default managers if not provided
        if tenant_manager is None:
            from .tenant import TenantManager
            tenant_manager = TenantManager(db_path=":memory:")
        if team_manager is None:
            from .team import TeamManager
            team_manager = TeamManager(db_path=":memory:")
        
        self.tenant_manager = tenant_manager
        self.team_manager = team_manager
        self.console = Console()

    def render(self) -> Layout:
        """渲染仪表盘"""
        layout = Layout()

        # 获取统计数据
        stats = self.get_stats()

        # 顶部统计卡片
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
        )

        layout["header"].update(self._render_header())

        # 主体内容
        body = Layout()
        body.split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        body["left"].split(
            Layout(name="stats", size=15),
            Layout(name="tenants"),
        )

        body["right"].split(
            Layout(name="activity", size=10),
            Layout(name="alerts"),
        )

        body["left"]["stats"].update(self._render_stats_panel(stats))
        body["left"]["tenants"].update(self._render_tenants_table())
        body["right"]["activity"].update(self._render_activity_panel())
        body["right"]["alerts"].update(self._render_alerts_panel())

        layout["body"].update(body)
        return layout

    def display(self):
        """显示仪表盘"""
        layout = self.render()
        self.console.print(layout)

    def _render_header(self) -> Panel:
        """渲染头部"""
        title = Text("🏢 Enterprise Admin Dashboard", style="bold blue")
        subtitle = Text(f"Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style="dim")
        
        header_text = Text()
        header_text.append(title)
        header_text.append("\n")
        header_text.append(subtitle)

        return Panel(header_text, border_style="blue")

    def _render_stats_panel(self, stats: AdminStats) -> Panel:
        """渲染统计面板"""
        table = Table(show_header=True, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green", justify="right")

        table.add_row("Total Tenants", str(stats.total_tenants))
        table.add_row("Active Tenants", str(stats.active_tenants))
        table.add_row("Total Teams", str(stats.total_teams))
        table.add_row("Total Users", str(stats.total_users))
        table.add_row("Total Sessions", str(stats.total_sessions))
        table.add_row("Sessions Today", str(stats.sessions_today))
        table.add_row("Sessions This Week", str(stats.sessions_this_week))
        table.add_row("Revenue (MTD)", f"${stats.revenue_mtd:,.2f}")
        table.add_row("Revenue (YTD)", f"${stats.revenue_ytd:,.2f}")
        table.add_row("Expiring Trials", str(stats.expiring_trials))
        
        health_style = "green" if stats.system_health == "healthy" else "red"
        table.add_row("System Health", Text(stats.system_health, style=health_style))

        return Panel(table, title="📊 System Statistics", border_style="green")

    def _render_tenants_table(self) -> Panel:
        """渲染租户表格"""
        tenants = self.tenant_manager.list_tenants()[:10]  # 最近 10 个

        table = Table(show_header=True)
        table.add_column("ID", style="dim", width=15)
        table.add_column("Name", style="cyan")
        table.add_column("Plan", style="yellow")
        table.add_column("Status", width=10)
        table.add_column("Expires", width=12)

        for tenant in tenants:
            plan_style = {
                "free": "green",
                "basic": "cyan",
                "professional": "blue",
                "enterprise": "magenta",
            }.get(tenant.plan.value, "white")

            status_style = {
                "active": "green",
                "trial": "yellow",
                "suspended": "red",
                "inactive": "dim",
            }.get(tenant.status.value, "white")

            expires = tenant.expires_at.strftime("%Y-%m-%d") if tenant.expires_at else "N/A"

            table.add_row(
                tenant.id,
                tenant.name,
                Text(tenant.plan.value, style=plan_style),
                Text(tenant.status.value, style=status_style),
                expires,
            )

        return Panel(table, title="🏢 Recent Tenants", border_style="cyan")

    def _render_activity_panel(self) -> Panel:
        """渲染活动面板"""
        # 模拟活动数据
        activities = [
            ("10:30", "New tenant created: Acme Corp", "green"),
            ("09:45", "Team 'Engineering' created", "cyan"),
            ("09:15", "Session completed: Interview #123", "blue"),
            ("08:30", "User login: admin@company.com", "dim"),
        ]

        text = Text()
        for time, event, style in activities:
            text.append(f"{time} ", style="dim")
            text.append(f"{event}\n", style=style)

        return Panel(text, title="📈 Recent Activity", border_style="yellow")

    def _render_alerts_panel(self) -> Panel:
        """渲染告警面板"""
        alerts = []

        # 检查即将过期的试用
        tenants = self.tenant_manager.list_tenants()
        for tenant in tenants:
            if tenant.days_remaining and tenant.days_remaining <= 7:
                alerts.append((
                    "warning",
                    f"Trial expiring: {tenant.name} ({tenant.days_remaining} days)",
                ))

        if not alerts:
            text = Text("✅ No alerts at this time", style="green")
        else:
            text = Text()
            for level, message in alerts:
                icon = "⚠️" if level == "warning" else "🔴"
                text.append(f"{icon} {message}\n", style="yellow" if level == "warning" else "red")

        return Panel(text, title="🔔 Alerts", border_style="red" if alerts else "green")

    def get_stats(self) -> AdminStats:
        """获取统计数据"""
        tenants = self.tenant_manager.list_tenants()
        tenant_stats = self.tenant_manager.get_statistics()

        # 收集所有团队的统计
        all_teams = []
        for tenant in tenants:
            teams = self.team_manager.list_teams(tenant_id=tenant.id)
            all_teams.extend(teams)

        team_stats = {}
        for team in all_teams:
            stats = self.team_manager.get_statistics(team.tenant_id)
            team_stats[team.tenant_id] = stats

        total_teams = len(all_teams)
        total_users = sum(t.config.max_users for t in tenants if t.is_active)

        return AdminStats(
            total_tenants=tenant_stats["total_tenants"],
            active_tenants=tenant_stats["by_status"].get("active", 0),
            total_teams=total_teams,
            total_users=total_users,
            total_sessions=0,  # 从会话管理器获取
            sessions_today=0,
            sessions_this_week=0,
            revenue_mtd=0.0,
            revenue_ytd=0.0,
            expiring_trials=tenant_stats.get("expiring_soon", 0),
            system_health="healthy",
        )

    def get_dashboard_data(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """获取仪表盘数据"""
        stats = self.get_stats()
        return {
            "total_sessions": stats.total_sessions,
            "active_users": stats.total_users,
            "average_score": 0.0,
            "total_tenants": stats.total_tenants,
            "total_teams": stats.total_teams,
            "system_health": stats.system_health,
        }

    def show_tenant_detail(self, tenant_id: str):
        """显示租户详情"""
        tenant = self.tenant_manager.get_tenant(tenant_id)
        if not tenant:
            self.console.print(f"[red]Tenant {tenant_id} not found[/red]")
            return

        table = Table(show_header=True)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("ID", tenant.id)
        table.add_row("Name", tenant.name)
        table.add_row("Status", tenant.status.value)
        table.add_row("Plan", tenant.plan.value)
        table.add_row("Created", tenant.created_at.strftime("%Y-%m-%d"))
        if tenant.expires_at:
            table.add_row("Expires", tenant.expires_at.strftime("%Y-%m-%d"))
            if tenant.days_remaining:
                table.add_row("Days Remaining", str(tenant.days_remaining))
        table.add_row("Contact", tenant.contact_email or "N/A")
        table.add_row("Max Users", str(tenant.config.max_users))
        table.add_row("Max Teams", str(tenant.config.max_teams))

        self.console.print(Panel(table, title=f"Tenant: {tenant.name}", border_style="blue"))
