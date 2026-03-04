"""
Progress Metrics Calculation

进度指标计算模块：
- 七维度评估分数计算
- 改进率计算
- 趋势分析

Design Principles:
- 单一职责原则
- 可配置的权重
- 支持自定义指标
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class EvaluationDimension(str, Enum):
    """七维度评估指标"""
    # 1. 语言表达能力
    LANGUAGE_EXPRESSION = "language_expression"
    # 2. 逻辑思维能力
    LOGICAL_THINKING = "logical_thinking"
    # 3. 专业知识掌握
    PROFESSIONAL_KNOWLEDGE = "professional_knowledge"
    # 4. 问题解决能力
    PROBLEM_SOLVING = "problem_solving"
    # 5. 沟通协作能力
    COMMUNICATION_COLLABORATION = "communication_collaboration"
    # 6. 应变能力
    ADAPTABILITY = "adaptability"
    # 7. 综合素质
    OVERALL_QUALITY = "overall_quality"


@dataclass
class DimensionScore:
    """维度分数数据类"""
    dimension: EvaluationDimension
    score: float = field(default=0.0)  # 0-100
    weight: float = field(default=1.0)  # 权重
    trend: str = field(default="stable")  # stable, improving, declining
    change_rate: float = field(default=0.0)  # 变化率 (%)
    
    def weighted_score(self) -> float:
        """计算加权分数"""
        return self.score * self.weight


@dataclass
class SessionMetrics:
    """单次会话的指标"""
    session_id: int
    scene_type: str
    completed_at: datetime
    duration_seconds: int
    overall_score: float
    dimension_scores: Dict[EvaluationDimension, float]
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)


@dataclass
class AggregatedMetrics:
    """聚合指标"""
    period_days: int
    total_sessions: int = 0
    completed_sessions: int = 0
    avg_duration_seconds: float = 0.0
    avg_overall_score: float = 0.0
    avg_dimension_scores: Dict[EvaluationDimension, float] = field(default_factory=dict)
    best_session_id: Optional[int] = None
    best_score: float = 0.0
    improvement_rate: float = 0.0  # %
    streak_days: int = 0


class ProgressMetricsCalculator:
    """
    进度指标计算器
    
    负责计算各种进度指标和统计数据
    """
    
    # 默认权重（七维度）
    DEFAULT_WEIGHTS = {
        EvaluationDimension.LANGUAGE_EXPRESSION: 1.0,
        EvaluationDimension.LOGICAL_THINKING: 1.2,
        EvaluationDimension.PROFESSIONAL_KNOWLEDGE: 1.3,
        EvaluationDimension.PROBLEM_SOLVING: 1.2,
        EvaluationDimension.COMMUNICATION_COLLABORATION: 1.0,
        EvaluationDimension.ADAPTABILITY: 1.1,
        EvaluationDimension.OVERALL_QUALITY: 1.2,
    }
    
    def __init__(self, weights: Optional[Dict[EvaluationDimension, float]] = None):
        """
        初始化指标计算器
        
        Args:
            weights: 各维度权重（可选，默认使用 DEFAULT_WEIGHTS）
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
    
    # =========================================================================
    # Single Session Metrics
    # =========================================================================
    
    def calculate_session_metrics(self, session_data: Dict[str, Any]) -> SessionMetrics:
        """
        计算单次会话的指标
        
        Args:
            session_data: 会话数据字典，包含：
                - session_id, scene_type, completed_at, duration_seconds
                - evaluation_result (包含各维度分数)
                
        Returns:
            SessionMetrics 对象
        """
        # 提取评估结果
        eval_result = session_data.get("evaluation_result", {})
        
        # 计算各维度分数
        dimension_scores = {}
        for dim in EvaluationDimension:
            score = eval_result.get(dim.value, 0.0)
            dimension_scores[dim] = score
        
        # 计算总体分数（加权平均）
        overall_score = self.calculate_overall_score(dimension_scores)
        
        # 识别优势和改进项
        strengths, improvements = self.analyze_performance(dimension_scores)
        
        return SessionMetrics(
            session_id=session_data.get("session_id", 0),
            scene_type=session_data.get("scene_type", "unknown"),
            completed_at=session_data.get("completed_at", datetime.utcnow()),
            duration_seconds=session_data.get("duration_seconds", 0),
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            strengths=strengths,
            improvements=improvements
        )
    
    def calculate_overall_score(self, dimension_scores: Dict[EvaluationDimension, float]) -> float:
        """
        计算总体分数（加权平均）
        
        Args:
            dimension_scores: 各维度分数字典
            
        Returns:
            总体分数 (0-100)
        """
        if not dimension_scores:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dim, score in dimension_scores.items():
            weight = self.weights.get(dim, 1.0)
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_weighted_score / total_weight
    
    def analyze_performance(self, dimension_scores: Dict[EvaluationDimension, float],
                           threshold_high: float = 80.0,
                           threshold_low: float = 60.0) -> tuple[List[str], List[str]]:
        """
        分析表现，识别优势和改进项
        
        Args:
            dimension_scores: 各维度分数字典
            threshold_high: 高分阈值
            threshold_low: 低分阈值
            
        Returns:
            (优势项列表，改进项列表)
        """
        strengths = []
        improvements = []
        
        dimension_names = {
            EvaluationDimension.LANGUAGE_EXPRESSION: "语言表达能力",
            EvaluationDimension.LOGICAL_THINKING: "逻辑思维能力",
            EvaluationDimension.PROFESSIONAL_KNOWLEDGE: "专业知识掌握",
            EvaluationDimension.PROBLEM_SOLVING: "问题解决能力",
            EvaluationDimension.COMMUNICATION_COLLABORATION: "沟通协作能力",
            EvaluationDimension.ADAPTABILITY: "应变能力",
            EvaluationDimension.OVERALL_QUALITY: "综合素质",
        }
        
        for dim, score in dimension_scores.items():
            name = dimension_names.get(dim, dim.value)
            
            if score >= threshold_high:
                strengths.append(f"{name} ({score:.1f}分)")
            elif score < threshold_low:
                improvements.append(f"{name} ({score:.1f}分) - 需要加强练习")
        
        return strengths, improvements
    
    # =========================================================================
    # Aggregated Metrics
    # =========================================================================
    
    def calculate_aggregated_metrics(self, sessions: List[Dict[str, Any]],
                                    period_days: int = 30) -> AggregatedMetrics:
        """
        计算聚合指标
        
        Args:
            sessions: 会话数据列表
            period_days: 统计周期（天）
            
        Returns:
            AggregatedMetrics 对象
        """
        if not sessions:
            return AggregatedMetrics(period_days=period_days)
        
        # 过滤周期内的会话
        cutoff_date = datetime.utcnow() - timedelta(days=period_days)
        recent_sessions = [
            s for s in sessions
            if s.get("completed_at", datetime.utcnow()) >= cutoff_date
        ]
        
        if not recent_sessions:
            return AggregatedMetrics(period_days=period_days)
        
        # 计算各项指标
        total_sessions = len(sessions)
        completed_sessions = len([s for s in recent_sessions if s.get("status") == "completed"])
        
        # 计算平均时长
        total_duration = sum(s.get("duration_seconds", 0) for s in recent_sessions)
        avg_duration = total_duration / len(recent_sessions) if recent_sessions else 0.0
        
        # 计算平均分数
        session_metrics_list = [self.calculate_session_metrics(s) for s in recent_sessions]
        overall_scores = [m.overall_score for m in session_metrics_list if m.overall_score > 0]
        avg_overall_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
        
        # 计算各维度平均分
        avg_dimension_scores = {}
        for dim in EvaluationDimension:
            scores = [
                m.dimension_scores.get(dim, 0.0)
                for m in session_metrics_list
                if m.dimension_scores.get(dim, 0.0) > 0
            ]
            if scores:
                avg_dimension_scores[dim] = sum(scores) / len(scores)
        
        # 找出最佳会话
        best_session = max(session_metrics_list, key=lambda m: m.overall_score, default=None)
        best_session_id = best_session.session_id if best_session else None
        best_score = best_session.overall_score if best_session else 0.0
        
        # 计算改进率
        improvement_rate = self.calculate_improvement_rate(session_metrics_list)
        
        # 计算连续练习天数
        streak_days = self.calculate_streak_days(sessions)
        
        return AggregatedMetrics(
            period_days=period_days,
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            avg_duration_seconds=avg_duration,
            avg_overall_score=avg_overall_score,
            avg_dimension_scores=avg_dimension_scores,
            best_session_id=best_session_id,
            best_score=best_score,
            improvement_rate=improvement_rate,
            streak_days=streak_days
        )
    
    def calculate_improvement_rate(self, session_metrics: List[SessionMetrics]) -> float:
        """
        计算改进率
        
        通过比较最近 5 次会话和前 5 次会话的平均分数
        
        Args:
            session_metrics: 会话指标列表（按时间排序）
            
        Returns:
            改进率 (%)
        """
        if len(session_metrics) < 2:
            return 0.0
        
        # 按完成时间排序
        sorted_metrics = sorted(session_metrics, key=lambda m: m.completed_at)
        
        # 取前半段和后半段
        mid = len(sorted_metrics) // 2
        early_metrics = sorted_metrics[:mid]
        late_metrics = sorted_metrics[mid:]
        
        if not early_metrics or not late_metrics:
            return 0.0
        
        # 计算平均分
        early_avg = sum(m.overall_score for m in early_metrics) / len(early_metrics)
        late_avg = sum(m.overall_score for m in late_metrics) / len(late_metrics)
        
        if early_avg == 0:
            return 0.0
        
        # 计算改进率
        improvement_rate = ((late_avg - early_avg) / early_avg) * 100
        return improvement_rate
    
    def calculate_streak_days(self, sessions: List[Dict[str, Any]]) -> int:
        """
        计算连续练习天数
        
        Args:
            sessions: 会话数据列表
            
        Returns:
            连续天数
        """
        if not sessions:
            return 0
        
        # 提取完成日期
        dates = set()
        for session in sessions:
            completed_at = session.get("completed_at")
            if completed_at:
                if isinstance(completed_at, datetime):
                    date = completed_at.date()
                else:
                    date = datetime.fromisoformat(completed_at).date()
                dates.add(date)
        
        if not dates:
            return 0
        
        # 计算连续天数
        streak = 0
        current_date = datetime.utcnow().date()
        
        while current_date in dates or current_date == datetime.utcnow().date():
            if current_date in dates:
                streak += 1
            elif current_date != datetime.utcnow().date():
                break
            current_date -= timedelta(days=1)
        
        return streak
    
    # =========================================================================
    # Trend Analysis
    # =========================================================================
    
    def calculate_trend(self, session_metrics: List[SessionMetrics],
                       dimension: Optional[EvaluationDimension] = None) -> str:
        """
        计算趋势
        
        Args:
            session_metrics: 会话指标列表
            dimension: 指定维度（None 表示总体趋势）
            
        Returns:
            趋势字符串：improving, declining, stable
        """
        if len(session_metrics) < 3:
            return "stable"
        
        # 按时间排序
        sorted_metrics = sorted(session_metrics, key=lambda m: m.completed_at)
        
        # 取最近 3 次的分数
        recent_scores = []
        for m in sorted_metrics[-3:]:
            if dimension:
                score = m.dimension_scores.get(dimension, 0.0)
            else:
                score = m.overall_score
            recent_scores.append(score)
        
        if len(recent_scores) < 3:
            return "stable"
        
        # 计算趋势
        if recent_scores[0] < recent_scores[1] < recent_scores[2]:
            return "improving"
        elif recent_scores[0] > recent_scores[1] > recent_scores[2]:
            return "declining"
        else:
            return "stable"
    
    def generate_progress_report(self, sessions: List[Dict[str, Any]],
                                period_days: int = 30) -> Dict[str, Any]:
        """
        生成进度报告
        
        Args:
            sessions: 会话数据列表
            period_days: 统计周期（天）
            
        Returns:
            进度报告字典
        """
        # 计算聚合指标
        metrics = self.calculate_aggregated_metrics(sessions, period_days)
        
        # 计算各会话指标
        session_metrics = [self.calculate_session_metrics(s) for s in sessions]
        
        # 生成报告
        report = {
            "period_days": period_days,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_sessions": metrics.total_sessions,
                "completed_sessions": metrics.completed_sessions,
                "avg_score": round(metrics.avg_overall_score, 2),
                "improvement_rate": round(metrics.improvement_rate, 2),
                "streak_days": metrics.streak_days,
            },
            "best_performance": {
                "session_id": metrics.best_session_id,
                "score": round(metrics.best_score, 2),
            },
            "dimension_analysis": {},
            "recommendations": [],
        }
        
        # 维度分析
        dimension_names = {
            EvaluationDimension.LANGUAGE_EXPRESSION: "语言表达能力",
            EvaluationDimension.LOGICAL_THINKING: "逻辑思维能力",
            EvaluationDimension.PROFESSIONAL_KNOWLEDGE: "专业知识掌握",
            EvaluationDimension.PROBLEM_SOLVING: "问题解决能力",
            EvaluationDimension.COMMUNICATION_COLLABORATION: "沟通协作能力",
            EvaluationDimension.ADAPTABILITY: "应变能力",
            EvaluationDimension.OVERALL_QUALITY: "综合素质",
        }
        
        for dim, avg_score in metrics.avg_dimension_scores.items():
            trend = self.calculate_trend(session_metrics, dim)
            report["dimension_analysis"][dim.value] = {
                "name": dimension_names.get(dim, dim.value),
                "avg_score": round(avg_score, 2),
                "trend": trend,
            }
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(metrics, session_metrics)
        
        return report
    
    def _generate_recommendations(self, metrics: AggregatedMetrics,
                                  session_metrics: List[SessionMetrics]) -> List[str]:
        """
        生成改进建议
        
        Args:
            metrics: 聚合指标
            session_metrics: 会话指标列表
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 基于改进率
        if metrics.improvement_rate < 0:
            recommendations.append("近期表现有所下降，建议增加练习频率")
        elif metrics.improvement_rate > 10:
            recommendations.append("进步显著，继续保持！")
        
        # 基于连续练习
        if metrics.streak_days == 0:
            recommendations.append("尚未建立练习习惯，建议每天练习 15 分钟")
        elif metrics.streak_days >= 7:
            recommendations.append(f"已连续练习{metrics.streak_days}天，表现优秀！")
        
        # 基于维度分析
        weak_dimensions = [
            dim for dim, score in metrics.avg_dimension_scores.items()
            if score < 60
        ]
        
        dimension_names = {
            EvaluationDimension.LANGUAGE_EXPRESSION: "语言表达能力",
            EvaluationDimension.LOGICAL_THINKING: "逻辑思维",
            EvaluationDimension.PROFESSIONAL_KNOWLEDGE: "专业知识",
            EvaluationDimension.PROBLEM_SOLVING: "问题解决",
            EvaluationDimension.COMMUNICATION_COLLABORATION: "沟通协作",
            EvaluationDimension.ADAPTABILITY: "应变能力",
        }
        
        for dim in weak_dimensions:
            name = dimension_names.get(dim, dim.value)
            recommendations.append(f"建议重点加强{name}方面的练习")
        
        return recommendations
