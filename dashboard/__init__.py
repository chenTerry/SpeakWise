"""
AgentScope AI Interview - Dashboard Module

用户仪表盘模块提供：
- CLI 仪表盘显示
- Web 仪表盘页面
- 进度报告导出

版本：v0.6.0
"""

from .cli_dashboard import CLIDashboard
from .web_dashboard import WebDashboardRouter
from .report import ReportGenerator

__version__ = "0.6.0"

__all__ = [
    "CLIDashboard",
    "WebDashboardRouter",
    "ReportGenerator",
]
