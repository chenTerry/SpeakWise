"""
Recommendation Engine Module

推荐引擎模块提供：
- RecommendationEngine: 个性化推荐系统
- 基于弱点的练习主题推荐
- 难度级别推荐
- 个性化学习路径生成

Version: v0.7.0
Author: AgentScope AI Interview Team
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import random


class RecommendationType(str, Enum):
    """推荐类型"""
    TOPIC = "topic"  # 练习主题
    DIFFICULTY = "difficulty"  # 难度级别
    SCENE = "scene"  # 场景类型
    LEARNING_PATH = "learning_path"  # 学习路径
    PRACTICE_METHOD = "practice_method"  # 练习方法


class DifficultyLevel(str, Enum):
    """难度级别"""
    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家


@dataclass
class TopicRecommendation:
    """主题推荐"""
    topic_id: str
    topic_name: str
    dimension: str  # 关联的能力维度
    reason: str  # 推荐理由
    priority: int  # 优先级 (1-5, 5 最高)
    estimated_duration_minutes: int
    difficulty: DifficultyLevel
    expected_improvement: float  # 预期提升 (%)


@dataclass
class DifficultyRecommendation:
    """难度推荐"""
    recommended_level: DifficultyLevel
    current_level: DifficultyLevel
    reason: str
    confidence: float  # 0-1
    adjustment_factors: List[str] = field(default_factory=list)


@dataclass
class LearningPathItem:
    """学习路径项目"""
    step: int
    activity_type: str  # practice, review, challenge, rest
    description: str
    topic: Optional[str]
    difficulty: DifficultyLevel
    duration_minutes: int
    goals: List[str] = field(default_factory=list)


@dataclass
class LearningPath:
    """学习路径"""
    path_id: str
    user_id: str
    duration_days: int
    items: List[LearningPathItem]
    expected_outcomes: List[str]
    success_criteria: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PracticeMethodRecommendation:
    """练习方法推荐"""
    method_name: str
    description: str
    suitable_for: List[str]  # 适合的情况
    steps: List[str]
    tips: List[str] = field(default_factory=list)


@dataclass
class RecommendationReport:
    """推荐报告"""
    user_id: str
    generated_at: datetime
    topic_recommendations: List[TopicRecommendation] = field(default_factory=list)
    difficulty_recommendation: Optional[DifficultyRecommendation] = None
    learning_path: Optional[LearningPath] = None
    practice_methods: List[PracticeMethodRecommendation] = field(default_factory=list)
    general_advice: List[str] = field(default_factory=list)


class RecommendationEngine:
    """
    推荐引擎

    基于用户学习数据和表现，生成个性化的练习推荐

    Design Principles:
    - 个性化：根据用户特点定制推荐
    - 可操作性：推荐具体可行的练习
    - 渐进性：难度逐步提升
    - 数据驱动：基于历史数据做出推荐
    """

    # 维度到主题的映射
    DIMENSION_TOPICS = {
        "language_expression": [
            {"id": "le_001", "name": "清晰表达训练", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "le_002", "name": "结构化表达", "difficulty": DifficultyLevel.ADVANCED},
            {"id": "le_003", "name": "精炼语言练习", "difficulty": DifficultyLevel.INTERMEDIATE},
        ],
        "logical_thinking": [
            {"id": "lt_001", "name": "逻辑思维训练", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "lt_002", "name": "论证结构练习", "difficulty": DifficultyLevel.ADVANCED},
            {"id": "lt_003", "name": "因果关系分析", "difficulty": DifficultyLevel.INTERMEDIATE},
        ],
        "professional_knowledge": [
            {"id": "pk_001", "name": "专业知识梳理", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "pk_002", "name": "技术深度挖掘", "difficulty": DifficultyLevel.ADVANCED},
            {"id": "pk_003", "name": "行业趋势分析", "difficulty": DifficultyLevel.EXPERT},
        ],
        "problem_solving": [
            {"id": "ps_001", "name": "问题分析框架", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "ps_002", "name": "解决方案设计", "difficulty": DifficultyLevel.ADVANCED},
            {"id": "ps_003", "name": "案例研究练习", "difficulty": DifficultyLevel.ADVANCED},
        ],
        "communication_collaboration": [
            {"id": "cc_001", "name": "积极倾听训练", "difficulty": DifficultyLevel.BEGINNER},
            {"id": "cc_002", "name": "反馈技巧练习", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "cc_003", "name": "团队协作模拟", "difficulty": DifficultyLevel.ADVANCED},
        ],
        "adaptability": [
            {"id": "ad_001", "name": "压力应对训练", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "ad_002", "name": "灵活应变练习", "difficulty": DifficultyLevel.ADVANCED},
            {"id": "ad_003", "name": "多场景切换", "difficulty": DifficultyLevel.EXPERT},
        ],
        "overall_quality": [
            {"id": "oq_001", "name": "综合能力提升", "difficulty": DifficultyLevel.INTERMEDIATE},
            {"id": "oq_002", "name": "模拟面试实战", "difficulty": DifficultyLevel.ADVANCED},
            {"id": "oq_003", "name": "高阶挑战", "difficulty": DifficultyLevel.EXPERT},
        ],
    }

    # 难度阈值
    DIFFICULTY_THRESHOLDS = {
        DifficultyLevel.BEGINNER: (0, 60),
        DifficultyLevel.INTERMEDIATE: (60, 75),
        DifficultyLevel.ADVANCED: (75, 90),
        DifficultyLevel.EXPERT: (90, 100),
    }

    # 练习方法库
    PRACTICE_METHODS = {
        "deliberate_practice": {
            "name": "刻意练习",
            "description": "针对弱点进行有目的的重复练习",
            "suitable_for": ["plateau", "weak_dimension", "skill_building"],
            "steps": [
                "明确要改进的具体技能",
                "分解技能为小步骤",
                "专注练习每个步骤",
                "获取即时反馈",
                "走出舒适区",
            ],
            "tips": [
                "每次练习聚焦一个技能点",
                "记录练习过程和感受",
                "定期回顾进步",
            ],
        },
        "spaced_repetition": {
            "name": "间隔重复",
            "description": "按照特定时间间隔复习已学内容",
            "suitable_for": ["knowledge_retention", "long_term_improvement"],
            "steps": [
                "学习新知识或技能",
                "1 天后复习",
                "3 天后再次复习",
                "1 周后复习",
                "2 周后复习",
            ],
            "tips": [
                "使用闪卡或笔记辅助",
                "在复习时尝试主动回忆",
                "逐渐延长间隔时间",
            ],
        },
        "scenario_variation": {
            "name": "场景变换",
            "description": "在不同场景中练习相同技能",
            "suitable_for": ["adaptability", "skill_transfer"],
            "steps": [
                "选择一个核心技能",
                "在不同场景中应用",
                "观察不同场景的要求",
                "调整表达方式",
                "总结共通点",
            ],
            "tips": [
                "从熟悉场景开始",
                "逐步增加场景难度",
                "记录不同场景的特点",
            ],
        },
        "peer_learning": {
            "name": "同伴学习",
            "description": "通过观察和交流向他人学习",
            "suitable_for": ["communication", "perspective_expansion"],
            "steps": [
                "寻找学习伙伴",
                "互相模拟面试",
                "交换反馈意见",
                "讨论改进方法",
                "共同制定计划",
            ],
            "tips": [
                "选择水平相当的伙伴",
                "保持开放的心态",
                "定期交流进展",
            ],
        },
        "reflection_practice": {
            "name": "反思练习",
            "description": "通过深度反思提升元认知能力",
            "suitable_for": ["self_awareness", "continuous_improvement"],
            "steps": [
                "完成练习后立即反思",
                "记录做得好的地方",
                "识别需要改进的地方",
                "分析原因",
                "制定改进计划",
            ],
            "tips": [
                "使用反思模板",
                "保持诚实和客观",
                "关注可控制的因素",
            ],
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化推荐引擎

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self._topic_cache: Dict[str, Any] = {}
        self._path_cache: Dict[str, LearningPath] = {}

    # =========================================================================
    # Main Recommendation Method
    # =========================================================================

    def generate_recommendations(self, user_id: str,
                                 sessions: List[Dict[str, Any]],
                                 learning_profile: Optional[Dict[str, Any]] = None,
                                 behavior_report: Optional[Dict[str, Any]] = None) -> RecommendationReport:
        """
        生成推荐报告

        Args:
            user_id: 用户 ID
            sessions: 会话数据列表
            learning_profile: 学习画像（可选）
            behavior_report: 行为报告（可选）

        Returns:
            RecommendationReport 对象
        """
        # 分析用户数据
        user_analysis = self._analyze_user_data(sessions, learning_profile, behavior_report)

        # 生成主题推荐
        topic_recommendations = self._generate_topic_recommendations(user_analysis)

        # 生成难度推荐
        difficulty_recommendation = self._generate_difficulty_recommendation(user_analysis)

        # 生成学习路径
        learning_path = self._generate_learning_path(user_id, user_analysis, topic_recommendations)

        # 生成练习方法推荐
        practice_methods = self._generate_practice_methods(user_analysis)

        # 生成一般建议
        general_advice = self._generate_general_advice(user_analysis)

        return RecommendationReport(
            user_id=user_id,
            generated_at=datetime.utcnow(),
            topic_recommendations=topic_recommendations,
            difficulty_recommendation=difficulty_recommendation,
            learning_path=learning_path,
            practice_methods=practice_methods,
            general_advice=general_advice
        )

    def _analyze_user_data(self, sessions: List[Dict[str, Any]],
                          learning_profile: Optional[Dict[str, Any]],
                          behavior_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """分析用户数据"""
        analysis = {
            "total_sessions": len(sessions),
            "avg_score": 0.0,
            "dimension_scores": {},
            "weaknesses": [],
            "strengths": [],
            "learning_pattern": "unknown",
            "engagement_level": "unknown",
            "in_plateau": False,
            "current_difficulty": DifficultyLevel.BEGINNER,
        }

        # 从会话数据计算
        if sessions:
            scores = []
            dimension_totals = {}
            dimension_counts = {}

            for session in sessions:
                eval_result = session.get("evaluation_result", {})
                overall = eval_result.get("overall_quality", 0.0)
                if overall > 0:
                    scores.append(overall)

                for dim, score in eval_result.items():
                    if dim != "overall_quality" and score > 0:
                        if dim not in dimension_totals:
                            dimension_totals[dim] = 0
                            dimension_counts[dim] = 0
                        dimension_totals[dim] += score
                        dimension_counts[dim] += 1

            if scores:
                analysis["avg_score"] = statistics.mean(scores)

            for dim in dimension_totals:
                analysis["dimension_scores"][dim] = (
                    dimension_totals[dim] / dimension_counts[dim]
                )

            # 确定当前难度
            analysis["current_difficulty"] = self._determine_difficulty_from_score(
                analysis["avg_score"]
            )

        # 从学习画像获取
        if learning_profile:
            analysis["learning_pattern"] = learning_profile.get("learning_pattern", "unknown")
            analysis["weaknesses"] = learning_profile.get("weaknesses", [])
            analysis["strengths"] = learning_profile.get("strengths", [])

        # 从行为报告获取
        if behavior_report:
            analysis["engagement_level"] = behavior_report.get("engagement", {}).get("level", "unknown")
            plateau = behavior_report.get("plateau_analysis", {})
            analysis["in_plateau"] = plateau.get("status") == "in_plateau"

        return analysis

    def _determine_difficulty_from_score(self, avg_score: float) -> DifficultyLevel:
        """根据平均分确定难度级别"""
        for level, (min_score, max_score) in self.DIFFICULTY_THRESHOLDS.items():
            if min_score <= avg_score < max_score:
                return level
        return DifficultyLevel.EXPERT

    # =========================================================================
    # Topic Recommendations
    # =========================================================================

    def _generate_topic_recommendations(self, user_analysis: Dict[str, Any]) -> List[TopicRecommendation]:
        """生成主题推荐"""
        recommendations = []

        # 基于弱点推荐
        weaknesses = user_analysis.get("weaknesses", [])
        for weakness in weaknesses[:3]:  # 最多 3 个弱点
            dim = weakness.get("dimension", "")
            priority_map = {"high": 5, "medium": 3, "low": 1}
            priority = priority_map.get(weakness.get("priority", "low"), 2)

            topics = self.DIMENSION_TOPICS.get(dim, [])
            for topic in topics[:2]:  # 每个维度最多 2 个主题
                rec = TopicRecommendation(
                    topic_id=topic["id"],
                    topic_name=topic["name"],
                    dimension=dim,
                    reason=f"针对{self._get_dimension_name(dim)}弱项的专项练习",
                    priority=priority,
                    estimated_duration_minutes=20,
                    difficulty=topic["difficulty"],
                    expected_improvement=5.0 + priority  # 优先级越高，预期提升越大
                )
                recommendations.append(rec)

        # 如果没有弱点，基于维度分数推荐
        if not recommendations and user_analysis["dimension_scores"]:
            dim_scores = user_analysis["dimension_scores"]
            sorted_dims = sorted(dim_scores.items(), key=lambda x: x[1])

            for dim, score in sorted_dims[:2]:  # 最低的 2 个维度
                if score < 80:  # 只对低于 80 分的维度推荐
                    topics = self.DIMENSION_TOPICS.get(dim, [])
                    for topic in topics[:1]:
                        rec = TopicRecommendation(
                            topic_id=topic["id"],
                            topic_name=topic["name"],
                            dimension=dim,
                            reason=f"提升{self._get_dimension_name(dim)}能力",
                            priority=3,
                            estimated_duration_minutes=15,
                            difficulty=topic["difficulty"],
                            expected_improvement=3.0
                        )
                        recommendations.append(rec)

        # 按优先级排序
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        return recommendations[:5]  # 最多返回 5 个推荐

    def _get_dimension_name(self, dimension: str) -> str:
        """获取维度中文名"""
        names = {
            "language_expression": "语言表达能力",
            "logical_thinking": "逻辑思维",
            "professional_knowledge": "专业知识",
            "problem_solving": "问题解决",
            "communication_collaboration": "沟通协作",
            "adaptability": "应变能力",
            "overall_quality": "综合素质",
        }
        return names.get(dimension, dimension)

    # =========================================================================
    # Difficulty Recommendation
    # =========================================================================

    def _generate_difficulty_recommendation(self, user_analysis: Dict[str, Any]) -> DifficultyRecommendation:
        """生成难度推荐"""
        current_level = user_analysis.get("current_difficulty", DifficultyLevel.BEGINNER)
        avg_score = user_analysis.get("avg_score", 0.0)
        in_plateau = user_analysis.get("in_plateau", False)
        learning_pattern = user_analysis.get("learning_pattern", "unknown")

        # 确定推荐级别
        recommended_level = current_level
        reason = "保持当前难度，稳步提升"
        confidence = 0.8
        adjustment_factors = []

        # 基于分数调整
        if avg_score >= 85:
            recommended_level = self._get_next_difficulty(current_level)
            reason = "表现优秀，建议提升难度"
            confidence = 0.9
            adjustment_factors.append("高分数表现")
        elif avg_score < 50:
            recommended_level = self._get_prev_difficulty(current_level)
            reason = "建议降低难度，夯实基础"
            confidence = 0.85
            adjustment_factors.append("基础需要加强")

        # 基于平台期调整
        if in_plateau and current_level != DifficultyLevel.BEGINNER:
            recommended_level = self._get_prev_difficulty(current_level)
            reason = "处于平台期，适当降低难度重建信心"
            confidence = 0.75
            adjustment_factors.append("平台期调整")

        # 基于学习模式调整
        if learning_pattern == "burst":
            adjustment_factors.append("爆发式学习，注意难度梯度")

        return DifficultyRecommendation(
            recommended_level=recommended_level,
            current_level=current_level,
            reason=reason,
            confidence=confidence,
            adjustment_factors=adjustment_factors
        )

    def _get_next_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """获取下一个难度级别"""
        order = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
            DifficultyLevel.EXPERT,
        ]
        idx = order.index(current)
        if idx < len(order) - 1:
            return order[idx + 1]
        return current

    def _get_prev_difficulty(self, current: DifficultyLevel) -> DifficultyLevel:
        """获取上一个难度级别"""
        order = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
            DifficultyLevel.EXPERT,
        ]
        idx = order.index(current)
        if idx > 0:
            return order[idx - 1]
        return current

    # =========================================================================
    # Learning Path Generation
    # =========================================================================

    def _generate_learning_path(self, user_id: str,
                                user_analysis: Dict[str, Any],
                                topic_recommendations: List[TopicRecommendation]) -> LearningPath:
        """生成学习路径"""
        path_id = f"path_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}"

        # 确定路径长度
        if user_analysis["total_sessions"] < 5:
            duration_days = 7  # 新手 7 天路径
        elif user_analysis["total_sessions"] < 20:
            duration_days = 14  # 中级 14 天路径
        else:
            duration_days = 21  # 高级 21 天路径

        # 生成路径项目
        items = self._create_path_items(duration_days, topic_recommendations, user_analysis)

        # 生成预期结果
        expected_outcomes = self._generate_expected_outcomes(topic_recommendations, duration_days)

        # 生成成功标准
        success_criteria = self._generate_success_criteria(user_analysis)

        return LearningPath(
            path_id=path_id,
            user_id=user_id,
            duration_days=duration_days,
            items=items,
            expected_outcomes=expected_outcomes,
            success_criteria=success_criteria,
            created_at=datetime.utcnow()
        )

    def _create_path_items(self, duration_days: int,
                          topic_recommendations: List[TopicRecommendation],
                          user_analysis: Dict[str, Any]) -> List[LearningPathItem]:
        """创建路径项目"""
        items = []
        step = 1

        # 按难度分组推荐
        topics_by_difficulty = {}
        for rec in topic_recommendations:
            diff = rec.difficulty
            if diff not in topics_by_difficulty:
                topics_by_difficulty[diff] = []
            topics_by_difficulty[diff].append(rec)

        # 创建每周计划
        weeks = duration_days // 7
        for week in range(weeks):
            # 每周的练习日（5 天练习，2 天休息）
            for day in range(7):
                day_num = week * 7 + day + 1
                if day_num > duration_days:
                    break

                if day >= 5:  # 休息日
                    item = LearningPathItem(
                        step=step,
                        activity_type="rest",
                        description=f"第{day_num}天：休息与反思",
                        topic=None,
                        difficulty=DifficultyLevel.BEGINNER,
                        duration_minutes=0,
                        goals=["放松身心", "回顾本周学习"],
                    )
                else:
                    # 选择主题
                    topic_rec = self._select_topic_for_day(
                        day, week, topic_recommendations, topics_by_difficulty
                    )

                    activity_type = "practice"
                    if day == 4:  # 每周五为挑战日
                        activity_type = "challenge"

                    item = LearningPathItem(
                        step=step,
                        activity_type=activity_type,
                        description=f"第{day_num}天：{topic_rec.topic_name if topic_rec else '综合练习'}",
                        topic=topic_rec.topic_id if topic_rec else None,
                        difficulty=topic_rec.difficulty if topic_rec else DifficultyLevel.INTERMEDIATE,
                        duration_minutes=topic_rec.estimated_duration_minutes if topic_rec else 20,
                        goals=[
                            f"练习{topic_rec.topic_name if topic_rec else '综合技能'}",
                            "记录练习心得",
                        ] if topic_rec else ["综合练习", "查漏补缺"],
                    )

                items.append(item)
                step += 1

        return items

    def _select_topic_for_day(self, day: int, week: int,
                             topic_recommendations: List[TopicRecommendation],
                             topics_by_difficulty: Dict[DifficultyLevel, List[TopicRecommendation]]
                             ) -> Optional[TopicRecommendation]:
        """为每天选择主题"""
        if not topic_recommendations:
            return None

        # 第一周：重点练习弱点
        if week == 0:
            if day < len(topic_recommendations):
                return topic_recommendations[day]

        # 后续周：循环练习
        idx = day % len(topic_recommendations)
        return topic_recommendations[idx]

    def _generate_expected_outcomes(self, topic_recommendations: List[TopicRecommendation],
                                   duration_days: int) -> List[str]:
        """生成预期结果"""
        outcomes = []

        total_improvement = sum(rec.expected_improvement for rec in topic_recommendations)
        avg_improvement = total_improvement / max(1, len(topic_recommendations))

        outcomes.append(f"总体能力提升{avg_improvement * (duration_days / 7):.1f}%")
        outcomes.append(f"完成{len(topic_recommendations)}个专项练习")
        outcomes.append("建立稳定的练习习惯")

        if duration_days >= 14:
            outcomes.append("突破当前平台期")

        if duration_days >= 21:
            outcomes.append("达到新的技能水平")

        return outcomes

    def _generate_success_criteria(self, user_analysis: Dict[str, Any]) -> List[str]:
        """生成成功标准"""
        criteria = []

        current_score = user_analysis.get("avg_score", 0.0)

        criteria.append(f"练习完成率达到 80%")
        criteria.append(f"平均分提升{max(5, current_score * 0.1):.1f}分以上")

        if user_analysis.get("weaknesses"):
            criteria.append("弱点维度分数提升 10 分以上")

        criteria.append("建立连续 7 天练习习惯")

        return criteria

    # =========================================================================
    # Practice Method Recommendations
    # =========================================================================

    def _generate_practice_methods(self, user_analysis: Dict[str, Any]) -> List[PracticeMethodRecommendation]:
        """生成练习方法推荐"""
        methods = []

        # 基于用户情况选择适合的方法
        suitable_methods = []

        if user_analysis.get("in_plateau"):
            suitable_methods.append("deliberate_practice")
            suitable_methods.append("scenario_variation")

        if user_analysis.get("learning_pattern") == "irregular":
            suitable_methods.append("spaced_repetition")

        if user_analysis.get("engagement_level") in ["low", "inactive"]:
            suitable_methods.append("peer_learning")

        if user_analysis.get("weaknesses"):
            suitable_methods.append("deliberate_practice")
            suitable_methods.append("reflection_practice")

        # 默认至少推荐 2 个方法
        if len(suitable_methods) < 2:
            suitable_methods.extend(["deliberate_practice", "reflection_practice"])

        # 去重
        suitable_methods = list(dict.fromkeys(suitable_methods))[:3]

        for method_key in suitable_methods:
            method_data = self.PRACTICE_METHODS.get(method_key, {})
            if method_data:
                methods.append(PracticeMethodRecommendation(
                    method_name=method_data["name"],
                    description=method_data["description"],
                    suitable_for=method_data["suitable_for"],
                    steps=method_data["steps"],
                    tips=method_data["tips"],
                ))

        return methods

    # =========================================================================
    # General Advice
    # =========================================================================

    def _generate_general_advice(self, user_analysis: Dict[str, Any]) -> List[str]:
        """生成一般建议"""
        advice = []

        # 基于练习频率
        total_sessions = user_analysis.get("total_sessions", 0)
        if total_sessions < 5:
            advice.append("刚开始练习，建议从每天 15 分钟开始建立习惯")
        elif total_sessions < 20:
            advice.append("保持当前的练习频率，逐步增加难度")
        else:
            advice.append("练习量充足，注重练习质量和反思")

        # 基于平台期
        if user_analysis.get("in_plateau"):
            advice.append("平台期是正常现象，尝试新的练习方法或适当休息")

        # 基于学习模式
        pattern = user_analysis.get("learning_pattern", "")
        if pattern == "burst":
            advice.append("爆发式学习后记得安排复习时间，巩固所学内容")
        elif pattern == "irregular":
            advice.append("尝试固定练习时间，建立规律的学习习惯")

        # 基于弱点
        if user_analysis.get("weaknesses"):
            advice.append("针对弱点进行刻意练习，不要回避困难")

        # 通用建议
        advice.append("每次练习后进行反思，记录收获和改进点")
        advice.append("定期回顾之前的练习，观察进步轨迹")

        return advice

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self, report: RecommendationReport) -> Dict[str, Any]:
        """将 RecommendationReport 转换为字典"""
        return {
            "user_id": report.user_id,
            "generated_at": report.generated_at.isoformat(),
            "topic_recommendations": [
                {
                    "topic_id": t.topic_id,
                    "topic_name": t.topic_name,
                    "dimension": t.dimension,
                    "reason": t.reason,
                    "priority": t.priority,
                    "estimated_duration_minutes": t.estimated_duration_minutes,
                    "difficulty": t.difficulty.value,
                    "expected_improvement": round(t.expected_improvement, 2),
                }
                for t in report.topic_recommendations
            ],
            "difficulty_recommendation": {
                "recommended_level": report.difficulty_recommendation.recommended_level.value,
                "current_level": report.difficulty_recommendation.current_level.value,
                "reason": report.difficulty_recommendation.reason,
                "confidence": round(report.difficulty_recommendation.confidence, 2),
                "adjustment_factors": report.difficulty_recommendation.adjustment_factors,
            } if report.difficulty_recommendation else None,
            "learning_path": {
                "path_id": report.learning_path.path_id,
                "duration_days": report.learning_path.duration_days,
                "items": [
                    {
                        "step": i.step,
                        "activity_type": i.activity_type,
                        "description": i.description,
                        "topic": i.topic,
                        "difficulty": i.difficulty.value,
                        "duration_minutes": i.duration_minutes,
                        "goals": i.goals,
                    }
                    for i in report.learning_path.items
                ],
                "expected_outcomes": report.learning_path.expected_outcomes,
                "success_criteria": report.learning_path.success_criteria,
                "created_at": report.learning_path.created_at.isoformat(),
            } if report.learning_path else None,
            "practice_methods": [
                {
                    "method_name": m.method_name,
                    "description": m.description,
                    "suitable_for": m.suitable_for,
                    "steps": m.steps,
                    "tips": m.tips,
                }
                for m in report.practice_methods
            ],
            "general_advice": report.general_advice,
        }

    def clear_cache(self):
        """清除缓存"""
        self._topic_cache.clear()
        self._path_cache.clear()
