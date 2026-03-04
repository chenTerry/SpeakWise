"""
AgentScope AI Interview - History Module

历史回放模块提供：
- SessionReplay: 会话回放功能
- 步骤导航
- 注释和笔记

版本：v0.6.0
"""

from .replay import SessionReplay, ReplayStep, ReplayNote

__version__ = "0.6.0"

__all__ = [
    "SessionReplay",
    "ReplayStep",
    "ReplayNote",
]
