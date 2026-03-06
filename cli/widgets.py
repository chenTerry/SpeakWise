"""
CLI Widgets - CLI UI 组件模块

提供可复用的 UI 组件，用于构建丰富的命令行界面。

核心组件:
- UIWidget: 基础组件类
- Header: 页头组件
- Footer: 页脚组件
- MessageBubble: 消息气泡
- TypingIndicator: 打字指示器
- ProgressBar: 进度条
- Spinner: 旋转加载器
- Panel: 面板组件
"""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from rich.console import Console, RenderableType
from rich.live import Live
from rich.panel import Panel as RichPanel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text
from rich.style import Style

from .themes import Theme, get_current_theme


class UIWidget(ABC):
    """
    UI 组件基类

    所有 UI 组件的抽象基类，提供统一的渲染接口。
    """

    def __init__(self, theme: Optional[Theme] = None):
        """
        初始化组件

        Args:
            theme: 主题对象，默认使用当前全局主题
        """
        self._theme = theme or get_current_theme()

    @property
    def theme(self) -> Theme:
        """获取主题"""
        return self._theme

    @theme.setter
    def theme(self, theme: Theme) -> None:
        """设置主题"""
        self._theme = theme

    @abstractmethod
    def render(self, console: Optional[Console] = None) -> Any:
        """
        渲染组件

        Args:
            console: Rich Console 对象，可选

        Returns:
            渲染结果
        """
        pass

    def _get_style(self, name: str) -> Style:
        """获取样式"""
        return self._theme.get_style(name)


class Header(UIWidget):
    """
    页头组件

    显示应用程序标题和状态信息。

    Example:
        >>> header = Header(title="AI Interview", subtitle="v0.4")
        >>> header.render(console)
    """

    def __init__(
        self,
        title: str = "AI Interview",
        subtitle: str = "",
        show_version: bool = True,
        theme: Optional[Theme] = None,
    ):
        """
        初始化页头

        Args:
            title: 主标题
            subtitle: 副标题
            show_version: 是否显示版本号
            theme: 主题对象
        """
        super().__init__(theme)
        self.title = title
        self.subtitle = subtitle
        self.show_version = show_version

    def render(self, console: Optional[Console] = None) -> RichPanel:
        """渲染页头"""
        text = Text()

        # 主标题
        text.append(self.title, style=self._get_style("primary"))

        # 版本号
        if self.show_version:
            text.append(" v0.4.0", style=self._get_style("muted"))

        # 副标题
        if self.subtitle:
            text.append("\n")
            text.append(self.subtitle, style=self._get_style("secondary"))

        # 分隔线
        text.append("\n")
        text.append("─" * 60, style=self._get_style("border"))

        return RichPanel(
            text,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(0, 2),
        )


class Footer(UIWidget):
    """
    页脚组件

    显示帮助信息和快捷操作提示。

    Example:
        >>> footer = Footer(hints=["/help - 帮助", "/quit - 退出"])
        >>> footer.render(console)
    """

    def __init__(
        self,
        hints: Optional[List[str]] = None,
        show_shortcuts: bool = True,
        theme: Optional[Theme] = None,
    ):
        """
        初始化页脚

        Args:
            hints: 提示信息列表
            show_shortcuts: 是否显示快捷键
            theme: 主题对象
        """
        super().__init__(theme)
        self.hints = hints or []
        self.show_shortcuts = show_shortcuts

        # 默认快捷键
        self.shortcuts = [
            ("/help", "帮助"),
            ("/quit", "退出"),
            ("/theme", "切换主题"),
        ]

    def render(self, console: Optional[Console] = None) -> RichPanel:
        """渲染页脚"""
        text = Text()

        # 快捷键
        if self.show_shortcuts:
            text.append("快捷操作: ", style=self._get_style("muted"))
            shortcut_texts = []
            for cmd, desc in self.shortcuts:
                shortcut_texts.append(f"{cmd} ")
                shortcut_texts.append(f"- {desc}  ")
            text.append("".join(shortcut_texts), style=self._get_style("info"))
            text.append("\n")

        # 自定义提示
        if self.hints:
            for hint in self.hints:
                text.append(f"• {hint}\n", style=self._get_style("muted"))

        return RichPanel(
            text,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(0, 2),
        )


