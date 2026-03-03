"""
Base Scene Module - 场景基类模块

定义场景系统的抽象基类和核心数据结构。
所有具体场景必须继承 BaseScene 并实现其抽象方法。

设计原则:
- 单一职责：每个场景专注于特定对话类型
- 开闭原则：通过继承扩展新场景，不修改现有代码
- 依赖倒置：高层模块依赖抽象基类而非具体实现
"""

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext

if TYPE_CHECKING:
    from .registry import SceneRegistry


class SceneState(Enum):
    """
    场景状态枚举

    用于跟踪场景的生命周期状态
    """
    CREATED = "created"       # 已创建，未初始化
    INITIALIZED = "initialized"  # 已初始化，准备就绪
    RUNNING = "running"       # 运行中
    PAUSED = "paused"         # 已暂停
    COMPLETED = "completed"   # 已完成
    ERROR = "error"           # 错误状态


@dataclass
class SceneConfig:
    """
    场景配置数据类

    封装场景相关的配置参数，提供类型安全的访问接口。

    Attributes:
        scene_id: 场景唯一标识符
        scene_type: 场景类型名称
        name: 场景显示名称
        description: 场景描述
        settings: 场景特定设置
        agents: Agent 配置列表
        max_turns: 最大对话轮数
        timeout_seconds: 超时时间（秒）
    """
    scene_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scene_type: str = "base"
    name: str = "基础场景"
    description: str = "基础对话场景"
    settings: Dict[str, Any] = field(default_factory=dict)
    agents: List[Dict[str, Any]] = field(default_factory=list)
    max_turns: int = 20
    timeout_seconds: int = 600

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneConfig":
        """
        从字典创建场景配置

        Args:
            data: 配置字典

        Returns:
            SceneConfig 实例
        """
        return cls(
            scene_id=data.get("scene_id", str(uuid.uuid4())),
            scene_type=data.get("scene_type", "base"),
            name=data.get("name", "基础场景"),
            description=data.get("description", "基础对话场景"),
            settings=data.get("settings", {}),
            agents=data.get("agents", []),
            max_turns=data.get("max_turns", 20),
            timeout_seconds=data.get("timeout_seconds", 600),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典

        Returns:
            配置字典
        """
        return {
            "scene_id": self.scene_id,
            "scene_type": self.scene_type,
            "name": self.name,
            "description": self.description,
            "settings": self.settings,
            "agents": self.agents,
            "max_turns": self.max_turns,
            "timeout_seconds": self.timeout_seconds,
        }


class BaseScene(ABC):
    """
    场景抽象基类

    所有具体场景必须继承此类并实现其抽象方法。
    场景是对话流程的高级抽象，封装了特定类型的对话逻辑。

    生命周期:
        1. 创建：通过构造函数或工厂方法创建场景实例
        2. 初始化：调用 initialize() 进行初始化
        3. 运行：调用 handle_message() 处理对话
        4. 结束：调用 cleanup() 清理资源

    Attributes:
        config: 场景配置对象
        state: 当前场景状态
        context: 对话上下文
        created_at: 创建时间戳
    """

    def __init__(
        self,
        config: Optional[SceneConfig] = None,
        global_config: Optional[Config] = None,
    ):
        """
        初始化场景基类

        Args:
            config: 场景特定配置
            global_config: 全局配置对象
        """
        self.config = config or SceneConfig()
        self.global_config = global_config or Config()
        self.state = SceneState.CREATED
        self.context = DialogueContext()
        self.created_at: float = time.time()
        self._agents: Dict[str, BaseAgent] = {}
        self._metadata: Dict[str, Any] = {}
        self._errors: List[str] = []

    @abstractmethod
    def get_scene_type(self) -> str:
        """
        获取场景类型标识符

        Returns:
            场景类型字符串，用于注册和识别
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        获取场景描述

        Returns:
            场景描述字符串
        """
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化场景

        在此方法中创建和配置所有需要的 Agent。

        Returns:
            初始化是否成功

        Raises:
            SceneError: 初始化失败时抛出异常
        """
        pass

    @abstractmethod
    def handle_message(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """
        处理用户消息

        场景的核心逻辑，根据当前状态和消息内容生成响应。

        Args:
            message: 用户输入消息
            context: 对话上下文

        Returns:
            Agent 响应消息
        """
        pass

    @abstractmethod
    def get_agents(self) -> List[BaseAgent]:
        """
        获取场景中的所有 Agent

        Returns:
            Agent 列表
        """
        pass

    def start(self) -> Message:
        """
        启动场景

        生成场景的开场消息。

        Returns:
            开场消息
        """
        if self.state not in [SceneState.CREATED, SceneState.INITIALIZED]:
            return self._create_error_message("场景未就绪，无法启动")

        self.state = SceneState.RUNNING
        opening = self._get_opening_message()

        return Message(
            content=opening,
            role="system",
            type=MessageType.SYSTEM,
            metadata={"scene_type": self.get_scene_type()},
        )

    def pause(self) -> bool:
        """
        暂停场景

        Returns:
            是否成功暂停
        """
        if self.state == SceneState.RUNNING:
            self.state = SceneState.PAUSED
            return True
        return False

    def resume(self) -> bool:
        """
        恢复场景

        Returns:
            是否成功恢复
        """
        if self.state == SceneState.PAUSED:
            self.state = SceneState.RUNNING
            return True
        return False

    def complete(self) -> Message:
        """
        完成场景

        执行清理操作并生成结束消息。

        Returns:
            结束消息
        """
        self.state = SceneState.COMPLETED
        closing = self._get_closing_message()

        return Message(
            content=closing,
            role="system",
            type=MessageType.SYSTEM,
            metadata={"scene_type": self.get_scene_type()},
        )

    def cleanup(self) -> None:
        """
        清理场景资源

        子类可重写此方法释放特定资源
        """
        self.context.clear()
        self._agents.clear()
        self.state = SceneState.CREATED

    def is_running(self) -> bool:
        """检查场景是否正在运行"""
        return self.state == SceneState.RUNNING

    def is_completed(self) -> bool:
        """检查场景是否已完成"""
        return self.state == SceneState.COMPLETED

    def get_state(self) -> SceneState:
        """获取当前状态"""
        return self.state

    def get_context(self) -> DialogueContext:
        """获取对话上下文"""
        return self.context

    def get_metadata(self) -> Dict[str, Any]:
        """获取场景元数据"""
        return self._metadata.copy()

    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        self._metadata[key] = value

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self._errors.copy()

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        """
        注册 Agent 到场景

        Args:
            name: Agent 名称
            agent: Agent 实例
        """
        self._agents[name] = agent

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        获取已注册的 Agent

        Args:
            name: Agent 名称

        Returns:
            Agent 实例或 None
        """
        return self._agents.get(name)

    def _create_error_message(self, error: str) -> Message:
        """创建错误消息"""
        self._errors.append(error)
        self.state = SceneState.ERROR

        return Message(
            content=f"场景错误：{error}",
            role="system",
            type=MessageType.SYSTEM,
            metadata={"error": error},
        )

    def _get_opening_message(self) -> str:
        """获取开场消息（可被子类重写）"""
        return f"欢迎进入{self.config.name}场景。{self.config.description}"

    def _get_closing_message(self) -> str:
        """获取结束消息（可被子类重写）"""
        return "场景已结束，感谢参与。"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type='{self.get_scene_type()}', state={self.state.value})"


# 导入 MessageType 避免循环依赖
from core.agent import MessageType


class SceneError(Exception):
    """
    场景相关异常

    用于处理场景生命周期中的各种错误情况
    """
    pass
