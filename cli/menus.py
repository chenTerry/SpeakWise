"""
CLI Menus - CLI 菜单系统模块

提供交互式菜单系统，支持场景选择、对话控制和反馈展示。

核心类:
- MenuManager: 菜单管理器
- SceneMenu: 场景选择菜单
- DialogueMenu: 对话控制菜单
- FeedbackMenu: 反馈展示菜单
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from .themes import Theme, get_current_theme, ThemeManager
from .widgets import Menu, Header, Footer, Divider, UIWidget


class MenuManager:
    """
    菜单管理器

    管理菜单的显示、导航和选择。

    Example:
        >>> manager = MenuManager(console)
        >>> manager.show_menu(main_menu)
        >>> choice = manager.get_choice()
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        theme: Optional[Theme] = None,
    ):
        """
        初始化菜单管理器

        Args:
            console: Rich Console 对象
            theme: 主题对象
        """
        self.console = console or Console(theme=theme.to_rich_theme() if theme else None)
        self.theme = theme or get_current_theme()
        self._history: List[str] = []
        self._callbacks: Dict[str, Callable] = {}

    def register_callback(self, key: str, callback: Callable) -> None:
        """
        注册菜单项回调

        Args:
            key: 菜单项键
            callback: 回调函数
        """
        self._callbacks[key] = callback

    def show_menu(
        self,
        menu: Menu,
        header: Optional[Header] = None,
        footer: Optional[Footer] = None,
    ) -> None:
        """
        显示菜单

        Args:
            menu: 菜单对象
            header: 页头组件
            footer: 页脚组件
        """
        self.console.clear()

        if header:
            self.console.print(header.render())

        self.console.print()
        self.console.print(menu.render())

        if footer:
            self.console.print()
            self.console.print(footer.render())

    def get_choice(
        self,
        menu: Menu,
        prompt: str = "请选择",
        valid_choices: Optional[List[str]] = None,
    ) -> str:
        """
        获取用户选择

        Args:
            menu: 菜单对象
            prompt: 提示文本
            valid_choices: 有效选择列表

        Returns:
            用户选择的键
        """
        if valid_choices is None:
            valid_choices = [key for key, _ in menu.items]

        choice = Prompt.ask(
            prompt,
            choices=valid_choices,
            default=valid_choices[0] if valid_choices else "",
        )

        self._history.append(choice)
        return choice

    def execute_callback(self, key: str, *args, **kwargs) -> Any:
        """
        执行菜单项回调

        Args:
            key: 菜单项键
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            回调函数返回值
        """
        if key in self._callbacks:
            return self._callbacks[key](*args, **kwargs)
        return None

    def clear(self) -> None:
        """清屏"""
        self.console.clear()

    def get_history(self) -> List[str]:
        """获取选择历史"""
        return self._history.copy()

    def clear_history(self) -> None:
        """清除历史"""
        self._history.clear()


class SceneMenu(UIWidget):
    """
    场景选择菜单

    显示可用的面试场景列表供用户选择。

    Example:
        >>> scene_menu = SceneMenu(scenes)
        >>> menu.render(console)
    """

    def __init__(
        self,
        scenes: List[Dict[str, Any]],
        title: str = "选择面试场景",
        theme: Optional[Theme] = None,
    ):
        """
        初始化场景菜单

        Args:
            scenes: 场景列表，每个场景包含 name, description, difficulty 等
            title: 菜单标题
            theme: 主题对象
        """
        super().__init__(theme)
        self.scenes = scenes
        self.title = title

    def render(self, console: Optional[Console] = None) -> Panel:
        """渲染场景菜单"""
        text = Text()

        for i, scene in enumerate(self.scenes, 1):
            name = scene.get("name", f"场景{i}")
            description = scene.get("description", "")
            difficulty = scene.get("difficulty", 0)

            # 场景名称
            text.append(f"  {i}. ", style=self._get_style("primary"))
            text.append(f"{name}\n", style=self._get_style("text"))

            # 场景描述
            if description:
                text.append(f"     {description}\n", style=self._get_style("muted"))

            # 难度指示
            if difficulty:
                difficulty_bar = "★" * difficulty + "☆" * (5 - difficulty)
                text.append(f"     难度：{difficulty_bar}\n", style=self._get_style("warning"))

            text.append("\n")

        return Panel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )

    def get_scene_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """根据索引获取场景"""
        if 1 <= index <= len(self.scenes):
            return self.scenes[index - 1]
        return None


