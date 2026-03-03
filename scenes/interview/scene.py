"""
Interview Scene Implementation - 面试场景实现

实现完整的面试流程，包括开场、技术问答、压力测试和结束阶段。
支持多种面试风格和领域配置。

面试流程:
1. Opening: 开场白和自我介绍
2. Technical: 技术问题问答
3. Behavioral: 行为面试问题
4. Pressure: 压力测试（可选）
5. Closing: 总结和结束
"""

import logging
import random
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType
from scenes.base import BaseScene, SceneConfig, SceneState, SceneError

from .interviewer import EnhancedInterviewerAgent, QuestionBank, DomainType

logger = logging.getLogger(__name__)


class InterviewStyle(Enum):
    """
    面试风格枚举

    定义面试官的行为风格和语调
    """
    FRIENDLY = "friendly"     # 友好鼓励型
    STRICT = "strict"         # 严格专业型
    PRESSURE = "pressure"     # 压力测试型


class InterviewPhase(Enum):
    """
    面试阶段枚举

    定义面试流程的各个阶段
    """
    OPENING = "opening"           # 开场阶段
    TECHNICAL = "technical"       # 技术问答
    BEHAVIORAL = "behavioral"     # 行为面试
    PRESSURE = "pressure"         # 压力测试
    CLOSING = "closing"           # 结束阶段


