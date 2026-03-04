"""
Salon Host Agent - 沙龙主持人 Agent

负责沙龙活动的整体把控，包括：
- 开场介绍和暖场
- 话题引导和转场
- 时间控制
- 总结陈词

主持人是沙龙的核心角色，需要具备良好的控场能力和沟通技巧。
"""

import logging
from typing import Any, Dict, List, Optional

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

logger = logging.getLogger(__name__)


class SalonHostAgent(BaseAgent):
    """
    沙龙主持人 Agent

    职责:
    - 开场介绍沙龙主题和嘉宾
    - 引导讨论方向，确保话题不偏离
    - 控制发言时间，平衡各角色参与度
    - 总结关键观点和结论
    - 营造友好、开放的讨论氛围

    Attributes:
        topic: 沙龙主题
        discussion_style: 讨论风格 (formal/casual/debate)
        current_phase: 当前阶段
    """

    def __init__(
        self,
        name: str = "主持人",
        config: Optional[Config] = None,
        topic: str = "技术前沿探索",
        discussion_style: str = "casual",
        **kwargs,
    ):
        """
        初始化主持人 Agent

        Args:
            name: Agent 名称
            config: 全局配置
            topic: 沙龙主题
            discussion_style: 讨论风格
            **kwargs: 其他参数
        """
        super().__init__(name=name, config=config, **kwargs)

        self.topic = topic
        self.discussion_style = discussion_style
        self.current_phase = "opening"
        self._turn_count = 0
        self._key_points: List[str] = []

    def initialize(self) -> bool:
        """
        初始化 Agent

        Returns:
            初始化是否成功
        """
        try:
            logger.info(f"初始化主持人 Agent: topic={self.topic}, style={self.discussion_style}")

            # 构建系统提示词
            self.system_prompt = self._build_system_prompt()

            # 调用父类初始化
            if hasattr(super(), 'initialize') and callable(super().initialize):
                super().initialize()

            self._initialized = True
            logger.info("主持人 Agent 初始化成功")
            return True

        except Exception as e:
            logger.error(f"主持人 Agent 初始化失败：{e}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词字符串
        """
        style_prompts = {
            "formal": "你的风格应该专业、正式，使用规范的商务语言。",
            "casual": "你的风格应该轻松、亲切，像朋友聊天一样自然。",
            "debate": "你的风格应该具有引导性，鼓励不同观点的碰撞。",
        }

        style_prompt = style_prompts.get(
            self.discussion_style,
            "你的风格应该专业但不失亲和力。",
        )

        return f"""你是一个专业的沙龙主持人，正在主持一场关于"{self.topic}"的技术沙龙活动。

你的职责包括:
1. 开场介绍沙龙主题和演讲嘉宾
2. 引导讨论方向，确保话题不偏离主题
3. 控制发言时间，平衡各角色的参与度
4. 在适当时机进行阶段性总结
5. 营造友好、开放的讨论氛围
6. 最后进行闭幕总结

{style_prompt}

注意事项:
- 善于倾听和总结各方观点
- 能够巧妙引导话题回到主线
- 照顾到所有参与者，避免冷场
- 保持中立客观的立场
- 适时提出问题引发思考"""

    def respond(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        phase: str = "opening",
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
        if phase == "opening":
            return self._respond_opening(user_message)
        elif phase == "presentation":
            return self._respond_presentation(user_message, context)
        elif phase == "q_and_a":
            return self._respond_q_and_a(user_message, context)
        elif phase == "discussion":
            return self._respond_discussion(user_message, context)
        elif phase == "closing":
            return self._respond_closing(user_message, context)
        else:
            return self._respond_default(user_message)

    def generate_opening(
        self,
        topic: str,
        speaker_topic: str,
    ) -> str:
        """
        生成开场白

        Args:
            topic: 沙龙主题
            speaker_topic: 演讲主题

        Returns:
            开场白文本
        """
        style_greetings = {
            "formal": "尊敬的各位来宾，大家好！",
            "casual": "哈喽大家好！欢迎来到我们的技术沙龙！",
            "debate": "各位好！今天我们有一场精彩的思想碰撞！",
        }

        greeting = style_greetings.get(
            self.discussion_style,
            "欢迎大家！",
        )

        return (
            f"{greeting}\n\n"
            f"我是今天的主持人。非常高兴能和大家相聚在这里，"
            f"共同参与这场关于 **{topic}** 的技术沙龙活动。\n\n"
            f"今天我们的演讲嘉宾将围绕 **{speaker_topic}** 这一主题，"
            f"与大家分享他们的见解和实践经验。\n\n"
            f"在座的有我们的演讲嘉宾，还有多位对技术充满热情的观众朋友们。"
            f"希望大家能够积极互动、畅所欲言，共同度过一段愉快的交流时光！\n\n"
            f"那么，让我们正式开始今天的技术之旅吧！"
        )

    def generate_closing(
        self,
        topic: str,
        key_points: Optional[List[str]] = None,
    ) -> str:
        """
        生成闭幕词

        Args:
            topic: 沙龙主题
            key_points: 关键点列表

        Returns:
            闭幕词文本
        """
        points_str = ""
        if key_points:
            points_str = "\n\n今天我们讨论了几个关键点：\n"
            for i, point in enumerate(key_points[:5], 1):
                points_str += f"{i}. {point}\n"

        style_closings = {
            "formal": "感谢各位的参与，本次沙龙到此结束。",
            "casual": "今天的交流就到这里啦，大家回去路上注意安全！",
            "debate": "今天的思想碰撞非常精彩，期待下次再聚！",
        }

        closing = style_closings.get(
            self.discussion_style,
            "感谢大家的参与！",
        )

        return (
            f"美好的时光总是短暂的，我们的沙龙活动也接近尾声了。\n\n"
            f"回顾今天的讨论，我们围绕 **{topic}** 这一主题，"
            f"进行了深入的交流和探讨。{points_str}"
            f"\n感谢演讲嘉宾的精彩分享，也感谢各位观众的热情参与！"
            f"正是因为有了大家的智慧和见解，才让今天的活动如此精彩。\n\n"
            f"{closing}\n\n"
            f"期待下次再会！"
        )

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
            "感谢你的参与！我能感受到大家对今天话题的热情。\n\n"
            "在开始之前，我想先简单介绍一下今天的流程：\n"
            "首先由演讲嘉宾进行主题分享，然后是问答互动环节，"
            "最后我们会有一段自由讨论的时间。\n\n"
            "希望大家在讨论中能够：\n"
            "- 尊重不同观点\n"
            "- 积极提问互动\n"
            "- 分享自己的经验\n\n"
            "好了，让我们进入主题分享环节！"
        )

    def _respond_presentation(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应分享阶段"""
        return (
            "感谢演讲嘉宾的精彩分享！\n\n"
            "我注意到嘉宾提到了很多有价值的观点。"
            "不知道大家有什么想法或者问题想要交流的吗？\n\n"
            "接下来我们进入问答互动环节，欢迎大家踊跃提问！"
        )

    def _respond_q_and_a(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应问答阶段"""
        return (
            "非常好的问题！让我们请演讲嘉宾来解答。\n\n"
            "其他朋友如果也有问题，可以稍等一下，"
            "我们会给大家充分的提问机会。"
        )

    def _respond_discussion(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应讨论阶段"""
        return (
            "这个观点很有意思！\n\n"
            "我想邀请其他朋友也分享一下自己的看法。\n"
            "在面对这个问题时，你们会怎么处理呢？"
        )

    def _respond_closing(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应闭幕阶段"""
        return self.generate_closing(self.topic, self._key_points)

    def _respond_default(self, user_message: str) -> str:
        """默认回应"""
        return (
            "感谢你的分享！\n\n"
            "这个观点很有启发性。让我们继续今天的讨论。"
        )

    def add_key_point(self, point: str) -> None:
        """
        添加关键点

        Args:
            point: 关键点内容
        """
        self._key_points.append(point)

    def get_turn_count(self) -> int:
        """获取发言次数"""
        return self._turn_count

    def reset(self) -> None:
        """重置状态"""
        self._turn_count = 0
        self._key_points.clear()
        self.current_phase = "opening"
