"""
Scene Registry Module - 场景注册中心模块

提供场景的注册、发现和生命周期管理功能。
采用单例模式确保全局唯一的注册中心。

设计模式:
- Singleton: 确保全局唯一注册中心
- Factory: 通过注册信息创建场景实例
- Observer: 支持场景事件监听（扩展点）
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type

from core.config import Config
from .base import BaseScene, SceneConfig, SceneError

logger = logging.getLogger(__name__)


class SceneRegistryError(Exception):
    """
    场景注册中心异常

    用于处理注册、查找和创建场景时的错误
    """
    pass


class SceneRegistry:
    """
    场景注册中心

    全局唯一的场景管理中枢，负责：
    - 场景类型的注册和注销
    - 场景实例的创建和获取
    - 场景元数据的管理

    使用示例:
        >>> registry = SceneRegistry.get_instance()
        >>> registry.register("interview", InterviewScene)
        >>> scene = registry.create_scene("interview", config)
    """

    _instance: Optional["SceneRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "SceneRegistry":
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化注册中心"""
        if SceneRegistry._initialized:
            return

        self._scenes: Dict[str, Type[BaseScene]] = {}
        self._scene_configs: Dict[str, Dict[str, Any]] = {}
        self._factories: Dict[str, Callable[[], BaseScene]] = {}
        self._aliases: Dict[str, str] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "before_create": [],
            "after_create": [],
            "before_initialize": [],
            "after_initialize": [],
        }
        SceneRegistry._initialized = True

    @classmethod
    def get_instance(cls) -> "SceneRegistry":
        """
        获取注册中心单例实例

        Returns:
            SceneRegistry 单例实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """
        重置注册中心（主要用于测试）

        清除所有注册信息并允许重新初始化
        """
        if cls._instance is not None:
            cls._instance._scenes.clear()
            cls._instance._scene_configs.clear()
            cls._instance._factories.clear()
            cls._instance._aliases.clear()
            cls._instance._hooks = {
                "before_create": [],
                "after_create": [],
                "before_initialize": [],
                "after_initialize": [],
            }
            cls._initialized = False
            cls._instance = None

    def register(
        self,
        scene_type: str,
        scene_class: Type[BaseScene],
        config: Optional[Dict[str, Any]] = None,
        aliases: Optional[List[str]] = None,
    ) -> None:
        """
        注册场景类型

        Args:
            scene_type: 场景类型标识符
            scene_class: 场景类
            config: 场景默认配置
            aliases: 场景别名列表

        Raises:
            SceneRegistryError: 注册失败时抛出

        Example:
            >>> registry.register("interview", InterviewScene, {
            ...     "name": "技术面试"
            ... })
        """
        if not scene_type:
            raise SceneRegistryError("场景类型不能为空")

        if not issubclass(scene_class, BaseScene):
            raise SceneRegistryError(
                f"场景类必须是 BaseScene 的子类：{scene_class}"
            )

        if scene_type in self._scenes:
            logger.warning(f"场景类型 '{scene_type}' 已注册，将被覆盖")

        # 注册场景类
        self._scenes[scene_type] = scene_class

        # 保存默认配置
        if config:
            self._scene_configs[scene_type] = config

        # 注册别名
        if aliases:
            for alias in aliases:
                self._aliases[alias] = scene_type

        logger.info(f"场景 '{scene_type}' 注册成功")

    def register_factory(
        self,
        scene_type: str,
        factory: Callable[[], BaseScene],
        aliases: Optional[List[str]] = None,
    ) -> None:
        """
        注册场景工厂函数

        用于需要特殊构造逻辑的场景

        Args:
            scene_type: 场景类型标识符
            factory: 工厂函数
            aliases: 场景别名列表
        """
        if not scene_type:
            raise SceneRegistryError("场景类型不能为空")

        self._factories[scene_type] = factory

        if aliases:
            for alias in aliases:
                self._aliases[alias] = scene_type

        logger.info(f"场景工厂 '{scene_type}' 注册成功")

    def unregister(self, scene_type: str) -> bool:
        """
        注销场景类型

        Args:
            scene_type: 场景类型标识符

        Returns:
            是否成功注销
        """
        if scene_type not in self._scenes:
            return False

        del self._scenes[scene_type]
        self._scene_configs.pop(scene_type, None)
        self._factories.pop(scene_type, None)

        # 清理别名
        aliases_to_remove = [
            alias for alias, target in self._aliases.items()
            if target == scene_type
        ]
        for alias in aliases_to_remove:
            del self._aliases[alias]

        logger.info(f"场景 '{scene_type}' 注销成功")
        return True

    def get_scene_class(self, scene_type: str) -> Type[BaseScene]:
        """
        获取场景类

        Args:
            scene_type: 场景类型标识符或别名

        Returns:
            场景类

        Raises:
            SceneRegistryError: 场景未找到时抛出
        """
        # 解析别名
        actual_type = self._resolve_alias(scene_type)

        if actual_type in self._scenes:
            return self._scenes[actual_type]

        raise SceneRegistryError(f"未找到场景类型：{scene_type}")

    def create_scene(
        self,
        scene_type: str,
        config: Optional[SceneConfig] = None,
        global_config: Optional[Config] = None,
        **kwargs: Any,
    ) -> BaseScene:
        """
        创建场景实例

        Args:
            scene_type: 场景类型标识符
            config: 场景配置
            global_config: 全局配置
            **kwargs: 额外参数

        Returns:
            场景实例

        Raises:
            SceneRegistryError: 创建失败时抛出
        """
        # 触发 before_create 钩子
        self._trigger_hooks("before_create", scene_type)

        try:
            # 解析别名
            actual_type = self._resolve_alias(scene_type)

            # 检查是否有工厂函数
            if actual_type in self._factories:
                scene = self._factories[actual_type]()
            elif actual_type in self._scenes:
                # 使用默认配置合并
                scene_config = self._merge_config(
                    actual_type,
                    config,
                )
                scene_class = self._scenes[actual_type]
                # Filter out scene_key as it's used by SceneManager, not the scene class
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'scene_key'}
                scene = scene_class(
                    config=scene_config,
                    global_config=global_config,
                    **filtered_kwargs,
                )
            else:
                raise SceneRegistryError(f"未找到场景类型：{scene_type}")

            # 触发 after_create 钩子
            self._trigger_hooks("after_create", scene_type, scene)

            return scene

        except Exception as e:
            logger.error(f"创建场景失败：{e}")
            raise SceneRegistryError(f"创建场景失败：{e}")

    def get_scene(
        self,
        scene_type: str,
        config: Optional[SceneConfig] = None,
        global_config: Optional[Config] = None,
        initialize: bool = True,
        **kwargs: Any,
    ) -> BaseScene:
        """
        获取并初始化场景

        Args:
            scene_type: 场景类型标识符
            config: 场景配置
            global_config: 全局配置
            initialize: 是否自动初始化
            **kwargs: 额外参数

        Returns:
            已初始化的场景实例

        Raises:
            SceneRegistryError: 获取或初始化失败时抛出
        """
        scene = self.create_scene(
            scene_type,
            config,
            global_config,
            **kwargs,
        )

        if initialize:
            # 触发 before_initialize 钩子
            self._trigger_hooks("before_initialize", scene_type, scene)

            success = scene.initialize()

            # 触发 after_initialize 钩子
            self._trigger_hooks("after_initialize", scene_type, scene)

            if not success:
                raise SceneRegistryError(f"场景初始化失败：{scene_type}")

        return scene

    def list_scenes(self) -> List[Dict[str, Any]]:
        """
        列出所有已注册的场景

        Returns:
            场景信息列表
        """
        result = []

        for scene_type, scene_class in self._scenes.items():
            info = {
                "type": scene_type,
                "class": scene_class.__name__,
                "module": scene_class.__module__,
                "config": self._scene_configs.get(scene_type, {}),
            }

            # 添加别名信息
            aliases = [
                alias for alias, target in self._aliases.items()
                if target == scene_type
            ]
            if aliases:
                info["aliases"] = aliases

            result.append(info)

        return result

    def has_scene(self, scene_type: str) -> bool:
        """
        检查场景是否已注册

        Args:
            scene_type: 场景类型标识符或别名

        Returns:
            是否已注册
        """
        actual_type = self._resolve_alias(scene_type)
        return actual_type in self._scenes or actual_type in self._factories

    def get_config(self, scene_type: str) -> Dict[str, Any]:
        """
        获取场景默认配置

        Args:
            scene_type: 场景类型标识符

        Returns:
            配置字典
        """
        actual_type = self._resolve_alias(scene_type)
        return self._scene_configs.get(actual_type, {}).copy()

    def register_hook(
        self,
        event: str,
        callback: Callable,
    ) -> None:
        """
        注册场景事件钩子

        支持的事件:
        - before_create: 创建场景前
        - after_create: 创建场景后
        - before_initialize: 初始化前
        - after_initialize: 初始化后

        Args:
            event: 事件名称
            callback: 回调函数
        """
        if event not in self._hooks:
            raise SceneRegistryError(f"未知事件：{event}")

        self._hooks[event].append(callback)
        logger.debug(f"钩子注册：{event}")

    def _resolve_alias(self, scene_type: str) -> str:
        """解析别名到实际场景类型"""
        return self._aliases.get(scene_type, scene_type)

    def _merge_config(
        self,
        scene_type: str,
        config: Optional[SceneConfig],
    ) -> SceneConfig:
        """合并默认配置和用户配置"""
        default_config = self._scene_configs.get(scene_type, {})

        if config is None:
            return SceneConfig.from_dict({
                "scene_type": scene_type,
                **default_config,
            })

        # 合并配置
        merged = {
            "scene_type": scene_type,
            **default_config,
            **config.to_dict(),
        }

        return SceneConfig.from_dict(merged)

    def _trigger_hooks(
        self,
        event: str,
        *args: Any,
    ) -> None:
        """触发事件钩子"""
        for callback in self._hooks.get(event, []):
            try:
                callback(*args)
            except Exception as e:
                logger.error(f"钩子执行失败 ({event}): {e}")

    def __len__(self) -> int:
        """获取注册场景数量"""
        return len(self._scenes)

    def __contains__(self, scene_type: str) -> bool:
        """检查场景是否已注册"""
        return self.has_scene(scene_type)

    def __repr__(self) -> str:
        return f"SceneRegistry(scenes={list(self._scenes.keys())})"


# 便捷函数
def get_registry() -> SceneRegistry:
    """获取全局注册中心实例"""
    return SceneRegistry.get_instance()


def register_scene(
    scene_type: str,
    scene_class: Type[BaseScene],
    config: Optional[Dict[str, Any]] = None,
) -> None:
    """便捷函数：注册场景"""
    get_registry().register(scene_type, scene_class, config)


def create_scene(
    scene_type: str,
    config: Optional[SceneConfig] = None,
    **kwargs: Any,
) -> BaseScene:
    """便捷函数：创建场景"""
    return get_registry().create_scene(scene_type, config, **kwargs)