class InterviewScene(BaseScene):
    """
    面试场景实现

    提供完整的面试流程管理，包括：
    - 多阶段面试流程控制
    - 基于领域的智能问题选择
    - 面试风格适配
    - 候选人表现跟踪

    Attributes:
        style: 面试风格
        domain: 面试领域
        phase: 当前面试阶段
        question_bank: 问题库实例
        interviewer: 面试官 Agent
    """

    def __init__(
        self,
        config: Optional[SceneConfig] = None,
        global_config: Optional[Config] = None,
        style: str = "friendly",
        domain: str = "tech",
    ):
        """
        初始化面试场景

        Args:
            config: 场景配置
            global_config: 全局配置
            style: 面试风格 (friendly/strict/pressure)
            domain: 面试领域 (tech/frontend/backend/system_design/hr)
        """
        super().__init__(config, global_config)

        # 面试特定配置
        self.style = InterviewStyle(style.lower()) if isinstance(style, str) else style
        self.domain = DomainType(domain.lower()) if isinstance(domain, str) else domain

        # 面试状态
        self.phase = InterviewPhase.OPENING
        self._question_count = 0
        self._candidate_answers: List[Dict[str, Any]] = []
        self._key_points: List[str] = []

        # 组件初始化
        self.question_bank: Optional[QuestionBank] = None
        self.interviewer: Optional[EnhancedInterviewerAgent] = None

        # 更新配置
        if self.config:
            self.config.scene_type = "interview"
            self.config.name = self._get_scene_name()
            self.config.description = self._get_scene_description()

    def get_scene_type(self) -> str:
        """获取场景类型标识符"""
        return "interview"

    def get_description(self) -> str:
        """获取场景描述"""
        style_names = {
            InterviewStyle.FRIENDLY: "友好型",
            InterviewStyle.STRICT: "严格型",
            InterviewStyle.PRESSURE: "压力型",
        }
        domain_names = {
            DomainType.TECH: "技术",
            DomainType.FRONTEND: "前端",
            DomainType.BACKEND: "后端",
            DomainType.SYSTEM_DESIGN: "系统设计",
            DomainType.HR: "HR",
        }

        style_name = style_names.get(self.style, "专业")
        domain_name = domain_names.get(self.domain, "综合")

        return f"{style_name}{domain_name}面试场景"

    def initialize(self) -> bool:
        """
        初始化面试场景

        创建面试官 Agent 和问题库

        Returns:
            初始化是否成功
        """
        try:
            logger.info(f"初始化面试场景：style={self.style.value}, domain={self.domain.value}")

            # 加载问题库
            self.question_bank = QuestionBank()
            questions_path = Path(__file__).parent / "questions.yaml"

            if questions_path.exists():
                self.question_bank.load_from_yaml(questions_path)
            else:
                logger.warning(f"问题库文件不存在：{questions_path}，使用默认问题")
                self.question_bank.load_default_questions()

            # 创建增强的面试官 Agent
            self.interviewer = EnhancedInterviewerAgent(
                name=self._get_interviewer_name(),
                config=self.global_config,
                style=self.style.value,
                domain=self.domain.value,
                question_bank=self.question_bank,
            )

            # 初始化面试官
            self.interviewer.initialize()

            # 注册 Agent
            self.register_agent("interviewer", self.interviewer)

            # 设置场景元数据
            self.set_metadata("style", self.style.value)
            self.set_metadata("domain", self.domain.value)
            self.set_metadata("max_questions", self.config.settings.get("max_questions", 10))

            self.state = SceneState.INITIALIZED
            logger.info("面试场景初始化成功")
            return True

        except Exception as e:
            logger.error(f"面试场景初始化失败：{e}")
            self.state = SceneState.ERROR
            return False

    def handle_message(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """
        处理用户消息

        根据当前面试阶段和消息内容生成适当的响应

        Args:
            message: 用户输入消息
            context: 对话上下文

        Returns:
            Agent 响应消息
        """
        if not self.interviewer:
            return self._create_error_message("面试官未初始化")

        # 记录候选人回答
        self._record_answer(message)

        # 检查面试是否应该结束
        if self._should_end_interview():
            self.phase = InterviewPhase.CLOSING
            return self._handle_closing(message, context)

        # 根据阶段处理消息
        if self.phase == InterviewPhase.OPENING:
            response = self._handle_opening(message, context)
        elif self.phase == InterviewPhase.TECHNICAL:
            response = self._handle_technical(message, context)
        elif self.phase == InterviewPhase.BEHAVIORAL:
            response = self._handle_behavioral(message, context)
        elif self.phase == InterviewPhase.PRESSURE:
            response = self._handle_pressure(message, context)
        else:
            response = self._handle_closing(message, context)

        # 更新上下文
        context.add_message(message)
        context.add_message(response)

        return response

    def get_agents(self) -> List[BaseAgent]:
        """获取场景中的所有 Agent"""
        agents = []
        if self.interviewer:
            agents.append(self.interviewer)
        return agents

    def start(self) -> Message:
        """启动面试场景"""
        if self.state != SceneState.INITIALIZED:
            return self._create_error_message("场景未初始化")

        self.state = SceneState.RUNNING
        self.phase = InterviewPhase.OPENING

        # 获取开场白
        opening_message = self.interviewer.get_opening_message() if self.interviewer else self._get_opening_message()

        return Message(
            content=opening_message,
            role="interviewer",
            type=MessageType.AGENT,
            metadata={
                "phase": self.phase.value,
                "style": self.style.value,
                "domain": self.domain.value,
            },
        )

    def get_current_phase(self) -> InterviewPhase:
        """获取当前面试阶段"""
        return self.phase

    def get_interview_stats(self) -> Dict[str, Any]:
        """
        获取面试统计信息

        Returns:
            统计信息字典
        """
        return {
            "phase": self.phase.value,
            "question_count": self._question_count,
            "answer_count": len(self._candidate_answers),
            "key_points": len(self._key_points),
            "style": self.style.value,
            "domain": self.domain.value,
        }

    def _get_scene_name(self) -> str:
        """获取场景名称"""
        style_prefixes = {
            InterviewStyle.FRIENDLY: "轻松",
            InterviewStyle.STRICT: "专业",
            InterviewStyle.PRESSURE: "压力",
        }
        prefix = style_prefixes.get(self.style, "")
        return f"{prefix}面试场景"

    def _get_scene_description(self) -> str:
        """获取场景描述"""
        return f"模拟{self.style.value}风格的{self.domain.value}领域面试"

    def _get_interviewer_name(self) -> str:
        """获取面试官名称"""
        names = {
            InterviewStyle.FRIENDLY: "张面试官",
            InterviewStyle.STRICT: "李面试官",
            InterviewStyle.PRESSURE: "王面试官",
        }
        return names.get(self.style, "面试官")

    def _handle_opening(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理开场阶段"""
        # 开场阶段结束后进入技术问答
        self.phase = InterviewPhase.TECHNICAL

        if not self.interviewer:
            return self._create_error_message("面试官未初始化")

        # 生成第一个技术问题
        question = self.interviewer.generate_question(
            phase="technical",
            difficulty=2,  # 从简单开始
        )

        return Message(
            content=question,
            role="interviewer",
            type=MessageType.AGENT,
            metadata={"phase": "technical"},
        )

    def _handle_technical(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理技术问答阶段"""
        if not self.interviewer:
            return self._create_error_message("面试官未初始化")

        self._question_count += 1

        # 评估回答质量以决定下一步
        answer_quality = self._evaluate_answer_quality(message.content)

        # 生成追问或新问题
        if answer_quality >= 0.7:
            # 回答良好，增加难度或换话题
            next_difficulty = min(5, 2 + self._question_count // 2)
            question = self.interviewer.generate_question(
                phase="technical",
                difficulty=next_difficulty,
            )
        else:
            # 回答一般，生成引导性追问
            question = self.interviewer.generate_follow_up(
                message.content,
                context.get_history(),
            )

        # 检查是否应该进入下一阶段
        if self._question_count >= self.config.settings.get("technical_questions", 5):
            self.phase = InterviewPhase.BEHAVIORAL
            question = self.interviewer.generate_question(phase="behavioral")

        return Message(
            content=question,
            role="interviewer",
            type=MessageType.AGENT,
            metadata={"phase": "technical"},
        )

    def _handle_behavioral(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理行为面试阶段"""
        if not self.interviewer:
            return self._create_error_message("面试官未初始化")

        self._question_count += 1

        # 生成行为面试问题
        question = self.interviewer.generate_question(phase="behavioral")

        # 检查是否进入压力测试（仅压力风格）
        if self.style == InterviewStyle.PRESSURE:
            if self._question_count >= self.config.settings.get("behavioral_questions", 3):
                self.phase = InterviewPhase.PRESSURE
                question = self.interviewer.generate_question(phase="pressure")
        else:
            # 非压力风格直接进入结束
            if self._question_count >= self.config.settings.get("behavioral_questions", 3):
                self.phase = InterviewPhase.CLOSING

        return Message(
            content=question,
            role="interviewer",
            type=MessageType.AGENT,
            metadata={"phase": self.phase.value},
        )

    def _handle_pressure(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理压力测试阶段"""
        if not self.interviewer:
            return self._create_error_message("面试官未初始化")

        self._question_count += 1

        # 生成压力测试问题
        question = self.interviewer.generate_question(
            phase="pressure",
            follow_up_context=message.content,
        )

        # 压力测试后进入结束
        if self._question_count >= self.config.settings.get("pressure_questions", 2):
            self.phase = InterviewPhase.CLOSING

        return Message(
            content=question,
            role="interviewer",
            type=MessageType.AGENT,
            metadata={"phase": self.phase.value},
        )

    def _handle_closing(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        """处理结束阶段"""
        if not self.interviewer:
            return self._create_error_message("面试官未初始化")

        closing_message = self.interviewer.get_closing_message()

        return Message(
            content=closing_message,
            role="interviewer",
            type=MessageType.AGENT,
            metadata={"phase": "closing"},
        )

    def _record_answer(self, message: Message) -> None:
        """记录候选人回答"""
        self._candidate_answers.append({
            "content": message.content,
            "phase": self.phase.value,
            "timestamp": message.timestamp,
        })

        # 提取关键点（简单实现）
        if len(message.content) > 50:
            self._key_points.append(message.content[:100])

    def _evaluate_answer_quality(self, content: str) -> float:
        """
        简单评估回答质量

        Args:
            content: 回答内容

        Returns:
            质量分数 0-1
        """
        # 简单实现：基于长度和关键词
        score = 0.5

        # 长度评分
        if len(content) > 200:
            score += 0.2
        elif len(content) < 50:
            score -= 0.2

        # 关键词评分
        keywords = ["因为", "所以", "首先", "然后", "最后", "例如", "比如"]
        for kw in keywords:
            if kw in content:
                score += 0.05

        return min(1.0, max(0.0, score))

    def _should_end_interview(self) -> bool:
        """检查面试是否应该结束"""
        max_turns = self.config.settings.get("max_questions", 10)
        return self._question_count >= max_turns

    def cleanup(self) -> None:
        """清理场景资源"""
        super().cleanup()
        self._candidate_answers.clear()
        self._key_points.clear()
        self._question_count = 0
        self.phase = InterviewPhase.OPENING
