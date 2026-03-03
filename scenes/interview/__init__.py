"""
Interview Scene Module - 面试场景模块

提供完整的面试场景实现，包括：
- InterviewScene: 面试场景主类
- InterviewerAgent: 增强的面试官 Agent
- 问题库加载和管理

使用示例:
    >>> from scenes.interview import InterviewScene, InterviewerAgent
    >>> scene = InterviewScene()
    >>> scene.initialize()
    >>> message = scene.start()
"""

from .scene import InterviewScene, InterviewPhase, InterviewStyle
from .interviewer import EnhancedInterviewerAgent, QuestionBank, DomainType

__all__ = [
    # Scene
    "InterviewScene",
    "InterviewPhase",
    "InterviewStyle",
    # Interviewer
    "EnhancedInterviewerAgent",
    "QuestionBank",
    "DomainType",
]
