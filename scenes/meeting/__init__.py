"""
Meeting Scene Module - 会议场景模块 (v0.5)

提供完整的会议场景模拟，支持多种会议子场景：
- Requirement Review (需求评审)
- Standup Meeting (站会/进度同步)
- Conflict Resolution (冲突解决)
- Project Kickoff (项目启动)
- Retrospective (复盘会议)

核心组件:
- MeetingScene: 会议场景主类
- MeetingSceneConfig: 会议场景配置
- MeetingPhase: 会议阶段枚举
- MeetingType: 会议类型枚举
- MeetingManager: 会议管理器 (非 Agent)

会议流程:
1. Opening: 会议开场，明确议程
2. RoundTable: 轮流发言
3. Discussion: 自由讨论
4. Summary: 总结要点
5. ActionItems: 确定行动项
6. Closing: 会议结束

使用示例:
    >>> from scenes.meeting import MeetingScene, MeetingType
    >>>
    >>> # 创建站会场景
    >>> scene = MeetingScene(meeting_type=MeetingType.STANDUP)
    >>> scene.initialize()
    >>> opening = scene.start()
"""

from .scene import (
    MeetingScene,
    MeetingSceneConfig,
    MeetingPhase,
    MeetingType,
)
from .manager import MeetingManagerAgent
from .participant import MeetingParticipantAgent

__all__ = [
    # Scene
    "MeetingScene",
    "MeetingSceneConfig",
    "MeetingPhase",
    "MeetingType",
    # Manager
    "MeetingManagerAgent",
    # Participants
    "MeetingParticipantAgent",
]

__version__ = "0.5.0"
__author__ = "AgentScope AI Interview Team"
