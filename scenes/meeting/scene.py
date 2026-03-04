"""
Meeting Scene Implementation - 会议场景实现

实现完整的会议流程管理，支持多种会议类型：
- 需求评审：评审产品需求，识别风险
- 站会：每日进度同步，识别阻塞
- 冲突解决：调解分歧，达成共识
- 项目启动：明确目标，分配任务
- 复盘会议：总结经验，持续改进

会议流程:
1. Opening: 会议开场，明确议程和目标
2. RoundTable: 轮流发言，每人陈述观点
3. Discussion: 自由讨论，深入交流
4. Summary: 总结要点，确认共识
5. ActionItems: 确定行动项和负责人
6. Closing: 会议结束

支持多 Agent 参与，模拟真实会议场景。
"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType
from scenes.base import BaseScene, SceneConfig, SceneState, SceneError

logger = logging.getLogger(__name__)


class MeetingType(Enum):
    """
    会议类型枚举

    定义支持的会议类型
    """
    REQUIREMENT_REVIEW = "requirement_review"  # 需求评审
    STANDUP = "standup"                         # 站会/进度同步
    CONFLICT_RESOLUTION = "conflict_resolution" # 冲突解决
    PROJECT_KICKOFF = "project_kickoff"         # 项目启动
    RETROSPECTIVE = "retrospective"             # 复盘会议


class MeetingPhase(Enum):
    """
    会议阶段枚举

    定义会议流程的各个阶段
    """
    OPENING = "opening"           # 开场阶段
    ROUND_TABLE = "round_table"   # 轮流发言
    DISCUSSION = "discussion"     # 自由讨论
    SUMMARY = "summary"          # 总结要点
    ACTION_ITEMS = "action_items" # 行动项
    CLOSING = "closing"          # 结束


class MeetingSceneConfig(SceneConfig):
    """
    会议场景配置

    扩展基础 SceneConfig，添加会议特定配置

    Attributes:
        meeting_type: 会议类型
        project_name: 项目名称
        agenda: 会议议程
        duration_minutes: 预计时长（分钟）
        participant_count: 参与人数
    """

    def __init__(
        self,
        meeting_type: MeetingType = MeetingType.STANDUP,
        project_name: str = "项目 A",
        agenda: Optional[List[str]] = None,
        duration_minutes: int = 30,
        participant_count: int = 4,
        **kwargs,
    ):
        """
        初始化会议配置

        Args:
            meeting_type: 会议类型
            project_name: 项目名称
            agenda: 会议议程列表
            duration_minutes: 预计时长
            participant_count: 参与人数
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.scene_type = "meeting"
        self.name = self._get_meeting_name(meeting_type)
        self.description = f"模拟{self.name}场景"

        self.meeting_type = meeting_type
        self.project_name = project_name
        self.agenda = agenda or self._get_default_agenda(meeting_type)
        self.duration_minutes = duration_minutes
        self.participant_count = participant_count

        # 默认设置
        self.settings = {
            "opening_turns": 1,
            "round_table_turns": participant_count,
            "discussion_turns": 8,
            "summary_turns": 2,
            "action_item_turns": 2,
            "auto_transition": True,
            "time_boxing": True,  # 时间盒控制
        }

    def _get_meeting_name(self, meeting_type: MeetingType) -> str:
        """获取会议名称"""
        names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }
        return names.get(meeting_type, "项目会议")

    def _get_default_agenda(self, meeting_type: MeetingType) -> List[str]:
        """获取默认议程"""
        agendas = {
            MeetingType.REQUIREMENT_REVIEW: [
                "需求背景介绍",
                "功能点评审",
                "技术可行性讨论",
                "风险评估",
                "下一步计划",
            ],
            MeetingType.STANDUP: [
                "昨日完成工作",
                "今日计划",
                "阻塞问题",
            ],
            MeetingType.CONFLICT_RESOLUTION: [
                "问题陈述",
                "各方观点",
                "寻找共识",
                "解决方案",
            ],
            MeetingType.PROJECT_KICKOFF: [
                "项目背景",
                "目标范围",
                "团队分工",
                "时间计划",
            ],
            MeetingType.RETROSPECTIVE: [
                "做得好的",
                "需要改进的",
                "行动计划",
            ],
        }
        return agendas.get(meeting_type, ["讨论议题"])

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base_dict = super().to_dict()
        base_dict.update({
            "meeting_type": self.meeting_type.value,
            "project_name": self.project_name,
            "agenda": self.agenda,
            "duration_minutes": self.duration_minutes,
            "participant_count": self.participant_count,
        })
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeetingSceneConfig":
        """从字典创建"""
        meeting_type_data = data.get("meeting_type", "standup")
        meeting_type = MeetingType(meeting_type_data) if isinstance(meeting_type_data, str) else meeting_type_data

        return cls(
            meeting_type=meeting_type,
            project_name=data.get("project_name", "项目 A"),
            agenda=data.get("agenda"),
            duration_minutes=data.get("duration_minutes", 30),
            participant_count=data.get("participant_count", 4),
            **{k: v for k, v in data.items() if k not in [
                "meeting_type", "project_name", "agenda",
                "duration_minutes", "participant_count",
            ]},
        )


