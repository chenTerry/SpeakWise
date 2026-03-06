"""
Insights Dashboard Module

洞察仪表盘模块提供：
- InsightsDashboard: 洞察可视化系统
- 关键洞察展示
- 趋势分析
- 可操作建议

Version: v0.7.0
Author: AgentScope AI Interview Team
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics


class InsightCategory(str, Enum):
    """洞察类别"""
    PERFORMANCE = "performance"  # 表现
    PROGRESS = "progress"  # 进步
    BEHAVIOR = "behavior"  # 行为
    RECOMMENDATION = "recommendation"  # 推荐
    ALERT = "alert"  # 警告
    ACHIEVEMENT = "achievement"  # 成就


class InsightPriority(str, Enum):
    """洞察优先级"""
    CRITICAL = "critical"  # 关键
    HIGH = "high"  # 高
    MEDIUM = "medium"  # 中
    LOW = "low"  # 低


@dataclass
class KeyInsight:
    """关键洞察"""
    insight_id: str
    category: InsightCategory
    priority: InsightPriority
    title: str
    description: str
    icon: str  # emoji 或图标名称
    metrics: Dict[str, Any]
    trend: str  # positive, negative, neutral
    actionable_items: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TrendAnalysis:
    """趋势分析"""
    metric_name: str
    current_value: float
    previous_value: float
    change_value: float
    change_percent: float
    trend_direction: str  # upward, downward, stable
    trend_strength: str  # strong, moderate, weak
    forecast_next: float
    confidence: float


@dataclass
class PerformanceCard:
    """表现卡片"""
    dimension: str
    dimension_name: str
    current_score: float
    previous_score: float
    change: float
    percentile: float
    level: str  # excellent, good, average, below_average, poor
    status: str  # improving, stable, declining
    summary: str


@dataclass
class ActionableRecommendation:
    """可操作建议"""
    rec_id: str
    title: str
    description: str
    priority: int  # 1-5
    estimated_impact: str  # high, medium, low
    time_required_minutes: int
    steps: List[str]
    related_dimensions: List[str]


@dataclass
class Achievement:
    """成就徽章"""
    achievement_id: str
    name: str
    description: str
    icon: str
    unlocked_at: datetime
    category: str
    progress: float  # 0-100，如果未完全解锁


@dataclass
class DashboardData:
    """仪表盘数据"""
    user_id: str
    generated_at: datetime
    period_days: int
    key_insights: List[KeyInsight]
    performance_cards: List[PerformanceCard]
    trend_analyses: List[TrendAnalysis]
    recommendations: List[ActionableRecommendation]
    achievements: List[Achievement]
    summary_text: str


class InsightsDashboard:
    """
    洞察仪表盘

    整合各分析模块的数据，生成可视化的洞察仪表盘

    Design Principles:
    - 直观性：一目了然的关键信息
    - 可操作性：提供明确的行动建议
    - 个性化：根据用户特点定制展示
    - 及时性：反映最新的状态和趋势
    """

    # 维度名称映射
    DIMENSION_NAMES = {
        "language_expression": "语言表达能力",
        "logical_thinking": "逻辑思维能力",
        "professional_knowledge": "专业知识掌握",
        "problem_solving": "问题解决能力",
        "communication_collaboration": "沟通协作能力",
        "adaptability": "应变能力",
        "overall_quality": "综合素质",
    }

    # 成就配置
    ACHIEVEMENTS_CONFIG = {
        "first_session": {
            "name": "初次尝试",
            "description": "完成第一次练习",
            "icon": "🎯",
            "category": "milestone",
        },
        "week_streak": {
            "name": "持之以恒",
            "description": "连续练习 7 天",
            "icon": "🔥",
            "category": "streak",
        },
        "high_scorer": {
            "name": "表现优异",
            "description": "单次得分超过 90 分",
            "icon": "🏆",
            "category": "performance",
        },
        "improver": {
            "name": "进步之星",
            "description": "周平均分提升超过 10%",
            "icon": "📈",
            "category": "progress",
        },
        "dedicated": {
            "name": "勤奋学习",
            "description": "累计练习超过 10 小时",
            "icon": "⏰",
            "category": "dedication",
        },
        "versatile": {
            "name": "全面发展",
            "description": "所有维度得分超过 75 分",
            "icon": "🌟",
            "category": "comprehensive",
        },
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化洞察仪表盘

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self._insight_counter = 0
        self._rec_counter = 0

    # =========================================================================
    # Main Dashboard Generation
    # =========================================================================

    def generate_dashboard(self, user_id: str,
                          sessions: List[Dict[str, Any]],
                          learning_profile: Optional[Dict[str, Any]] = None,
                          behavior_report: Optional[Dict[str, Any]] = None,
                          statistical_report: Optional[Dict[str, Any]] = None,
                          recommendation_report: Optional[Dict[str, Any]] = None,
                          period_days: int = 30) -> DashboardData:
        """
        生成仪表盘数据

        Args:
            user_id: 用户 ID
            sessions: 会话数据列表
            learning_profile: 学习画像
            behavior_report: 行为报告
            statistical_report: 统计报告
            recommendation_report: 推荐报告
            period_days: 统计周期

        Returns:
            DashboardData 对象
        """
        # 生成关键洞察
        key_insights = self._generate_key_insights(
            sessions, learning_profile, behavior_report, statistical_report
        )

        # 生成表现卡片
        performance_cards = self._generate_performance_cards(sessions, statistical_report)

        # 生成趋势分析
        trend_analyses = self._generate_trend_analyses(sessions)

        # 生成可操作建议
        recommendations = self._generate_actionable_recommendations(
            learning_profile, behavior_report, recommendation_report
        )

        # 生成成就
        achievements = self._generate_achievements(sessions, learning_profile)

        # 生成摘要文本
        summary_text = self._generate_dashboard_summary(
            key_insights, performance_cards, achievements
        )

        return DashboardData(
            user_id=user_id,
            generated_at=datetime.utcnow(),
            period_days=period_days,
            key_insights=key_insights,
            performance_cards=performance_cards,
            trend_analyses=trend_analyses,
            recommendations=recommendations,
            achievements=achievements,
            summary_text=summary_text
        )

    def _generate_insight_id(self) -> str:
        """生成洞察 ID"""
        self._insight_counter += 1
        return f"insight_{self._insight_counter}"

    def _generate_rec_id(self) -> str:
        """生成建议 ID"""
        self._rec_counter += 1
        return f"rec_{self._rec_counter}"

    # =========================================================================
    # Key Insights Generation
    # =========================================================================

    def _generate_key_insights(self,
                               sessions: List[Dict[str, Any]],
                               learning_profile: Optional[Dict[str, Any]],
                               behavior_report: Optional[Dict[str, Any]],
                               statistical_report: Optional[Dict[str, Any]]) -> List[KeyInsight]:
        """生成关键洞察"""
        insights = []

        # 基于学习画像的洞察
        if learning_profile:
            insights.extend(self._create_learning_insights(learning_profile))

        # 基于行为报告的洞察
        if behavior_report:
            insights.extend(self._create_behavior_insights(behavior_report))

        # 基于统计报告的洞察
        if statistical_report:
            insights.extend(self._create_statistical_insights(statistical_report))

        # 基于会话数据的洞察
        insights.extend(self._create_session_insights(sessions))

        # 按优先级排序
        priority_order = {
            InsightPriority.CRITICAL: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3,
        }
        insights.sort(key=lambda i: priority_order[i.priority])

        return insights[:10]  # 最多显示 10 个关键洞察

    def _create_learning_insights(self, learning_profile: Any) -> List[KeyInsight]:
        """创建学习洞察"""
        insights = []

        # Handle both dict and object types
        def get_value(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # 技能水平洞察
        skill_level = get_value(learning_profile, "skill_level", "unknown")
        if skill_level != "unknown":
            level_names = {
                "beginner": "初学者",
                "intermediate": "中级",
                "advanced": "高级",
                "expert": "专家",
            }
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.PERFORMANCE,
                priority=InsightPriority.MEDIUM,
                title="当前技能水平",
                description=f"您目前的技能水平为{level_names.get(skill_level.value if hasattr(skill_level, 'value') else skill_level, skill_level)}",
                icon="📊",
                metrics={"skill_level": str(skill_level)},
                trend="neutral",
                actionable_items=["继续练习以提升水平", "设定下一个水平目标"],
            ))

        # 学习模式洞察
        learning_pattern = get_value(learning_profile, "learning_pattern", "unknown")
        if learning_pattern != "unknown":
            pattern_info = {
                "consistent": ("稳定的学习习惯", "positive", "继续保持规律的练习节奏"),
                "burst": ("爆发式学习", "neutral", "注意在爆发练习后安排复习"),
                "gradual": ("渐进式进步", "positive", "稳步前进，持续积累"),
                "irregular": ("不规律的学习", "negative", "建议建立固定的练习时间"),
                "declining": ("需要关注的趋势", "negative", "适当调整学习方法或休息"),
            }
            pattern_str = learning_pattern.value if hasattr(learning_pattern, 'value') else str(learning_pattern)
            info = pattern_info.get(pattern_str, ("未知模式", "neutral", ""))
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.BEHAVIOR,
                priority=InsightPriority.MEDIUM if info[1] != "negative" else InsightPriority.HIGH,
                title=info[0],
                description=f"您的学习模式为{info[0]}",
                icon="📈",
                metrics={"learning_pattern": learning_pattern},
                trend=info[1],
                actionable_items=[info[2]],
            ))

        # 优势洞察
        strengths = learning_profile.get("strengths", [])
        for strength in strengths[:2]:
            dim_name = self.DIMENSION_NAMES.get(strength.get("dimension", ""), "未知维度")
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.ACHIEVEMENT,
                priority=InsightPriority.LOW,
                title=f"优势项：{dim_name}",
                description=f"您在{dim_name}方面表现优秀（{strength.get('score', 0):.1f}分）",
                icon="⭐",
                metrics={"dimension": strength.get("dimension"), "score": strength.get("score")},
                trend="positive",
                actionable_items=["继续发挥优势", "帮助其他方面的提升"],
            ))

        # 弱点洞察
        weaknesses = learning_profile.get("weaknesses", [])
        for weakness in weaknesses[:2]:
            dim_name = self.DIMENSION_NAMES.get(weakness.get("dimension", ""), "未知维度")
            priority = InsightPriority.HIGH if weakness.get("priority") == "high" else InsightPriority.MEDIUM
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.RECOMMENDATION,
                priority=priority,
                title=f"需要加强：{dim_name}",
                description=f"建议在{dim_name}方面加强练习（当前{weakness.get('score', 0):.1f}分）",
                icon="💪",
                metrics={"dimension": weakness.get("dimension"), "score": weakness.get("score")},
                trend="negative",
                actionable_items=weakness.get("suggestions", [])[:2],
            ))

        return insights

    def _create_behavior_insights(self, behavior_report: Any) -> List[KeyInsight]:
        """创建行为洞察"""
        insights = []

        # Handle both dict and object types
        def get_value(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # 参与度洞察
        engagement = get_value(behavior_report, "engagement", {})
        level = get_value(engagement, "level", "unknown")
        if level != "unknown":
            level_str = level.value if hasattr(level, 'value') else str(level)
            level_info = {
                "inactive": ("练习较少", "negative", "建议从每天 10 分钟开始"),
                "low": ("低参与度", "negative", "尝试增加练习频率"),
                "medium": ("中等参与度", "neutral", "保持当前节奏，逐步提升"),
                "high": ("高参与度", "positive", "表现优秀，继续保持"),
                "very_high": ("非常高参与度", "positive", "注意劳逸结合"),
            }
            info = level_info.get(level_str, ("未知", "neutral", ""))
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.BEHAVIOR,
                priority=InsightPriority.MEDIUM if info[1] != "negative" else InsightPriority.HIGH,
                title=info[0],
                description=f"当前参与度：{info[0]}",
                icon="🔥",
                metrics={"engagement_level": level},
                trend=info[1],
                actionable_items=[info[2]],
            ))

        # 连续天数洞察
        current_streak = get_value(engagement, "current_streak", 0)
        if current_streak >= 7:
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.ACHIEVEMENT,
                priority=InsightPriority.LOW,
                title="连续练习",
                description=f"已连续练习{current_streak}天",
                icon="🎉",
                metrics={"streak": current_streak},
                trend="positive",
                actionable_items=["继续保持，挑战更长记录"],
            ))
        elif current_streak == 0 and get_value(engagement, "longest_streak", 0) > 0:
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.RECOMMENDATION,
                priority=InsightPriority.MEDIUM,
                title="恢复练习",
                description="练习中断了，加油恢复练习！",
                icon="💪",
                metrics={"current_streak": 0},
                trend="neutral",
                actionable_items=["从今天开始重新练习", "设定小目标重建习惯"],
            ))

        # 平台期洞察
        plateau = get_value(behavior_report, "plateau_analysis", {})
        plateau_status = get_value(plateau, "status", "")
        if plateau_status == "in_plateau":
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.ALERT,
                priority=InsightPriority.HIGH,
                title="平台期提醒",
                description=f"检测到平台期（已持续{get_value(plateau, 'duration_days', 0)}天）",
                icon="⚠️",
                metrics={"plateau_duration": get_value(plateau, "duration_days")},
                trend="negative",
                actionable_items=get_value(plateau, "recommendations", [])[:3],
            ))

        return insights

    def _create_statistical_insights(self, statistical_report: Any) -> List[KeyInsight]:
        """创建统计洞察"""
        insights = []

        # Handle both dict and object types
        def get_value(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # 对比分析洞察
        comparative = get_value(statistical_report, "comparative_analysis")
        if comparative:
            perf_level = get_value(comparative, "performance_level", "average")
            percentile = get_value(comparative, "percentile_rank", 50)

            if perf_level in ["excellent", "good"]:
                insights.append(KeyInsight(
                    insight_id=self._generate_insight_id(),
                    category=InsightCategory.ACHIEVEMENT,
                    priority=InsightPriority.LOW,
                    title="超越多数用户",
                    description=f"您的表现超过了{percentile:.0f}%的用户",
                    icon="🏅",
                    metrics={"percentile": percentile},
                    trend="positive",
                    actionable_items=["继续保持优秀表现"],
                ))
            elif perf_level in ["below_average", "poor"]:
                insights.append(KeyInsight(
                    insight_id=self._generate_insight_id(),
                    category=InsightCategory.RECOMMENDATION,
                    priority=InsightPriority.HIGH,
                    title="有提升空间",
                    description=f"超过了{percentile:.0f}%的用户，还有进步空间",
                    icon="📈",
                    metrics={"percentile": percentile},
                    trend="neutral",
                    actionable_items=["增加练习频率", "针对性强化弱点"],
                ))

        # 趋势洞察
        trend = get_value(statistical_report, "trend_statistics", {})
        trend_dir = get_value(trend, "trend_direction", "stable")
        if trend_dir == "upward":
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.PROGRESS,
                priority=InsightPriority.MEDIUM,
                title="持续进步中",
                description="您的表现呈现上升趋势",
                icon="📈",
                metrics={"trend": trend_dir},
                trend="positive",
                actionable_items=["总结有效方法并坚持"],
            ))
        elif trend_dir == "downward":
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.ALERT,
                priority=InsightPriority.HIGH,
                title="需要关注",
                description="近期表现有所下降",
                icon="📉",
                metrics={"trend": trend_dir},
                trend="negative",
                actionable_items=["回顾成功经验", "调整学习方法"],
            ))

        return insights

    def _create_session_insights(self, sessions: List[Dict[str, Any]]) -> List[KeyInsight]:
        """创建会话洞察"""
        insights = []

        if not sessions:
            return insights

        # 总会话数
        total = len(sessions)
        if total >= 1:
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.ACHIEVEMENT,
                priority=InsightPriority.LOW,
                title="练习统计",
                description=f"已完成{total}次练习",
                icon="📝",
                metrics={"total_sessions": total},
                trend="neutral",
                actionable_items=["继续积累练习量"],
            ))

        # 最佳表现
        best_score = 0
        best_session = None
        for session in sessions:
            score = session.get("evaluation_result", {}).get("overall_quality", 0.0)
            if score > best_score:
                best_score = score
                best_session = session

        if best_score > 0:
            insights.append(KeyInsight(
                insight_id=self._generate_insight_id(),
                category=InsightCategory.ACHIEVEMENT,
                priority=InsightPriority.LOW,
                title="最佳表现",
                description=f"最高得分{best_score:.1f}分",
                icon="🌟",
                metrics={"best_score": best_score},
                trend="positive",
                actionable_items=["回顾最佳表现的经验"],
            ))

        return insights

    # =========================================================================
    # Performance Cards
    # =========================================================================

    def _generate_performance_cards(self, sessions: List[Dict[str, Any]],
                                    statistical_report: Optional[Any]) -> List[PerformanceCard]:
        """生成表现卡片"""
        cards = []

        if not sessions:
            return cards

        # Handle both dict and object types
        def get_value(obj, key, default=None):
            if obj is None:
                return default
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # 计算各维度当前和之前的分数
        dimension_data = self._calculate_dimension_comparison(sessions)

        # 获取百分位数据
        percentile_data = {}
        if statistical_report:
            comp = get_value(statistical_report, "comparative_analysis", {})
            if comp:
                percentile_data["overall_quality"] = get_value(comp, "percentile_rank", 50)

        for dim, data in dimension_data.items():
            dim_name = self.DIMENSION_NAMES.get(dim, dim)
            change = data["current"] - data["previous"]

            # 确定水平
            if data["current"] >= 90:
                level = "excellent"
            elif data["current"] >= 75:
                level = "good"
            elif data["current"] >= 60:
                level = "average"
            elif data["current"] >= 50:
                level = "below_average"
            else:
                level = "poor"

            # 确定状态
            if change > 2:
                status = "improving"
            elif change < -2:
                status = "declining"
            else:
                status = "stable"

            # 生成摘要
            summary = f"{dim_name}: {data['current']:.1f}分"
            if change > 0:
                summary += f" (↑{change:.1f})"
            elif change < 0:
                summary += f" (↓{abs(change):.1f})"

            cards.append(PerformanceCard(
                dimension=dim,
                dimension_name=dim_name,
                current_score=round(data["current"], 1),
                previous_score=round(data["previous"], 1),
                change=round(change, 1),
                percentile=percentile_data.get(dim, 50),
                level=level,
                status=status,
                summary=summary,
            ))

        # 按当前分数排序
        cards.sort(key=lambda c: c.current_score, reverse=True)
        return cards

    def _calculate_dimension_comparison(self, sessions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """计算维度对比数据"""
        if len(sessions) < 2:
            return {}

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 分成前后两半
        mid = len(sorted_sessions) // 2
        early_sessions = sorted_sessions[:mid]
        late_sessions = sorted_sessions[mid:]

        dimensions = list(self.DIMENSION_NAMES.keys())
        dimension_data = {}

        for dim in dimensions:
            early_scores = [
                s.get("evaluation_result", {}).get(dim, 0.0)
                for s in early_sessions
                if s.get("evaluation_result", {}).get(dim, 0.0) > 0
            ]
            late_scores = [
                s.get("evaluation_result", {}).get(dim, 0.0)
                for s in late_sessions
                if s.get("evaluation_result", {}).get(dim, 0.0) > 0
            ]

            current = statistics.mean(late_scores) if late_scores else 0.0
            previous = statistics.mean(early_scores) if early_scores else current

            dimension_data[dim] = {
                "current": current,
                "previous": previous,
            }

        return dimension_data

    # =========================================================================
    # Trend Analyses
    # =========================================================================

    def _generate_trend_analyses(self, sessions: List[Dict[str, Any]]) -> List[TrendAnalysis]:
        """生成趋势分析"""
        analyses = []

        if len(sessions) < 3:
            return analyses

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 分析总体趋势
        overall_trend = self._analyze_metric_trend(sorted_sessions, "overall_quality")
        if overall_trend:
            analyses.append(overall_trend)

        # 分析关键维度趋势
        key_dimensions = ["language_expression", "logical_thinking", "problem_solving"]
        for dim in key_dimensions:
            dim_trend = self._analyze_metric_trend(sorted_sessions, dim)
            if dim_trend:
                analyses.append(dim_trend)

        return analyses

    def _analyze_metric_trend(self, sessions: List[Dict[str, Any]],
                             metric: str) -> Optional[TrendAnalysis]:
        """分析指标趋势"""
        # 提取数据
        values = []
        for session in sessions:
            val = session.get("evaluation_result", {}).get(metric, 0.0)
            if val > 0:
                values.append(val)

        if len(values) < 3:
            return None

        current = values[-1]
        previous = statistics.mean(values[:-1])
        change = current - previous
        change_percent = (change / previous * 100) if previous > 0 else 0

        # 趋势方向
        if change > 3:
            direction = "upward"
            strength = "strong" if change > 5 else "moderate"
        elif change < -3:
            direction = "downward"
            strength = "strong" if change < -5 else "moderate"
        else:
            direction = "stable"
            strength = "weak"

        # 简单预测
        forecast = current + (change * 0.5)  # 假设趋势延续一半

        return TrendAnalysis(
            metric_name=metric,
            current_value=round(current, 2),
            previous_value=round(previous, 2),
            change_value=round(change, 2),
            change_percent=round(change_percent, 2),
            trend_direction=direction,
            trend_strength=strength,
            forecast_next=round(forecast, 2),
            confidence=0.7 if strength == "strong" else 0.5
        )

    # =========================================================================
    # Actionable Recommendations
    # =========================================================================

    def _generate_actionable_recommendations(self,
                                             learning_profile: Optional[Any],
                                             behavior_report: Optional[Any],
                                             recommendation_report: Optional[Any]) -> List[ActionableRecommendation]:
        """生成可操作建议"""
        recommendations = []

        # Handle both dict and object types
        def get_value(obj, key, default=None):
            if obj is None:
                return default
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # 从推荐报告获取
        if recommendation_report:
            topic_recs = get_value(recommendation_report, "topic_recommendations", [])
            for i, rec in enumerate(topic_recs[:3]):
                rec_dict = rec if isinstance(rec, dict) else getattr(rec, '__dict__', {})
                recommendations.append(ActionableRecommendation(
                    rec_id=self._generate_rec_id(),
                    title=get_value(rec, "topic_name", rec_dict.get("topic_name", "专项练习")),
                    description=get_value(rec, "reason", rec_dict.get("reason", "")),
                    priority=get_value(rec, "priority", rec_dict.get("priority", 3)),
                    estimated_impact="high" if get_value(rec, "priority", rec_dict.get("priority", 3)) >= 4 else "medium",
                    time_required_minutes=get_value(rec, "estimated_duration_minutes", rec_dict.get("estimated_duration_minutes", 20)),
                    steps=[
                        f"选择{get_value(rec, 'topic_name', rec_dict.get('topic_name', '该主题'))}练习",
                        "专注练习 20 分钟",
                        "记录练习心得",
                        "回顾反馈并改进",
                    ],
                    related_dimensions=[get_value(rec, "dimension", rec_dict.get("dimension", ""))],
                ))

        # 基于弱点生成
        if learning_profile:
            weaknesses = get_value(learning_profile, "weaknesses", [])
            for weakness in weaknesses[:2]:
                weakness_dict = weakness if isinstance(weakness, dict) else getattr(weakness, '__dict__', {})
                dim = get_value(weakness, "dimension", weakness_dict.get("dimension", ""))
                dim_name = self.DIMENSION_NAMES.get(dim, "该维度")
                suggestions = get_value(weakness, "suggestions", weakness_dict.get("suggestions", []))

                recommendations.append(ActionableRecommendation(
                    rec_id=self._generate_rec_id(),
                    title=f"加强{dim_name}",
                    description=f"针对{dim_name}的专项提升计划",
                    priority=4 if get_value(weakness, "priority", weakness_dict.get("priority")) == "high" else 3,
                    estimated_impact="high",
                    time_required_minutes=30,
                    steps=suggestions[:4] if suggestions else [
                        f"学习{dim_name}相关理论知识",
                        "进行针对性练习",
                        "寻求反馈",
                        "持续改进",
                    ],
                    related_dimensions=[dim],
                ))

        # 基于行为生成
        if behavior_report:
            plateau = get_value(behavior_report, "plateau_analysis", {})
            plateau_status = get_value(plateau, "status", "")
            if plateau_status == "in_plateau":
                recs = get_value(plateau, "recommendations", [])
                recommendations.append(ActionableRecommendation(
                    rec_id=self._generate_rec_id(),
                    title="突破平台期",
                    description="采取新策略突破当前平台期",
                    priority=5,
                    estimated_impact="high",
                    time_required_minutes=15,
                    steps=recs[:4] if recs else [
                        "尝试新的练习方法",
                        "增加练习难度",
                        "寻求外部反馈",
                        "适当休息调整",
                    ],
                    related_dimensions=[],
                ))

        # 按优先级排序
        recommendations.sort(key=lambda r: r.priority, reverse=True)
        return recommendations[:5]

    # =========================================================================
    # Achievements
    # =========================================================================

    def _generate_achievements(self, sessions: List[Dict[str, Any]],
                              learning_profile: Optional[Dict[str, Any]]) -> List[Achievement]:
        """生成成就"""
        achievements = []

        if not sessions:
            return achievements

        # 检查第一次会话
        achievements.append(Achievement(
            achievement_id="first_session",
            name=self.ACHIEVEMENTS_CONFIG["first_session"]["name"],
            description=self.ACHIEVEMENTS_CONFIG["first_session"]["description"],
            icon=self.ACHIEVEMENTS_CONFIG["first_session"]["icon"],
            unlocked_at=sessions[0].get("completed_at", datetime.utcnow()),
            category=self.ACHIEVEMENTS_CONFIG["first_session"]["category"],
            progress=100.0,
        ))

        # 检查连续天数
        streak = self._calculate_current_streak(sessions)
        if streak >= 7:
            achievements.append(Achievement(
                achievement_id="week_streak",
                name=self.ACHIEVEMENTS_CONFIG["week_streak"]["name"],
                description=self.ACHIEVEMENTS_CONFIG["week_streak"]["description"],
                icon=self.ACHIEVEMENTS_CONFIG["week_streak"]["icon"],
                unlocked_at=datetime.utcnow(),
                category=self.ACHIEVEMENTS_CONFIG["week_streak"]["category"],
                progress=100.0,
            ))

        # 检查最高分
        max_score = max(
            s.get("evaluation_result", {}).get("overall_quality", 0.0)
            for s in sessions
        )
        if max_score >= 90:
            achievements.append(Achievement(
                achievement_id="high_scorer",
                name=self.ACHIEVEMENTS_CONFIG["high_scorer"]["name"],
                description=self.ACHIEVEMENTS_CONFIG["high_scorer"]["description"],
                icon=self.ACHIEVEMENTS_CONFIG["high_scorer"]["icon"],
                unlocked_at=datetime.utcnow(),
                category=self.ACHIEVEMENTS_CONFIG["high_scorer"]["category"],
                progress=100.0,
            ))

        # 检查总时长
        total_hours = sum(s.get("duration_seconds", 0) for s in sessions) / 3600
        if total_hours >= 10:
            achievements.append(Achievement(
                achievement_id="dedicated",
                name=self.ACHIEVEMENTS_CONFIG["dedicated"]["name"],
                description=self.ACHIEVEMENTS_CONFIG["dedicated"]["description"],
                icon=self.ACHIEVEMENTS_CONFIG["dedicated"]["icon"],
                unlocked_at=datetime.utcnow(),
                category=self.ACHIEVEMENTS_CONFIG["dedicated"]["category"],
                progress=100.0,
            ))

        # 检查全面发展
        if learning_profile:
            strengths = learning_profile.get("strengths", [])
            if len(strengths) >= 5:
                achievements.append(Achievement(
                    achievement_id="versatile",
                    name=self.ACHIEVEMENTS_CONFIG["versatile"]["name"],
                    description=self.ACHIEVEMENTS_CONFIG["versatile"]["description"],
                    icon=self.ACHIEVEMENTS_CONFIG["versatile"]["icon"],
                    unlocked_at=datetime.utcnow(),
                    category=self.ACHIEVEMENTS_CONFIG["versatile"]["category"],
                    progress=100.0,
                ))

        return achievements

    def _calculate_current_streak(self, sessions: List[Dict[str, Any]]) -> int:
        """计算当前连续天数"""
        if not sessions:
            return 0

        dates = set()
        for session in sessions:
            completed_at = session.get("completed_at")
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                dates.add(completed_at.date())

        streak = 0
        current_date = datetime.utcnow().date()

        while current_date in dates:
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    # =========================================================================
    # Summary Generation
    # =========================================================================

    def _generate_dashboard_summary(self,
                                    key_insights: List[KeyInsight],
                                    performance_cards: List[PerformanceCard],
                                    achievements: List[Achievement]) -> str:
        """生成仪表盘摘要"""
        parts = []

        # 成就摘要
        if achievements:
            parts.append(f"恭喜您获得了{len(achievements)}个成就！")

        # 表现摘要
        if performance_cards:
            overall = next((c for c in performance_cards if c.dimension == "overall_quality"), None)
            if overall:
                parts.append(f"当前综合表现：{overall.current_score:.1f}分，"
                           f"{'表现优秀' if overall.current_score >= 80 else '继续加油'}。")

        # 关键洞察摘要
        positive_insights = [i for i in key_insights if i.trend == "positive"]
        alert_insights = [i for i in key_insights if i.priority in ["critical", "high"]]

        if positive_insights:
            parts.append(f"有{len(positive_insights)}个积极进展。")
        if alert_insights:
            parts.append(f"有{len(alert_insights)}个需要关注的方面。")

        return " ".join(parts) if parts else "开始您的第一次练习吧！"

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self, dashboard: DashboardData) -> Dict[str, Any]:
        """将 DashboardData 转换为字典"""
        return {
            "user_id": dashboard.user_id,
            "generated_at": dashboard.generated_at.isoformat(),
            "period_days": dashboard.period_days,
            "key_insights": [
                {
                    "insight_id": i.insight_id,
                    "category": i.category.value,
                    "priority": i.priority.value,
                    "title": i.title,
                    "description": i.description,
                    "icon": i.icon,
                    "metrics": i.metrics,
                    "trend": i.trend,
                    "actionable_items": i.actionable_items,
                }
                for i in dashboard.key_insights
            ],
            "performance_cards": [
                {
                    "dimension": c.dimension,
                    "dimension_name": c.dimension_name,
                    "current_score": c.current_score,
                    "previous_score": c.previous_score,
                    "change": c.change,
                    "percentile": c.percentile,
                    "level": c.level,
                    "status": c.status,
                    "summary": c.summary,
                }
                for c in dashboard.performance_cards
            ],
            "trend_analyses": [
                {
                    "metric_name": t.metric_name,
                    "current_value": t.current_value,
                    "previous_value": t.previous_value,
                    "change_value": t.change_value,
                    "change_percent": t.change_percent,
                    "trend_direction": t.trend_direction,
                    "trend_strength": t.trend_strength,
                    "forecast_next": t.forecast_next,
                    "confidence": t.confidence,
                }
                for t in dashboard.trend_analyses
            ],
            "recommendations": [
                {
                    "rec_id": r.rec_id,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "estimated_impact": r.estimated_impact,
                    "time_required_minutes": r.time_required_minutes,
                    "steps": r.steps,
                    "related_dimensions": r.related_dimensions,
                }
                for r in dashboard.recommendations
            ],
            "achievements": [
                {
                    "achievement_id": a.achievement_id,
                    "name": a.name,
                    "description": a.description,
                    "icon": a.icon,
                    "unlocked_at": a.unlocked_at.isoformat() if isinstance(a.unlocked_at, datetime) else a.unlocked_at,
                    "category": a.category,
                    "progress": a.progress,
                }
                for a in dashboard.achievements
            ],
            "summary_text": dashboard.summary_text,
        }
