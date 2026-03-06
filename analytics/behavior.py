"""
Behavior Tracking Module

行为追踪模块提供：
- BehaviorTracker: 用户行为追踪系统
- 会话频率和时长追踪
- 改进模式监控
- 学习平台期检测

Version: v0.7.0
Author: AgentScope AI Interview Team
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import math


class EngagementLevel(str, Enum):
    """用户参与度等级"""
    INACTIVE = "inactive"  # 不活跃
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    VERY_HIGH = "very_high"  # 非常高


class PlateauStatus(str, Enum):
    """平台期状态"""
    NONE = "none"  # 无平台期
    APPROACHING = "approaching"  # 接近平台期
    IN_PLATEAU = "in_plateau"  # 处于平台期
    BREAKING_THROUGH = "breaking_through"  # 突破中


@dataclass
class SessionPattern:
    """会话模式"""
    avg_sessions_per_week: float
    avg_duration_minutes: float
    preferred_time_of_day: str  # morning, afternoon, evening, night
    preferred_days: List[int]  # 0=Monday, 6=Sunday
    consistency_score: float  # 0-1


@dataclass
class EngagementMetrics:
    """参与度指标"""
    level: EngagementLevel
    total_sessions: int
    total_hours: float
    sessions_last_7_days: int
    sessions_last_30_days: int
    avg_session_duration: float
    longest_streak: int
    current_streak: int
    last_active: Optional[datetime]

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for compatibility"""
        if hasattr(self, key):
            value = getattr(self, key)
            if hasattr(value, 'value'):
                return value.value
            return value
        return default


@dataclass
class ImprovementPattern:
    """改进模式"""
    overall_trend: str  # improving, stable, declining
    improvement_rate: float  # % per week
    acceleration: float  # 加速度
    key_inflection_points: List[datetime] = field(default_factory=list)


@dataclass
class PlateauAnalysis:
    """平台期分析"""
    status: PlateauStatus
    duration_days: int
    avg_score_during_plateau: float
    previous_avg_score: float
    breakthrough_probability: float  # 0-1
    recommendations: List[str] = field(default_factory=list)

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for compatibility"""
        if hasattr(self, key):
            value = getattr(self, key)
            if hasattr(value, 'value'):
                return value.value
            return value
        return default


@dataclass
class BehaviorReport:
    """行为报告"""
    user_id: str
    period_days: int
    session_pattern: SessionPattern
    engagement: EngagementMetrics
    improvement_pattern: ImprovementPattern
    plateau_analysis: PlateauAnalysis
    behavioral_insights: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access for compatibility"""
        if hasattr(self, key):
            value = getattr(self, key)
            # Convert dataclass to dict for nested access
            if hasattr(value, '__dataclass_fields__'):
                return value
            return value
        return default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "period_days": self.period_days,
            "session_pattern": self.session_pattern.value if hasattr(self.session_pattern, 'value') else self.session_pattern,
            "engagement": {
                "level": self.engagement.level if hasattr(self.engagement, 'level') else "unknown",
                "score": self.engagement.score if hasattr(self.engagement, 'score') else 0,
            },
            "improvement_pattern": self.improvement_pattern.value if hasattr(self.improvement_pattern, 'value') else self.improvement_pattern,
            "behavioral_insights": self.behavioral_insights,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }


