"""
Meeting Manager Agent - 会议主持人 Agent

负责会议的整体把控，包括：
- 会议开场和议程介绍
- 控制会议节奏和时间
- 引导讨论方向
- 总结会议要点
- 确定行动项

主持人是会议的核心角色，需要确保会议高效进行并达成目标。
"""

import logging
from typing import Any, Dict, List, Optional

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

# 延迟导入避免循环依赖
logger = logging.getLogger(__name__)


class MeetingManagerAgent(BaseAgent):
    """
    会议主持人 Agent

    职责:
    - 开场介绍会议议程和目标
    - 控制会议节奏和时间
    - 引导讨论方向，确保不偏离议程
    - 总结会议要点和决策
    - 确定行动项和负责人

    Attributes:
        meeting_type: 会议类型
        project_name: 项目名称
        agenda: 会议议程
        current_phase: 当前阶段
    """

    def __init__(
        self,
        name: str = "会议主持人",
        config: Optional[Config] = None,
        meeting_type: Any = None,
        project_name: str = "项目 A",
        agenda: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        初始化会议主持人 Agent

        Args:
            name: Agent 名称
            config: 全局配置
            meeting_type: 会议类型
            project_name: 项目名称
            agenda: 会议议程列表
            **kwargs: 其他参数
        """
        super().__init__(name=name, config=config, **kwargs)

        # 延迟导入 MeetingType 避免循环依赖
        from .scene import MeetingType

        self.meeting_type = meeting_type
        self.project_name = project_name
        self.agenda = agenda or ["讨论议题"]
        self.current_phase = "opening"
        self._turn_count = 0
        self._key_points: List[str] = []
        self._decisions: List[str] = []
        self._action_items: List[Dict[str, Any]] = []

    def initialize(self) -> bool:
        """
        初始化 Agent

        Returns:
            初始化是否成功
        """
        try:
            logger.info(
                f"初始化会议主持人 Agent: type={self.meeting_type}, "
                f"project={self.project_name}"
            )

            # 构建系统提示词
            self.system_prompt = self._build_system_prompt()

            # 调用父类初始化
            if hasattr(super(), 'initialize') and callable(super().initialize):
                super().initialize()

            self._initialized = True
            logger.info("会议主持人 Agent 初始化成功")
            return True

        except Exception as e:
            logger.error(f"会议主持人 Agent 初始化失败：{e}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词字符串
        """
        # 延迟导入 MeetingType
        from .scene import MeetingType

        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }

        meeting_name = type_names.get(
            self.meeting_type,
            "项目会议",
        ) if hasattr(self.meeting_type, 'value') else "项目会议"

        type_specific_instructions = {
            MeetingType.REQUIREMENT_REVIEW: (
                "- 确保每个需求点都被充分讨论\n"
                "- 识别潜在的技术风险和实现难点\n"
                "- 确认需求的优先级和排期\n"
            ),
            MeetingType.STANDUP: (
                "- 控制每人发言时间在 2 分钟内\n"
                "- 重点关注阻塞问题和需要协调的事项\n"
                "- 快速同步，不展开深入讨论\n"
            ),
            MeetingType.CONFLICT_RESOLUTION: (
                "- 保持中立，让各方充分表达观点\n"
                "- 寻找共同点，引导达成共识\n"
                "- 聚焦问题本身，避免人身攻击\n"
            ),
            MeetingType.PROJECT_KICKOFF: (
                "- 确保项目目标和范围清晰\n"
                "- 明确团队分工和职责\n"
                "- 确认关键里程碑和时间节点\n"
            ),
            MeetingType.RETROSPECTIVE: (
                "- 营造开放、安全的氛围\n"
                "- 鼓励坦诚反馈，对事不对人\n"
                "- 聚焦可执行的改进措施\n"
            ),
        }

        specific_instruction = type_specific_instructions.get(
            self.meeting_type,
            "- 确保会议高效进行\n"
            "- 引导讨论达成预期目标\n",
        ) if hasattr(self.meeting_type, 'value') else "- 确保会议高效进行\n"

        return f"""你是一名专业的会议主持人，正在主持一场{meeting_name}。
项目名称：{self.project_name}

你的职责包括:
1. 开场介绍会议议程和目标
2. 控制会议节奏和时间
3. 引导讨论方向，确保不偏离议程
4. 总结会议要点和决策
5. 确定行动项和负责人
6. 营造高效、积极的会议氛围

{specific_instruction}
注意事项:
- 时间意识强，避免会议超时
- 善于总结，确保信息对齐
- 平衡发言机会，避免少数人垄断
- 聚焦行动，确保会议有产出
- 保持中立客观的立场"""

    def respond(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        phase: str = "opening",
        key_points: Optional[List[str]] = None,
        decisions: Optional[List[str]] = None,
        action_items: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        """
        生成响应

        Args:
            user_message: 用户消息
            context: 对话上下文
            phase: 当前阶段
            key_points: 关键点列表
            decisions: 决策列表
            action_items: 行动项列表
            **kwargs: 其他参数

        Returns:
            响应文本
        """
        self._turn_count += 1
        self.current_phase = phase

        # 更新记录
        if key_points:
            self._key_points.extend(key_points)
        if decisions:
            self._decisions.extend(decisions)
        if action_items:
            self._action_items.extend(action_items)

        # 根据阶段生成不同的响应
        if phase == "opening":
            return self._respond_opening(user_message)
        elif phase == "round_table":
            return self._respond_round_table(user_message, context)
        elif phase == "discussion":
            return self._respond_discussion(user_message, context)
        elif phase == "summary":
            return self._respond_summary(user_message, context)
        elif phase == "action_items":
            return self._respond_action_items(user_message, context)
        elif phase == "closing":
            return self._respond_closing(user_message, context)
        else:
            return self._respond_default(user_message)

    def generate_opening(
        self,
        meeting_type: Any,
        project_name: str,
        agenda: List[str],
    ) -> str:
        """
        生成开场白

        Args:
            meeting_type: 会议类型
            project_name: 项目名称
            agenda: 会议议程

        Returns:
            开场白文本
        """
        # 延迟导入 MeetingType
        from .scene import MeetingType

        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }

        meeting_name = type_names.get(
            meeting_type,
            "项目会议",
        ) if hasattr(meeting_type, 'value') else "项目会议"

        agenda_str = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(agenda)])

        return (
            f"各位同事好，现在开始我们的{meeting_name}。\n\n"
            f"📋 项目名称：{project_name}\n\n"
            f"📌 今天会议的议程：\n"
            f"{agenda_str}\n\n"
            f"⏱️ 预计会议时长：30 分钟\n\n"
            f"希望各位能够：\n"
            f"- 聚焦议题，高效讨论\n"
            f"- 积极发言，充分交流\n"
            f"- 明确行动，确保落地\n\n"
            f"让我们正式开始今天的会议。"
        )

    def generate_closing(
        self,
        meeting_type: Any,
        action_items: Optional[List[Dict[str, Any]]] = None,
        decisions: Optional[List[str]] = None,
    ) -> str:
        """
        生成闭幕词

        Args:
            meeting_type: 会议类型
            action_items: 行动项列表
            decisions: 决策列表

        Returns:
            闭幕词文本
        """
        # 延迟导入 MeetingType
        from .scene import MeetingType

        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }

        meeting_name = type_names.get(
            meeting_type,
            "项目会议",
        ) if hasattr(meeting_type, 'value') else "项目会议"

        content = f"好的，今天的{meeting_name}即将结束。\n\n"

        # 总结决策
        all_decisions = decisions or self._decisions
        if all_decisions:
            content += "✅ 会议决策：\n"
            for i, decision in enumerate(all_decisions[-5:], 1):
                content += f"  {i}. {decision}\n"
            content += "\n"

        # 总结行动项
        all_items = action_items or self._action_items
        if all_items:
            content += "📝 行动项：\n"
            for item in all_items[-5:]:
                owner = item.get("owner", "待分配")
                deadline = item.get("deadline", "待定")
                content += f"  • {item.get('content', '')}\n"
                content += f"    负责人：{owner} | 截止：{deadline}\n"
            content += "\n"

        content += (
            "感谢各位的参与和贡献！\n\n"
            "会议纪要和行动项会后会整理发出，请各位及时关注。\n"
            "散会！"
        )

        return content

    def set_current_phase(self, phase: str) -> None:
        """
        设置当前阶段

        Args:
            phase: 阶段名称
        """
        self.current_phase = phase

    def _respond_opening(self, user_message: str) -> str:
        """回应开场阶段"""
        return (
            "感谢大家的准时参会。\n\n"
            "在开始正式议程之前，我想确认一下：\n"
            "- 各位是否都收到了会议材料？\n"
            "- 对议程有没有补充或调整？\n\n"
            "如果没有问题，我们就按照既定议程开始。"
        )

    def _respond_round_table(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应轮流发言阶段"""
        return (
            "好的，感谢分享。\n\n"
            "让我们继续听取下一位的发言。\n"
            "请按照顺序依次进行，每人控制在 2 分钟左右。"
        )

    def _respond_discussion(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应讨论阶段"""
        return (
            "这个观点很有价值，大家有什么看法？\n\n"
            "我们可以就这个问题深入讨论一下，\n"
            "但也请注意时间，我们还有其他议题需要覆盖。"
        )

    def _respond_summary(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应总结阶段"""
        content = "让我来总结一下今天会议的主要内容和结论。\n\n"

        if self._key_points:
            content += "📌 关键要点：\n"
            for point in self._key_points[-5:]:
                content += f"  • {point}\n"
            content += "\n"

        if self._decisions:
            content += "✅ 达成的决策：\n"
            for decision in self._decisions[-3:]:
                content += f"  • {decision}\n"
            content += "\n"

        content += "接下来我们确认一下行动项。"

        return content

    def _respond_action_items(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应行动项阶段"""
        return (
            "好的，我们来确认一下今天的行动项。\n\n"
            "请各位明确：\n"
            "- 要做什么（What）\n"
            "- 谁负责（Who）\n"
            "- 何时完成（When）\n\n"
            "我来记录一下大家确认的行动项..."
        )

    def _respond_closing(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应闭幕阶段"""
        return self.generate_closing(
            self.meeting_type,
            self._action_items,
            self._decisions,
        )

    def _respond_default(self, user_message: str) -> str:
        """默认回应"""
        return (
            "好的，我们继续会议议程。\n\n"
            "大家还有什么补充吗？"
        )

    def add_key_point(self, point: str) -> None:
        """添加关键点"""
        self._key_points.append(point)

    def add_decision(self, decision: str) -> None:
        """添加决策"""
        self._decisions.append(decision)

    def add_action_item(
        self,
        content: str,
        owner: str = "待分配",
        deadline: str = "待定",
    ) -> None:
        """添加行动项"""
        self._action_items.append({
            "content": content,
            "owner": owner,
            "deadline": deadline,
            "status": "pending",
        })

    def get_turn_count(self) -> int:
        """获取发言次数"""
        return self._turn_count

    def reset(self) -> None:
        """重置状态"""
        self._turn_count = 0
        self._key_points.clear()
        self._decisions.clear()
        self._action_items.clear()
        self.current_phase = "opening"

    def get_role(self) -> str:
        """获取角色描述"""
        from .scene import MeetingType

        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }

        meeting_name = type_names.get(
            self.meeting_type,
            "项目会议",
        ) if hasattr(self.meeting_type, 'value') else "项目会议"
        return f"{meeting_name}主持人，负责'{self.project_name}'项目的会议管理"
