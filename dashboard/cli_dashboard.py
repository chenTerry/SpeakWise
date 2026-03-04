"""
CLI Dashboard

CLI 终端仪表盘：
- 用户信息展示
- 进度统计
- 快速导航菜单

Design Principles:
- 使用 Rich 库美化输出
- 清晰的布局
- 交互式菜单
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.layout import Layout
from rich.text import Text

from users.service import UserService
from users.database import Database
from progress.tracker import ProgressTracker
from visualization.charts import create_bar_chart, create_progress_bar
from visualization.radar import DimensionRadarChart


class CLIDashboard:
    """
    CLI 仪表盘
    
    在终端显示用户仪表盘
    
    Usage:
        dashboard = CLIDashboard(user_id=1)
        dashboard.display()
    """
    
    def __init__(self, user_id: int, db: Optional[Database] = None):
        """
        初始化 CLI 仪表盘
        
        Args:
            user_id: 用户 ID
            db: 数据库实例（可选）
        """
        self.user_id = user_id
        self.db = db or Database.get_instance()
        self.console = Console()
        
        self.user_service = UserService(self.db)
        self.progress_tracker = ProgressTracker(user_id, self.db)
    
    def display(self) -> None:
        """
        显示仪表盘
        """
        self.console.clear()
        
        # 获取数据
        user = self.user_service.get_user(self.user_id)
        progress = self.progress_tracker.get_progress()
        
        if not user:
            self.console.print("[red]用户不存在[/red]")
            return
        
        # 创建布局
        layout = Layout()
        
        # 分割布局
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=10),
        )
        
        # 填充内容
        layout["header"].update(self._create_header(user))
        layout["body"].update(self._create_body(progress))
        layout["footer"].update(self._create_footer())
        
        self.console.print(layout)
    
    def _create_header(self, user: Dict[str, Any]) -> Panel:
        """创建头部面板"""
        display_name = user.get("display_name") or user.get("username")
        
        header_text = Text()
        header_text.append(f"👤 {display_name}", style="bold cyan")
        header_text.append(f"\n欢迎回来！", style="green")
        header_text.append(f"\n最后登录：{user.get('last_login', 'N/A')}", style="dim")
        
        return Panel(
            header_text,
            title="[bold]用户信息[/bold]",
            border_style="cyan",
        )
    
    def _create_body(self, progress: Optional[Dict[str, Any]]) -> Panel:
        """创建主体面板"""
        if not progress:
            return Panel(
                "[yellow]暂无进度数据，开始第一次练习吧！[/yellow]",
                title="[bold]进度概览[/bold]",
                border_style="yellow",
            )
        
        # 创建进度表格
        table = Table(show_header=False, box=None)
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="bold")
        
        table.add_row("总会话数", str(progress.get("total_sessions", 0)))
        table.add_row("完成会话数", str(progress.get("completed_sessions", 0)))
        
        # 格式化时长
        total_seconds = progress.get("total_duration_seconds", 0)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        duration_str = f"{hours}小时{minutes}分钟"
        table.add_row("总练习时长", duration_str)
        
        # 平均分
        avg_score = progress.get("avg_score", 0)
        score_style = "green" if avg_score >= 80 else "yellow" if avg_score >= 60 else "red"
        table.add_row("平均分数", f"[{score_style}]{avg_score:.1f}[/{score_style}]")
        
        # 改进率
        improvement_rate = progress.get("improvement_rate", 0)
        if improvement_rate > 0:
            rate_str = f"[green]+{improvement_rate:.1f}%[/green] ↑"
        elif improvement_rate < 0:
            rate_str = f"[red]{improvement_rate:.1f}%[/red] ↓"
        else:
            rate_str = "[dim]0.0%[/dim] -"
        table.add_row("改进率", rate_str)
        
        # 连续天数
        streak_days = progress.get("streak_days", 0)
        streak_icon = "🔥" if streak_days > 0 else "⏰"
        table.add_row("连续练习", f"{streak_icon} {streak_days}天")
        
        return Panel(
            table,
            title="[bold]进度统计[/bold]",
            border_style="green",
        )
    
    def _create_footer(self) -> Panel:
        """创建底部面板（菜单）"""
        menu_text = Text()
        menu_text.append("\n", end="")
        menu_text.append("  [1] 开始新练习  ", style="bold cyan")
        menu_text.append("  [2] 查看历史  ", style="bold cyan")
        menu_text.append("  [3] 进度报告  ", style="bold cyan")
        menu_text.append("  [4] 能力雷达图  ", style="bold cyan")
        menu_text.append("\n", end="")
        menu_text.append("  [5] 设置  ", style="bold yellow")
        menu_text.append("  [0] 退出  ", style="bold red")
        menu_text.append("\n")
        
        return Panel(
            menu_text,
            title="[bold]菜单[/bold]",
            border_style="blue",
        )
    
    def display_progress_chart(self) -> None:
        """显示进度图表"""
        progress = self.progress_tracker.get_progress()
        
        if not progress:
            self.console.print("[yellow]暂无数据[/yellow]")
            return
        
        self.console.print("\n[bold]七维度评估[/bold]\n")
        
        # 使用 ASCII 进度条显示
        dimension_scores = progress.get("dimension_scores", {})
        
        dimension_names = {
            "language_expression": "语言表达",
            "logical_thinking": "逻辑思维",
            "professional_knowledge": "专业知识",
            "problem_solving": "问题解决",
            "communication_collaboration": "沟通协作",
            "adaptability": "应变能力",
            "overall_quality": "综合素质",
        }
        
        for dim_key, dim_name in dimension_names.items():
            score = dimension_scores.get(dim_key, 0)
            bar = create_progress_bar(dim_name, score, 100, width=40)
            self.console.print(bar)
    
    def display_history(self, limit: int = 10) -> None:
        """显示最近历史"""
        history = self.progress_tracker.get_session_history(limit=limit)
        
        if not history:
            self.console.print("[yellow]暂无历史记录[/yellow]")
            return
        
        table = Table(title="最近会话历史")
        table.add_column("ID", style="dim")
        table.add_column("场景", style="cyan")
        table.add_column("标题", style="bold")
        table.add_column("状态", style="yellow")
        table.add_column("时长", style="green")
        table.add_column("分数", style="magenta")
        
        for session in history:
            # 解析分数
            score_str = "-"
            eval_result = session.get("evaluation_result")
            if eval_result:
                if isinstance(eval_result, dict):
                    score = eval_result.get("overall_score", 0)
                else:
                    import json
                    try:
                        result = json.loads(str(eval_result))
                        score = result.get("overall_score", 0)
                    except:
                        score = 0
                score_str = f"{score:.1f}"
            
            # 格式化时长
            duration = session.get("duration_seconds", 0)
            if duration:
                duration_str = f"{duration // 60}分钟"
            else:
                duration_str = "-"
            
            table.add_row(
                str(session.get("id", "")),
                session.get("scene_type", "unknown"),
                session.get("title") or "-",
                session.get("status", "unknown"),
                duration_str,
                score_str,
            )
        
        self.console.print(table)
    
    def display_menu(self) -> Optional[str]:
        """
        显示菜单并获取用户选择
        
        Returns:
            用户选择的选项
        """
        self.console.print("\n[bold cyan]请选择操作：[/bold cyan] ", end="")
        choice = input().strip()
        return choice
    
    def show_welcome(self) -> None:
        """显示欢迎信息"""
        welcome_panel = Panel(
            Text.from_markup(
                "[bold cyan]🎯 AgentScope AI Interview[/bold cyan]\n\n"
                "欢迎使用用户系统 v0.6\n\n"
                "在这里你可以：\n"
                "• 进行面试模拟练习\n"
                "• 查看进度和数据分析\n"
                "• 回放历史会话\n"
                "• 导出学习报告\n"
            ),
            title="[bold]欢迎[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )
        self.console.print(welcome_panel)