class MeetingScene(BaseScene):
    """
    会议场景实现

    提供完整的会议流程管理，包括：
    - 多会议类型支持
    - 阶段流程控制
    - 议程管理
    - 行动项跟踪

    Attributes:
        meeting_type: 会议类型
        project_name: 项目名称
        phase: 当前会议阶段
        agenda: 会议议程
    """

    def __init__(
        self,
        config: Optional[SceneConfig] = None,
        global_config: Optional[Config] = None,
        meeting_type: MeetingType = MeetingType.STANDUP,
        project_name: str = "项目 A",
        agenda: Optional[List[str]] = None,
    ):
        """
        初始化会议场景

        Args:
            config: 场景配置
            global_config: 全局配置
            meeting_type: 会议类型
            project_name: 项目名称
            agenda: 会议议程
        """
        # 创建会议特定配置
        if config is None:
            config = MeetingSceneConfig(
                meeting_type=meeting_type,
                project_name=project_name,
                agenda=agenda,
            )
        elif not isinstance(config, MeetingSceneConfig):
            config_dict = config.to_dict()
            config_dict["meeting_type"] = meeting_type.value if isinstance(meeting_type, MeetingType) else meeting_type
            config_dict["project_name"] = project_name
            config_dict["agenda"] = agenda
            config = MeetingSceneConfig.from_dict(config_dict)

        super().__init__(config, global_config)

        # 会议特定属性
        self.meeting_type = self.config.meeting_type
        self.project_name = self.config.project_name
        self.agenda = self.config.agenda

        # 会议状态
        self.phase = MeetingPhase.OPENING
        self._current_turn: int = 0
        self._current_agenda_item: int = 0
        self._action_items: List[Dict[str, Any]] = []
        self._decisions: List[str] = []
        self._key_points: List[str] = []

        # Agent 实例
        self._manager_agent: Optional[BaseAgent] = None
        self._participant_agents: List[BaseAgent] = []
        self._current_speaker_idx: int = 0

    def get_scene_type(self) -> str:
        """获取场景类型标识符"""
        return "meeting"

    def get_description(self) -> str:
        """获取场景描述"""
        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决",
            MeetingType.PROJECT_KICKOFF: "项目启动",
            MeetingType.RETROSPECTIVE: "项目复盘",
        }
        type_name = type_names.get(self.meeting_type, "项目会议")
        return f"{type_name}场景 - 项目：{self.project_name}"

    def initialize(self) -> bool:
        """
        初始化会议场景

        创建所有会议 Agent 并注册

        Returns:
            初始化是否成功
        """
        try:
            logger.info(
                f"初始化会议场景：type={self.meeting_type.value}, "
                f"project={self.project_name}"
            )

            # 延迟导入避免循环依赖
            from .manager import MeetingManagerAgent
            from .participant import MeetingParticipantAgent

            # 创建会议主持人 Agent
            self._manager_agent = MeetingManagerAgent(
                name="会议主持人",
                config=self.global_config,
                meeting_type=self.meeting_type,
                project_name=self.project_name,
                agenda=self.agenda,
            )
            self._manager_agent.initialize()
            self.register_agent("manager", self._manager_agent)

            # 创建参与者 Agent
            participant_count = self.config.participant_count
            participant_roles = self._get_participant_roles()

            for i in range(participant_count):
                role = participant_roles[i % len(participant_roles)]
                participant = MeetingParticipantAgent(
                    name=role["name"],
                    config=self.global_config,
                    participant_id=i,
                    role=role["role"],
                    meeting_type=self.meeting_type,
                    project_name=self.project_name,
                )
                participant.initialize()
                self._participant_agents.append(participant)
                self.register_agent(f"participant_{i}", participant)

            # 设置场景元数据
            self.set_metadata("meeting_type", self.meeting_type.value)
            self.set_metadata("project_name", self.project_name)
            self.set_metadata("agenda", self.agenda)
            self.set_metadata("participant_count", len(self._participant_agents))

            self.state = SceneState.INITIALIZED
            logger.info(
                f"会议场景初始化成功，共{len(self.get_agents())}个 Agent"
            )
            return True

        except Exception as e:
            logger.error(f"会议场景初始化失败：{e}")
            self.state = SceneState.ERROR
            return False

    def handle_message(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """
        处理用户消息

        根据当前会议阶段和消息内容生成响应

        Args:
            message: 用户输入消息
            context: 对话上下文

        Returns:
            Agent 响应消息
        """
        if not self._is_ready():
            return self._create_error_message("会议场景未就绪")

        # 更新轮次
        self._current_turn += 1

        # 检查阶段转换
        if self.config.settings.get("auto_transition", True):
            self._check_phase_transition()

        # 根据阶段路由到对应的处理器
        response = self._route_to_phase_handler(message, context)

        # 更新上下文
        context.add_message(message)
        context.add_message(response)

        return response

    def get_agents(self) -> List[BaseAgent]:
        """获取场景中的所有 Agent"""
        agents = []
        if self._manager_agent:
            agents.append(self._manager_agent)
        agents.extend(self._participant_agents)
        return agents

    def start(self) -> Message:
        """启动会议场景"""
        if self.state != SceneState.INITIALIZED:
            return self._create_error_message("场景未初始化")

        self.state = SceneState.RUNNING
        self.phase = MeetingPhase.OPENING

        # 生成开场消息
        opening_content = self._generate_opening()

        return Message(
            content=opening_content,
            role="manager",
            type=MessageType.AGENT,
            metadata={
                "phase": self.phase.value,
                "meeting_type": self.meeting_type.value,
                "project_name": self.project_name,
            },
        )

    def get_current_phase(self) -> MeetingPhase:
        """获取当前会议阶段"""
        return self.phase

    def get_meeting_stats(self) -> Dict[str, Any]:
        """
        获取会议统计信息

        Returns:
            统计信息字典
        """
        return {
            "phase": self.phase.value,
            "current_turn": self._current_turn,
            "current_agenda_item": self._current_agenda_item,
            "agenda_total": len(self.agenda),
            "action_items_count": len(self._action_items),
            "decisions_count": len(self._decisions),
            "participant_count": len(self._participant_agents),
        }

    def get_action_items(self) -> List[Dict[str, Any]]:
        """获取行动项"""
        return self._action_items.copy()

    def get_decisions(self) -> List[str]:
        """获取决策列表"""
        return self._decisions.copy()

    def switch_phase(self, new_phase: MeetingPhase) -> bool:
        """
        切换会议阶段

        Args:
            new_phase: 目标阶段

        Returns:
            是否成功切换
        """
        if not self.is_running():
            return False

        old_phase = self.phase
        self.phase = new_phase

        logger.info(f"会议阶段切换：{old_phase.value} -> {new_phase.value}")

        # 通知主持人 Agent
        if self._manager_agent:
            self._manager_agent.set_current_phase(new_phase.value)

        return True

    def _is_ready(self) -> bool:
        """检查场景是否就绪"""
        return (
            self.state == SceneState.INITIALIZED
            and self._manager_agent is not None
            and len(self._participant_agents) > 0
        )

    def _generate_opening(self) -> str:
        """生成开场白"""
        if self._manager_agent:
            return self._manager_agent.generate_opening(
                meeting_type=self.meeting_type,
                project_name=self.project_name,
                agenda=self.agenda,
            )

        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }

        meeting_name = type_names.get(self.meeting_type, "项目会议")

        return (
            f"大家好，现在开始我们的{meeting_name}。\n\n"
            f"项目名称：{self.project_name}\n\n"
            f"今天会议的议程包括：\n"
        ) + "\n".join([f"- {item}" for item in self.agenda]) + (
            f"\n\n"
            f"预计会议时长：{self.config.duration_minutes}分钟\n\n"
            f"让我们正式开始今天的会议。"
        )

    def _get_participant_roles(self) -> List[Dict[str, str]]:
        """
        获取参与者角色列表

        Returns:
            角色列表
        """
        roles = {
            MeetingType.REQUIREMENT_REVIEW: [
                {"name": "产品经理", "role": "product_manager"},
                {"name": "技术负责人", "role": "tech_lead"},
                {"name": "开发工程师", "role": "developer"},
                {"name": "测试工程师", "role": "qa_engineer"},
            ],
            MeetingType.STANDUP: [
                {"name": "开发工程师 A", "role": "developer"},
                {"name": "开发工程师 B", "role": "developer"},
                {"name": "测试工程师", "role": "qa_engineer"},
                {"name": "产品经理", "role": "product_manager"},
            ],
            MeetingType.CONFLICT_RESOLUTION: [
                {"name": "调解人", "role": "mediator"},
                {"name": "当事方 A", "role": "party_a"},
                {"name": "当事方 B", "role": "party_b"},
                {"name": "观察员", "role": "observer"},
            ],
            MeetingType.PROJECT_KICKOFF: [
                {"name": "项目经理", "role": "project_manager"},
                {"name": "产品负责人", "role": "product_owner"},
                {"name": "技术负责人", "role": "tech_lead"},
                {"name": "团队代表", "role": "team_rep"},
            ],
            MeetingType.RETROSPECTIVE: [
                {"name": "敏捷教练", "role": "scrum_master"},
                {"name": "产品负责人", "role": "product_owner"},
                {"name": "团队成员 A", "role": "team_member"},
                {"name": "团队成员 B", "role": "team_member"},
            ],
        }

        return roles.get(
            self.meeting_type,
            [
                {"name": "参与者 A", "role": "participant"},
                {"name": "参与者 B", "role": "participant"},
            ],
        )

    def _check_phase_transition(self) -> None:
        """检查是否需要进行阶段转换"""
        settings = self.config.settings

        if self.phase == MeetingPhase.OPENING:
            if self._current_turn >= settings.get("opening_turns", 1):
                self.switch_phase(MeetingPhase.ROUND_TABLE)

        elif self.phase == MeetingPhase.ROUND_TABLE:
            if self._current_turn >= settings.get("round_table_turns", 4):
                self.switch_phase(MeetingPhase.DISCUSSION)

        elif self.phase == MeetingPhase.DISCUSSION:
            if self._current_turn >= settings.get("discussion_turns", 8):
                self.switch_phase(MeetingPhase.SUMMARY)

        elif self.phase == MeetingPhase.SUMMARY:
            if self._current_turn >= settings.get("summary_turns", 2):
                self.switch_phase(MeetingPhase.ACTION_ITEMS)

        elif self.phase == MeetingPhase.ACTION_ITEMS:
            if self._current_turn >= settings.get("action_item_turns", 2):
                self.switch_phase(MeetingPhase.CLOSING)

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
            MeetingPhase.OPENING: self._handle_opening,
            MeetingPhase.ROUND_TABLE: self._handle_round_table,
            MeetingPhase.DISCUSSION: self._handle_discussion,
            MeetingPhase.SUMMARY: self._handle_summary,
            MeetingPhase.ACTION_ITEMS: self._handle_action_items,
            MeetingPhase.CLOSING: self._handle_closing,
        }

        handler = handlers.get(self.phase, self._handle_discussion)
        return handler(message, context)

    def _handle_opening(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理开场阶段"""
        if not self._manager_agent:
            return self._create_error_message("主持人未初始化")

        response = self._manager_agent.respond(
            user_message=message.content,
            context=context,
            phase="opening",
        )

        return Message(
            content=response,
            role="manager",
            type=MessageType.AGENT,
            metadata={"phase": "opening"},
        )

    def _handle_round_table(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理轮流发言阶段"""
        if not self._participant_agents:
            return self._create_error_message("没有参与者")

        # 轮流让参与者发言
        speaker_idx = self._current_turn % len(self._participant_agents)
        speaker = self._participant_agents[speaker_idx]

        response = speaker.respond(
            user_message=message.content,
            context=context,
            phase="round_table",
            agenda_item=self.agenda[self._current_agenda_item] if self._current_agenda_item < len(self.agenda) else "讨论",
        )

        return Message(
            content=response,
            role=speaker.name,
            type=MessageType.AGENT,
            metadata={
                "phase": "round_table",
                "speaker_idx": speaker_idx,
            },
        )

    def _handle_discussion(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理自由讨论阶段"""
        # 根据上下文决定谁回应
        if self._participant_agents:
            # 选择一个参与者回应
            speaker_idx = (self._current_turn + 1) % len(self._participant_agents)
            speaker = self._participant_agents[speaker_idx]

            response = speaker.respond(
                user_message=message.content,
                context=context,
                phase="discussion",
                agenda_item=self.agenda[self._current_agenda_item] if self._current_agenda_item < len(self.agenda) else "自由讨论",
            )

            return Message(
                content=response,
                role=speaker.name,
                type=MessageType.AGENT,
                metadata={"phase": "discussion"},
            )

        return self._handle_summary(message, context)

    def _handle_summary(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理总结阶段"""
        if not self._manager_agent:
            return self._create_error_message("主持人未初始化")

        response = self._manager_agent.respond(
            user_message=message.content,
            context=context,
            phase="summary",
            key_points=self._key_points,
            decisions=self._decisions,
        )

        return Message(
            content=response,
            role="manager",
            type=MessageType.AGENT,
            metadata={"phase": "summary"},
        )

    def _handle_action_items(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理行动项阶段"""
        if not self._manager_agent:
            return self._create_error_message("主持人未初始化")

        response = self._manager_agent.respond(
            user_message=message.content,
            context=context,
            phase="action_items",
            action_items=self._action_items,
        )

        # 记录新的行动项
        new_action_item = {
            "content": "根据讨论确定的行动项",
            "owner": "待分配",
            "deadline": "待定",
            "status": "pending",
        }
        self._action_items.append(new_action_item)

        return Message(
            content=response,
            role="manager",
            type=MessageType.AGENT,
            metadata={"phase": "action_items"},
        )

    def _handle_closing(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理结束阶段"""
        if not self._manager_agent:
            return self._create_error_message("主持人未初始化")

        response = self._manager_agent.generate_closing(
            meeting_type=self.meeting_type,
            action_items=self._action_items,
            decisions=self._decisions,
        )

        # 标记场景即将完成
        self.state = SceneState.COMPLETED

        return Message(
            content=response,
            role="manager",
            type=MessageType.AGENT,
            metadata={"phase": "closing"},
        )

    def add_action_item(
        self,
        content: str,
        owner: str = "待分配",
        deadline: str = "待定",
    ) -> None:
        """
        添加行动项

        Args:
            content: 行动项内容
            owner: 负责人
            deadline: 截止日期
        """
        self._action_items.append({
            "content": content,
            "owner": owner,
            "deadline": deadline,
            "status": "pending",
        })

    def add_decision(self, decision: str) -> None:
        """
        添加决策

        Args:
            decision: 决策内容
        """
        self._decisions.append(decision)

    def add_key_point(self, point: str) -> None:
        """
        添加关键点

        Args:
            point: 关键点内容
        """
        self._key_points.append(point)

    def cleanup(self) -> None:
        """清理场景资源"""
        super().cleanup()
        self._action_items.clear()
        self._decisions.clear()
        self._key_points.clear()
        self._current_turn = 0
        self._current_agenda_item = 0
        self.phase = MeetingPhase.OPENING
