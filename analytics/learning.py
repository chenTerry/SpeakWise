"""
Learning Analytics Module

学习分析模块提供：
- LearningAnalytics: 学习数据分析系统
- 学习模式识别
- 强弱项分析
- 学习洞察生成

Version: v0.7.0
Author: AgentScope AI Interview Team
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics


class LearningPattern(str, Enum):
    """学习模式类型"""
    CONSISTENT = "consistent"  # 稳定型
    BURST = "burst"  # 爆发型
    GRADUAL = "gradual"  # 渐进型
    IRREGULAR = "irregular"  # 不规则型
    DECLINING = "declining"  # 衰退型


class SkillLevel(str, Enum):
    """技能水平等级"""
    BEGINNER = "beginner"  # 初学者
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家


@dataclass
class LearningStrength:
    """学习优势"""
    dimension: str
    score: float
    confidence: float  # 0-1，置信度
    evidence_count: int  # 证据数量
    trend: str  # improving, stable, declining


@dataclass
class LearningWeakness:
    """学习弱点"""
    dimension: str
    score: float
    priority: str  # high, medium, low
    improvement_suggestions: List[str] = field(default_factory=list)


@dataclass
class LearningInsight:
    """学习洞察"""
    insight_type: str  # pattern, strength, weakness, recommendation
    title: str
    description: str
    confidence: float
    actionable_items: List[str] = field(default_factory=list)
    data_support: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningProfile:
    """学习者画像"""
    user_id: str
    skill_level: SkillLevel
    learning_pattern: LearningPattern
    total_sessions: int
    total_hours: float
    avg_score: float
    strengths: List[LearningStrength] = field(default_factory=list)
    weaknesses: List[LearningWeakness] = field(default_factory=list)
    insights: List[LearningInsight] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for compatibility"""
        if hasattr(self, key):
            value = getattr(self, key)
            # Convert enum to string for compatibility
            if isinstance(value, Enum):
                return value.value
            return value
        return default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "skill_level": self.skill_level.value if isinstance(self.skill_level, Enum) else self.skill_level,
            "learning_pattern": self.learning_pattern.value if isinstance(self.learning_pattern, Enum) else self.learning_pattern,
            "total_sessions": self.total_sessions,
            "total_hours": self.total_hours,
            "avg_score": self.avg_score,
            "strengths": [{"dimension": s.dimension, "score": s.score, "trend": s.trend} for s in self.strengths],
            "weaknesses": [{"dimension": w.dimension, "score": w.score, "impact": w.impact} for w in self.weaknesses],
            "insights": [{"title": i.title, "description": i.description} for i in self.insights],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LearningAnalytics:
    """
    学习分析器

    负责分析用户学习数据，识别学习模式，发现强弱项，生成学习洞察

    Design Principles:
    - 数据驱动：基于历史数据进行客观分析
    - 隐私优先：仅分析匿名化数据
    - 可操作性：提供具体可行的改进建议
    - 可扩展性：支持自定义分析维度
    """

    # 七维度评估指标映射
    DIMENSION_NAMES = {
        "language_expression": "语言表达能力",
        "logical_thinking": "逻辑思维能力",
        "professional_knowledge": "专业知识掌握",
        "problem_solving": "问题解决能力",
        "communication_collaboration": "沟通协作能力",
        "adaptability": "应变能力",
        "overall_quality": "综合素质",
    }

    # 技能水平阈值
    SKILL_LEVEL_THRESHOLDS = {
        SkillLevel.BEGINNER: (0, 60),
        SkillLevel.INTERMEDIATE: (60, 75),
        SkillLevel.ADVANCED: (75, 90),
        SkillLevel.EXPERT: (90, 100),
    }

    # 学习模式识别参数
    PATTERN_DETECTION_PARAMS = {
        "consistency_threshold": 0.7,  # 一致性阈值
        "burst_ratio": 2.0,  # 爆发比例
        "trend_significance": 0.3,  # 趋势显著性
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化学习分析器

        Args:
            config: 配置字典，可覆盖默认参数
        """
        self.config = config or {}
        self.params = {**self.PATTERN_DETECTION_PARAMS, **self.config.get("params", {})}
        self._cache: Dict[str, Any] = {}

    # =========================================================================
    # Learning Profile Generation
    # =========================================================================

    def generate_learning_profile(self, user_id: str,
                                  sessions: List[Dict[str, Any]]) -> LearningProfile:
        """
        生成学习者画像

        Args:
            user_id: 用户 ID
            sessions: 会话数据列表

        Returns:
            LearningProfile 对象
        """
        if not sessions:
            return self._create_empty_profile(user_id)

        # 计算基础统计
        total_sessions = len(sessions)
        total_hours = sum(s.get("duration_seconds", 0) for s in sessions) / 3600
        avg_score = self._calculate_average_score(sessions)

        # 识别技能水平
        skill_level = self._identify_skill_level(avg_score)

        # 识别学习模式
        learning_pattern = self._identify_learning_pattern(sessions)

        # 分析优势
        strengths = self._analyze_strengths(sessions)

        # 分析弱点
        weaknesses = self._analyze_weaknesses(sessions)

        # 生成洞察
        insights = self._generate_insights(sessions, strengths, weaknesses, learning_pattern)

        return LearningProfile(
            user_id=user_id,
            skill_level=skill_level,
            learning_pattern=learning_pattern,
            total_sessions=total_sessions,
            total_hours=total_hours,
            avg_score=avg_score,
            strengths=strengths,
            weaknesses=weaknesses,
            insights=insights,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def _create_empty_profile(self, user_id: str) -> LearningProfile:
        """创建空画像"""
        return LearningProfile(
            user_id=user_id,
            skill_level=SkillLevel.BEGINNER,
            learning_pattern=LearningPattern.IRREGULAR,
            total_sessions=0,
            total_hours=0.0,
            avg_score=0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    # =========================================================================
    # Skill Level Identification
    # =========================================================================

    def _identify_skill_level(self, avg_score: float) -> SkillLevel:
        """
        识别技能水平

        Args:
            avg_score: 平均分数

        Returns:
            SkillLevel 枚举值
        """
        for level, (min_score, max_score) in self.SKILL_LEVEL_THRESHOLDS.items():
            if min_score <= avg_score < max_score:
                return level
        return SkillLevel.EXPERT

    def _calculate_average_score(self, sessions: List[Dict[str, Any]]) -> float:
        """
        计算平均分数

        Args:
            sessions: 会话数据列表

        Returns:
            平均分数 (0-100)
        """
        scores = []
        for session in sessions:
            eval_result = session.get("evaluation_result", {})
            score = eval_result.get("overall_quality", 0.0)
            if score > 0:
                scores.append(score)

        return statistics.mean(scores) if scores else 0.0

    # =========================================================================
    # Learning Pattern Recognition
    # =========================================================================

    def _identify_learning_pattern(self, sessions: List[Dict[str, Any]]) -> LearningPattern:
        """
        识别学习模式

        Args:
            sessions: 会话数据列表

        Returns:
            LearningPattern 枚举值
        """
        if len(sessions) < 3:
            return LearningPattern.IRREGULAR

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 提取会话间隔
        intervals = self._calculate_session_intervals(sorted_sessions)

        # 提取分数趋势
        scores = [
            s.get("evaluation_result", {}).get("overall_quality", 0.0)
            for s in sorted_sessions
        ]

        # 分析一致性
        consistency = self._analyze_consistency(intervals)

        # 分析趋势
        trend = self._analyze_score_trend(scores)

        # 识别爆发模式
        is_burst = self._detect_burst_pattern(intervals)

        # 综合判断
        if consistency >= self.params["consistency_threshold"]:
            if trend > self.params["trend_significance"]:
                return LearningPattern.GRADUAL
            return LearningPattern.CONSISTENT
        elif is_burst:
            return LearningPattern.BURST
        elif trend < -self.params["trend_significance"]:
            return LearningPattern.DECLINING
        else:
            return LearningPattern.IRREGULAR

    def _calculate_session_intervals(self, sessions: List[Dict[str, Any]]) -> List[float]:
        """计算会话间隔（小时）"""
        intervals = []
        for i in range(1, len(sessions)):
            prev_time = sessions[i - 1].get("completed_at", datetime.utcnow())
            curr_time = sessions[i].get("completed_at", datetime.utcnow())

            if isinstance(prev_time, str):
                prev_time = datetime.fromisoformat(prev_time)
            if isinstance(curr_time, str):
                curr_time = datetime.fromisoformat(curr_time)

            interval = (curr_time - prev_time).total_seconds() / 3600
            intervals.append(interval)

        return intervals

    def _analyze_consistency(self, intervals: List[float]) -> float:
        """
        分析一致性

        Returns:
            一致性分数 (0-1)
        """
        if len(intervals) < 2:
            return 0.0

        # 计算变异系数（CV）
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 1.0

        std_interval = statistics.stdev(intervals)
        cv = std_interval / mean_interval

        # CV 越小，一致性越高
        consistency = max(0, 1 - cv)
        return consistency

    def _analyze_score_trend(self, scores: List[float]) -> float:
        """
        分析分数趋势

        Returns:
            趋势值 (-1 到 1，正数表示上升)
        """
        if len(scores) < 2:
            return 0.0

        # 使用线性回归斜率
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(scores)

        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # 归一化到 -1 到 1
        normalized_trend = slope / 10  # 假设最大变化为 10 分/会话
        return max(-1, min(1, normalized_trend))

    def _detect_burst_pattern(self, intervals: List[float]) -> bool:
        """检测爆发模式（短时间内大量练习）"""
        if len(intervals) < 3:
            return False

        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return False

        # 检查是否有显著小于平均值的间隔
        short_intervals = [i for i in intervals if i < mean_interval / self.params["burst_ratio"]]

        return len(short_intervals) > len(intervals) * 0.3

    # =========================================================================
    # Strength Analysis
    # =========================================================================

    def _analyze_strengths(self, sessions: List[Dict[str, Any]]) -> List[LearningStrength]:
        """
        分析学习优势

        Args:
            sessions: 会话数据列表

        Returns:
            LearningStrength 列表
        """
        if not sessions:
            return []

        # 计算各维度平均分
        dimension_stats = self._calculate_dimension_statistics(sessions)

        strengths = []
        overall_avg = statistics.mean(
            stats["avg"] for stats in dimension_stats.values()
            if stats["avg"] > 0
        ) if dimension_stats else 0

        for dim, stats in dimension_stats.items():
            if stats["avg"] == 0:
                continue

            # 优势：显著高于平均水平
            if stats["avg"] >= overall_avg * 1.15:  # 高于平均 15%
                confidence = min(1.0, stats["count"] / 10)  # 基于样本数的置信度
                trend = self._calculate_dimension_trend(sessions, dim)

                strengths.append(LearningStrength(
                    dimension=dim,
                    score=stats["avg"],
                    confidence=confidence,
                    evidence_count=stats["count"],
                    trend=trend
                ))

        # 按分数排序
        strengths.sort(key=lambda s: s.score, reverse=True)
        return strengths[:3]  # 返回前 3 个优势

    # =========================================================================
    # Weakness Analysis
    # =========================================================================

    def _analyze_weaknesses(self, sessions: List[Dict[str, Any]]) -> List[LearningWeakness]:
        """
        分析学习弱点

        Args:
            sessions: 会话数据列表

        Returns:
            LearningWeakness 列表
        """
        if not sessions:
            return []

        # 计算各维度平均分
        dimension_stats = self._calculate_dimension_statistics(sessions)

        weaknesses = []
        overall_avg = statistics.mean(
            stats["avg"] for stats in dimension_stats.values()
            if stats["avg"] > 0
        ) if dimension_stats else 0

        for dim, stats in dimension_stats.items():
            if stats["avg"] == 0:
                continue

            # 弱点：显著低于平均水平或绝对分数低
            is_weak = (stats["avg"] < overall_avg * 0.85) or (stats["avg"] < 60)

            if is_weak:
                # 确定优先级
                if stats["avg"] < 50:
                    priority = "high"
                elif stats["avg"] < 60:
                    priority = "medium"
                else:
                    priority = "low"

                # 生成改进建议
                suggestions = self._generate_improvement_suggestions(dim, stats["avg"])

                weaknesses.append(LearningWeakness(
                    dimension=dim,
                    score=stats["avg"],
                    priority=priority,
                    improvement_suggestions=suggestions
                ))

        # 按优先级和分数排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        weaknesses.sort(key=lambda w: (priority_order[w.priority], w.score))
        return weaknesses[:3]  # 返回前 3 个弱点

    def _calculate_dimension_statistics(self, sessions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """计算各维度统计数据"""
        dimension_data: Dict[str, List[float]] = {}

        for session in sessions:
            eval_result = session.get("evaluation_result", {})
            for dim in self.DIMENSION_NAMES.keys():
                score = eval_result.get(dim, 0.0)
                if score > 0:
                    if dim not in dimension_data:
                        dimension_data[dim] = []
                    dimension_data[dim].append(score)

        # 计算统计量
        stats = {}
        for dim, scores in dimension_data.items():
            stats[dim] = {
                "avg": statistics.mean(scores),
                "std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "count": len(scores),
            }

        return stats

    def _calculate_dimension_trend(self, sessions: List[Dict[str, Any]],
                                   dimension: str) -> str:
        """计算特定维度的趋势"""
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        if len(sorted_sessions) < 3:
            return "stable"

        # 取最近 3 次的分数
        recent_scores = []
        for session in sorted_sessions[-3:]:
            score = session.get("evaluation_result", {}).get(dimension, 0.0)
            if score > 0:
                recent_scores.append(score)

        if len(recent_scores) < 3:
            return "stable"

        # 判断趋势
        if recent_scores[0] < recent_scores[1] < recent_scores[2]:
            return "improving"
        elif recent_scores[0] > recent_scores[1] > recent_scores[2]:
            return "declining"
        else:
            return "stable"

    def _generate_improvement_suggestions(self, dimension: str,
                                          score: float) -> List[str]:
        """生成改进建议"""
        suggestions_map = {
            "language_expression": [
                "多进行口头表达练习，可以录音后回听改进",
                "阅读优秀文章，学习表达技巧",
                "参加演讲或辩论活动提升表达能力",
            ],
            "logical_thinking": [
                "练习结构化思考，使用金字塔原理",
                "学习逻辑思维课程，掌握推理方法",
                "在回答前先构建框架，再展开论述",
            ],
            "professional_knowledge": [
                "系统学习相关专业知识体系",
                "关注行业动态，保持知识更新",
                "通过项目实践深化理解",
            ],
            "problem_solving": [
                "学习问题分析框架（如 5W1H）",
                "多做案例分析练习",
                "培养多角度思考问题的习惯",
            ],
            "communication_collaboration": [
                "练习积极倾听技巧",
                "学习非暴力沟通方法",
                "参与团队项目提升协作能力",
            ],
            "adaptability": [
                "尝试不同类型的面试场景",
                "练习应对压力情境",
                "培养灵活应变的思维方式",
            ],
            "overall_quality": [
                "全面提升各维度能力",
                "增加练习频率和多样性",
                "寻求专业反馈和指导",
            ],
        }

        base_suggestions = suggestions_map.get(dimension, [])

        # 根据分数调整建议
        if score < 50:
            return [
                "建议从基础开始系统学习",
                "增加练习频率，每天至少 15 分钟",
                "寻求导师或同伴反馈",
            ] + base_suggestions[:2]
        elif score < 60:
            return base_suggestions[:3]
        else:
            return base_suggestions[:2]

    # =========================================================================
    # Insight Generation
    # =========================================================================

    def _generate_insights(self, sessions: List[Dict[str, Any]],
                          strengths: List[LearningStrength],
                          weaknesses: List[LearningWeakness],
                          learning_pattern: LearningPattern) -> List[LearningInsight]:
        """
        生成学习洞察

        Args:
            sessions: 会话数据列表
            strengths: 优势列表
            weaknesses: 弱点列表
            learning_pattern: 学习模式

        Returns:
            LearningInsight 列表
        """
        insights = []

        # 学习模式洞察
        pattern_insight = self._create_pattern_insight(learning_pattern, sessions)
        if pattern_insight:
            insights.append(pattern_insight)

        # 优势洞察
        for strength in strengths[:2]:
            insight = self._create_strength_insight(strength)
            if insight:
                insights.append(insight)

        # 弱点洞察
        for weakness in weaknesses[:2]:
            insight = self._create_weakness_insight(weakness)
            if insight:
                insights.append(insight)

        # 趋势洞察
        trend_insight = self._create_trend_insight(sessions)
        if trend_insight:
            insights.append(trend_insight)

        return insights

    def _create_pattern_insight(self, pattern: LearningPattern,
                                sessions: List[Dict[str, Any]]) -> Optional[LearningInsight]:
        """创建学习模式洞察"""
        pattern_descriptions = {
            LearningPattern.CONSISTENT: {
                "title": "稳定的学习习惯",
                "description": "您保持着稳定的练习节奏，这是持续进步的关键。",
                "actionable_items": [
                    "继续保持当前的练习频率",
                    "尝试增加练习难度以挑战自我",
                ],
            },
            LearningPattern.BURST: {
                "title": "爆发式学习模式",
                "description": "您倾向于在短时间内集中练习，这种方式效率高但需要注意休息。",
                "actionable_items": [
                    "在爆发练习后安排复习时间",
                    "尝试分散练习以加强长期记忆",
                ],
            },
            LearningPattern.GRADUAL: {
                "title": "渐进式进步",
                "description": "您的能力在稳步提升，这种渐进式学习非常健康。",
                "actionable_items": [
                    "设定阶段性目标以保持动力",
                    "记录进步轨迹以增强信心",
                ],
            },
            LearningPattern.IRREGULAR: {
                "title": "不规律的学习节奏",
                "description": "您的练习时间不太规律，建立固定习惯可能会有帮助。",
                "actionable_items": [
                    "设定固定的练习时间",
                    "使用提醒工具保持练习习惯",
                    "从每天 10 分钟开始建立习惯",
                ],
            },
            LearningPattern.DECLINING: {
                "title": "需要关注的趋势",
                "description": "近期表现有所下降，可能需要调整学习方法或休息。",
                "actionable_items": [
                    "回顾之前的成功经验",
                    "适当降低难度重建信心",
                    "考虑寻求外部反馈",
                ],
            },
        }

        info = pattern_descriptions.get(pattern)
        if not info:
            return None

        return LearningInsight(
            insight_type="pattern",
            title=info["title"],
            description=info["description"],
            confidence=0.9,
            actionable_items=info["actionable_items"],
            data_support={"pattern": pattern.value}
        )

    def _create_strength_insight(self, strength: LearningStrength) -> Optional[LearningInsight]:
        """创建优势洞察"""
        if strength.confidence < 0.5:
            return None

        dim_name = self.DIMENSION_NAMES.get(strength.dimension, strength.dimension)

        trend_text = {
            "improving": "且在持续进步",
            "stable": "且保持稳定",
            "declining": "但需注意保持",
        }.get(strength.trend, "")

        return LearningInsight(
            insight_type="strength",
            title=f"{dim_name}是您的优势项",
            description=f"您在{dim_name}方面表现优秀（{strength.score:.1f}分）{trend_text}。",
            confidence=strength.confidence,
            actionable_items=[
                f"继续发挥{dim_name}的优势",
                "尝试将这项能力应用到其他领域",
            ],
            data_support={
                "dimension": strength.dimension,
                "score": strength.score,
                "trend": strength.trend,
            }
        )

    def _create_weakness_insight(self, weakness: LearningWeakness) -> Optional[LearningInsight]:
        """创建弱点洞察"""
        dim_name = self.DIMENSION_NAMES.get(weakness.dimension, weakness.dimension)

        priority_text = {
            "high": "需要优先关注",
            "medium": "建议重点关注",
            "low": "可以适当加强",
        }.get(weakness.priority, "")

        return LearningInsight(
            insight_type="weakness",
            title=f"{priority_text}：{dim_name}",
            description=f"您在{dim_name}方面还有提升空间（{weakness.score:.1f}分）。",
            confidence=0.8,
            actionable_items=weakness.improvement_suggestions[:3],
            data_support={
                "dimension": weakness.dimension,
                "score": weakness.score,
                "priority": weakness.priority,
            }
        )

    def _create_trend_insight(self, sessions: List[Dict[str, Any]]) -> Optional[LearningInsight]:
        """创建趋势洞察"""
        if len(sessions) < 5:
            return None

        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 比较前 25% 和后 25% 的平均分
        quarter = max(1, len(sorted_sessions) // 4)
        early_scores = [
            s.get("evaluation_result", {}).get("overall_quality", 0.0)
            for s in sorted_sessions[:quarter]
        ]
        late_scores = [
            s.get("evaluation_result", {}).get("overall_quality", 0.0)
            for s in sorted_sessions[-quarter:]
        ]

        early_avg = statistics.mean(early_scores) if early_scores else 0
        late_avg = statistics.mean(late_scores) if late_scores else 0

        if early_avg == 0:
            return None

        change_rate = ((late_avg - early_avg) / early_avg) * 100

        if abs(change_rate) < 5:
            return None

        if change_rate > 0:
            title = "显著的进步趋势"
            description = f"相比早期，近期表现提升了{change_rate:.1f}%。"
            actionable_items = [
                "总结有效的学习方法并坚持",
                "设定更高的目标继续挑战",
            ]
        else:
            title = "需要调整学习方法"
            description = f"近期表现相比早期下降了{abs(change_rate):.1f}%。"
            actionable_items = [
                "回顾之前的成功经验",
                "尝试不同的练习方式",
                "适当休息后重新开始",
            ]

        return LearningInsight(
            insight_type="trend",
            title=title,
            description=description,
            confidence=0.85,
            actionable_items=actionable_items,
            data_support={
                "early_avg": early_avg,
                "late_avg": late_avg,
                "change_rate": change_rate,
            }
        )

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self, profile: LearningProfile) -> Dict[str, Any]:
        """将 LearningProfile 转换为字典"""
        return {
            "user_id": profile.user_id,
            "skill_level": profile.skill_level.value,
            "learning_pattern": profile.learning_pattern.value,
            "total_sessions": profile.total_sessions,
            "total_hours": round(profile.total_hours, 2),
            "avg_score": round(profile.avg_score, 2),
            "strengths": [
                {
                    "dimension": s.dimension,
                    "score": round(s.score, 2),
                    "confidence": round(s.confidence, 2),
                    "evidence_count": s.evidence_count,
                    "trend": s.trend,
                }
                for s in profile.strengths
            ],
            "weaknesses": [
                {
                    "dimension": w.dimension,
                    "score": round(w.score, 2),
                    "priority": w.priority,
                    "suggestions": w.improvement_suggestions,
                }
                for w in profile.weaknesses
            ],
            "insights": [
                {
                    "type": i.insight_type,
                    "title": i.title,
                    "description": i.description,
                    "confidence": round(i.confidence, 2),
                    "actionable_items": i.actionable_items,
                }
                for i in profile.insights
            ],
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
