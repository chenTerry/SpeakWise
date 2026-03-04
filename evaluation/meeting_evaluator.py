"""
Meeting Evaluator Module - 会议场景评估器 (v0.5)

提供会议场景专用的评估指标和反馈生成。

评估维度:
1. meeting_efficiency (会议效率): 时间利用和议程完成度
2. communication_effectiveness (沟通效果): 表达清晰度和理解度
3. collaboration_quality (协作质量): 团队合作和共识达成
4. problem_solving (问题解决): 问题分析和解决能力
5. action_orientation (行动导向): 行动项明确和可执行性

使用示例:
    >>> from evaluation.meeting_evaluator import MeetingEvaluator
    >>>
    >>> evaluator = MeetingEvaluator()
    >>> result = evaluator.evaluate(dialogue_context, meeting_stats)
    >>> report = evaluator.generate_report(result)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from core.agent import Message, DialogueContext

logger = logging.getLogger(__name__)


class MeetingEvaluationDimension(Enum):
    """
    会议评估维度枚举

    定义会议场景的评估维度
    """
    MEETING_EFFICIENCY = "meeting_efficiency"        # 会议效率
    COMMUNICATION_EFFECTIVENESS = "communication_effectiveness"  # 沟通效果
    COLLABORATION_QUALITY = "collaboration_quality"  # 协作质量
    PROBLEM_SOLVING = "problem_solving"              # 问题解决
    ACTION_ORIENTATION = "action_orientation"        # 行动导向


@dataclass
class MeetingDimensionScore:
    """
    会议维度评分数据类

    Attributes:
        dimension: 评估维度
        score: 分数 (0-100)
        weight: 权重
        feedback: 反馈意见
        evidence: 支撑证据
    """
    dimension: MeetingEvaluationDimension
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
class MeetingEvaluationResult:
    """
    会议评估结果数据类

    Attributes:
        session_id: 会话 ID
        scene_type: 场景类型
        meeting_type: 会议类型
        overall_score: 总体分数
        dimension_scores: 各维度评分
        role: 用户扮演的角色
        statistics: 统计数据
        summary: 总结
        suggestions: 改进建议
        action_items_quality: 行动项质量评估
    """
    session_id: str
    scene_type: str
    meeting_type: str
    overall_score: float
    dimension_scores: List[MeetingDimensionScore]
    role: str = "participant"
    statistics: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    suggestions: List[str] = field(default_factory=list)
    action_items_quality: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "scene_type": self.scene_type,
            "meeting_type": self.meeting_type,
            "overall_score": self.overall_score,
            "dimension_scores": [
                score.to_dict() for score in self.dimension_scores
            ],
            "role": self.role,
            "statistics": self.statistics,
            "summary": self.summary,
            "suggestions": self.suggestions,
            "action_items_quality": self.action_items_quality,
        }


class MeetingEvaluator:
    """
    会议场景评估器

    提供会议场景专用的评估功能

    Attributes:
        dimension_weights: 维度权重配置
    """

    def __init__(
        self,
        dimension_weights: Optional[Dict[str, float]] = None,
    ):
        """
        初始化会议评估器

        Args:
            dimension_weights: 维度权重配置
        """
        # 默认权重（根据会议类型可调整）
        self.dimension_weights = dimension_weights or {
            MeetingEvaluationDimension.MEETING_EFFICIENCY.value: 0.20,
            MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS.value: 0.20,
            MeetingEvaluationDimension.COLLABORATION_QUALITY.value: 0.20,
            MeetingEvaluationDimension.PROBLEM_SOLVING.value: 0.20,
            MeetingEvaluationDimension.ACTION_ORIENTATION.value: 0.20,
        }

        # 会议类型特定权重
        self.meeting_type_weights = {
            "standup": {
                MeetingEvaluationDimension.MEETING_EFFICIENCY.value: 0.30,
                MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS.value: 0.25,
                MeetingEvaluationDimension.COLLABORATION_QUALITY.value: 0.15,
                MeetingEvaluationDimension.PROBLEM_SOLVING.value: 0.15,
                MeetingEvaluationDimension.ACTION_ORIENTATION.value: 0.15,
            },
            "requirement_review": {
                MeetingEvaluationDimension.MEETING_EFFICIENCY.value: 0.15,
                MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS.value: 0.20,
                MeetingEvaluationDimension.COLLABORATION_QUALITY.value: 0.20,
                MeetingEvaluationDimension.PROBLEM_SOLVING.value: 0.25,
                MeetingEvaluationDimension.ACTION_ORIENTATION.value: 0.20,
            },
            "conflict_resolution": {
                MeetingEvaluationDimension.MEETING_EFFICIENCY.value: 0.15,
                MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS.value: 0.30,
                MeetingEvaluationDimension.COLLABORATION_QUALITY.value: 0.30,
                MeetingEvaluationDimension.PROBLEM_SOLVING.value: 0.15,
                MeetingEvaluationDimension.ACTION_ORIENTATION.value: 0.10,
            },
        }

        # 维度反馈模板
        self.feedback_templates = self._init_feedback_templates()

    def _init_feedback_templates(self) -> Dict[MeetingEvaluationDimension, List[str]]:
        """初始化反馈模板"""
        return {
            MeetingEvaluationDimension.MEETING_EFFICIENCY: [
                "会议效率高，时间利用充分，议程完成度好",
                "会议效率良好，基本按时完成议程",
                "会议效率有待提高，时间管理需要改进",
            ],
            MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS: [
                "沟通效果优秀，表达清晰，理解准确",
                "沟通效果良好，基本表达清楚",
                "沟通效果需要改进，表达可以更清晰",
            ],
            MeetingEvaluationDimension.COLLABORATION_QUALITY: [
                "协作质量高，团队合作顺畅，共识达成好",
                "协作质量良好，有一定团队合作",
                "协作质量需要改进，需要更多团队配合",
            ],
            MeetingEvaluationDimension.PROBLEM_SOLVING: [
                "问题解决能力强，分析深入，方案可行",
                "问题解决能力良好，能提出有效方案",
                "问题解决能力需要提升，分析可以更深入",
            ],
            MeetingEvaluationDimension.ACTION_ORIENTATION: [
                "行动导向强，行动项明确可执行",
                "行动导向良好，有明确的行动项",
                "行动导向需要加强，行动项可以更具体",
            ],
        }

    def evaluate(
        self,
        dialogue_context: DialogueContext,
        meeting_stats: Dict[str, Any],
        meeting_type: str = "standup",
        user_role: str = "participant",
    ) -> MeetingEvaluationResult:
        """
        评估会议表现

        Args:
            dialogue_context: 对话上下文
            meeting_stats: 会议统计数据
            meeting_type: 会议类型
            user_role: 用户角色

        Returns:
            评估结果
        """
        # 根据会议类型调整权重
        self._adjust_weights_for_meeting_type(meeting_type)

        # 分析对话
        analysis = self._analyze_dialogue(dialogue_context, meeting_stats)

        # 计算各维度分数
        dimension_scores = self._calculate_dimension_scores(
            analysis, meeting_stats, meeting_type
        )

        # 计算总体分数
        overall_score = self._calculate_overall_score(dimension_scores)

        # 评估行动项质量
        action_items_quality = self._evaluate_action_items(meeting_stats)

        # 生成总结
        summary = self._generate_summary(
            overall_score, dimension_scores, meeting_type, user_role
        )

        # 生成建议
        suggestions = self._generate_suggestions(
            dimension_scores, meeting_type
        )

        # 创建评估结果
        result = MeetingEvaluationResult(
            session_id=meeting_stats.get("session_id", "unknown"),
            scene_type="meeting",
            meeting_type=meeting_type,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            role=user_role,
            statistics=analysis,
            summary=summary,
            suggestions=suggestions,
            action_items_quality=action_items_quality,
        )

        logger.info(
            f"会议评估完成：type={meeting_type}, overall_score={overall_score}"
        )
        return result

    def _adjust_weights_for_meeting_type(self, meeting_type: str) -> None:
        """
        根据会议类型调整权重

        Args:
            meeting_type: 会议类型
        """
        if meeting_type in self.meeting_type_weights:
            self.dimension_weights = self.meeting_type_weights[meeting_type]

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
            if msg.role in ["user", "participant", "manager"]
        ]

        # 计算基本统计
        analysis = {
            "total_messages": len(messages),
            "user_message_count": len(user_messages),
            "avg_message_length": 0,
            "decision_count": 0,
            "action_item_count": 0,
            "question_count": 0,
            "consensus_indicators": 0,
        }

        if user_messages:
            # 平均消息长度
            total_length = sum(len(msg.content) for msg in user_messages)
            analysis["avg_message_length"] = total_length / len(user_messages)

            # 问题计数
            for msg in user_messages:
                if "?" in msg.content or "？" in msg.content:
                    analysis["question_count"] += 1

        # 从统计数据中获取
        analysis["decision_count"] = stats.get("decisions_count", 0)
        analysis["action_item_count"] = stats.get("action_items_count", 0)

        # 共识指标
        consensus_keywords = ["同意", "共识", "确认", "好的", "没问题", "understood"]
        for msg in messages:
            for kw in consensus_keywords:
                if kw in msg.content.lower():
                    analysis["consensus_indicators"] += 1
                    break

        return analysis

    def _calculate_dimension_scores(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
        meeting_type: str,
    ) -> List[MeetingDimensionScore]:
        """
        计算各维度分数

        Args:
            analysis: 分析结果
            stats: 统计数据
            meeting_type: 会议类型

        Returns:
            维度评分列表
        """
        scores = []

        # 会议效率
        efficiency_score = self._calculate_efficiency_score(analysis, stats)
        scores.append(MeetingDimensionScore(
            dimension=MeetingEvaluationDimension.MEETING_EFFICIENCY,
            score=efficiency_score,
            weight=self.dimension_weights.get("meeting_efficiency", 0.20),
            feedback=self._get_feedback(
                MeetingEvaluationDimension.MEETING_EFFICIENCY,
                efficiency_score,
            ),
        ))

        # 沟通效果
        communication_score = self._calculate_communication_score(analysis)
        scores.append(MeetingDimensionScore(
            dimension=MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS,
            score=communication_score,
            weight=self.dimension_weights.get("communication_effectiveness", 0.20),
            feedback=self._get_feedback(
                MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS,
                communication_score,
            ),
        ))

        # 协作质量
        collaboration_score = self._calculate_collaboration_score(analysis, stats)
        scores.append(MeetingDimensionScore(
            dimension=MeetingEvaluationDimension.COLLABORATION_QUALITY,
            score=collaboration_score,
            weight=self.dimension_weights.get("collaboration_quality", 0.20),
            feedback=self._get_feedback(
                MeetingEvaluationDimension.COLLABORATION_QUALITY,
                collaboration_score,
            ),
        ))

        # 问题解决
        problem_solving_score = self._calculate_problem_solving_score(
            analysis, stats, meeting_type
        )
        scores.append(MeetingDimensionScore(
            dimension=MeetingEvaluationDimension.PROBLEM_SOLVING,
            score=problem_solving_score,
            weight=self.dimension_weights.get("problem_solving", 0.20),
            feedback=self._get_feedback(
                MeetingEvaluationDimension.PROBLEM_SOLVING,
                problem_solving_score,
            ),
        ))

        # 行动导向
        action_score = self._calculate_action_score(analysis, stats)
        scores.append(MeetingDimensionScore(
            dimension=MeetingEvaluationDimension.ACTION_ORIENTATION,
            score=action_score,
            weight=self.dimension_weights.get("action_orientation", 0.20),
            feedback=self._get_feedback(
                MeetingEvaluationDimension.ACTION_ORIENTATION,
                action_score,
            ),
        ))

        return scores

    def _calculate_efficiency_score(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> float:
        """计算会议效率分数"""
        score = 60.0

        # 基于议程完成度
        agenda_item = stats.get("current_agenda_item", 0)
        agenda_total = stats.get("agenda_total", 1)
        if agenda_total > 0:
            completion_rate = agenda_item / agenda_total
            score += completion_rate * 30

        # 基于轮次效率
        current_turn = stats.get("current_turn", 0)
        if current_turn <= 15:  # 高效完成
            score += 10

        return min(100, max(0, score))

    def _calculate_communication_score(
        self,
        analysis: Dict[str, Any],
    ) -> float:
        """计算沟通效果分数"""
        score = 60.0

        # 基于平均消息长度（表达完整性）
        avg_length = analysis.get("avg_message_length", 0)
        if avg_length >= 80:
            score += 25
        elif avg_length >= 40:
            score += 15
        elif avg_length >= 20:
            score += 5

        # 基于问题数量（互动性）
        question_count = analysis.get("question_count", 0)
        if question_count >= 3:
            score += 15
        elif question_count >= 1:
            score += 8

        return min(100, max(0, score))

    def _calculate_collaboration_score(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> float:
        """计算协作质量分数"""
        score = 60.0

        # 基于共识指标
        consensus_count = analysis.get("consensus_indicators", 0)
        if consensus_count >= 5:
            score += 25
        elif consensus_count >= 3:
            score += 15
        elif consensus_count >= 1:
            score += 8

        # 基于决策数量
        decision_count = analysis.get("decision_count", 0)
        if decision_count >= 3:
            score += 15
        elif decision_count >= 1:
            score += 8

        return min(100, max(0, score))

    def _calculate_problem_solving_score(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
        meeting_type: str,
    ) -> float:
        """计算问题解决分数"""
        score = 60.0

        # 不同类型会议的问题解决侧重点不同
        if meeting_type == "requirement_review":
            # 需求评审关注风险识别
            if analysis.get("question_count", 0) >= 3:
                score += 25
        elif meeting_type == "conflict_resolution":
            # 冲突解决关注共识达成
            if analysis.get("consensus_indicators", 0) >= 3:
                score += 25
        elif meeting_type == "standup":
            # 站会关注阻塞问题识别
            if stats.get("action_items_count", 0) >= 1:
                score += 25
        else:
            # 通用
            if analysis.get("decision_count", 0) >= 2:
                score += 25

        # 基于行动项
        if analysis.get("action_item_count", 0) >= 2:
            score += 15

        return min(100, max(0, score))

    def _calculate_action_score(
        self,
        analysis: Dict[str, Any],
        stats: Dict[str, Any],
    ) -> float:
        """计算行动导向分数"""
        score = 50.0

        # 基于行动项数量
        action_count = analysis.get("action_item_count", 0)
        if action_count >= 3:
            score += 30
        elif action_count >= 1:
            score += 20

        # 基于决策数量
        decision_count = analysis.get("decision_count", 0)
        if decision_count >= 2:
            score += 20
        elif decision_count >= 1:
            score += 10

        return min(100, max(0, score))

    def _evaluate_action_items(
        self,
        stats: Dict[str, Any],
    ) -> str:
        """
        评估行动项质量

        Args:
            stats: 统计数据

        Returns:
            质量评估文本
        """
        action_count = stats.get("action_items_count", 0)

        if action_count >= 3:
            return "行动项明确且数量适当，具有良好的可执行性"
        elif action_count >= 1:
            return "有行动项，但可以更具体和可衡量"
        else:
            return "缺少明确的行动项，建议增加具体的后续行动"

    def _get_feedback(
        self,
        dimension: MeetingEvaluationDimension,
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
        dimension_scores: List[MeetingDimensionScore],
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
        dimension_scores: List[MeetingDimensionScore],
        meeting_type: str,
        user_role: str,
    ) -> str:
        """
        生成总结

        Args:
            overall_score: 总体分数
            dimension_scores: 维度评分列表
            meeting_type: 会议类型
            user_role: 用户角色

        Returns:
            总结文本
        """
        type_names = {
            "standup": "站会",
            "requirement_review": "需求评审会",
            "conflict_resolution": "冲突解决会",
            "project_kickoff": "项目启动会",
            "retrospective": "复盘会",
        }

        meeting_name = type_names.get(meeting_type, "会议")

        role_names = {
            "manager": "主持人",
            "participant": "参与者",
            "product_manager": "产品经理",
            "tech_lead": "技术负责人",
            "developer": "开发工程师",
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
            f"作为{role_name}，您在本场{meeting_name}中的整体表现为{level}，"
            f"综合得分{overall_score:.1f}分。\n\n"
            f"会议整体进行顺利，"
            f"继续保持可以提升会议参与效果。"
        )

    def _generate_suggestions(
        self,
        dimension_scores: List[MeetingDimensionScore],
        meeting_type: str,
    ) -> List[str]:
        """
        生成改进建议

        Args:
            dimension_scores: 维度评分列表
            meeting_type: 会议类型

        Returns:
            建议列表
        """
        suggestions = []

        for score in dimension_scores:
            if score.score < 60:
                suggestion = self._get_suggestion(
                    score.dimension, score.score, meeting_type
                )
                if suggestion:
                    suggestions.append(suggestion)

        # 如果没有低分维度，给一些通用建议
        if not suggestions:
            suggestions = [
                "继续保持高效的会议参与",
                "可以更多地分享自己的观点",
                "关注行动项的跟进和落实",
            ]

        return suggestions

    def _get_suggestion(
        self,
        dimension: MeetingEvaluationDimension,
        score: float,
        meeting_type: str,
    ) -> str:
        """
        获取维度建议

        Args:
            dimension: 维度
            score: 分数
            meeting_type: 会议类型

        Returns:
            建议文本
        """
        base_suggestions = {
            MeetingEvaluationDimension.MEETING_EFFICIENCY: (
                "建议更好地管理会议时间，确保议程按时完成"
            ),
            MeetingEvaluationDimension.COMMUNICATION_EFFECTIVENESS: (
                "发言时注意表达清晰，确保信息准确传达"
            ),
            MeetingEvaluationDimension.COLLABORATION_QUALITY: (
                "多与团队成员互动，促进共识达成"
            ),
            MeetingEvaluationDimension.PROBLEM_SOLVING: (
                "深入分析问题，提出更可行的解决方案"
            ),
            MeetingEvaluationDimension.ACTION_ORIENTATION: (
                "确保每个讨论都有明确的后续行动项"
            ),
        }

        return base_suggestions.get(dimension, "")

    def generate_report(
        self,
        result: MeetingEvaluationResult,
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
        result: MeetingEvaluationResult,
    ) -> str:
        """生成文本报告"""
        type_names = {
            "standup": "站会",
            "requirement_review": "需求评审会",
            "conflict_resolution": "冲突解决会",
            "project_kickoff": "项目启动会",
            "retrospective": "复盘会",
        }

        meeting_name = type_names.get(result.meeting_type, "会议")

        lines = [
            "=" * 50,
            f"{meeting_name}表现评估报告",
            "=" * 50,
            "",
            f"综合得分：{result.overall_score:.1f}分",
            f"参与角色：{result.role}",
            f"行动项质量：{result.action_items_quality}",
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
        result: MeetingEvaluationResult,
    ) -> str:
        """生成 Markdown 报告"""
        type_names = {
            "standup": "站会",
            "requirement_review": "需求评审会",
            "conflict_resolution": "冲突解决会",
            "project_kickoff": "项目启动会",
            "retrospective": "复盘会",
        }

        meeting_name = type_names.get(result.meeting_type, "会议")

        lines = [
            f"## 📋 {meeting_name}表现评估报告",
            "",
            f"**综合得分**: {result.overall_score:.1f}分",
            f"**参与角色**: {result.role}",
            f"**行动项质量**: {result.action_items_quality}",
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
