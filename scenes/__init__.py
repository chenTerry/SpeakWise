"""
Scenes Module - 场景模块

场景系统提供可插拔的对话场景管理，支持多种面试场景的切换和扩展。

核心组件:
- BaseScene: 场景抽象基类
- SceneRegistry: 场景注册和发现中心
- InterviewScene: 面试场景实现

使用示例:
    >>> from scenes import SceneRegistry, InterviewScene
    >>> registry = SceneRegistry.get_instance()
    >>> registry.register("interview", InterviewScene)
    >>> scene = registry.get_scene("interview")
"""

from .base import BaseScene, SceneConfig, SceneState
from .registry import SceneRegistry, SceneRegistryError

__all__ = [
    # Base Scene
    "BaseScene",
    "SceneConfig",
    "SceneState",
    # Registry
    "SceneRegistry",
    "SceneRegistryError",
]
