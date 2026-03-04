"""
Salon Speaker Agent - 沙龙演讲者 Agent

负责主题分享和回答问题，包括：
- 主题内容呈现
- 知识点讲解
- 问题解答
- 案例分享

演讲者应该是某一领域的专家，能够深入浅出地讲解复杂概念。
"""

import logging
from typing import Any, Dict, List, Optional

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

logger = logging.getLogger(__name__)


class SalonSpeakerAgent(BaseAgent):
    """
    沙龙演讲者 Agent

    职责:
    - 分享专业知识和独到见解
    - 回答观众的提问
    - 用通俗易懂的方式解释复杂概念
    - 提供实际案例和经验分享

    Attributes:
        topic: 演讲主题
        main_topic: 沙龙主主题
        expertise_level: 专业水平
        presentation_style: 演讲风格
    """

    def __init__(
        self,
        name: str = "演讲嘉宾",
        config: Optional[Config] = None,
        topic: str = "AI 技术应用",
        main_topic: str = "技术前沿探索",
        expertise_level: str = "expert",
        presentation_style: str = "interactive",
        **kwargs,
    ):
        """
        初始化演讲者 Agent

        Args:
            name: Agent 名称
            config: 全局配置
            topic: 演讲主题
            main_topic: 沙龙主主题
            expertise_level: 专业水平 (beginner/intermediate/expert)
            presentation_style: 演讲风格 (interactive/lecture/storytelling)
            **kwargs: 其他参数
        """
        super().__init__(name=name, config=config, **kwargs)

        self.topic = topic
        self.main_topic = main_topic
        self.expertise_level = expertise_level
        self.presentation_style = presentation_style
        self.current_phase = "opening"
        self._turn_count = 0
        self._presented_points: List[str] = []
        self._questions_answered: List[Dict[str, Any]] = []

    def initialize(self) -> bool:
        """
        初始化 Agent

        Returns:
            初始化是否成功
        """
        try:
            logger.info(
                f"初始化演讲者 Agent: topic={self.topic}, "
                f"level={self.expertise_level}, style={self.presentation_style}"
            )

            # 构建系统提示词
            self.system_prompt = self._build_system_prompt()

            # 调用父类初始化
            if hasattr(super(), 'initialize') and callable(super().initialize):
                super().initialize()

            self._initialized = True
            logger.info("演讲者 Agent 初始化成功")
            return True

        except Exception as e:
            logger.error(f"演讲者 Agent 初始化失败：{e}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词字符串
        """
        level_prompts = {
            "beginner": "你的讲解应该通俗易懂，避免使用过多专业术语，多用类比和例子。",
            "intermediate": "你的讲解应该平衡专业性和可理解性，适当使用术语但要解释清楚。",
            "expert": "你的讲解应该专业深入，可以熟练使用专业术语，同时也能深入浅出。",
        }

        style_prompts = {
            "interactive": "你的风格应该是互动式的，经常提问并邀请听众思考。",
            "lecture": "你的风格应该是讲授式的，系统性地讲解知识点。",
            "storytelling": "你的风格应该是故事性的，通过案例和故事传达观点。",
        }

        level_prompt = level_prompts.get(
            self.expertise_level,
            "你的讲解应该专业且易于理解。",
        )

        style_prompt = style_prompts.get(
            self.presentation_style,
            "你的风格应该生动有趣。",
        )

        return f"""你是一位在"{self.topic}"领域有深厚造诣的专家，
正在一场关于"{self.main_topic}"的技术沙龙中进行主题分享。

你的职责包括:
1. 分享"{self.topic}"相关的专业知识和独到见解
2. 回答观众提出的问题
3. 用通俗易懂的方式解释复杂概念
4. 提供实际案例和实践经验分享
5. 引导听众思考和讨论

{level_prompt}
{style_prompt}

注意事项:
- 专业权威但不傲慢
- 善于用具体例子说明抽象概念
- 耐心解答疑问，鼓励追问
- 适时与听众互动，调动气氛
- 分享真实案例和个人经验"""

    def respond(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        phase: str = "presentation",
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

        # 根据阶段生成不同的响应
        if phase == "presentation":
            return self._respond_presentation(user_message, context)
        elif phase == "q_and_a":
            return self._respond_q_and_a(user_message, context, **kwargs)
        elif phase == "discussion":
            return self._respond_discussion(user_message, context)
        else:
            return self._respond_default(user_message)

    def generate_presentation(
        self,
        duration: int = 5,
        key_points: Optional[List[str]] = None,
    ) -> str:
        """
        生成主题演讲内容

        Args:
            duration: 预计时长（轮次）
            key_points: 关键点列表

        Returns:
            演讲内容文本
        """
        # 生成演讲大纲
        outline = self._generate_outline(key_points)

        content = (
            f"大家好！今天我很荣幸能在这里和大家分享关于 **{self.topic}** 的一些思考。\n\n"
            f"我今天的分享将围绕以下几个方面展开：\n\n"
        )

        for i, point in enumerate(outline, 1):
            content += f"{i}. {point}\n"

        content += "\n"

        # 生成各部分内容
        for i, point in enumerate(outline[:duration], 1):
            content += f"\n---\n\n## {i}. {point}\n\n"
            content += self._elaborate_point(point)
            content += "\n"

        content += (
            "\n---\n\n"
            "以上就是我今天要分享的主要内容。\n\n"
            "相信大家对这个话题有了一些了解，"
            "下面我很乐意回答大家的问题，我们一起交流讨论！"
        )

        self._presented_points.extend(outline)
        return content

    def _generate_outline(
        self,
        key_points: Optional[List[str]] = None,
    ) -> List[str]:
        """
        生成演讲大纲

        Args:
            key_points: 用户提供的关键点

        Returns:
            大纲列表
        """
        if key_points:
            return key_points

        # 根据主题生成默认大纲
        default_outlines = {
            "AI": [
                "AI 技术的发展历程",
                "当前 AI 技术的核心能力",
                "AI 在实际业务中的应用场景",
                "AI 应用的挑战和解决方案",
                "AI 技术的未来趋势",
            ],
            "技术": [
                "技术背景和现状",
                "核心技术原理",
                "最佳实践和案例",
                "常见问题和解决方案",
                "技术发展趋势",
            ],
        }

        # 匹配主题
        for keyword, outline in default_outlines.items():
            if keyword in self.topic:
                return outline

        # 通用大纲
        return [
            f"{self.topic}概述",
            f"{self.topic}的核心概念",
            f"{self.topic}的实践应用",
            f"{self.topic}的挑战与机遇",
            f"{self.topic}的未来展望",
        ]

    def _elaborate_point(self, point: str) -> str:
        """
        详细阐述一个观点

        Args:
            point: 观点/要点

        Returns:
            阐述内容
        """
        # 根据演讲风格生成内容
        if self.presentation_style == "storytelling":
            return (
                f'关于"{point}"，我想先分享一个真实的案例。\n\n'
                f'去年我们团队在做一个项目时，就遇到了相关的问题...\n\n'
                f'通过这个案例，我们可以看到{point}的重要性。'
                f'具体来说，有以下几点值得注意：\n\n'
                f'第一，要理解问题的本质...\n'
                f'第二，要选择合适的方法...\n'
                f'第三，要持续优化和改进...\n\n'
                f'这个经验对我们后续的工作有很大启发。'
            )
        elif self.presentation_style == "interactive":
            return (
                f'关于"{point}"，大家是怎么理解的呢？\n\n'
                f'在深入讲解之前，我想先请大家思考一个问题...\n\n'
                f'好，让我来详细解释一下。\n\n'
                f'首先，{point}的核心是...\n\n'
                f'其次，在实际应用中，我们需要注意...\n\n'
                f'最后，给大家留一个思考题：如何在自己的工作中应用这个概念？'
            )
        else:  # lecture
            return (
                f'下面我们来详细讲解"{point}"。\n\n'
                f'从定义上来说，{point}指的是...\n\n'
                f'从技术角度来看，它包含以下几个关键要素：\n'
                f"- 要素一：...\n"
                f"- 要素二：...\n"
                f"- 要素三：...\n\n"
                f"在实际应用中，我们通常采用以下方法：\n"
                f"1. 第一步...\n"
                f"2. 第二步...\n"
                f"3. 第三步...\n\n"
                f"需要注意的是，常见的误区有..."
            )

    def _respond_presentation(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应分享阶段"""
        # 如果是第一次，生成完整演讲
        if self._turn_count == 1:
            return self.generate_presentation()

        # 否则继续阐述
        return (
            "让我继续刚才的话题...\n\n"
            "除了刚才提到的内容，还有一点非常重要，那就是...\n\n"
            "在实际应用中，我们发现..."
        )

    def _respond_q_and_a(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        **kwargs,
    ) -> str:
        """回应问答阶段"""
        # 记录问题
        self._questions_answered.append({
            "question": user_message,
            "turn": self._turn_count,
        })

        # 生成回答
        return (
            f'非常好的问题！你提到的"{user_message[:20]}..."确实是一个关键点。\n\n'
            f'让我来详细解答一下：\n\n'
            f'首先，从原理上来说...\n\n'
            f'其次，在实际操作中，我们建议...\n\n'
            f'最后，给大家一个实用的建议：...\n\n'
            f'不知道这样解释是否清楚？欢迎继续追问。'
        )

    def _respond_discussion(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应讨论阶段"""
        return (
            "你的这个观点很有启发性！\n\n"
            "我补充一点我的看法：\n\n"
            "从我的经验来看，这个问题还可以从另一个角度理解...\n\n"
            "比如说，我们之前遇到的一个案例..."
        )

    def _respond_default(self, user_message: str) -> str:
        """默认回应"""
        return (
            "感谢你的提问/分享！\n\n"
            "关于这个话题，我的理解是..."
        )

    def set_current_phase(self, phase: str) -> None:
        """设置当前阶段"""
        self.current_phase = phase

    def get_presented_points(self) -> List[str]:
        """获取已分享的观点"""
        return self._presented_points.copy()

    def get_questions_answered(self) -> List[Dict[str, Any]]:
        """获取已回答的问题"""
        return self._questions_answered.copy()

    def get_turn_count(self) -> int:
        """获取发言次数"""
        return self._turn_count

    def reset(self) -> None:
        """重置状态"""
        self._turn_count = 0
        self._presented_points.clear()
        self._questions_answered.clear()
        self.current_phase = "opening"
