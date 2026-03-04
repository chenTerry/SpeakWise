"""
Salon Scene Module - 沙龙场景模块 (v0.5)

提供完整的沙龙活动模拟，支持多角色 AI Agent 协同对话。

核心组件:
- SalonScene: 沙龙场景主类
- SalonSceneConfig: 沙龙场景配置
- SalonPhase: 沙龙阶段枚举
- RoleConfig/RoleManager: 角色配置和管理
- SalonHostAgent: 主持人 Agent
- SalonSpeakerAgent: 演讲者 Agent
- SalonAudienceAgent: 观众 Agent
- SalonObserverAgent: 观察者 Agent

沙龙流程:
1. Opening: 主持人开场，介绍主题和嘉宾
2. Presentation: 演讲者主题分享
3. Q&A: 观众提问互动
4. Discussion: 自由讨论
5. Summary: 观察者总结
6. Closing: 主持人闭幕

使用示例:
    >>> from scenes.salon import SalonScene, SalonSceneConfig
    >>>
    >>> # 创建沙龙场景
    >>> config = SalonSceneConfig(
    ...     topic="AI 技术应用",
    ...     speaker_topic="大模型在开发中的实践",
    ...     discussion_style="casual",
    ... )
    >>> scene = SalonScene(config=config)
    >>>
    >>> # 初始化并启动
    >>> scene.initialize()
    >>> opening = scene.start()
    >>> print(opening.content)
"""

from .scene import SalonScene, SalonSceneConfig, SalonPhase
from .roles import (
    SalonRoleType,
    RoleConfig,
    RoleState,
    RoleManager,
)
from .host import SalonHostAgent
from .speaker import SalonSpeakerAgent
from .audience import SalonAudienceAgent
from .observer import SalonObserverAgent

__all__ = [
    # Scene
    "SalonScene",
    "SalonSceneConfig",
    "SalonPhase",
    # Roles
    "SalonRoleType",
    "RoleConfig",
    "RoleState",
    "RoleManager",
    # Agents
    "SalonHostAgent",
    "SalonSpeakerAgent",
    "SalonAudienceAgent",
    "SalonObserverAgent",
]

__version__ = "0.5.0"
__author__ = "AgentScope AI Interview Team"
