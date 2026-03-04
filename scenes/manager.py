"""
Scene Manager Module - 场景管理器模块 (v0.5)

提供场景生命周期管理和场景切换功能，包括：
- 场景注册和发现
- 场景实例管理
- 场景切换和状态迁移
- 上下文保持和恢复
- 场景状态序列化/反序列化

核心功能:
1. 支持多个场景同时存在（但只有一个活跃）
2. 场景切换时保持对话上下文连续性
3. 场景状态可序列化，支持断点续玩
4. 提供场景切换的平滑过渡

使用示例:
    >>> from scenes.manager import SceneManager
    >>>
    >>> # 创建场景管理器
    >>> manager = SceneManager()
    >>>
    >>> # 创建并激活场景
    >>> manager.create_scene("interview", style="friendly")
    >>> manager.activate_scene("interview")
    >>>
    >>> # 切换到沙龙场景
    >>> manager.create_scene("salon", topic="AI 技术")
    >>> transition = manager.switch_scene("salon")
    >>> print(transition.message)
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from core.config import Config
from core.agent import Message, DialogueContext, MessageType
from scenes.base import BaseScene, SceneConfig, SceneState
from scenes.registry import SceneRegistry, SceneRegistryError

logger = logging.getLogger(__name__)


class SceneManagerError(Exception):
    """
    场景管理器异常

    用于处理场景管理过程中的各种错误
    """
    pass


@dataclass
class SceneTransition:
    """
    场景转换结果数据类

    封装场景切换的结果信息

    Attributes:
        success: 是否成功切换
        message: 转换消息
        from_scene: 源场景类型
        to_scene: 目标场景类型
        context_preserved: 上下文是否保留
        timestamp: 转换时间戳
    """
    success: bool
    message: str = ""
    from_scene: Optional[str] = None
    to_scene: Optional[str] = None
    context_preserved: bool = True
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "message": self.message,
            "from_scene": self.from_scene,
            "to_scene": self.to_scene,
            "context_preserved": self.context_preserved,
            "timestamp": self.timestamp,
        }


@dataclass
class SceneStateSnapshot:
    """
    场景状态快照

    用于保存场景的序列化状态

    Attributes:
        scene_type: 场景类型
        scene_id: 场景 ID
        config: 场景配置
        context: 对话上下文
        metadata: 场景元数据
        created_at: 创建时间
        saved_at: 保存时间
    """
    scene_type: str
    scene_id: str
    config: Dict[str, Any]
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: float
    saved_at: float = field(default_factory=time.time)

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps({
            "scene_type": self.scene_type,
            "scene_id": self.scene_id,
            "config": self.config,
            "context": self.context,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "saved_at": self.saved_at,
        }, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "SceneStateSnapshot":
        """从 JSON 字符串创建"""
        data = json.loads(json_str)
        return cls(
            scene_type=data["scene_type"],
            scene_id=data["scene_id"],
            config=data["config"],
            context=data["context"],
            metadata=data["metadata"],
            created_at=data["created_at"],
            saved_at=data.get("saved_at", time.time()),
        )


class SceneManager:
    """
    场景管理器

    负责场景的生命周期管理和切换：
    - 创建和销毁场景
    - 激活和停用场景
    - 场景切换和状态迁移
    - 上下文保持和恢复
    - 场景状态持久化

    使用示例:
        >>> manager = SceneManager()
        >>> manager.create_scene("interview")
        >>> manager.activate_scene("interview")
        >>> result = manager.handle_message(message, context)
    """

    def __init__(self, global_config: Optional[Config] = None):
        """
        初始化场景管理器

        Args:
            global_config: 全局配置对象
        """
        self.global_config = global_config or Config()
        self._registry = SceneRegistry.get_instance()

        # 场景实例池
        self._scenes: Dict[str, BaseScene] = {}

        # 当前活跃场景
        self._active_scene_key: Optional[str] = None

        # 场景状态快照（用于恢复）
        self._snapshots: Dict[str, SceneStateSnapshot] = {}

        # 对话上下文（跨场景共享）
        self._global_context = DialogueContext()

        # 场景历史（用于返回）
        self._scene_history: List[str] = []

        # 转换历史
        self._transition_history: List[SceneTransition] = []

    def create_scene(
        self,
        scene_type: str,
        config: Optional[SceneConfig] = None,
        scene_key: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        创建场景实例

        Args:
            scene_type: 场景类型
            config: 场景配置
            scene_key: 场景键（用于标识，默认使用 scene_type）
            **kwargs: 传递给场景构造函数的参数

        Returns:
            场景键

        Raises:
            SceneManagerError: 创建失败时抛出
        """
        try:
            # 生成场景键
            if scene_key is None:
                scene_key = scene_type

            # 如果场景已存在，先清理
            if scene_key in self._scenes:
                self.destroy_scene(scene_key)

            # 创建场景实例
            scene = self._registry.get_scene(
                scene_type,
                config=config,
                global_config=self.global_config,
                initialize=True,
                **kwargs,
            )

            # 存储场景
            self._scenes[scene_key] = scene

            logger.info(f"场景创建成功：{scene_key} (type={scene_type})")

            return scene_key

        except Exception as e:
            logger.error(f"创建场景失败：{e}")
            raise SceneManagerError(f"创建场景失败：{e}")

    def destroy_scene(self, scene_key: str) -> bool:
        """
        销毁场景实例

        Args:
            scene_key: 场景键

        Returns:
            是否成功销毁
        """
        if scene_key not in self._scenes:
            return False

        # 如果是活跃场景，先停用
        if self._active_scene_key == scene_key:
            self._active_scene_key = None

        # 清理场景
        scene = self._scenes[scene_key]
        scene.cleanup()

        # 删除引用
        del self._scenes[scene_key]

        logger.info(f"场景销毁成功：{scene_key}")
        return True

    def activate_scene(self, scene_key: str) -> bool:
        """
        激活场景

        Args:
            scene_key: 场景键

        Returns:
            是否成功激活
        """
        if scene_key not in self._scenes:
            logger.error(f"场景不存在：{scene_key}")
            return False

        scene = self._scenes[scene_key]

        # 检查场景状态
        if scene.state not in [SceneState.CREATED, SceneState.INITIALIZED, SceneState.PAUSED]:
            logger.error(f"场景状态不允许激活：{scene.state}")
            return False

        # 停用当前活跃场景
        if self._active_scene_key and self._active_scene_key != scene_key:
            self._scenes[self._active_scene_key].pause()

        # 激活新场景
        self._active_scene_key = scene_key
        scene.resume()

        # 添加到历史
        if scene_key not in self._scene_history or self._scene_history[-1] != scene_key:
            self._scene_history.append(scene_key)

        logger.info(f"场景激活成功：{scene_key}")
        return True

    def switch_scene(
        self,
        target_scene_key: str,
        preserve_context: bool = True,
    ) -> SceneTransition:
        """
        切换到目标场景

        Args:
            target_scene_key: 目标场景键
            preserve_context: 是否保留上下文

        Returns:
            场景转换结果
        """
        # 获取当前场景
        current_key = self._active_scene_key
        current_scene = self._scenes.get(current_key) if current_key else None

        # 检查目标场景是否存在
        if target_scene_key not in self._scenes:
            return SceneTransition(
                success=False,
                message=f"目标场景不存在：{target_scene_key}",
                from_scene=current_key,
                to_scene=target_scene_key,
            )

        # 如果已经是目标场景，无需切换
        if current_key == target_scene_key:
            return SceneTransition(
                success=True,
                message="已在目标场景中",
                from_scene=current_key,
                to_scene=target_scene_key,
            )

        # 保存当前场景状态
        if current_key and preserve_context:
            self._save_scene_snapshot(current_key)

        # 激活目标场景
        success = self.activate_scene(target_scene_key)

        if not success:
            return SceneTransition(
                success=False,
                message=f"激活场景失败：{target_scene_key}",
                from_scene=current_key,
                to_scene=target_scene_key,
                context_preserved=preserve_context,
            )

        # 恢复目标场景上下文
        if preserve_context:
            self._restore_scene_context(target_scene_key)

        # 创建转换结果
        transition = SceneTransition(
            success=True,
            message=f"成功切换到{target_scene_key}场景",
            from_scene=current_key,
            to_scene=target_scene_key,
            context_preserved=preserve_context,
        )

        # 记录转换历史
        self._transition_history.append(transition)

        logger.info(
            f"场景切换成功：{current_key} -> {target_scene_key}"
        )

        return transition

    def get_active_scene(self) -> Optional[BaseScene]:
        """
        获取当前活跃场景

        Returns:
            活跃场景实例或 None
        """
        if self._active_scene_key is None:
            return None
        return self._scenes.get(self._active_scene_key)

    def get_scene(self, scene_key: str) -> Optional[BaseScene]:
        """
        获取场景实例

        Args:
            scene_key: 场景键

        Returns:
            场景实例或 None
        """
        return self._scenes.get(scene_key)

    def list_scenes(self) -> List[Dict[str, Any]]:
        """
        列出所有已创建的场景

        Returns:
            场景信息列表
        """
        result = []

        for key, scene in self._scenes.items():
            info = {
                "key": key,
                "type": scene.get_scene_type(),
                "state": scene.get_state().value,
                "active": key == self._active_scene_key,
                "description": scene.get_description(),
            }
            result.append(info)

        return result

    def handle_message(
        self,
        message: Message,
        context: Optional[DialogueContext] = None,
    ) -> Tuple[Message, Optional[SceneTransition]]:
        """
        处理用户消息

        如果消息包含场景切换指令，会自动切换场景

        Args:
            message: 用户消息
            context: 对话上下文

        Returns:
            (响应消息，场景转换结果)
        """
        transition = None

        # 检查是否有场景切换指令
        switch_result = self._check_switch_command(message)
        if switch_result:
            target_key, preserve = switch_result
            transition = self.switch_scene(target_key, preserve)

            if transition.success:
                # 返回切换成功的消息
                switch_message = Message(
                    content=f"🔄 {transition.message}",
                    role="system",
                    type=MessageType.SYSTEM,
                    metadata=transition.to_dict(),
                )
                return switch_message, transition

        # 获取活跃场景
        scene = self.get_active_scene()
        if not scene:
            return Message(
                content="❌ 没有活跃的场景，请先创建或激活场景",
                role="system",
                type=MessageType.SYSTEM,
            ), None

        # 使用全局上下文（如果未提供）
        if context is None:
            context = self._global_context

        # 处理消息
        try:
            response = scene.handle_message(message, context)
            return response, transition
        except Exception as e:
            logger.error(f"处理消息失败：{e}")
            return Message(
                content=f"❌ 处理消息失败：{e}",
                role="system",
                type=MessageType.SYSTEM,
            ), None

    def _check_switch_command(
        self,
        message: Message,
    ) -> Optional[Tuple[str, bool]]:
        """
        检查消息是否包含场景切换指令

        支持的指令格式:
        - /switch salon
        - /switch meeting preserve
        - /scene interview

        Args:
            message: 用户消息

        Returns:
            (目标场景键，是否保留上下文) 或 None
        """
        content = message.content.strip()

        # 检查切换指令
        prefixes = ["/switch ", "/scene ", "切换到", "进入"]

        for prefix in prefixes:
            if content.startswith(prefix):
                parts = content[len(prefix):].split()
                if not parts:
                    return None

                target_key = parts[0]
                preserve_context = True

                # 检查是否指定不保留上下文
                if len(parts) > 1:
                    if parts[1].lower() in ["nopreserve", "no_context", "不保留"]:
                        preserve_context = False

                return (target_key, preserve_context)

        return None

    def _save_scene_snapshot(self, scene_key: str) -> None:
        """
        保存场景状态快照

        Args:
            scene_key: 场景键
        """
        scene = self._scenes.get(scene_key)
        if not scene:
            return

        try:
            # 创建快照
            snapshot = SceneStateSnapshot(
                scene_type=scene.get_scene_type(),
                scene_id=scene.config.scene_id,
                config=scene.config.to_dict(),
                context=self._serialize_context(scene.context),
                metadata=scene.get_metadata(),
                created_at=scene.created_at,
            )

            self._snapshots[scene_key] = snapshot

            logger.debug(f"场景快照保存：{scene_key}")

        except Exception as e:
            logger.warning(f"保存场景快照失败：{e}")

    def _restore_scene_context(self, scene_key: str) -> None:
        """
        恢复场景上下文

        Args:
            scene_key: 场景键
        """
        snapshot = self._snapshots.get(scene_key)
        if not snapshot:
            return

        scene = self._scenes.get(scene_key)
        if not scene:
            return

        try:
            # 恢复上下文
            self._deserialize_context(scene.context, snapshot.context)

            logger.debug(f"场景上下文恢复：{scene_key}")

        except Exception as e:
            logger.warning(f"恢复场景上下文失败：{e}")

    def _serialize_context(self, context: DialogueContext) -> Dict[str, Any]:
        """
        序列化对话上下文

        Args:
            context: 对话上下文

        Returns:
            序列化后的字典
        """
        return {
            "messages": [msg.to_dict() for msg in context.messages],
            "metadata": context.metadata,
        }

    def _deserialize_context(
        self,
        context: DialogueContext,
        data: Dict[str, Any],
    ) -> None:
        """
        反序列化对话上下文

        Args:
            context: 对话上下文对象
            data: 序列化数据
        """
        # 清空现有内容
        context.messages.clear()
        context.metadata.clear()

        # 恢复元数据
        context.metadata.update(data.get("metadata", {}))

        # 恢复消息
        for msg_data in data.get("messages", []):
            msg = Message.from_dict(msg_data)
            context.add_message(msg)

    def get_global_context(self) -> DialogueContext:
        """
        获取全局上下文

        Returns:
            全局对话上下文
        """
        return self._global_context

    def get_scene_history(self) -> List[str]:
        """
        获取场景历史

        Returns:
            场景键列表
        """
        return self._scene_history.copy()

    def get_transition_history(self) -> List[SceneTransition]:
        """
        获取转换历史

        Returns:
            转换结果列表
        """
        return self._transition_history.copy()

    def export_state(self) -> Dict[str, Any]:
        """
        导出管理器状态

        Returns:
            状态字典
        """
        return {
            "active_scene": self._active_scene_key,
            "scenes": list(self._scenes.keys()),
            "snapshots": {
                key: snapshot.to_json()
                for key, snapshot in self._snapshots.items()
            },
            "history": self._scene_history,
            "global_context": self._serialize_context(self._global_context),
        }

    def import_state(self, state: Dict[str, Any]) -> bool:
        """
        导入管理器状态

        Args:
            state: 状态字典

        Returns:
            是否成功导入
        """
        try:
            # 恢复活跃场景
            self._active_scene_key = state.get("active_scene")

            # 恢复场景历史
            self._scene_history = state.get("history", [])

            # 恢复快照
            snapshots_data = state.get("snapshots", {})
            for key, json_str in snapshots_data.items():
                self._snapshots[key] = SceneStateSnapshot.from_json(json_str)

            # 恢复全局上下文
            context_data = state.get("global_context", {})
            self._deserialize_context(self._global_context, context_data)

            logger.info("管理器状态导入成功")
            return True

        except Exception as e:
            logger.error(f"导入管理器状态失败：{e}")
            return False

    def clear(self) -> None:
        """
        清空管理器

        销毁所有场景并重置状态
        """
        # 销毁所有场景
        for key in list(self._scenes.keys()):
            self.destroy_scene(key)

        # 重置状态
        self._active_scene_key = None
        self._snapshots.clear()
        self._scene_history.clear()
        self._transition_history.clear()
        self._global_context.clear()

        logger.info("场景管理器已清空")
