"""
Salon Audience Agent - 沙龙观众 Agent

负责参与互动和提问，包括：
- 提出有深度的问题
- 分享自己的观点和经验
- 与其他观众互动讨论
- 给予演讲者积极反馈

观众是沙龙活跃氛围的重要角色，代表不同背景和视角的参与者。
"""

import logging
import random
from typing import Any, Dict, List, Optional

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

logger = logging.getLogger(__name__)


class SalonAudienceAgent(BaseAgent):
    """
    沙龙观众 Agent

    职责:
    - 提出有深度的问题
    - 分享自己的观点和经验
    - 与其他观众互动讨论
    - 给予演讲者积极反馈

    Attributes:
        audience_id: 观众 ID
        topic: 沙龙主题
        engagement_level: 参与程度 (quiet/active/very_active)
        question_style: 提问风格 (technical/practical/conceptual)
        background: 背景 (student/practitioner/manager/researcher)
    """

    def __init__(
        self,
        name: str = "观众",
        config: Optional[Config] = None,
        audience_id: int = 0,
        topic: str = "技术前沿探索",
        engagement_level: str = "active",
        question_style: str = "thoughtful",
        background: str = "practitioner",
        **kwargs,
    ):
        """
        初始化观众 Agent

        Args:
            name: Agent 名称
            config: 全局配置
            audience_id: 观众 ID
            topic: 沙龙主题
            engagement_level: 参与程度
            question_style: 提问风格
            background: 背景
            **kwargs: 其他参数
        """
        super().__init__(name=name, config=config, **kwargs)

        self.audience_id = audience_id
        self.topic = topic
        self.engagement_level = engagement_level
        self.question_style = question_style
        self.background = background
        self.current_phase = "opening"
        self._turn_count = 0
        self._questions_asked: List[str] = []
        self._comments_made: List[str] = []

        # 根据背景设置不同的特征
        self._background_traits = self._init_background_traits()

    def _init_background_traits(self) -> Dict[str, Any]:
        """
        初始化背景特征

        Returns:
            背景特征字典
        """
        traits = {
            "student": {
                "curiosity": "high",
                "experience": "limited",
                "focus": "learning",
                "question_types": ["conceptual", "career", "learning_path"],
            },
            "practitioner": {
                "curiosity": "medium",
                "experience": "moderate",
                "focus": "practical_application",
                "question_types": ["technical", "best_practices", "challenges"],
            },
            "manager": {
                "curiosity": "medium",
                "experience": "varied",
                "focus": "team_impact",
                "question_types": ["roi", "team_adoption", "strategy"],
            },
            "researcher": {
                "curiosity": "very_high",
                "experience": "deep",
                "focus": "innovation",
                "question_types": ["cutting_edge", "methodology", "future_directions"],
            },
        }

        return traits.get(
            self.background,
            traits["practitioner"],
        )

    def initialize(self) -> bool:
        """
        初始化 Agent

        Returns:
            初始化是否成功
        """
        try:
            logger.info(
                f"初始化观众 Agent: id={self.audience_id}, "
                f"background={self.background}, style={self.question_style}"
            )

            # 构建系统提示词
            self.system_prompt = self._build_system_prompt()

            # 调用父类初始化
            if hasattr(super(), 'initialize') and callable(super().initialize):
                super().initialize()

            self._initialized = True
            logger.info("观众 Agent 初始化成功")
            return True

        except Exception as e:
            logger.error(f"观众 Agent 初始化失败：{e}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词字符串
        """
        engagement_prompts = {
            "quiet": "你比较内向，发言较少但每次发言都经过深思熟虑。",
            "active": "你积极参与讨论，会主动提问和分享观点。",
            "very_active": "你非常活跃，经常发言并引导讨论方向。",
        }

        engagement_prompt = engagement_prompts.get(
            self.engagement_level,
            "你适度参与讨论。",
        )

        background_prompts = {
            "student": "你是一名正在学习的学生，对行业充满好奇，希望从分享中学到知识。",
            "practitioner": "你是一名一线从业者，有丰富的实践经验，关注技术的实际应用。",
            "manager": "你是一名技术管理者，关注技术对团队和业务的影响。",
            "researcher": "你是一名研究人员，关注前沿技术和创新方向。",
        }

        background_prompt = background_prompts.get(
            self.background,
            "你是一名对技术有热情的参与者。",
        )

        return f"""你是一名参加技术沙龙的观众，沙龙主题是"{self.topic}"。

{background_prompt}
{engagement_prompt}

你的职责包括:
1. 提出有深度的问题
2. 分享自己的观点和经验
3. 与其他观众互动讨论
4. 给予演讲者积极反馈

注意事项:
- 积极但不抢话
- 提问有针对性和深度
- 尊重他人观点
- 乐于分享和学习
- 根据自己的背景提出符合身份的问题"""

    def respond(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        phase: str = "discussion",
        **kwargs,
    ) -> str:
        """
        生成响应

        Args:
            user_message: 用户消息
            context: 对话上下文
            phase: 当前阶段
            **kwargs: 其他参数

        Returns:
            响应文本
        """
        self._turn_count += 1
        self.current_phase = phase

        # 根据参与程度决定是否回应
        if not self._should_respond():
            return ""

        # 根据阶段生成不同的响应
        if phase == "presentation":
            return self._respond_presentation(user_message, context)
        elif phase == "q_and_a":
            return self._respond_q_and_a(user_message, context)
        elif phase == "discussion":
            return self._respond_discussion(user_message, context)
        else:
            return self._respond_default(user_message)

    def _should_respond(self) -> bool:
        """
        判断是否应该回应

        Returns:
            是否回应
        """
        engagement_probs = {
            "quiet": 0.3,
            "active": 0.7,
            "very_active": 0.9,
        }

        prob = engagement_probs.get(self.engagement_level, 0.5)
        return random.random() < prob

    def generate_question(
        self,
        context_topic: str,
        previous_content: str = "",
    ) -> str:
        """
        生成问题

        Args:
            context_topic: 上下文主题
            previous_content: 之前的内容

        Returns:
            问题文本
        """
        question_templates = self._get_question_templates()

        # 根据提问风格选择模板
        style_questions = {
            "technical": [
                f"关于{context_topic}，我想请教一个技术细节...",
                "这个方案在性能方面有什么考虑吗？",
                "如何处理边界情况和异常？",
            ],
            "practical": [
                f"在实际项目中应用{context_topic}时，有什么需要注意的？",
                "这个方法的落地成本高吗？",
                "有没有可以分享的成功案例？",
            ],
            "conceptual": [
                f"{context_topic}的核心理念是什么？",
                "这个概念和传统方法有什么本质区别？",
                "如何理解这个理论框架？",
            ],
            "thoughtful": [
                f"我注意到您提到了{context_topic}，这让我想到...",
                "从另一个角度看，这个问题是否还有其他的解决方案？",
                "这个方法的局限性在哪里？",
            ],
        }

        questions = style_questions.get(
            self.question_style,
            style_questions["thoughtful"],
        )

        question = random.choice(questions)

        # 记录问题
        self._questions_asked.append(question)

        return question

    def generate_comment(
        self,
        topic: str,
        previous_speaker: str = "",
    ) -> str:
        """
        生成评论/观点

        Args:
            topic: 话题
            previous_speaker: 前一个发言者

        Returns:
            评论文本
        """
        comment_templates = [
            f"我同意刚才的观点，补充一点我的经验...",
            "这个话题我也很有感触，分享一下我的经历...",
            "从我的角度来看，这个问题还可以这样理解...",
            "我之前也遇到过类似的情况，当时我是这样处理的...",
        ]

        comment = random.choice(comment_templates)

        # 根据背景添加特定内容
        if self.background == "practitioner":
            comment += "\n\n在我们团队的实际项目中..."
        elif self.background == "manager":
            comment += "\n\n从团队管理的角度来看..."
        elif self.background == "student":
            comment += "\n\n作为学习者，我的理解是..."
        elif self.background == "researcher":
            comment += "\n\n从研究的角度，最近有一些新的发现..."

        # 记录评论
        self._comments_made.append(comment)

        return comment

    def _get_question_templates(self) -> List[str]:
        """
        获取问题模板

        Returns:
            问题模板列表
        """
        question_types = self._background_traits.get("question_types", [])

        templates = []

        for qtype in question_types:
            if qtype == "technical":
                templates.extend([
                    "这个技术的性能瓶颈在哪里？",
                    "如何保证系统的可扩展性？",
                    "有没有遇到并发处理的问题？",
                ])
            elif qtype == "practical":
                templates.extend([
                    "在实际应用中最大的挑战是什么？",
                    "如何说服团队采用这个方案？",
                    "落地周期大概需要多久？",
                ])
            elif qtype == "conceptual":
                templates.extend([
                    "这个概念的本质是什么？",
                    "和传统方法的核心区别在哪？",
                    "理论基础是什么？",
                ])
            elif qtype == "career":
                templates.extend([
                    "想请教一下职业发展方面的建议...",
                    "如何在这个领域持续成长？",
                    "需要重点培养哪些能力？",
                ])

        return templates if templates else ["我有一个问题..."]

    def _respond_presentation(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应分享阶段"""
        # 观众在分享阶段主要是倾听，偶尔提问
        if random.random() > 0.3:
            return ""  # 不回应

        return (
            "刚才提到的内容很有启发，我记一下笔记。\n\n"
            "期待后面的详细讲解！"
        )

    def _respond_q_and_a(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应问答阶段"""
        # 生成一个问题
        question = self.generate_question(self.topic)

        return (
            f"谢谢演讲嘉宾的分享！{question}\n\n"
            "希望能得到您的指点。"
        )

    def _respond_discussion(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应讨论阶段"""
        # 生成一个评论
        comment = self.generate_comment(self.topic)

        return comment

    def _respond_default(self, user_message: str) -> str:
        """默认回应"""
        return (
            "感谢分享！\n\n"
            "我学习到了很多。"
        )

    def set_current_phase(self, phase: str) -> None:
        """设置当前阶段"""
        self.current_phase = phase

    def get_questions_asked(self) -> List[str]:
        """获取已提的问题"""
        return self._questions_asked.copy()

    def get_comments_made(self) -> List[str]:
        """获取已发表的评论"""
        return self._comments_made.copy()

    def get_turn_count(self) -> int:
        """获取发言次数"""
        return self._turn_count

    def reset(self) -> None:
        """重置状态"""
        self._turn_count = 0
        self._questions_asked.clear()
        self._comments_made.clear()
        self.current_phase = "opening"
