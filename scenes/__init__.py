"""
Scenes Module - 场景模块 (v0.5)

场景系统提供可插拔的对话场景管理，支持多种场景的切换和扩展。

v0.2 (基础场景):
- BaseScene: 场景抽象基类
- SceneRegistry: 场景注册和发现中心
- InterviewScene: 面试场景实现

v0.5 (多场景支持):
- SalonScene: 沙龙场景（多角色对话）
- MeetingScene: 会议场景（多种会议类型）
- SceneManager: 场景管理器（场景切换和状态管理）

核心组件:
- BaseScene: 场景抽象基类
- SceneRegistry: 场景注册和发现中心
- SceneManager: 场景生命周期管理
- InterviewScene: 面试场景
- SalonScene: 沙龙场景
- MeetingScene: 会议场景

使用示例:
    >>> from scenes import SceneRegistry, SceneManager
    >>> from scenes import InterviewScene, SalonScene, MeetingScene
    >>>
    >>> # 使用注册中心
    >>> registry = SceneRegistry.get_instance()
    >>> registry.register("interview", InterviewScene)
    >>> scene = registry.get_scene("interview")
    >>>
    >>> # 使用场景管理器（支持切换）
    >>> manager = SceneManager()
    >>> manager.create_scene("interview")
    >>> manager.switch_scene("salon")
"""

from .base import BaseScene, SceneConfig, SceneState
from .registry import SceneRegistry, SceneRegistryError
from .manager import SceneManager, SceneManagerError, SceneTransition

__all__ = [
    # Base Scene
    "BaseScene",
    "SceneConfig",
    "SceneState",
    # Registry
    "SceneRegistry",
    "SceneRegistryError",
    # Manager (v0.5)
    "SceneManager",
    "SceneManagerError",
    "SceneTransition",
]