class BehaviorTracker:
    """
    行为追踪器

    负责追踪用户行为模式，监控学习进展，检测平台期

    Design Principles:
    - 连续性：追踪长期行为模式
    - 敏感性：及时检测重要变化
    - 隐私保护：仅分析必要数据
    - 可操作性：提供具体建议
    """

    # 参与度阈值配置
    ENGAGEMENT_THRESHOLDS = {
        "sessions_per_week": {
            "very_high": 5.0,
            "high": 3.0,
            "medium": 1.5,
            "low": 0.5,
        },
        "session_duration_minutes": {
            "very_high": 45.0,
            "high": 30.0,
            "medium": 15.0,
            "low": 5.0,
        },
    }

    # 平台期检测参数
    PLATEAU_PARAMS = {
        "min_sessions_for_detection": 5,  # 最少会话数
        "score_variance_threshold": 5.0,  # 分数方差阈值
        "trend_threshold": 0.02,  # 趋势阈值（每周变化率）
        "min_plateau_duration_days": 7,  # 最小平合期天数
    }

    # 时间偏好分类
    TIME_OF_DAY_RANGES = {
        "morning": (5, 12),
        "afternoon": (12, 17),
        "evening": (17, 22),
        "night": (22, 5),
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化行为追踪器

        Args:
            config: 配置字典，可覆盖默认参数
        """
        self.config = config or {}
        self.params = {**self.PLATEAU_PARAMS, **self.config.get("params", {})}
        self._cache: Dict[str, Any] = {}

    # =========================================================================
    # Main Analysis Method
    # =========================================================================

    def analyze_behavior(self, user_id: str,
                        sessions: List[Dict[str, Any]],
                        period_days: int = 30) -> BehaviorReport:
        """
        分析用户行为

        Args:
            user_id: 用户 ID
            sessions: 会话数据列表
            period_days: 分析周期（天）

        Returns:
            BehaviorReport 对象
        """
        # 过滤周期内的会话
        filtered_sessions = self._filter_by_period(sessions, period_days)

        # 分析会话模式
        session_pattern = self._analyze_session_pattern(filtered_sessions)

        # 计算参与度指标
        engagement = self._calculate_engagement(filtered_sessions)

        # 分析改进模式
        improvement_pattern = self._analyze_improvement_pattern(filtered_sessions)

        # 检测平台期
        plateau_analysis = self._detect_plateau(filtered_sessions)

        # 生成行为洞察
        behavioral_insights = self._generate_behavioral_insights(
            session_pattern, engagement, improvement_pattern, plateau_analysis
        )

        return BehaviorReport(
            user_id=user_id,
            period_days=period_days,
            session_pattern=session_pattern,
            engagement=engagement,
            improvement_pattern=improvement_pattern,
            plateau_analysis=plateau_analysis,
            behavioral_insights=behavioral_insights,
            generated_at=datetime.utcnow()
        )

    def _filter_by_period(self, sessions: List[Dict[str, Any]],
                         period_days: int) -> List[Dict[str, Any]]:
        """过滤指定周期内的会话"""
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)

        filtered = []
        for session in sessions:
            completed_at = session.get("completed_at")
            if not completed_at:
                continue

            if isinstance(completed_at, str):
                completed_at = datetime.fromisoformat(completed_at)

            if completed_at >= cutoff_date:
                filtered.append(session)

        return filtered

    # =========================================================================
    # Session Pattern Analysis
    # =========================================================================

    def _analyze_session_pattern(self, sessions: List[Dict[str, Any]]) -> SessionPattern:
        """分析会话模式"""
        if not sessions:
            return SessionPattern(
                avg_sessions_per_week=0.0,
                avg_duration_minutes=0.0,
                preferred_time_of_day="unknown",
                preferred_days=[],
                consistency_score=0.0
            )

        # 计算平均每周会话数
        date_range = self._calculate_date_range(sessions)
        weeks = max(1, date_range / (7 * 24 * 3600))
        avg_sessions_per_week = len(sessions) / weeks

        # 计算平均时长
        durations = [s.get("duration_seconds", 0) for s in sessions]
        avg_duration_minutes = (statistics.mean(durations) / 60) if durations else 0.0

        # 分析时间偏好
        preferred_time = self._analyze_time_preference(sessions)
        preferred_days = self._analyze_day_preference(sessions)

        # 计算一致性分数
        consistency_score = self._calculate_consistency_score(sessions)

        return SessionPattern(
            avg_sessions_per_week=round(avg_sessions_per_week, 2),
            avg_duration_minutes=round(avg_duration_minutes, 2),
            preferred_time_of_day=preferred_time,
            preferred_days=preferred_days,
            consistency_score=round(consistency_score, 2)
        )

    def _calculate_date_range(self, sessions: List[Dict[str, Any]]) -> float:
        """计算会话时间范围（秒）"""
        times = []
        for session in sessions:
            completed_at = session.get("completed_at")
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                times.append(completed_at)

        if len(times) < 2:
            return 7 * 24 * 3600  # 默认 7 天

        return (max(times) - min(times)).total_seconds()

    def _analyze_time_preference(self, sessions: List[Dict[str, Any]]) -> str:
        """分析时间偏好"""
        time_counts = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}

        for session in sessions:
            completed_at = session.get("completed_at")
            if not completed_at:
                continue

            if isinstance(completed_at, str):
                completed_at = datetime.fromisoformat(completed_at)

            hour = completed_at.hour

            for time_period, (start, end) in self.TIME_OF_DAY_RANGES.items():
                if start < end:  # 正常范围（如 5-12）
                    if start <= hour < end:
                        time_counts[time_period] += 1
                        break
                else:  # 跨天范围（如 22-5）
                    if hour >= start or hour < end:
                        time_counts[time_period] += 1
                        break

        # 返回最多的时间段
        return max(time_counts, key=time_counts.get) if time_counts else "unknown"

    def _analyze_day_preference(self, sessions: List[Dict[str, Any]]) -> List[int]:
        """分析日期偏好（返回最喜欢的 2-3 天）"""
        day_counts = {i: 0 for i in range(7)}

        for session in sessions:
            completed_at = session.get("completed_at")
            if not completed_at:
                continue

            if isinstance(completed_at, str):
                completed_at = datetime.fromisoformat(completed_at)

            day_counts[completed_at.weekday()] += 1

        # 排序并返回前 2-3 天
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        top_days = [day for day, count in sorted_days[:3] if count > 0]

        return top_days

    def _calculate_consistency_score(self, sessions: List[Dict[str, Any]]) -> float:
        """
        计算一致性分数

        基于会话间隔的规律性
        """
        if len(sessions) < 3:
            return 0.0

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 计算间隔
        intervals = []
        for i in range(1, len(sorted_sessions)):
            prev_time = sorted_sessions[i - 1].get("completed_at", datetime.utcnow())
            curr_time = sorted_sessions[i].get("completed_at", datetime.utcnow())

            if isinstance(prev_time, str):
                prev_time = datetime.fromisoformat(prev_time)
            if isinstance(curr_time, str):
                curr_time = datetime.fromisoformat(curr_time)

            interval = (curr_time - prev_time).total_seconds() / 3600  # 小时
            intervals.append(interval)

        if len(intervals) < 2:
            return 0.5

        # 计算变异系数
        mean_interval = statistics.mean(intervals)
        if mean_interval == 0:
            return 1.0

        std_interval = statistics.stdev(intervals)
        cv = std_interval / mean_interval

        # CV 越小，一致性越高
        consistency = max(0, min(1, 1 - cv))
        return consistency

    # =========================================================================
    # Engagement Calculation
    # =========================================================================

    def _calculate_engagement(self, sessions: List[Dict[str, Any]]) -> EngagementMetrics:
        """计算参与度指标"""
        if not sessions:
            return EngagementMetrics(
                level=EngagementLevel.INACTIVE,
                total_sessions=0,
                total_hours=0.0,
                sessions_last_7_days=0,
                sessions_last_30_days=0,
                avg_session_duration=0.0,
                longest_streak=0,
                current_streak=0,
                last_active=None
            )

        # 总会话数和总时长
        total_sessions = len(sessions)
        total_hours = sum(s.get("duration_seconds", 0) for s in sessions) / 3600

        # 最近 7 天和 30 天的会话数
        now = datetime.utcnow()
        sessions_last_7_days = self._count_sessions_in_period(sessions, 7)
        sessions_last_30_days = self._count_sessions_in_period(sessions, 30)

        # 平均时长
        durations = [s.get("duration_seconds", 0) for s in sessions]
        avg_session_duration = (statistics.mean(durations) / 60) if durations else 0.0

        # 连续天数
        longest_streak = self._calculate_longest_streak(sessions)
        current_streak = self._calculate_current_streak(sessions)

        # 最后活跃时间
        last_active = self._get_last_active(sessions)

        # 确定参与度等级
        level = self._determine_engagement_level(
            sessions_last_7_days, avg_session_duration
        )

        return EngagementMetrics(
            level=level,
            total_sessions=total_sessions,
            total_hours=round(total_hours, 2),
            sessions_last_7_days=sessions_last_7_days,
            sessions_last_30_days=sessions_last_30_days,
            avg_session_duration=round(avg_session_duration, 2),
            longest_streak=longest_streak,
            current_streak=current_streak,
            last_active=last_active
        )

    def _count_sessions_in_period(self, sessions: List[Dict[str, Any]],
                                  days: int) -> int:
        """计算指定天数内的会话数"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = 0

        for session in sessions:
            completed_at = session.get("completed_at")
            if not completed_at:
                continue

            if isinstance(completed_at, str):
                completed_at = datetime.fromisoformat(completed_at)

            if completed_at >= cutoff:
                count += 1

        return count

    def _determine_engagement_level(self, sessions_per_week: float,
                                    avg_duration: float) -> EngagementLevel:
        """确定参与度等级"""
        thresholds = self.ENGAGEMENT_THRESHOLDS

        # 基于会话频率和时长综合判断
        score = 0

        # 会话频率得分
        if sessions_per_week >= thresholds["sessions_per_week"]["very_high"]:
            score += 4
        elif sessions_per_week >= thresholds["sessions_per_week"]["high"]:
            score += 3
        elif sessions_per_week >= thresholds["sessions_per_week"]["medium"]:
            score += 2
        elif sessions_per_week >= thresholds["sessions_per_week"]["low"]:
            score += 1

        # 时长得分
        if avg_duration >= thresholds["session_duration_minutes"]["very_high"]:
            score += 4
        elif avg_duration >= thresholds["session_duration_minutes"]["high"]:
            score += 3
        elif avg_duration >= thresholds["session_duration_minutes"]["medium"]:
            score += 2
        elif avg_duration >= thresholds["session_duration_minutes"]["low"]:
            score += 1

        # 综合判断
        if score >= 7:
            return EngagementLevel.VERY_HIGH
        elif score >= 5:
            return EngagementLevel.HIGH
        elif score >= 3:
            return EngagementLevel.MEDIUM
        elif score >= 1:
            return EngagementLevel.LOW
        else:
            return EngagementLevel.INACTIVE

    def _calculate_longest_streak(self, sessions: List[Dict[str, Any]]) -> int:
        """计算最长连续天数"""
        if not sessions:
            return 0

        # 提取日期
        dates = set()
        for session in sessions:
            completed_at = session.get("completed_at")
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                dates.add(completed_at.date())

        if not dates:
            return 0

        # 计算最长连续
        sorted_dates = sorted(dates)
        longest = 1
        current = 1

        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i - 1]).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest

    def _calculate_current_streak(self, sessions: List[Dict[str, Any]]) -> int:
        """计算当前连续天数"""
        if not sessions:
            return 0

        # 提取日期
        dates = set()
        for session in sessions:
            completed_at = session.get("completed_at")
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                dates.add(completed_at.date())

        if not dates:
            return 0

        # 从今天开始往前数
        streak = 0
        current_date = datetime.utcnow().date()

        while current_date in dates:
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    def _get_last_active(self, sessions: List[Dict[str, Any]]) -> Optional[datetime]:
        """获取最后活跃时间"""
        if not sessions:
            return None

        times = []
        for session in sessions:
            completed_at = session.get("completed_at")
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                times.append(completed_at)

        return max(times) if times else None

    # =========================================================================
    # Improvement Pattern Analysis
    # =========================================================================

    def _analyze_improvement_pattern(self, sessions: List[Dict[str, Any]]) -> ImprovementPattern:
        """分析改进模式"""
        if len(sessions) < 3:
            return ImprovementPattern(
                overall_trend="stable",
                improvement_rate=0.0,
                acceleration=0.0,
                key_inflection_points=[]
            )

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 提取分数和时间
        data_points = []
        for session in sorted_sessions:
            score = session.get("evaluation_result", {}).get("overall_quality", 0.0)
            completed_at = session.get("completed_at")

            if score > 0 and completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                data_points.append((completed_at, score))

        if len(data_points) < 3:
            return ImprovementPattern(
                overall_trend="stable",
                improvement_rate=0.0,
                acceleration=0.0,
                key_inflection_points=[]
            )

        # 计算趋势
        trend = self._calculate_score_trend(data_points)
        improvement_rate = self._calculate_improvement_rate(data_points)
        acceleration = self._calculate_acceleration(data_points)
        inflection_points = self._detect_inflection_points(data_points)

        return ImprovementPattern(
            overall_trend=trend,
            improvement_rate=round(improvement_rate, 2),
            acceleration=round(acceleration, 4),
            key_inflection_points=inflection_points
        )

    def _calculate_score_trend(self, data_points: List[Tuple[datetime, float]]) -> str:
        """计算分数趋势"""
        if len(data_points) < 2:
            return "stable"

        scores = [dp[1] for dp in data_points]

        # 使用线性回归
        n = len(scores)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(scores)

        numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # 判断趋势
        if slope > 0.5:
            return "improving"
        elif slope < -0.5:
            return "declining"
        else:
            return "stable"

    def _calculate_improvement_rate(self, data_points: List[Tuple[datetime, float]]) -> float:
        """计算改进率（每周百分比）"""
        if len(data_points) < 2:
            return 0.0

        # 计算时间范围（周）
        first_time = data_points[0][0]
        last_time = data_points[-1][0]
        weeks = max(1, (last_time - first_time).total_seconds() / (7 * 24 * 3600))

        # 计算分数变化
        first_score = data_points[0][1]
        last_score = data_points[-1][1]

        if first_score == 0:
            return 0.0

        total_change = ((last_score - first_score) / first_score) * 100
        weekly_rate = total_change / weeks

        return weekly_rate

    def _calculate_acceleration(self, data_points: List[Tuple[datetime, float]]) -> float:
        """计算加速度（改进率的变化）"""
        if len(data_points) < 4:
            return 0.0

        mid = len(data_points) // 2
        first_half = data_points[:mid]
        second_half = data_points[mid:]

        rate1 = self._calculate_improvement_rate(first_half)
        rate2 = self._calculate_improvement_rate(second_half)

        # 加速度 = 改进率的变化
        acceleration = rate2 - rate1
        return acceleration

    def _detect_inflection_points(self, data_points: List[Tuple[datetime, float]]) -> List[datetime]:
        """检测转折点"""
        if len(data_points) < 5:
            return []

        inflection_points = []
        scores = [dp[1] for dp in data_points]
        times = [dp[0] for dp in data_points]

        # 计算移动平均
        window = 3
        for i in range(window, len(scores) - window):
            prev_avg = statistics.mean(scores[i - window:i])
            curr_avg = statistics.mean(scores[i:i + window])

            # 检测显著变化
            change = curr_avg - prev_avg
            if abs(change) > 5:  # 5 分阈值
                inflection_points.append(times[i])

        return inflection_points

    # =========================================================================
    # Plateau Detection
    # =========================================================================

    def _detect_plateau(self, sessions: List[Dict[str, Any]]) -> PlateauAnalysis:
        """检测平台期"""
        if len(sessions) < self.params["min_sessions_for_detection"]:
            return PlateauAnalysis(
                status=PlateauStatus.NONE,
                duration_days=0,
                avg_score_during_plateau=0.0,
                previous_avg_score=0.0,
                breakthrough_probability=0.0,
                recommendations=[]
            )

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 提取分数
        scores = []
        times = []
        for session in sorted_sessions:
            score = session.get("evaluation_result", {}).get("overall_quality", 0.0)
            completed_at = session.get("completed_at")

            if score > 0 and completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at)
                scores.append(score)
                times.append(completed_at)

        if len(scores) < self.params["min_sessions_for_detection"]:
            return PlateauAnalysis(
                status=PlateauStatus.NONE,
                duration_days=0,
                avg_score_during_plateau=0.0,
                previous_avg_score=0.0,
                breakthrough_probability=0.0,
                recommendations=[]
            )

        # 检测平台期
        status, duration_days, plateau_scores = self._analyze_plateau(scores, times)

        if status == PlateauStatus.NONE:
            return PlateauAnalysis(
                status=PlateauStatus.NONE,
                duration_days=0,
                avg_score_during_plateau=0.0,
                previous_avg_score=0.0,
                breakthrough_probability=0.0,
                recommendations=[]
            )

        # 计算分数
        avg_score_during = statistics.mean(plateau_scores) if plateau_scores else 0.0

        # 计算之前的平均分
        plateau_start_idx = len(scores) - len(plateau_scores)
        previous_scores = scores[:plateau_start_idx]
        previous_avg = statistics.mean(previous_scores) if previous_scores else 0.0

        # 计算突破概率
        breakthrough_prob = self._calculate_breakthrough_probability(scores, times)

        # 生成建议
        recommendations = self._generate_plateau_recommendations(status, avg_score_during, previous_avg)

        return PlateauAnalysis(
            status=status,
            duration_days=duration_days,
            avg_score_during_plateau=round(avg_score_during, 2),
            previous_avg_score=round(previous_avg, 2),
            breakthrough_probability=round(breakthrough_prob, 2),
            recommendations=recommendations
        )

    def _analyze_plateau(self, scores: List[float],
                        times: List[datetime]) -> Tuple[PlateauStatus, int, List[float]]:
        """分析平台期"""
        if len(scores) < self.params["min_sessions_for_detection"]:
            return PlateauStatus.NONE, 0, []

        # 计算最近会话的方差
        recent_n = min(10, len(scores))
        recent_scores = scores[-recent_n:]
        variance = statistics.variance(recent_scores) if len(recent_scores) > 1 else 0

        # 计算趋势
        trend = self._calculate_score_trend(list(zip(times, scores)))

        # 判断平台期状态
        if variance < self.params["score_variance_threshold"] and abs(trend) < self.params["trend_threshold"]:
            # 处于平台期
            duration = (times[-1] - times[0]).days if times else 0
            return PlateauStatus.IN_PLATEAU, duration, recent_scores
        elif variance < self.params["score_variance_threshold"] * 1.5:
            # 接近平台期
            return PlateauStatus.APPROACHING, 0, recent_scores
        elif trend == "improving":
            # 突破中
            return PlateauStatus.BREAKING_THROUGH, 0, recent_scores

        return PlateauStatus.NONE, 0, []

    def _calculate_breakthrough_probability(self, scores: List[float],
                                           times: List[datetime]) -> float:
        """计算突破概率"""
        if len(scores) < 5:
            return 0.0

        # 基于多个因素计算概率
        factors = []

        # 因素 1：最近趋势
        recent_scores = scores[-5:]
        trend = (recent_scores[-1] - recent_scores[0]) / max(1, len(recent_scores))
        factors.append(max(0, min(1, 0.5 + trend / 10)))

        # 因素 2：方差变化
        if len(scores) >= 10:
            early_variance = statistics.variance(scores[:5])
            late_variance = statistics.variance(scores[-5:])
            variance_ratio = late_variance / max(0.1, early_variance)
            factors.append(max(0, min(1, variance_ratio)))

        # 因素 3：最高分出现时间
        max_score = max(scores)
        max_score_idx = scores.index(max_score)
        recency_factor = (max_score_idx + 1) / len(scores)
        factors.append(recency_factor)

        # 平均概率
        probability = statistics.mean(factors) if factors else 0.0
        return probability

    def _generate_plateau_recommendations(self, status: PlateauStatus,
                                         current_avg: float,
                                         previous_avg: float) -> List[str]:
        """生成平台期建议"""
        recommendations = []

        if status == PlateauStatus.IN_PLATEAU:
            recommendations = [
                "尝试新的练习方法或场景类型",
                "增加练习难度，挑战更高水平",
                "寻求外部反馈，发现盲点",
                "适当休息，避免过度练习",
                "回顾早期学习材料，巩固基础",
            ]
        elif status == PlateauStatus.APPROACHING:
            recommendations = [
                "保持当前练习节奏，预防平台期",
                "提前规划新的学习目标",
            ]
        elif status == PlateauStatus.BREAKING_THROUGH:
            recommendations = [
                "继续保持当前的学习方法",
                "总结突破经验，形成系统方法",
            ]

        return recommendations

    # =========================================================================
    # Behavioral Insights
    # =========================================================================

    def _generate_behavioral_insights(self,
                                      session_pattern: SessionPattern,
                                      engagement: EngagementMetrics,
                                      improvement_pattern: ImprovementPattern,
                                      plateau_analysis: PlateauAnalysis) -> List[str]:
        """生成行为洞察"""
        insights = []

        # 基于参与度
        if engagement.level == EngagementLevel.VERY_HIGH:
            insights.append("您的练习频率非常高，表现优秀！")
        elif engagement.level == EngagementLevel.INACTIVE:
            insights.append("近期练习较少，建议增加练习频率。")

        # 基于一致性
        if session_pattern.consistency_score > 0.7:
            insights.append("您保持着非常规律的学习习惯。")
        elif session_pattern.consistency_score < 0.3 and session_pattern.avg_sessions_per_week > 0:
            insights.append("练习时间不太规律，建议建立固定的学习时间。")

        # 基于改进趋势
        if improvement_pattern.overall_trend == "improving":
            insights.append(f"您的能力正在稳步提升（每周+{improvement_pattern.improvement_rate:.1f}%）。")
        elif improvement_pattern.overall_trend == "declining":
            insights.append("近期表现有所下降，建议调整学习方法。")

        # 基于平台期
        if plateau_analysis.status == PlateauStatus.IN_PLATEAU:
            insights.append(f"检测到平台期（已持续{plateau_analysis.duration_days}天），建议尝试新的练习方式。")

        # 基于连续天数
        if engagement.current_streak >= 7:
            insights.append(f"已连续练习{engagement.current_streak}天，继续保持！")
        elif engagement.longest_streak > 0 and engagement.current_streak == 0:
            insights.append(f"曾连续练习{engagement.longest_streak}天，加油恢复练习！")

        return insights

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self, report: BehaviorReport) -> Dict[str, Any]:
        """将 BehaviorReport 转换为字典"""
        return {
            "user_id": report.user_id,
            "period_days": report.period_days,
            "session_pattern": {
                "avg_sessions_per_week": report.session_pattern.avg_sessions_per_week,
                "avg_duration_minutes": report.session_pattern.avg_duration_minutes,
                "preferred_time_of_day": report.session_pattern.preferred_time_of_day,
                "preferred_days": report.session_pattern.preferred_days,
                "consistency_score": report.session_pattern.consistency_score,
            },
            "engagement": {
                "level": report.engagement.level.value,
                "total_sessions": report.engagement.total_sessions,
                "total_hours": report.engagement.total_hours,
                "sessions_last_7_days": report.engagement.sessions_last_7_days,
                "sessions_last_30_days": report.engagement.sessions_last_30_days,
                "avg_session_duration": report.engagement.avg_session_duration,
                "longest_streak": report.engagement.longest_streak,
                "current_streak": report.engagement.current_streak,
                "last_active": report.engagement.last_active.isoformat() if report.engagement.last_active else None,
            },
            "improvement_pattern": {
                "overall_trend": report.improvement_pattern.overall_trend,
                "improvement_rate": report.improvement_pattern.improvement_rate,
                "acceleration": report.improvement_pattern.acceleration,
                "key_inflection_points": [
                    dt.isoformat() for dt in report.improvement_pattern.key_inflection_points
                ],
            },
            "plateau_analysis": {
                "status": report.plateau_analysis.status.value,
                "duration_days": report.plateau_analysis.duration_days,
                "avg_score_during_plateau": report.plateau_analysis.avg_score_during_plateau,
                "previous_avg_score": report.plateau_analysis.previous_avg_score,
                "breakthrough_probability": report.plateau_analysis.breakthrough_probability,
                "recommendations": report.plateau_analysis.recommendations,
            },
            "behavioral_insights": report.behavioral_insights,
            "generated_at": report.generated_at.isoformat(),
        }

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
