"""
CLI Module - 命令行界面模块 (v0.4)

提供基于 Rich 库的增强命令行界面，包括：
- 彩色终端 UI
- 交互式菜单系统
- 进度指示器和旋转器
- 实时打字效果

版本：v0.4.0
"""

from .app import CLIApplication
from .menus import MenuManager, SceneMenu, DialogueMenu, FeedbackMenu
from .themes import Theme, ThemeManager, ThemeType
from .widgets import (
    UIWidget,
    Header,
    Footer,
    MessageBubble,
    TypingIndicator,
    ProgressBar,
    Spinner,
    Panel,
)

__version__ = "0.4.0"

__all__ = [
    # Version
    "__version__",
    # Application
    "CLIApplication",
    # Menus
    "MenuManager",
    "SceneMenu",
    "DialogueMenu",
    "FeedbackMenu",
    # Themes
    "Theme",
    "ThemeManager",
    "ThemeType",
    # Widgets
    "UIWidget",
    "Header",
    "Footer",
    "MessageBubble",
    "TypingIndicator",
    "ProgressBar",
    "Spinner",
    "Panel",
]
