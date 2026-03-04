"""
Salon Evaluator Module - 沙龙场景评估器 (v0.5)

提供沙龙场景专用的评估指标和反馈生成。

评估维度:
1. participation_quality (参与质量): 发言的积极性和质量
2. topic_relevance (话题相关性): 发言与主题的相关程度
3. interaction_effectiveness (互动效果): 与他人互动的有效性
4. knowledge_contribution (知识贡献): 分享知识的价值
5. communication_style (沟通风格): 表达方式和风格

使用示例:
    >>> from evaluation.salon_evaluator import SalonEvaluator
    >>>
    >>> evaluator = SalonEvaluator()
    >>> result = evaluator.evaluate(dialogue_history, scene_stats)
    >>> report = evaluator.generate_report(result)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from core.agent import Message, DialogueContext

logger = logging.getLogger(__name__)


class SalonEvaluationDimension(Enum):
    """
    沙龙评估维度枚举

    定义沙龙场景的评估维度
    """
    PARTICIPATION_QUALITY = "participation_quality"      # 参与质量
    TOPIC_RELEVANCE = "topic_relevance"                   # 话题相关性
    INTERACTION_EFFECTIVENESS = "interaction_effectiveness"  # 互动效果
    KNOWLEDGE_CONTRIBUTION = "knowledge_contribution"     # 知识贡献
    COMMUNICATION_STYLE = "communication_style"           # 沟通风格


@dataclass
class SalonDimensionScore:
    """
    沙龙维度评分数据类

    Attributes:
        dimension: 评估维度
        score: 分数 (0-100)
        weight: 权重
        feedback: 反馈意见
        evidence: 支撑证据
    """
    dimension: SalonEvaluationDimension
    score: float
    weight: float = 1.0
    feedback: str = ""
    evidence: List[str] = field(default_factory=list)

    def weighted_score(self) -> float:
        """计算加权分数"""
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimension": self.dimension.value,
            "score": self.score,
            "weight": self.weight,
            "weighted_score": self.weighted_score(),
            "feedback": self.feedback,
            "evidence": self.evidence,
        }


@dataclass
class SalonEvaluationResult:
    """
    沙龙评估结果数据类

    Attributes:
        session_id: 会话 ID
        scene_type: 场景类型
        overall_score: 总体分数
        dimension_scores: 各维度评分
        role: 用户扮演的角色
        statistics: 统计数据
        summary: 总结
        suggestions: 改进建议
    """
    session_id: str
    scene_type: str
    overall_score: float
    dimension_scores: List[SalonDimensionScore]
    role: str = "participant"
    statistics: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "scene_type": self.scene_type,
            "overall_score": self.overall_score,
            "dimension_scores": [
                score.to_dict() for score in self.dimension_scores
            ],
            "role": self.role,
            "statistics": self.statistics,
            "summary": self.summary,
            "suggestions": self.suggestions,
        }


class SalonEvaluator:
    """
    沙龙场景评估器

    提供沙龙场景专用的评估功能

    Attributes:
        dimension_weights: 维度权重配置
    """

    def __init__(
        self,
        dimension_weights: Optional[Dict[str, float]] = None,
    ):
        """
        初始化沙龙评估器

        Args:
            dimension_weights: 维度权重配置
        """
        # 默认权重
        self.dimension_weights = dimension_weights or {
            SalonEvaluationDimension.PARTICIPATION_QUALITY.value: 0.25,
            SalonEvaluationDimension.TOPIC_RELEVANCE.value: 0.20,
            SalonEvaluationDimension.INTERACTION_EFFECTIVENESS.value: 0.20,
            SalonEvaluationDimension.KNOWLEDGE_CONTRIBUTION.value: 0.20,
            SalonEvaluationDimension.COMMUNICATION_STYLE.value: 0.15,
        }

        # 维度反馈模板
        self.feedback_templates = {
            SalonEvaluationDimension.PARTICIPATION_QUALITY: [
                "参与度高，发言积极且质量良好",
                "参与度适中，发言有一定价值",
                "参与度较低，需要更积极参与",
            ],
            SalonEvaluationDimension.TOPIC_RELEVANCE: [
                "发言紧扣主题，贡献度高",
                "发言基本相关，偶有偏离",
                "发言偏离主题较多，需要改进",
            ],
            SalonEvaluationDimension.INTERACTION_EFFECTIVENESS: [
                "互动效果好，善于回应他人",
                "互动一般，可以更多回应",
                "互动较少，需要更多交流",
            ],
            SalonEvaluationDimension.KNOWLEDGE_CONTRIBUTION: [
                "知识贡献突出，分享有价值",
                "有一定知识分享",
                "知识贡献较少，可以多分享",
            ],
            SalonEvaluationDimension.COMMUNICATION_STYLE: [
                "沟通风格优秀，表达清晰",
                "沟通风格良好，基本清晰",
                "沟通风格需要改进，表达可以更清晰",
            ],
        }

    def evaluate(
        self,
        dialogue_context: DialogueContext,
        scene_stats: Dict[str, Any],
        user_role: str = "participant",
    ) -> SalonEvaluationResult:
        """
        评估沙龙表现

        Args:
            dialogue_context: 对话上下文
            scene_stats: 场景统计数据
            user_role: 用户角色

        Returns:
            评估结果
        """
        # 分析对话
        analysis = self._analyze_dialogue(dialogue_context, scene_stats)

        # 计算各维度分数
        dimension_scores = self._calculate_dimension_scores(
            analysis, scene_stats
        )

        # 计算总体分数
        overall_score = self._calculate_overall_score(dimension_scores)

        # 生成总结
        summary = self._generate_summary(
            overall_score, dimension_scores, user_role
        )

        # 生成建议
        suggestions = self._generate_suggestions(dimension_scores)

        # 创建评估结果
        result = SalonEvaluationResult(
            session_id=scene_stats.get("session_id", "unknown"),
            scene_type="salon",
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            role=user_role,
            statistics=analysis,
            summary=summary,
            suggestions=suggestions,
        )

        logger.info(f"沙龙评估完成：overall_score={overall_score}")
        return result

    def _analyze_dialogue(
        self,
        context: DialogueContext,
        stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        分析对话内容

        Args:
            context: 对话上下文
            stats: 统计数据

        Returns:
            分析结果
        """
        messages = context.messages

        # 统计用户消息
        user_messages = [
            msg for msg in messages
            if msg.role in ["user", "audience_1", "audience_2"]
        ]

        # 计算基本统计
        analysis = {
            "total_messages": len(messages),
            "user_message_count": len(user_messages),
            "avg_message_length": 0,
            "keyword_count": 0,
            "question_count": 0,
            "interaction_count": 0,
        }

        if user_messages:
            # 平均消息长度
            total_length = sum(len(msg.content) for msg in user_messages)
            analysis["avg_message_length"] = total_length / len(user_messages)

            # 关键词计数
            keywords = ["技术", "经验", "案例", "建议", "观点", "理解"]
            for msg in user_messages:
                for kw in keywords:
                    if kw in msg.content:
                        analysis["keyword_count"] += 1

            # 问题计数
            for msg in user_messages:
                if "?" in msg.content or "？" in msg.content:
                    analysis["question_count"] += 1

        # 互动计数
        analysis["interaction_count"] = stats.get("questions_count", 0)

        return analysis

    def _calculate_dimension_scores(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> List[SalonDimensionScore]:
        """
        计算各维度分数

        Args:
            analysis: 分析结果
            stats: 统计数据

        Returns:
            维度评分列表
        """
        scores = []

        # 参与质量 (基于发言次数和长度)
        participation_score = self._calculate_participation_score(analysis)
        scores.append(SalonDimensionScore(
            dimension=SalonEvaluationDimension.PARTICIPATION_QUALITY,
            score=participation_score,
            weight=self.dimension_weights.get("participation_quality", 0.25),
            feedback=self._get_feedback(
                SalonEvaluationDimension.PARTICIPATION_QUALITY,
                participation_score,
            ),
        ))

        # 话题相关性 (基于关键词)
        relevance_score = self._calculate_relevance_score(analysis)
        scores.append(SalonDimensionScore(
            dimension=SalonEvaluationDimension.TOPIC_RELEVANCE,
            score=relevance_score,
            weight=self.dimension_weights.get("topic_relevance", 0.20),
            feedback=self._get_feedback(
                SalonEvaluationDimension.TOPIC_RELEVANCE,
                relevance_score,
            ),
        ))

        # 互动效果 (基于问题和互动)
        interaction_score = self._calculate_interaction_score(analysis, stats)
        scores.append(SalonDimensionScore(
            dimension=SalonEvaluationDimension.INTERACTION_EFFECTIVENESS,
            score=interaction_score,
            weight=self.dimension_weights.get("interaction_effectiveness", 0.20),
            feedback=self._get_feedback(
                SalonEvaluationDimension.INTERACTION_EFFECTIVENESS,
                interaction_score,
            ),
        ))

        # 知识贡献 (基于关键词和内容质量)
        knowledge_score = self._calculate_knowledge_score(analysis)
        scores.append(SalonDimensionScore(
            dimension=SalonEvaluationDimension.KNOWLEDGE_CONTRIBUTION,
            score=knowledge_score,
            weight=self.dimension_weights.get("knowledge_contribution", 0.20),
            feedback=self._get_feedback(
                SalonEvaluationDimension.KNOWLEDGE_CONTRIBUTION,
                knowledge_score,
            ),
        ))

        # 沟通风格 (基于表达清晰度)
        style_score = self._calculate_style_score(analysis)
        scores.append(SalonDimensionScore(
            dimension=SalonEvaluationDimension.COMMUNICATION_STYLE,
            score=style_score,
            weight=self.dimension_weights.get("communication_style", 0.15),
            feedback=self._get_feedback(
                SalonEvaluationDimension.COMMUNICATION_STYLE,
                style_score,
            ),
        ))

        return scores

    def _calculate_participation_score(
        self,
        analysis: Dict[str, Any],
    ) -> float:
        """计算参与质量分数"""
        score = 50.0

        # 基于消息数量
        msg_count = analysis.get("user_message_count", 0)
        if msg_count >= 5:
            score += 30
        elif msg_count >= 3:
            score += 20
        elif msg_count >= 1:
            score += 10

        # 基于平均长度
        avg_length = analysis.get("avg_message_length", 0)
        if avg_length >= 100:
            score += 20
        elif avg_length >= 50:
            score += 10

        return min(100, max(0, score))

    def _calculate_relevance_score(
        self,
        analysis: Dict[str, Any],
    ) -> float:
        """计算话题相关性分数"""
        score = 50.0

        # 基于关键词密度
        keyword_count = analysis.get("keyword_count", 0)
        msg_count = max(1, analysis.get("user_message_count", 1))
        keyword_density = keyword_count / msg_count

        if keyword_density >= 2:
            score += 40
        elif keyword_density >= 1:
            score += 30
        elif keyword_density >= 0.5:
            score += 20

        return min(100, max(0, score))

    def _calculate_interaction_score(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> float:
        """计算互动效果分数"""
        score = 50.0

        # 基于问题数量
        question_count = analysis.get("question_count", 0)
        if question_count >= 3:
            score += 30
        elif question_count >= 1:
            score += 20

        # 基于互动次数
        interaction_count = analysis.get("interaction_count", 0)
        if interaction_count >= 3:
            score += 20
        elif interaction_count >= 1:
            score += 10

        return min(100, max(0, score))

    def _calculate_knowledge_score(
        self,
        analysis: Dict[str, Any],
    ) -> float:
        """计算知识贡献分数"""
        score = 50.0

        # 基于关键词和长度
        keyword_count = analysis.get("keyword_count", 0)
        avg_length = analysis.get("avg_message_length", 0)

        if keyword_count >= 5 and avg_length >= 80:
            score += 40
        elif keyword_count >= 3 and avg_length >= 50:
            score += 30
        elif keyword_count >= 1:
            score += 15

        return min(100, max(0, score))

    def _calculate_style_score(
        self,
        analysis: Dict[str, Any],
    ) -> float:
        """计算沟通风格分数"""
        score = 60.0

        # 基于平均长度（表达完整性）
        avg_length = analysis.get("avg_message_length", 0)
        if avg_length >= 100:
            score += 30
        elif avg_length >= 50:
            score += 20
        elif avg_length >= 20:
            score += 10

        return min(100, max(0, score))

    def _get_feedback(
        self,
        dimension: SalonEvaluationDimension,
        score: float,
    ) -> str:
        """
        获取维度反馈

        Args:
            dimension: 维度
            score: 分数

        Returns:
            反馈文本
        """
        templates = self.feedback_templates.get(dimension, [""])

        if score >= 80:
            return templates[0] if len(templates) > 0 else "表现优秀"
        elif score >= 60:
            return templates[1] if len(templates) > 1 else "表现良好"
        else:
            return templates[2] if len(templates) > 2 else "需要改进"

    def _calculate_overall_score(
        self,
        dimension_scores: List[SalonDimensionScore],
    ) -> float:
        """
        计算总体分数

        Args:
            dimension_scores: 维度评分列表

        Returns:
            总体分数
        """
        total_weighted = sum(
            score.weighted_score() for score in dimension_scores
        )
        total_weight = sum(score.weight for score in dimension_scores)

        if total_weight == 0:
            return 0.0

        return total_weighted / total_weight

    def _generate_summary(
        self,
        overall_score: float,
        dimension_scores: List[SalonDimensionScore],
        user_role: str,
    ) -> str:
        """
        生成总结

        Args:
            overall_score: 总体分数
            dimension_scores: 维度评分列表
            user_role: 用户角色

        Returns:
            总结文本
        """
        role_names = {
            "host": "主持人",
            "speaker": "演讲者",
            "audience": "观众",
            "observer": "观察员",
            "participant": "参与者",
        }

        role_name = role_names.get(user_role, "参与者")

        if overall_score >= 85:
            level = "优秀"
        elif overall_score >= 70:
            level = "良好"
        elif overall_score >= 60:
            level = "合格"
        else:
            level = "需要改进"

        return (
            f"作为{role_name}，您在本场沙龙中的整体表现为{level}，"
            f"综合得分{overall_score:.1f}分。\n\n"
            f"您在多个维度都有不错的表现，"
            f"继续保持可以提升沙龙参与体验。"
        )

    def _generate_suggestions(
        self,
        dimension_scores: List[SalonDimensionScore],
    ) -> List[str]:
        """
        生成改进建议

        Args:
            dimension_scores: 维度评分列表

        Returns:
            建议列表
        """
        suggestions = []

        for score in dimension_scores:
            if score.score < 60:
                suggestion = self._get_suggestion(score.dimension, score.score)
                if suggestion:
                    suggestions.append(suggestion)

        # 如果没有低分维度，给一些通用建议
        if not suggestions:
            suggestions = [
                "继续保持积极参与的态度",
                "可以尝试提出更有深度的问题",
                "多分享个人经验和见解",
            ]

        return suggestions

    def _get_suggestion(
        self,
        dimension: SalonEvaluationDimension,
        score: float,
    ) -> str:
        """
        获取维度建议

        Args:
            dimension: 维度
            score: 分数

        Returns:
            建议文本
        """
        suggestions = {
            SalonEvaluationDimension.PARTICIPATION_QUALITY: (
                "建议更积极地参与讨论，主动发言分享观点"
            ),
            SalonEvaluationDimension.TOPIC_RELEVANCE: (
                "发言时尽量紧扣主题，提高贡献度"
            ),
            SalonEvaluationDimension.INTERACTION_EFFECTIVENESS: (
                "多与他人互动，回应他人观点并提出问题"
            ),
            SalonEvaluationDimension.KNOWLEDGE_CONTRIBUTION: (
                "多分享专业知识和实践经验"
            ),
            SalonEvaluationDimension.COMMUNICATION_STYLE: (
                "注意表达的清晰度和逻辑性"
            ),
        }

        return suggestions.get(dimension, "")

    def generate_report(
        self,
        result: SalonEvaluationResult,
        format: str = "text",
    ) -> str:
        """
        生成评估报告

        Args:
            result: 评估结果
            format: 报告格式 (text/markdown/json)

        Returns:
            报告文本
        """
        if format == "json":
            import json
            return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

        elif format == "markdown":
            return self._generate_markdown_report(result)

        else:  # text
            return self._generate_text_report(result)

    def _generate_text_report(
        self,
        result: SalonEvaluationResult,
    ) -> str:
        """生成文本报告"""
        lines = [
            "=" * 50,
            "沙龙表现评估报告",
            "=" * 50,
            "",
            f"综合得分：{result.overall_score:.1f}分",
            f"参与角色：{result.role}",
            "",
            "维度评分:",
        ]

        for score in result.dimension_scores:
            lines.append(
                f"  - {score.dimension.value}: {score.score:.1f}分 "
                f"({score.feedback})"
            )

        lines.extend([
            "",
            "总结:",
            result.summary,
            "",
            "改进建议:",
        ])

        for i, suggestion in enumerate(result.suggestions, 1):
            lines.append(f"  {i}. {suggestion}")

        lines.append("")
        lines.append("=" * 50)

        return "\n".join(lines)

    def _generate_markdown_report(
        self,
        result: SalonEvaluationResult,
    ) -> str:
        """生成 Markdown 报告"""
        lines = [
            "## 🎯 沙龙表现评估报告",
            "",
            f"**综合得分**: {result.overall_score:.1f}分",
            f"**参与角色**: {result.role}",
            "",
            "### 维度评分",
            "",
            "| 维度 | 分数 | 反馈 |",
            "|------|------|------|",
        ]

        for score in result.dimension_scores:
            dim_name = score.dimension.value
            lines.append(
                f"| {dim_name} | {score.score:.1f} | {score.feedback} |"
            )

        lines.extend([
            "",
            "### 总结",
            "",
            result.summary,
            "",
            "### 改进建议",
            "",
        ])

        for suggestion in result.suggestions:
            lines.append(f"- {suggestion}")

        return "\n".join(lines)
