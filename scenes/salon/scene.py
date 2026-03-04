"""
Salon Scene Implementation - 沙龙场景实现

实现完整的沙龙活动流程，包括：
- 多角色协同对话（主持人、演讲者、观众、观察者）
- 话题引导和转场控制
- 阶段性总结
- 自由讨论管理

沙龙流程:
1. Opening: 主持人开场，介绍主题和嘉宾
2. Presentation: 演讲者主题分享
3. Q&A: 观众提问互动
4. Discussion: 自由讨论
5. Summary: 观察者总结，主持人闭幕

支持 4+ AI Agent 同时参与，模拟真实沙龙场景。
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType
from scenes.base import BaseScene, SceneConfig, SceneState, SceneError

from .roles import (
    SalonRoleType,
    RoleConfig,
    RoleState,
    RoleManager,
)

logger = logging.getLogger(__name__)


class SalonPhase(Enum):
    """
    沙龙阶段枚举

    定义沙龙流程的各个阶段
    """
    OPENING = "opening"           # 开场阶段
    PRESENTATION = "presentation" # 主题分享
    Q_AND_A = "q_and_a"          # 问答互动
    DISCUSSION = "discussion"     # 自由讨论
    SUMMARY = "summary"          # 总结阶段
    CLOSING = "closing"          # 闭幕


class SalonSceneConfig(SceneConfig):
    """
    沙龙场景配置

    扩展基础 SceneConfig，添加沙龙特定配置

    Attributes:
        topic: 沙龙主题
        speaker_topic: 演讲者分享主题
        max_participants: 最大参与人数
        enable_pressure: 是否启用压力测试
        discussion_style: 讨论风格 (formal/casual/debate)
    """
    def __init__(
        self,
        topic: str = "技术前沿探索",
        speaker_topic: str = "AI 技术应用",
        max_participants: int = 10,
        discussion_style: str = "casual",
        **kwargs,
    ):
        """
        初始化沙龙配置

        Args:
            topic: 沙龙主题
            speaker_topic: 演讲主题
            max_participants: 最大参与人数
            discussion_style: 讨论风格
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.scene_type = "salon"
        self.name = "技术沙龙"
        self.description = "模拟真实技术沙龙活动，多角色互动讨论"

        self.topic = topic
        self.speaker_topic = speaker_topic
        self.max_participants = max_participants
        self.discussion_style = discussion_style

        # 默认设置
        self.settings = {
            "opening_turns": 2,
            "presentation_turns": 5,
            "qa_turns": 8,
            "discussion_turns": 10,
            "summary_turns": 3,
            "auto_transition": True,  # 自动阶段转换
            "observer_intervene": True,  # 观察者介入总结
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            "topic": self.topic,
            "speaker_topic": self.speaker_topic,
            "max_participants": self.max_participants,
            "discussion_style": self.discussion_style,
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SalonSceneConfig":
        """从字典创建"""
        return cls(
            topic=data.get("topic", "技术前沿探索"),
            speaker_topic=data.get("speaker_topic", "AI 技术应用"),
            max_participants=data.get("max_participants", 10),
            discussion_style=data.get("discussion_style", "casual"),
            **{k: v for k, v in data.items() if k not in [
                "topic", "speaker_topic", "max_participants", "discussion_style"
            ]},
        )


class SalonScene(BaseScene):
    """
    沙龙场景实现

    提供完整的沙龙活动管理，包括：
    - 多角色 Agent 协同
    - 阶段流程控制
    - 话题引导和转场
    - 讨论记录和总结

    Attributes:
        phase: 当前沙龙阶段
        role_manager: 角色管理器
        topic: 沙龙主题
        speaker_topic: 演讲主题
    """

    def __init__(
        self,
        config: Optional[SceneConfig] = None,
        global_config: Optional[Config] = None,
        topic: str = "技术前沿探索",
        speaker_topic: str = "AI 技术应用",
        discussion_style: str = "casual",
    ):
        """
        初始化沙龙场景

        Args:
            config: 场景配置
            global_config: 全局配置
            topic: 沙龙主题
            speaker_topic: 演讲主题
            discussion_style: 讨论风格
        """
        # 创建沙龙特定配置
        if config is None:
            config = SalonSceneConfig(
                topic=topic,
                speaker_topic=speaker_topic,
                discussion_style=discussion_style,
            )
        elif not isinstance(config, SalonSceneConfig):
            # 转换普通 SceneConfig 为 SalonSceneConfig
            config_dict = config.to_dict()
            config_dict["topic"] = topic
            config_dict["speaker_topic"] = speaker_topic
            config_dict["discussion_style"] = discussion_style
            config = SalonSceneConfig.from_dict(config_dict)

        super().__init__(config, global_config)

        # 沙龙特定属性
        self.topic = self.config.settings.get("topic", topic)
        self.speaker_topic = self.config.settings.get("speaker_topic", speaker_topic)
        self.discussion_style = discussion_style

        # 沙龙状态
        self.phase = SalonPhase.OPENING
        self._current_turn: int = 0
        self._key_points: List[str] = []
        self._questions: List[Dict[str, Any]] = []
        self._summary_notes: List[str] = []

        # 角色管理器
        self.role_manager = RoleManager()

        # Agent 实例
        self._host_agent: Optional[BaseAgent] = None
        self._speaker_agent: Optional[BaseAgent] = None
        self._audience_agents: List[BaseAgent] = []
        self._observer_agent: Optional[BaseAgent] = None

    def get_scene_type(self) -> str:
        """获取场景类型标识符"""
        return "salon"

    def get_description(self) -> str:
        """获取场景描述"""
        style_names = {
            "formal": "正式",
            "casual": "轻松",
            "debate": "辩论",
        }
        style_name = style_names.get(self.discussion_style, "互动")
        return f"{style_name}风格的技术沙龙场景 - 主题：{self.topic}"

    def initialize(self) -> bool:
        """
        初始化沙龙场景

        创建所有角色 Agent 并注册

        Returns:
            初始化是否成功
        """
        try:
            logger.info(f"初始化沙龙场景：topic={self.topic}, style={self.discussion_style}")

            # 延迟导入避免循环依赖
            from .host import SalonHostAgent
            from .speaker import SalonSpeakerAgent
            from .audience import SalonAudienceAgent
            from .observer import SalonObserverAgent

            # 创建主持人 Agent
            self._host_agent = SalonHostAgent(
                name="主持人",
                config=self.global_config,
                topic=self.topic,
                discussion_style=self.discussion_style,
            )
            self._host_agent.initialize()
            self.register_agent("host", self._host_agent)

            # 创建演讲者 Agent
            self._speaker_agent = SalonSpeakerAgent(
                name="演讲嘉宾",
                config=self.global_config,
                topic=self.speaker_topic,
                main_topic=self.topic,
            )
            self._speaker_agent.initialize()
            self.register_agent("speaker", self._speaker_agent)

            # 创建观众 Agent (多个)
            audience_count = self.config.settings.get("audience_count", 2)
            for i in range(audience_count):
                audience = SalonAudienceAgent(
                    name=f"观众{i + 1}",
                    config=self.global_config,
                    audience_id=i,
                    topic=self.topic,
                )
                audience.initialize()
                self._audience_agents.append(audience)
                self.register_agent(f"audience_{i}", audience)

            # 创建观察者 Agent
            self._observer_agent = SalonObserverAgent(
                name="观察员",
                config=self.global_config,
                focus_areas=["key_points", "consensus", "controversy"],
            )
            self._observer_agent.initialize()
            self.register_agent("observer", self._observer_agent)

            # 初始化角色管理器
            self._init_role_manager()

            # 设置场景元数据
            self.set_metadata("topic", self.topic)
            self.set_metadata("speaker_topic", self.speaker_topic)
            self.set_metadata("discussion_style", self.discussion_style)
            self.set_metadata("agent_count", len(self.get_agents()))

            self.state = SceneState.INITIALIZED
            logger.info(f"沙龙场景初始化成功，共{len(self.get_agents())}个 Agent")
            return True

        except Exception as e:
            logger.error(f"沙龙场景初始化失败：{e}")
            self.state = SceneState.ERROR
            return False

    def handle_message(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """
        处理用户消息

        根据当前沙龙阶段和消息内容生成响应

        Args:
            message: 用户输入消息
            context: 对话上下文

        Returns:
            Agent 响应消息
        """
        if not self._is_ready():
            return self._create_error_message("沙龙场景未就绪")

        # 更新轮次
        self._current_turn += 1

        # 检查阶段转换
        if self.config.settings.get("auto_transition", True):
            self._check_phase_transition()

        # 根据阶段处理消息
        response = self._route_to_phase_handler(message, context)

        # 更新上下文
        context.add_message(message)
        context.add_message(response)

        return response

    def get_agents(self) -> List[BaseAgent]:
        """获取场景中的所有 Agent"""
        agents = []
        if self._host_agent:
            agents.append(self._host_agent)
        if self._speaker_agent:
            agents.append(self._speaker_agent)
        agents.extend(self._audience_agents)
        if self._observer_agent:
            agents.append(self._observer_agent)
        return agents

    def start(self) -> Message:
        """启动沙龙场景"""
        if self.state != SceneState.INITIALIZED:
            return self._create_error_message("场景未初始化")

        self.state = SceneState.RUNNING
        self.phase = SalonPhase.OPENING

        # 生成开场消息
        opening_content = self._generate_opening()

        return Message(
            content=opening_content,
            role="host",
            type=MessageType.AGENT,
            metadata={
                "phase": self.phase.value,
                "topic": self.topic,
                "agent_count": len(self.get_agents()),
            },
        )

    def get_current_phase(self) -> SalonPhase:
        """获取当前沙龙阶段"""
        return self.phase

    def get_salon_stats(self) -> Dict[str, Any]:
        """
        获取沙龙统计信息

        Returns:
            统计信息字典
        """
        return {
            "phase": self.phase.value,
            "current_turn": self._current_turn,
            "key_points_count": len(self._key_points),
            "questions_count": len(self._questions),
            "agent_count": len(self.get_agents()),
            "topic": self.topic,
            "speaker_topic": self.speaker_topic,
        }

    def switch_phase(self, new_phase: SalonPhase) -> bool:
        """
        切换沙龙阶段

        Args:
            new_phase: 目标阶段

        Returns:
            是否成功切换
        """
        if not self.is_running():
            return False

        old_phase = self.phase
        self.phase = new_phase

        logger.info(f"沙龙阶段切换：{old_phase.value} -> {new_phase.value}")

        # 生成阶段转换消息
        if new_phase == SalonPhase.PRESENTATION:
            self._host_agent.set_current_phase("presentation")
        elif new_phase == SalonPhase.Q_AND_A:
            self._host_agent.set_current_phase("q_and_a")
        elif new_phase == SalonPhase.DISCUSSION:
            self._host_agent.set_current_phase("discussion")
        elif new_phase == SalonPhase.SUMMARY:
            self._observer_agent.set_current_phase("summary")

        return True

    def _init_role_manager(self) -> None:
        """初始化角色管理器"""
        # 添加主持人角色
        self.role_manager.add_role(
            RoleConfig.create_host(
                name="主持人",
                settings={
                    "topic": self.topic,
                    "discussion_style": self.discussion_style,
                },
            )
        )

        # 添加演讲者角色
        self.role_manager.add_role(
            RoleConfig.create_speaker(
                topic=self.speaker_topic,
                name="演讲嘉宾",
            )
        )

        # 添加观众角色
        self.role_manager.add_role(
            RoleConfig.create_audience(name="观众")
        )

        # 添加观察者角色
        self.role_manager.add_role(
            RoleConfig.create_observer(name="观察员")
        )

    def _is_ready(self) -> bool:
        """检查场景是否就绪"""
        return (
            self.state == SceneState.INITIALIZED
            and self._host_agent is not None
            and self._speaker_agent is not None
        )

    def _generate_opening(self) -> str:
        """生成开场白"""
        if self._host_agent:
            return self._host_agent.generate_opening(
                topic=self.topic,
                speaker_topic=self.speaker_topic,
            )

        return (
            f"欢迎大家来到'{self.topic}'技术沙龙！\n\n"
            f"今天我们将围绕'{self.speaker_topic}'这一主题展开深入讨论。\n"
            f"现场有我们的演讲嘉宾和多位热心观众，希望大家积极互动，共同交流！\n\n"
            f"首先，让我们有请演讲嘉宾开始分享。"
        )

    def _check_phase_transition(self) -> None:
        """检查是否需要进行阶段转换"""
        settings = self.config.settings

        if self.phase == SalonPhase.OPENING:
            if self._current_turn >= settings.get("opening_turns", 2):
                self.switch_phase(SalonPhase.PRESENTATION)

        elif self.phase == SalonPhase.PRESENTATION:
            if self._current_turn >= settings.get("presentation_turns", 5):
                self.switch_phase(SalonPhase.Q_AND_A)

        elif self.phase == SalonPhase.Q_AND_A:
            if self._current_turn >= settings.get("qa_turns", 8):
                self.switch_phase(SalonPhase.DISCUSSION)

        elif self.phase == SalonPhase.DISCUSSION:
            if self._current_turn >= settings.get("discussion_turns", 10):
                self.switch_phase(SalonPhase.SUMMARY)

        elif self.phase == SalonPhase.SUMMARY:
            if self._current_turn >= settings.get("summary_turns", 3):
                self.switch_phase(SalonPhase.CLOSING)

    def _route_to_phase_handler(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """
        根据阶段路由到对应的处理器

        Args:
            message: 用户消息
            context: 对话上下文

        Returns:
            响应消息
        """
        handlers = {
            SalonPhase.OPENING: self._handle_opening,
            SalonPhase.PRESENTATION: self._handle_presentation,
            SalonPhase.Q_AND_A: self._handle_q_and_a,
            SalonPhase.DISCUSSION: self._handle_discussion,
            SalonPhase.SUMMARY: self._handle_summary,
            SalonPhase.CLOSING: self._handle_closing,
        }

        handler = handlers.get(self.phase, self._handle_discussion)
        return handler(message, context)

    def _handle_opening(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理开场阶段"""
        if not self._host_agent:
            return self._create_error_message("主持人未初始化")

        # 主持人回应用户并介绍演讲者
        response = self._host_agent.respond(
            user_message=message.content,
            context=context,
            phase="opening",
        )

        # 自动进入分享阶段
        if self._current_turn >= 1:
            self.switch_phase(SalonPhase.PRESENTATION)
            response += "\n\n[主持人]: 下面有请演讲嘉宾开始今天的主题分享！"

        return Message(
            content=response,
            role="host",
            type=MessageType.AGENT,
            metadata={"phase": "opening"},
        )

    def _handle_presentation(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理主题分享阶段"""
        if not self._speaker_agent:
            return self._create_error_message("演讲者未初始化")

        # 演讲者进行主题分享
        response = self._speaker_agent.respond(
            user_message=message.content,
            context=context,
            phase="presentation",
        )

        # 记录关键点
        self._key_points.extend(
            self._extract_key_points(response)
        )

        return Message(
            content=response,
            role="speaker",
            type=MessageType.AGENT,
            metadata={"phase": "presentation"},
        )

    def _handle_q_and_a(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理问答互动阶段"""
        # 优先由演讲者回答问题
        if self._speaker_agent:
            response = self._speaker_agent.respond(
                user_message=message.content,
                context=context,
                phase="q_and_a",
            )

            # 记录问题
            self._questions.append({
                "content": message.content,
                "turn": self._current_turn,
                "answered": True,
            })

            return Message(
                content=response,
                role="speaker",
                type=MessageType.AGENT,
                metadata={"phase": "q_and_a"},
            )

        return self._handle_discussion(message, context)

    def _handle_discussion(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理自由讨论阶段"""
        # 轮流使用不同观众 Agent 回应
        if self._audience_agents:
            # 选择一个观众回应
            audience_idx = self._current_turn % len(self._audience_agents)
            audience = self._audience_agents[audience_idx]

            response = audience.respond(
                user_message=message.content,
                context=context,
                phase="discussion",
            )

            return Message(
                content=response,
                role=f"audience_{audience_idx + 1}",
                type=MessageType.AGENT,
                metadata={"phase": "discussion"},
            )

        # 如果没有观众，由主持人回应
        if self._host_agent:
            response = self._host_agent.respond(
                user_message=message.content,
                context=context,
                phase="discussion",
            )

            return Message(
                content=response,
                role="host",
                type=MessageType.AGENT,
                metadata={"phase": "discussion"},
            )

        return self._create_error_message("没有可用的讨论 Agent")

    def _handle_summary(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理总结阶段"""
        if not self._observer_agent:
            return self._create_error_message("观察员未初始化")

        # 观察员进行总结
        response = self._observer_agent.respond(
            user_message=message.content,
            context=context,
            phase="summary",
            key_points=self._key_points,
            questions=self._questions,
        )

        # 记录总结要点
        self._summary_notes.append(response)

        return Message(
            content=response,
            role="observer",
            type=MessageType.AGENT,
            metadata={"phase": "summary"},
        )

    def _handle_closing(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理闭幕阶段"""
        if not self._host_agent:
            return self._create_error_message("主持人未初始化")

        response = self._host_agent.generate_closing(
            topic=self.topic,
            key_points=self._key_points,
        )

        # 标记场景即将完成
        self.state = SceneState.COMPLETED

        return Message(
            content=response,
            role="host",
            type=MessageType.AGENT,
            metadata={"phase": "closing"},
        )

    def _extract_key_points(self, content: str) -> List[str]:
        """
        从内容中提取关键点

        Args:
            content: 内容文本

        Returns:
            关键点列表
        """
        # 简单实现：按句号分割，取较长的句子
        points = []
        sentences = content.replace("。", "\n").replace("!", "\n").replace("?", "\n").split("\n")

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:
                points.append(sentence)

        return points[:5]  # 最多返回 5 个关键点

    def cleanup(self) -> None:
        """清理场景资源"""
        super().cleanup()
        self._key_points.clear()
        self._questions.clear()
        self._summary_notes.clear()
        self._current_turn = 0
        self.phase = SalonPhase.OPENING
        self.role_manager.reset()


# 导出
__all__ = [
    "SalonScene",
    "SalonSceneConfig",
    "SalonPhase",
]