class DialogueMenu(UIWidget):
    """
    对话控制菜单

    显示对话过程中的可用操作。

    Example:
        >>> dialogue_menu = DialogueMenu()
        >>> menu.render(console)
    """

    DEFAULT_ITEMS = [
        ("1", "继续对话"),
        ("2", "查看历史"),
        ("3", "结束面试"),
        ("4", "获取提示"),
        ("5", "切换主题"),
        ("/help", "帮助"),
        ("/quit", "退出"),
    ]

    def __init__(
        self,
        items: Optional[List[Tuple[str, str]]] = None,
        title: str = "对话操作",
        theme: Optional[Theme] = None,
    ):
        """
        初始化对话菜单

        Args:
            items: 菜单项列表
            title: 菜单标题
            theme: 主题对象
        """
        super().__init__(theme)
        self.items = items or self.DEFAULT_ITEMS.copy()
        self.title = title

    def render(self, console: Optional[Console] = None) -> Panel:
        """渲染对话菜单"""
        text = Text()

        for key, label in self.items:
            text.append(f"  {key}. ", style=self._get_style("secondary"))
            text.append(f"{label}\n", style=self._get_style("text"))

        return Panel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )


class FeedbackMenu(UIWidget):
    """
    反馈展示菜单

    显示评估反馈和报告。

    Example:
        >>> feedback_menu = FeedbackMenu(result)
        >>> menu.render(console)
    """

    def __init__(
        self,
        evaluation_result: Any = None,
        title: str = "面试反馈",
        theme: Optional[Theme] = None,
    ):
        """
        初始化反馈菜单

        Args:
            evaluation_result: 评估结果对象
            title: 菜单标题
            theme: 主题对象
        """
        super().__init__(theme)
        self.evaluation_result = evaluation_result
        self.title = title

    def render(self, console: Optional[Console] = None) -> Panel:
        """渲染反馈菜单"""
        text = Text()

        if self.evaluation_result:
            # 总体评分
            overall_score = getattr(self.evaluation_result, "overall_score", 0)
            rating = self._get_rating(overall_score)

            text.append("  总体评分：", style=self._get_style("muted"))
            text.append(f"{overall_score:.1f}/5.0 ", style=self._get_style("primary"))
            text.append(f"({rating})\n\n", style=self._get_style("accent"))

            # 维度评分
            text.append("  维度评分:\n", style=self._get_style("secondary"))

            dimensions = getattr(self.evaluation_result, "dimensions", {})
            for dim_name, dim_data in dimensions.items():
                score = dim_data.get("score", 0) if isinstance(dim_data, dict) else 0
                bar = self._create_score_bar(score)
                text.append(f"    {dim_name}: ", style=self._get_style("text"))
                text.append(f"{bar} ", style=self._get_style("success"))
                text.append(f"{score:.1f}\n", style=self._get_style("muted"))

            text.append("\n")

            # 改进建议
            suggestions = getattr(self.evaluation_result, "suggestions", [])
            if suggestions:
                text.append("  改进建议:\n", style=self._get_style("secondary"))
                for i, suggestion in enumerate(suggestions[:5], 1):
                    text.append(f"    {i}. {suggestion}\n", style=self._get_style("muted"))
        else:
            text.append("  暂无评估结果\n", style=self._get_style("muted"))

        return Panel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )

    def _get_rating(self, score: float) -> str:
        """根据分数获取评级"""
        if score >= 4.5:
            return "S - 卓越"
        elif score >= 4.0:
            return "A - 优秀"
        elif score >= 3.0:
            return "B - 良好"
        elif score >= 2.0:
            return "C - 一般"
        else:
            return "D - 需改进"

    def _create_score_bar(self, score: float, max_width: int = 20) -> str:
        """创建分数进度条"""
        filled = int((score / 5.0) * max_width)
        empty = max_width - filled
        return "█" * filled + "░" * empty


