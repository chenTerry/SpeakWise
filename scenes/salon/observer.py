"""
Salon Observer Agent - 沙龙观察者 Agent

负责记录和总结沙龙讨论，包括：
- 记录关键观点
- 识别共识和分歧点
- 提供阶段性总结
- 整理讨论成果

观察者是沙龙的"记录员"和"总结者"，帮助参与者梳理讨论脉络。
"""

import logging
from typing import Any, Dict, List, Optional

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

logger = logging.getLogger(__name__)


class SalonObserverAgent(BaseAgent):
    """
    沙龙观察者 Agent

    职责:
    - 记录讨论中的关键观点
    - 识别共识和分歧点
    - 在适当时机提供阶段性总结
    - 整理讨论成果和建议

    Attributes:
        focus_areas: 关注领域
        summary_style: 总结风格
        current_phase: 当前阶段
    """

    def __init__(
        self,
        name: str = "观察员",
        config: Optional[Config] = None,
        focus_areas: Optional[List[str]] = None,
        summary_style: str = "structured",
        intervention_frequency: str = "moderate",
        **kwargs,
    ):
        """
        初始化观察者 Agent

        Args:
            name: Agent 名称
            config: 全局配置
            focus_areas: 关注领域列表
            summary_style: 总结风格 (structured/narrative/bullet)
            intervention_frequency: 介入频率 (low/moderate/high)
            **kwargs: 其他参数
        """
        super().__init__(name=name, config=config, **kwargs)

        self.focus_areas = focus_areas or ["key_points", "consensus", "controversy"]
        self.summary_style = summary_style
        self.intervention_frequency = intervention_frequency
        self.current_phase = "opening"
        self._turn_count = 0
        self._key_points: List[Dict[str, Any]] = []
        self._consensus_points: List[str] = []
        self._controversy_points: List[str] = []
        self._action_items: List[str] = []
        self._quotes: List[Dict[str, str]] = []

    def get_role(self) -> str:
        """获取角色类型"""
        return "observer"

    def initialize(self) -> bool:
        """
        初始化 Agent

        Returns:
            初始化是否成功
        """
        try:
            logger.info(
                f"初始化观察者 Agent: style={self.summary_style}, "
                f"focus={self.focus_areas}"
            )

            # 构建系统提示词
            self.system_prompt = self._build_system_prompt()

            # 调用父类初始化
            if hasattr(super(), 'initialize') and callable(super().initialize):
                super().initialize()

            self._initialized = True
            logger.info("观察者 Agent 初始化成功")
            return True

        except Exception as e:
            logger.error(f"观察者 Agent 初始化失败：{e}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词字符串
        """
        style_prompts = {
            "structured": "你的总结应该结构清晰，使用标题和列表组织内容。",
            "narrative": "你的总结应该像讲故事一样，有起承转合。",
            "bullet": "你的总结应该简洁明了，使用要点列表。",
        }

        style_prompt = style_prompts.get(
            self.summary_style,
            "你的总结应该清晰易懂。",
        )

        frequency_prompts = {
            "low": "你只在关键时刻进行总结，不频繁打断讨论。",
            "moderate": "你在适当时机进行阶段性总结。",
            "high": "你经常进行小结，帮助参与者梳理思路。",
        }

        frequency_prompt = frequency_prompts.get(
            self.intervention_frequency,
            "你在适当时机进行总结。",
        )

        return f"""你是一名沙龙观察员，负责记录和总结技术沙龙的讨论内容。

你的职责包括:
1. 记录讨论中的关键观点和洞见
2. 识别参与者之间的共识和分歧点
3. 在适当时机提供阶段性总结
4. 整理讨论成果和后续行动建议
5. 引用精彩发言，保留讨论精华

{style_prompt}
{frequency_prompt}

注意事项:
- 客观中立，不偏袒任何一方
- 善于提炼要点，去粗取精
- 逻辑清晰，层次分明
- 总结精准，不失原意
- 适时介入，不打断讨论流"""

    def respond(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        phase: str = "summary",
        key_points: Optional[List[str]] = None,
        questions: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> str:
        """
        生成响应

        Args:
            user_message: 用户消息
            context: 对话上下文
            phase: 当前阶段
            key_points: 关键点列表
            questions: 问题列表
            **kwargs: 其他参数

        Returns:
            响应文本
        """
        self._turn_count += 1
        self.current_phase = phase

        # 根据阶段生成不同的响应
        if phase == "summary":
            return self._generate_summary(
                key_points=key_points,
                questions=questions,
            )
        elif phase == "discussion":
            return self._respond_discussion(user_message, context)
        else:
            return self._respond_default(user_message)

    def _generate_summary(
        self,
        key_points: Optional[List[str]] = None,
        questions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        生成总结

        Args:
            key_points: 关键点列表
            questions: 问题列表

        Returns:
            总结文本
        """
        # 合并传入的关键点和已记录的关键点
        all_points = self._key_points.copy()
        if key_points:
            for point in key_points:
                if point not in [p["content"] for p in all_points]:
                    all_points.append({
                        "content": point,
                        "source": "system",
                        "turn": self._turn_count,
                    })

        # 根据总结风格生成内容
        if self.summary_style == "structured":
            return self._generate_structured_summary(all_points, questions)
        elif self.summary_style == "narrative":
            return self._generate_narrative_summary(all_points, questions)
        else:  # bullet
            return self._generate_bullet_summary(all_points, questions)

    def _generate_structured_summary(
        self,
        key_points: List[Dict[str, Any]],
        questions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """生成结构化总结"""
        content = "## 沙龙讨论总结\n\n"

        # 关键点总结
        content += "### 📌 关键观点\n\n"
        if key_points:
            for i, point in enumerate(key_points[-10:], 1):  # 最多 10 个
                point_content = point.get("content", str(point))
                content += f"{i}. {point_content}\n"
        else:
            content += "本次讨论涉及多个有价值的观点，值得深入思考。\n"

        # 共识点
        content += "\n### ✅ 达成的共识\n\n"
        if self._consensus_points:
            for point in self._consensus_points:
                content += f"- {point}\n"
        else:
            content += "参与者在多个核心问题上达成了共识。\n"

        # 分歧点
        content += "\n### 🤔 存在的分歧\n\n"
        if self._controversy_points:
            for point in self._controversy_points:
                content += f"- {point}\n"
        else:
            content += "讨论中也呈现了一些不同视角，这有助于全面理解问题。\n"

        # 问答总结
        if questions:
            content += "\n### ❓ 主要问题\n\n"
            for q in questions[-5:]:  # 最多 5 个问题
                content += f"- {q.get('content', str(q))}\n"

        # 行动建议
        content += "\n### 💡 后续建议\n\n"
        content += (
            "1. 深入研究中提到的关键技术点\n"
            "2. 在实际项目中尝试应用讨论的方法\n"
            "3. 持续关注相关领域的最新发展\n"
        )

        return content

    def _generate_narrative_summary(
        self,
        key_points: List[Dict[str, Any]],
        questions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """生成叙述式总结"""
        content = (
            "今天的沙龙讨论非常精彩，让我来为大家梳理一下整个讨论的脉络。\n\n"
        )

        content += (
            "讨论伊始，我们围绕主题展开了深入的探讨。"
            "演讲嘉宾分享了宝贵的经验和见解，为整个讨论奠定了基调。\n\n"
        )

        if key_points:
            content += "在讨论过程中，有几个关键观点特别值得关注：\n\n"
            for i, point in enumerate(key_points[-5:], 1):
                point_content = point.get("content", str(point))
                content += f"首先是{point_content}；\n"

        content += (
            "\n值得一提的是，参与者在交流中也提出了一些很有深度的问题，"
            "演讲嘉宾都给予了详细的解答。\n\n"
        )

        content += (
            "整体来看，今天的讨论既有理论高度，又有实践指导意义。"
            "希望大家能把今天的收获应用到实际工作中，期待下次再聚！"
        )

        return content

    def _generate_bullet_summary(
        self,
        key_points: List[Dict[str, Any]],
        questions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """生成要点式总结"""
        content = "📋 讨论要点总结：\n\n"

        # 关键点
        content += "【关键观点】\n"
        if key_points:
            for point in key_points[-8:]:
                content = f"• {point.get('content', str(point))}\n"

        # 共识
        content += "\n【共识】\n"
        if self._consensus_points:
            for point in self._consensus_points:
                content += f"✓ {point}\n"

        # 待探讨
        content += "\n【待深入】\n"
        if self._controversy_points:
            for point in self._controversy_points:
                content += f"○ {point}\n"

        return content

    def record_key_point(
        self,
        content: str,
        speaker: str = "unknown",
        turn: int = 0,
    ) -> None:
        """
        记录关键点

        Args:
            content: 内容
            speaker: 发言者
            turn: 轮次
        """
        self._key_points.append({
            "content": content,
            "speaker": speaker,
            "turn": turn,
            "timestamp": self._turn_count,
        })

    def record_consensus(self, point: str) -> None:
        """
        记录共识点

        Args:
            point: 共识内容
        """
        if point not in self._consensus_points:
            self._consensus_points.append(point)

    def record_controversy(self, point: str) -> None:
        """
        记录分歧点

        Args:
            point: 分歧内容
        """
        if point not in self._controversy_points:
            self._controversy_points.append(point)

    def record_quote(
        self,
        content: str,
        speaker: str,
    ) -> None:
        """
        记录精彩发言

        Args:
            content: 发言内容
            speaker: 发言者
        """
        self._quotes.append({
            "content": content,
            "speaker": speaker,
            "turn": self._turn_count,
        })

    def add_action_item(self, item: str) -> None:
        """
        添加行动项

        Args:
            item: 行动项内容
        """
        self._action_items.append(item)

    def _respond_discussion(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
    ) -> str:
        """回应讨论阶段"""
        # 根据介入频率决定是否回应
        frequency_probs = {
            "low": 0.1,
            "moderate": 0.3,
            "high": 0.5,
        }

        prob = frequency_probs.get(self.intervention_frequency, 0.2)

        import random
        if random.random() > prob:
            return ""  # 不介入

        # 进行一个小结
        return (
            '我简单总结一下刚才的讨论：\n\n'
            f'主要观点是"{user_message[:50]}..."，\n'
            '这个角度很有启发性，值得我们深入思考。'
        )

    def _respond_default(self, user_message: str) -> str:
        """默认回应"""
        return (
            "感谢分享！\n\n"
            "这个观点我已经记录下来了。"
        )

    def set_current_phase(self, phase: str) -> None:
        """设置当前阶段"""
        self.current_phase = phase

    def get_key_points(self) -> List[Dict[str, Any]]:
        """获取关键点"""
        return self._key_points.copy()

    def get_consensus_points(self) -> List[str]:
        """获取共识点"""
        return self._consensus_points.copy()

    def get_controversy_points(self) -> List[str]:
        """获取分歧点"""
        return self._controversy_points.copy()

    def get_action_items(self) -> List[str]:
        """获取行动项"""
        return self._action_items.copy()

    def get_turn_count(self) -> int:
        """获取发言次数"""
        return self._turn_count

    def reset(self) -> None:
        """重置状态"""
        self._turn_count = 0
        self._key_points.clear()
        self._consensus_points.clear()
        self._controversy_points.clear()
        self._action_items.clear()
        self._quotes.clear()
        self.current_phase = "opening"
