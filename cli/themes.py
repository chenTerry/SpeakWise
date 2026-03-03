"""
CLI Themes - CLI 主题模块

提供可配置的颜色主题系统，支持暗色和亮色主题。

核心类:
- Theme: 主题配置数据类
- ThemeManager: 主题管理器
- ThemeType: 主题类型枚举
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from rich.console import Console
from rich.style import Style
from rich.theme import Theme as RichTheme


class ThemeType(str, Enum):
    """主题类型枚举"""
    DARK = "dark"
    LIGHT = "light"
    BLUE = "blue"
    GREEN = "green"
    MONOKAI = "monokai"


@dataclass
class Theme:
    """
    主题配置

    定义 CLI 界面的颜色方案。

    Attributes:
        name: 主题名称
        theme_type: 主题类型
        primary: 主色调
        secondary: 次色调
        accent: 强调色
        success: 成功色
        warning: 警告色
        error: 错误色
        info: 信息色
        background: 背景色
        text: 文本色
        muted: 淡化文本色
        border: 边框色
        user_message: 用户消息气泡颜色
        agent_message: Agent 消息气泡颜色
        system_message: 系统消息颜色
    """
    name: str
    theme_type: ThemeType
    primary: str = "blue"
    secondary: str = "cyan"
    accent: str = "magenta"
    success: str = "green"
    warning: str = "yellow"
    error: str = "red"
    info: str = "blue"
    background: str = "default"
    text: str = "white"
    muted: str = "dim white"
    border: str = "blue"
    user_message: str = "on blue"
    agent_message: str = "on green"
    system_message: str = "on yellow"

    def to_rich_theme(self) -> RichTheme:
        """
        转换为 Rich Theme 对象

        Returns:
            Rich Theme 对象
        """
        return RichTheme({
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "info": self.info,
            "text": self.text,
            "muted": self.muted,
            "border": self.border,
        })

    def get_style(self, name: str) -> Style:
        """
        获取指定样式的 Style 对象

        Args:
            name: 样式名称

        Returns:
            Rich Style 对象
        """
        color = getattr(self, name, self.text)
        return Style(color=color)


class ThemeManager:
    """
    主题管理器

    管理主题的注册、切换和应用。

    Example:
        >>> manager = ThemeManager()
        >>> manager.set_theme("dark")
        >>> theme = manager.current_theme
        >>> console = manager.create_console()
    """

    # 预定义主题
    PRESET_THEMES: Dict[str, Theme] = {
        "dark": Theme(
            name="Dark",
            theme_type=ThemeType.DARK,
            primary="bright_blue",
            secondary="bright_cyan",
            accent="bright_magenta",
            success="bright_green",
            warning="bright_yellow",
            error="bright_red",
            info="blue",
            background="black",
            text="white",
            muted="dim white",
            border="bright_blue",
            user_message="on blue",
            agent_message="on green",
            system_message="on yellow",
        ),
        "light": Theme(
            name="Light",
            theme_type=ThemeType.LIGHT,
            primary="blue",
            secondary="cyan",
            accent="magenta",
            success="green",
            warning="yellow",
            error="red",
            info="blue",
            background="white",
            text="black",
            muted="dim black",
            border="blue",
            user_message="on bright_blue white",
            agent_message="on bright_green white",
            system_message="on bright_yellow white",
        ),
        "blue": Theme(
            name="Blue Ocean",
            theme_type=ThemeType.BLUE,
            primary="bright_cyan",
            secondary="cyan",
            accent="bright_blue",
            success="green",
            warning="yellow",
            error="red",
            info="cyan",
            background="default",
            text="white",
            muted="dim cyan",
            border="bright_cyan",
            user_message="on blue",
            agent_message="on dark_blue",
            system_message="on cyan",
        ),
        "green": Theme(
            name="Green Terminal",
            theme_type=ThemeType.GREEN,
            primary="bright_green",
            secondary="green",
            accent="yellow",
            success="bright_green",
            warning="yellow",
            error="red",
            info="green",
            background="black",
            text="bright_green",
            muted="dim green",
            border="bright_green",
            user_message="on green",
            agent_message="on dark_green",
            system_message="on yellow",
        ),
        "monokai": Theme(
            name="Monokai",
            theme_type=ThemeType.MONOKAI,
            primary="#F92672",  # Pink
            secondary="#66D9EF",  # Light Blue
            accent="#A6E22E",  # Green
            success="#A6E22E",
            warning="#E6DB74",  # Yellow
            error="#F92672",
            info="#66D9EF",
            background="#272822",  # Dark Grey
            text="#F8F8F2",  # Off White
            muted="#75715E",
            border="#F92672",
            user_message="on #66D9EF",
            agent_message="on #A6E22E",
            system_message="on #E6DB74",
        ),
    }

    def __init__(self, default_theme: str = "dark"):
        """
        初始化主题管理器

        Args:
            default_theme: 默认主题名称
        """
        self._themes: Dict[str, Theme] = self.PRESET_THEMES.copy()
        self._current_theme_name: str = default_theme
        self._console: Optional[Console] = None

        if default_theme not in self._themes:
            raise ValueError(f"Unknown theme: {default_theme}")

    @property
    def current_theme(self) -> Theme:
        """获取当前主题"""
        return self._themes[self._current_theme_name]

    @property
    def current_theme_name(self) -> str:
        """获取当前主题名称"""
        return self._current_theme_name

    @property
    def available_themes(self) -> list:
        """获取可用主题列表"""
        return list(self._themes.keys())

    def set_theme(self, theme_name: str) -> bool:
        """
        设置当前主题

        Args:
            theme_name: 主题名称

        Returns:
            是否设置成功
        """
        if theme_name in self._themes:
            self._current_theme_name = theme_name
            self._console = None  # 重置 console 以应用新主题
            return True
        return False

    def register_theme(self, name: str, theme: Theme) -> None:
        """
        注册自定义主题

        Args:
            name: 主题名称
            theme: 主题对象
        """
        self._themes[name] = theme

    def get_theme(self, name: str) -> Optional[Theme]:
        """
        获取指定主题

        Args:
            name: 主题名称

        Returns:
            主题对象或 None
        """
        return self._themes.get(name)

    def create_console(self, **kwargs) -> Console:
        """
        创建应用当前主题的 Console 对象

        Args:
            **kwargs: 传递给 Console 构造函数的参数

        Returns:
            Rich Console 对象
        """
        if self._console is None:
            theme = self.current_theme
            self._console = Console(
                theme=theme.to_rich_theme(),
                **kwargs
            )
        return self._console

    def get_style(self, style_name: str) -> Style:
        """
        获取当前主题的样式

        Args:
            style_name: 样式名称

        Returns:
            Rich Style 对象
        """
        return self.current_theme.get_style(style_name)

    def cycle_theme(self) -> str:
        """
        循环切换到下一个主题

        Returns:
            新主题名称
        """
        themes = list(self._themes.keys())
        current_index = themes.index(self._current_theme_name)
        next_index = (current_index + 1) % len(themes)
        self._current_theme_name = themes[next_index]
        self._console = None
        return self._current_theme_name


# 全局主题管理器实例
_global_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """获取全局主题管理器"""
    global _global_theme_manager
    if _global_theme_manager is None:
        _global_theme_manager = ThemeManager()
    return _global_theme_manager


def set_global_theme(theme_name: str) -> bool:
    """设置全局主题"""
    return get_theme_manager().set_theme(theme_name)


def get_current_theme() -> Theme:
    """获取当前主题"""
    return get_theme_manager().current_theme


def create_console(**kwargs) -> Console:
    """创建应用当前主题的 Console"""
    return get_theme_manager().create_console(**kwargs)