class MessageBubble(UIWidget):
    """
    消息气泡组件

    用于显示对话消息，支持不同角色样式。

    Example:
        >>> bubble = MessageBubble("你好", role="user")
        >>> bubble.render(console)
    """

    ROLE_STYLES = {
        "user": "user_message",
        "assistant": "agent_message",
        "agent": "agent_message",
        "interviewer": "agent_message",
        "system": "system_message",
        "evaluation": "info",
    }

    ROLE_ICONS = {
        "user": "👤",
        "assistant": "🤖",
        "agent": "🤖",
        "interviewer": "👨‍🏫",
        "system": "⚙️",
        "evaluation": "📊",
    }

    def __init__(
        self,
        content: str,
        role: str = "user",
        show_timestamp: bool = True,
        timestamp: Optional[float] = None,
        theme: Optional[Theme] = None,
    ):
        """
        初始化消息气泡

        Args:
            content: 消息内容
            role: 角色类型
            show_timestamp: 是否显示时间戳
            timestamp: 时间戳，默认使用当前时间
            theme: 主题对象
        """
        super().__init__(theme)
        self.content = content
        self.role = role.lower()
        self.show_timestamp = show_timestamp
        self.timestamp = timestamp or time.time()

    def render(self, console: Optional[Console] = None) -> RichPanel:
        """渲染消息气泡"""
        text = Text()

        # 角色图标和名称
        icon = self.ROLE_ICONS.get(self.role, "💬")
        role_display = self.role.capitalize()
        text.append(f"{icon} {role_display}\n", style=self._get_style("muted"))

        # 消息内容
        text.append(self.content, style=self._get_style("text"))

        # 时间戳
        if self.show_timestamp:
            from datetime import datetime
            time_str = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
            text.append(f"\n\n{time_str}", style=self._get_style("muted"))

        # 获取样式
        style_name = self.ROLE_STYLES.get(self.role, "text")

        return RichPanel(
            text,
            title=f"[{self.role}]",
            style=self._get_style("background"),
            border_style=self._get_style(style_name),
            padding=(1, 2),
        )


class TypingIndicator(UIWidget):
    """
    打字指示器组件

    显示 AI 正在输入的动画效果。

    Example:
        >>> indicator = TypingIndicator()
        >>> with indicator.live(console):
        ...     time.sleep(2)  # 模拟打字
    """

    ANIMATION_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(
        self,
        message: str = "AI 正在输入",
        theme: Optional[Theme] = None,
    ):
        """
        初始化打字指示器

        Args:
            message: 提示消息
            theme: 主题对象
        """
        super().__init__(theme)
        self.message = message
        self._frame_index = 0

    def _get_current_frame(self) -> str:
        """获取当前动画帧"""
        frame = self.ANIMATION_FRAMES[self._frame_index]
        self._frame_index = (self._frame_index + 1) % len(self.ANIMATION_FRAMES)
        return frame

    def render(self, console: Optional[Console] = None) -> Text:
        """渲染打字指示器"""
        text = Text()
        frame = self._get_current_frame()
        text.append(f"{frame} {self.message}...", style=self._get_style("accent"))
        return text

    def live(self, console: Optional[Console] = None, refresh_per_second: int = 10):
        """
        创建 Live 显示上下文

        Args:
            console: Rich Console 对象
            refresh_per_second: 刷新频率

        Example:
            >>> with indicator.live(console):
            ...     time.sleep(2)
        """
        if console is None:
            console = Console()
        return Live(
            get_renderable=self.render,
            console=console,
            refresh_per_second=refresh_per_second,
            transient=True,
        )


class ProgressBar(UIWidget):
    """
    进度条组件

    显示任务进度。

    Example:
        >>> progress = ProgressBar(total=100, description="加载中")
        >>> with progress.live(console) as p:
        ...     for i in range(100):
        ...         p.update(i)
    """

    def __init__(
        self,
        total: int = 100,
        description: str = "进度",
        show_time: bool = True,
        theme: Optional[Theme] = None,
    ):
        """
        初始化进度条

        Args:
            total: 总进度值
            description: 描述文本
            show_time: 是否显示时间
            theme: 主题对象
        """
        super().__init__(theme)
        self.total = total
        self.description = description
        self.show_time = show_time

    def create_progress(self) -> Progress:
        """创建 Rich Progress 对象"""
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style=self._theme.primary),
            "[progress.percentage]{task.percentage:>3.0f}%",
        ]

        if self.show_time:
            columns.append(TimeElapsedColumn())

        return Progress(*columns, console=Console(theme=self._theme.to_rich_theme()))

    def live(self, console: Optional[Console] = None):
        """
        创建进度条上下文

        Example:
            >>> with progress.live(console) as p:
            ...     p.update(task_id, advance=10)
        """
        return self.create_progress()


class Spinner(UIWidget):
    """
    旋转加载器组件

    显示加载动画。

    Example:
        >>> spinner = Spinner(message="加载中...")
        >>> with spinner.live(console):
        ...     # 执行加载任务
        ...     pass
    """

    SPINNER_TYPES = ["dots", "line", "simpleDots", "moon", "arc"]

    def __init__(
        self,
        message: str = "加载中...",
        spinner_type: str = "dots",
        theme: Optional[Theme] = None,
    ):
        """
        初始化旋转加载器

        Args:
            message: 提示消息
            spinner_type: 旋转器类型
            theme: 主题对象
        """
        super().__init__(theme)
        self.message = message
        self.spinner_type = spinner_type

    def render(self, console: Optional[Console] = None) -> RenderableType:
        """渲染旋转加载器"""
        from rich.spinner import Spinner as RichSpinner
        return RichSpinner(
            self.spinner_type,
            text=self.message,
            style=self._get_style("accent"),
        )

    def live(self, console: Optional[Console] = None, refresh_per_second: int = 10):
        """创建 Live 显示上下文"""
        if console is None:
            console = Console()
        return Live(
            self.render(console),
            console=console,
            refresh_per_second=refresh_per_second,
            transient=True,
        )


class Panel(UIWidget):
    """
    面板组件

    通用面板容器，用于组织内容。

    Example:
        >>> panel = Panel(title="场景选择", content="内容...")
        >>> panel.render(console)
    """

    def __init__(
        self,
        content: str,
        title: str = "",
        subtitle: str = "",
        border_style: str = "primary",
        theme: Optional[Theme] = None,
    ):
        """
        初始化面板

        Args:
            content: 面板内容
            title: 标题
            subtitle: 副标题
            border_style: 边框样式
            theme: 主题对象
        """
        super().__init__(theme)
        self.content = content
        self.title = title
        self.subtitle = subtitle
        self.border_style = border_style

    def render(self, console: Optional[Console] = None) -> RichPanel:
        """渲染面板"""
        return RichPanel(
            self.content,
            title=self.title,
            subtitle=self.subtitle,
            style=self._get_style("background"),
            border_style=self._get_style(self.border_style),
            padding=(1, 2),
        )


class Menu(UIWidget):
    """
    菜单组件

    显示可选择的菜单项列表。

    Example:
        >>> menu = Menu(title="主菜单", items=[("1", "开始"), ("2", "退出")])
        >>> menu.render(console)
    """

    def __init__(
        self,
        title: str = "菜单",
        items: Optional[List[tuple]] = None,
        selected_index: int = -1,
        theme: Optional[Theme] = None,
    ):
        """
        初始化菜单

        Args:
            title: 菜单标题
            items: 菜单项列表 [(key, label), ...]
            selected_index: 选中项索引
            theme: 主题对象
        """
        super().__init__(theme)
        self.title = title
        self.items = items or []
        self.selected_index = selected_index

    def render(self, console: Optional[Console] = None) -> RichPanel:
        """渲染菜单"""
        text = Text()

        for i, (key, label) in enumerate(self.items):
            if i == self.selected_index:
                text.append(f"  ▶ ", style=self._get_style("accent"))
                text.append(f"{key}. ", style=self._get_style("primary"))
                text.append(f"{label}\n", style=self._get_style("success"))
            else:
                text.append(f"    ", style="dim")
                text.append(f"{key}. ", style=self._get_style("secondary"))
                text.append(f"{label}\n", style=self._get_style("text"))

        return RichPanel(
            text,
            title=self.title,
            style=self._get_style("background"),
            border_style=self._get_style("border"),
            padding=(1, 2),
        )

    def add_item(self, key: str, label: str) -> None:
        """添加菜单项"""
        self.items.append((key, label))

    def get_item(self, key: str) -> Optional[str]:
        """根据键获取标签"""
        for k, label in self.items:
            if k == key:
                return label
        return None


class Divider(UIWidget):
    """分隔线组件"""

    def __init__(
        self,
        char: str = "─",
        width: int = 60,
        style: str = "border",
        theme: Optional[Theme] = None,
    ):
        super().__init__(theme)
        self.char = char
        self.width = width
        self.style = style

    def render(self, console: Optional[Console] = None) -> Text:
        text = Text()
        text.append(self.char * self.width, style=self._get_style(self.style))
        return text


class StatusBadge(UIWidget):
    """
    状态徽章组件

    显示状态指示器。
    """

    STATUS_COLORS = {
        "success": "success",
        "error": "error",
        "warning": "warning",
        "info": "info",
        "pending": "muted",
    }

    STATUS_ICONS = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ",
        "pending": "○",
    }

    def __init__(
        self,
        status: str = "info",
        message: str = "",
        theme: Optional[Theme] = None,
    ):
        super().__init__(theme)
        self.status = status
        self.message = message

    def render(self, console: Optional[Console] = None) -> Text:
        text = Text()
        icon = self.STATUS_ICONS.get(self.status, "•")
        color = self.STATUS_COLORS.get(self.status, "text")
        text.append(f"{icon} ", style=self._get_style(color))
        text.append(self.message, style=self._get_style(color))
        return text