class MainMenu(UIWidget):
    """
    主菜单

    应用程序的主入口菜单。
    """

    DEFAULT_ITEMS = [
        ("1", "开始面试"),
        ("2", "场景选择"),
        ("3", "历史记录"),
        ("4", "设置"),
        ("5", "帮助"),
        ("0", "退出"),
    ]

    def __init__(
        self,
        items: Optional[List[Tuple[str, str]]] = None,
        title: str = "主菜单",
        theme: Optional[Theme] = None,
    ):
        super().__init__(theme)
        self.items = items or self.DEFAULT_ITEMS.copy()
        self.title = title

    def render(self, console: Optional[Console] = None) -> Panel:
        """渲染主菜单"""
        text = Text()

        for key, label in self.items:
            if key == "0":
                text.append(f"\n  {key}. ", style=self._get_style("error"))
            else:
                text.append(f"  {key}. ", style=self._get_style("secondary"))
            text.append(f"{label}\n", style=self._get_style("text"))

        return Panel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )


class SettingsMenu(UIWidget):
    """
    设置菜单

    显示和修改应用程序设置。
    """

    def __init__(
        self,
        settings: Dict[str, Any],
        title: str = "设置",
        theme: Optional[Theme] = None,
    ):
        super().__init__(theme)
        self.settings = settings
        self.title = title

    def render(self, console: Optional[Console] = None) -> Panel:
        """渲染设置菜单"""
        text = Text()

        text.append("  当前设置:\n\n", style=self._get_style("secondary"))

        for key, value in self.settings.items():
            text.append(f"    {key}: ", style=self._get_style("muted"))
            text.append(f"{value}\n", style=self._get_style("text"))

        text.append("\n  操作:\n", style=self._get_style("secondary"))
        text.append("    1. 切换主题\n", style=self._get_style("text"))
        text.append("    2. 修改配置\n", style=self._get_style("text"))
        text.append("    0. 返回\n", style=self._get_style("text"))

        return Panel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )


class HelpPanel(UIWidget):
    """
    帮助面板

    显示帮助信息和使用说明。
    """

    def __init__(
        self,
        title: str = "帮助",
        theme: Optional[Theme] = None,
    ):
        super().__init__(theme)
        self.title = title

    def render(self, console: Optional[Console] = None) -> Panel:
        """渲染帮助面板"""
        text = Text()

        text.append("  快捷命令:\n\n", style=self._get_style("secondary"))
        text.append("    /help     - 显示帮助信息\n", style=self._get_style("text"))
        text.append("    /quit     - 退出应用程序\n", style=self._get_style("text"))
        text.append("    /theme    - 切换主题\n", style=self._get_style("text"))
        text.append("    /history  - 查看对话历史\n", style=self._get_style("text"))
        text.append("    /clear    - 清屏\n", style=self._get_style("text"))
        text.append("    /export   - 导出对话记录\n", style=self._get_style("text"))

        text.append("\n  对话技巧:\n\n", style=self._get_style("secondary"))
        text.append("    • 清晰表达你的想法\n", style=self._get_style("muted"))
        text.append("    • 提供具体的例子\n", style=self._get_style("muted"))
        text.append("    • 遇到难题时不要慌张\n", style=self._get_style("muted"))
        text.append("    • 可以请求提示或澄清\n", style=self._get_style("muted"))

        return Panel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )
