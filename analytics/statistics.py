"""
Statistics Engine Module

统计引擎模块提供：
- StatisticsEngine: 统计分析系统
- 高级指标计算（百分位数、分布）
- 用户对比（匿名化）
- 统计报告生成

Version: v0.7.0
Author: AgentScope AI Interview Team
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import math


class DistributionType(str, Enum):
    """分布类型"""
    NORMAL = "normal"  # 正态分布
    SKEWED_LEFT = "skewed_left"  # 左偏
    SKEWED_RIGHT = "skewed_right"  # 右偏
    UNIFORM = "uniform"  # 均匀分布
    BIMODAL = "bimodal"  # 双峰分布


@dataclass
class DescriptiveStatistics:
    """描述性统计"""
    count: int
    mean: float
    median: float
    mode: Optional[float]
    std_dev: float
    variance: float
    min_value: float
    max_value: float
    range_value: float
    q1: float  # 第一四分位数
    q3: float  # 第三四分位数
    iqr: float  # 四分位距


@dataclass
class PercentileData:
    """百分位数据"""
    p10: float
    p25: float
    p50: float
    p75: float
    p90: float
    p95: float
    p99: float


@dataclass
class DistributionAnalysis:
    """分布分析"""
    type: DistributionType
    skewness: float
    kurtosis: float
    is_normal: bool
    outliers_count: int
    outliers_values: List[float]


@dataclass
class ComparativeAnalysis:
    """对比分析"""
    user_score: float
    population_mean: float
    population_std: float
    percentile_rank: float  # 百分位排名
    z_score: float  # Z 分数
    t_score: float  # T 分数
    performance_level: str  # excellent, good, average, below_average, poor
    comparison_summary: str


@dataclass
class TrendStatistics:
    """趋势统计"""
    slope: float
    r_squared: float  # 决定系数
    trend_direction: str  # upward, downward, stable
    trend_strength: str  # strong, moderate, weak
    predicted_next_value: float
    confidence_interval: Tuple[float, float]


@dataclass
class CorrelationData:
    """相关数据"""
    variable1: str
    variable2: str
    correlation_coefficient: float
    relationship: str  # positive, negative, none
    strength: str  # strong, moderate, weak


@dataclass
class StatisticalReport:
    """统计报告"""
    user_id: str
    generated_at: datetime
    period_days: int
    descriptive_stats: DescriptiveStatistics
    percentile_data: PercentileData
    distribution_analysis: DistributionAnalysis
    comparative_analysis: Optional[ComparativeAnalysis]
    trend_statistics: TrendStatistics
    correlations: List[CorrelationData]
    summary: str


class StatisticsEngine:
    """
    统计引擎

    提供全面的统计分析功能，包括描述性统计、分布分析、对比分析等

    Design Principles:
    - 准确性：使用标准统计方法
    - 隐私保护：匿名化对比数据
    - 可解释性：提供清晰的统计解释
    - 实用性：关注可操作的统计洞察
    """

    # 匿名化人口统计数据（模拟）
    ANONYMIZED_POPULATION_STATS = {
        "overall_quality": {
            "mean": 72.5,
            "std_dev": 12.3,
            "count": 10000,
        },
        "language_expression": {
            "mean": 74.2,
            "std_dev": 11.8,
        },
        "logical_thinking": {
            "mean": 71.8,
            "std_dev": 13.1,
        },
        "professional_knowledge": {
            "mean": 70.5,
            "std_dev": 14.2,
        },
        "problem_solving": {
            "mean": 73.1,
            "std_dev": 12.5,
        },
        "communication_collaboration": {
            "mean": 75.3,
            "std_dev": 11.2,
        },
        "adaptability": {
            "mean": 72.9,
            "std_dev": 13.0,
        },
    }

    # 性能水平阈值
    PERFORMANCE_THRESHOLDS = {
        "excellent": 1.5,  # Z 分数 >= 1.5
        "good": 0.5,  # Z 分数 >= 0.5
        "average": -0.5,  # Z 分数 >= -0.5
        "below_average": -1.5,  # Z 分数 >= -1.5
        # poor: Z 分数 < -1.5
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化统计引擎

        Args:
            config: 配置字典
        """
        self.config = config or {}
        self._population_cache: Dict[str, Any] = {}

    # =========================================================================
    # Main Statistical Analysis
    # =========================================================================

    def generate_statistical_report(self, user_id: str,
                                    sessions: List[Dict[str, Any]],
                                    period_days: int = 30,
                                    include_comparison: bool = True) -> StatisticalReport:
        """
        生成统计报告

        Args:
            user_id: 用户 ID
            sessions: 会话数据列表
            period_days: 统计周期（天）
            include_comparison: 是否包含对比分析

        Returns:
            StatisticalReport 对象
        """
        # 提取分数数据
        scores = self._extract_scores(sessions)

        # 描述性统计
        descriptive_stats = self._calculate_descriptive_statistics(scores)

        # 百分位数据
        percentile_data = self._calculate_percentiles(scores)

        # 分布分析
        distribution_analysis = self._analyze_distribution(scores)

        # 对比分析
        comparative_analysis = None
        if include_comparison and scores:
            comparative_analysis = self._compare_with_population(
                statistics.mean(scores) if scores else 0.0,
                "overall_quality"
            )

        # 趋势统计
        trend_statistics = self._calculate_trend_statistics(sessions)

        # 相关分析
        correlations = self._calculate_correlations(sessions)

        # 生成摘要
        summary = self._generate_statistical_summary(
            descriptive_stats, distribution_analysis, comparative_analysis, trend_statistics
        )

        return StatisticalReport(
            user_id=user_id,
            generated_at=datetime.utcnow(),
            period_days=period_days,
            descriptive_stats=descriptive_stats,
            percentile_data=percentile_data,
            distribution_analysis=distribution_analysis,
            comparative_analysis=comparative_analysis,
            trend_statistics=trend_statistics,
            correlations=correlations,
            summary=summary
        )

    def _extract_scores(self, sessions: List[Dict[str, Any]]) -> List[float]:
        """提取分数数据"""
        scores = []
        for session in sessions:
            # Try multiple score sources
            score = 0.0
            
            # First try evaluation_result.overall_quality
            eval_result = session.get("evaluation_result", {})
            score = eval_result.get("overall_quality", 0.0)
            
            # If not found, try direct score field
            if score == 0.0:
                score = session.get("score", 0.0)
            
            if score > 0:
                scores.append(score)
        return scores

    # =========================================================================
    # Descriptive Statistics
    # =========================================================================

    def _calculate_descriptive_statistics(self, data: List[float]) -> DescriptiveStatistics:
        """计算描述性统计"""
        if not data:
            return DescriptiveStatistics(
                count=0, mean=0.0, median=0.0, mode=None,
                std_dev=0.0, variance=0.0, min_value=0.0, max_value=0.0,
                range_value=0.0, q1=0.0, q3=0.0, iqr=0.0
            )

        n = len(data)
        mean_val = statistics.mean(data)
        median_val = statistics.median(data)

        # 众数（可能有多个）
        try:
            modes = statistics.multimode(data)
            mode_val = modes[0] if modes else None
        except:
            mode_val = None

        # 标准差和方差
        std_dev = statistics.stdev(data) if n > 1 else 0.0
        variance = std_dev ** 2

        # 最小值、最大值、范围
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val

        # 四分位数
        sorted_data = sorted(data)
        q1 = self._calculate_percentile_value(sorted_data, 25)
        q3 = self._calculate_percentile_value(sorted_data, 75)
        iqr = q3 - q1

        return DescriptiveStatistics(
            count=n,
            mean=round(mean_val, 2),
            median=round(median_val, 2),
            mode=round(mode_val, 2) if mode_val is not None else None,
            std_dev=round(std_dev, 2),
            variance=round(variance, 2),
            min_value=round(min_val, 2),
            max_value=round(max_val, 2),
            range_value=round(range_val, 2),
            q1=round(q1, 2),
            q3=round(q3, 2),
            iqr=round(iqr, 2)
        )

    def _calculate_percentile_value(self, sorted_data: List[float], percentile: float) -> float:
        """计算指定百分位值"""
        if not sorted_data:
            return 0.0

        n = len(sorted_data)
        k = (n - 1) * (percentile / 100)
        f = math.floor(k)
        c = math.ceil(k)

        if f == c:
            return sorted_data[int(k)]

        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1

    # =========================================================================
    # Percentile Data
    # =========================================================================

    def _calculate_percentiles(self, data: List[float]) -> PercentileData:
        """计算百分位数据"""
        if not data:
            return PercentileData(
                p10=0.0, p25=0.0, p50=0.0, p75=0.0,
                p90=0.0, p95=0.0, p99=0.0
            )

        sorted_data = sorted(data)

        return PercentileData(
            p10=round(self._calculate_percentile_value(sorted_data, 10), 2),
            p25=round(self._calculate_percentile_value(sorted_data, 25), 2),
            p50=round(self._calculate_percentile_value(sorted_data, 50), 2),
            p75=round(self._calculate_percentile_value(sorted_data, 75), 2),
            p90=round(self._calculate_percentile_value(sorted_data, 90), 2),
            p95=round(self._calculate_percentile_value(sorted_data, 95), 2),
            p99=round(self._calculate_percentile_value(sorted_data, 99), 2),
        )

    # =========================================================================
    # Distribution Analysis
    # =========================================================================

    def _analyze_distribution(self, data: List[float]) -> DistributionAnalysis:
        """分析数据分布"""
        if len(data) < 3:
            return DistributionAnalysis(
                type=DistributionType.UNIFORM,
                skewness=0.0,
                kurtosis=0.0,
                is_normal=True,
                outliers_count=0,
                outliers_values=[]
            )

        # 计算偏度
        skewness = self._calculate_skewness(data)

        # 计算峰度
        kurtosis = self._calculate_kurtosis(data)

        # 检测异常值
        outliers = self._detect_outliers(data)

        # 判断分布类型
        dist_type = self._determine_distribution_type(data, skewness, kurtosis)

        # 正态性检验（简化版）
        is_normal = self._is_normal_distribution(data, skewness, kurtosis)

        return DistributionAnalysis(
            type=dist_type,
            skewness=round(skewness, 3),
            kurtosis=round(kurtosis, 3),
            is_normal=is_normal,
            outliers_count=len(outliers),
            outliers_values=[round(v, 2) for v in outliers]
        )

    def _calculate_skewness(self, data: List[float]) -> float:
        """计算偏度"""
        n = len(data)
        if n < 3:
            return 0.0

        mean_val = statistics.mean(data)
        std_dev = statistics.stdev(data)

        if std_dev == 0:
            return 0.0

        # Fisher-Pearson 偏度
        skew = sum((x - mean_val) ** 3 for x in data) / n
        skew = skew / (std_dev ** 3)

        return skew

    def _calculate_kurtosis(self, data: List[float]) -> float:
        """计算峰度"""
        n = len(data)
        if n < 4:
            return 0.0

        mean_val = statistics.mean(data)
        std_dev = statistics.stdev(data)

        if std_dev == 0:
            return 0.0

        # Fisher 峰度（超额峰度）
        kurt = sum((x - mean_val) ** 4 for x in data) / n
        kurt = kurt / (std_dev ** 4) - 3

        return kurt

    def _detect_outliers(self, data: List[float]) -> List[float]:
        """检测异常值（使用 IQR 方法）"""
        if len(data) < 4:
            return []

        sorted_data = sorted(data)
        q1 = self._calculate_percentile_value(sorted_data, 25)
        q3 = self._calculate_percentile_value(sorted_data, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [x for x in data if x < lower_bound or x > upper_bound]
        return outliers

    def _determine_distribution_type(self, data: List[float],
                                     skewness: float,
                                     kurtosis: float) -> DistributionType:
        """判断分布类型"""
        # 检查偏度
        if abs(skewness) > 1.0:
            if skewness > 0:
                return DistributionType.SKEWED_RIGHT
            else:
                return DistributionType.SKEWED_LEFT

        # 检查双峰（简化版）
        if len(data) >= 10:
            histogram = self._create_simple_histogram(data, bins=10)
            peaks = self._count_peaks(histogram)
            if peaks >= 2:
                return DistributionType.BIMODAL

        # 检查均匀性
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return DistributionType.UNIFORM

        # 默认正态
        return DistributionType.NORMAL

    def _create_simple_histogram(self, data: List[float], bins: int = 10) -> List[int]:
        """创建简单直方图"""
        min_val = min(data)
        max_val = max(data)
        bin_width = (max_val - min_val) / bins

        histogram = [0] * bins
        for value in data:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            histogram[bin_idx] += 1

        return histogram

    def _count_peaks(self, histogram: List[int]) -> int:
        """计算峰值数量"""
        if len(histogram) < 3:
            return 1

        peaks = 0
        for i in range(1, len(histogram) - 1):
            if histogram[i] > histogram[i - 1] and histogram[i] > histogram[i + 1]:
                peaks += 1

        return max(1, peaks)

    def _is_normal_distribution(self, data: List[float],
                               skewness: float,
                               kurtosis: float) -> bool:
        """判断是否为正态分布"""
        # 简化的正态性检验
        # 偏度接近 0，峰度接近 0（超额峰度）
        return abs(skewness) < 0.5 and abs(kurtosis) < 0.5

    # =========================================================================
    # Comparative Analysis
    # =========================================================================

    def _compare_with_population(self, user_score: float,
                                 dimension: str = "overall_quality") -> ComparativeAnalysis:
        """与人口数据对比"""
        pop_stats = self.ANONYMIZED_POPULATION_STATS.get(dimension, {
            "mean": 72.5,
            "std_dev": 12.3,
        })

        pop_mean = pop_stats["mean"]
        pop_std = pop_stats["std_dev"]

        # 计算 Z 分数
        z_score = (user_score - pop_mean) / pop_std if pop_std > 0 else 0.0

        # 计算 T 分数（T = 50 + 10 * Z）
        t_score = 50 + 10 * z_score

        # 百分位排名
        percentile_rank = self._z_to_percentile(z_score)

        # 确定性能水平
        performance_level = self._determine_performance_level(z_score)

        # 生成对比摘要
        comparison_summary = self._generate_comparison_summary(
            user_score, pop_mean, pop_std, percentile_rank, performance_level
        )

        return ComparativeAnalysis(
            user_score=round(user_score, 2),
            population_mean=round(pop_mean, 2),
            population_std=round(pop_std, 2),
            percentile_rank=round(percentile_rank, 2),
            z_score=round(z_score, 2),
            t_score=round(t_score, 2),
            performance_level=performance_level,
            comparison_summary=comparison_summary
        )

    def _z_to_percentile(self, z_score: float) -> float:
        """将 Z 分数转换为百分位排名"""
        # 使用误差函数近似标准正态分布的累积分布函数
        percentile = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
        return percentile * 100

    def _determine_performance_level(self, z_score: float) -> str:
        """确定性能水平"""
        if z_score >= self.PERFORMANCE_THRESHOLDS["excellent"]:
            return "excellent"
        elif z_score >= self.PERFORMANCE_THRESHOLDS["good"]:
            return "good"
        elif z_score >= self.PERFORMANCE_THRESHOLDS["average"]:
            return "average"
        elif z_score >= self.PERFORMANCE_THRESHOLDS["below_average"]:
            return "below_average"
        else:
            return "poor"

    def _generate_comparison_summary(self, user_score: float,
                                     pop_mean: float,
                                     pop_std: float,
                                     percentile_rank: float,
                                     performance_level: str) -> str:
        """生成对比摘要"""
        diff = user_score - pop_mean
        diff_percent = abs(diff) / pop_mean * 100

        level_names = {
            "excellent": "优秀",
            "good": "良好",
            "average": "平均",
            "below_average": "低于平均",
            "poor": "需要提升",
        }

        level_name = level_names.get(performance_level, "未知")

        if diff > 0:
            summary = (
                f"您的表现{level_name}，高于平均水平{diff_percent:.1f}%，"
                f"超过了{percentile_rank:.0f}%的用户。"
            )
        elif diff < 0:
            summary = (
                f"您的表现{level_name}，低于平均水平{diff_percent:.1f}%，"
                f"超过了{percentile_rank:.0f}%的用户。"
            )
        else:
            summary = f"您的表现处于平均水平，超过了{percentile_rank:.0f}%的用户。"

        return summary

    # =========================================================================
    # Trend Statistics
    # =========================================================================

    def _calculate_trend_statistics(self, sessions: List[Dict[str, Any]]) -> TrendStatistics:
        """计算趋势统计"""
        if len(sessions) < 3:
            return TrendStatistics(
                slope=0.0,
                r_squared=0.0,
                trend_direction="stable",
                trend_strength="weak",
                predicted_next_value=0.0,
                confidence_interval=(0.0, 0.0)
            )

        # 按时间排序
        sorted_sessions = sorted(
            sessions,
            key=lambda s: s.get("completed_at", datetime.utcnow())
        )

        # 提取分数
        scores = []
        for session in sorted_sessions:
            score = session.get("evaluation_result", {}).get("overall_quality", 0.0)
            if score > 0:
                scores.append(score)

        if len(scores) < 3:
            return TrendStatistics(
                slope=0.0,
                r_squared=0.0,
                trend_direction="stable",
                trend_strength="weak",
                predicted_next_value=0.0,
                confidence_interval=(0.0, 0.0)
            )

        # 线性回归
        n = len(scores)
        x_values = list(range(n))

        slope, intercept = self._linear_regression(x_values, scores)
        r_squared = self._calculate_r_squared(x_values, scores, slope, intercept)

        # 趋势方向
        if slope > 0.5:
            trend_direction = "upward"
        elif slope < -0.5:
            trend_direction = "downward"
        else:
            trend_direction = "stable"

        # 趋势强度
        if r_squared >= 0.7:
            trend_strength = "strong"
        elif r_squared >= 0.3:
            trend_strength = "moderate"
        else:
            trend_strength = "weak"

        # 预测下一个值
        predicted_next = slope * n + intercept

        # 置信区间（95%）
        ci = self._calculate_confidence_interval(x_values, scores, slope, intercept, n)

        return TrendStatistics(
            slope=round(slope, 3),
            r_squared=round(r_squared, 3),
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            predicted_next_value=round(predicted_next, 2),
            confidence_interval=(round(ci[0], 2), round(ci[1], 2))
        )

    def _linear_regression(self, x: List[float], y: List[float]) -> Tuple[float, float]:
        """线性回归"""
        n = len(x)
        if n < 2:
            return 0.0, 0.0

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0, y_mean

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        return slope, intercept

    def _calculate_r_squared(self, x: List[float], y: List[float],
                            slope: float, intercept: float) -> float:
        """计算决定系数 R²"""
        n = len(y)
        if n < 2:
            return 0.0

        y_mean = statistics.mean(y)

        # 总平方和
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))

        # 残差平方和
        y_pred = [slope * x[i] + intercept for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))

        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0

        r_squared = 1 - (ss_res / ss_tot)
        return max(0, min(1, r_squared))

    def _calculate_confidence_interval(self, x: List[float], y: List[float],
                                       slope: float, intercept: float,
                                       x_pred: float) -> Tuple[float, float]:
        """计算置信区间"""
        n = len(y)
        if n < 3:
            return (0.0, 0.0)

        # 残差标准误
        y_pred = [slope * x[i] + intercept for i in range(n)]
        residuals = [y[i] - y_pred[i] for i in range(n)]
        sse = sum(r ** 2 for r in residuals)
        mse = sse / (n - 2)
        s = math.sqrt(mse)

        # t 值（95% 置信度，简化为 2）
        t_value = 2.0

        # 标准误
        x_mean = statistics.mean(x)
        ss_x = sum((xi - x_mean) ** 2 for xi in x)

        if ss_x == 0:
            return (0.0, 0.0)

        se = s * math.sqrt(1/n + (x_pred - x_mean) ** 2 / ss_x)

        # 预测值
        y_pred_value = slope * x_pred + intercept

        # 置信区间
        margin = t_value * se
        return (y_pred_value - margin, y_pred_value + margin)

    # =========================================================================
    # Correlation Analysis
    # =========================================================================

    def _calculate_correlations(self, sessions: List[Dict[str, Any]]) -> List[CorrelationData]:
        """计算相关分析"""
        correlations = []

        if len(sessions) < 5:
            return correlations

        # 提取各维度分数
        dimensions_data: Dict[str, List[float]] = {}

        for session in sessions:
            eval_result = session.get("evaluation_result", {})
            for dim, score in eval_result.items():
                if score > 0:
                    if dim not in dimensions_data:
                        dimensions_data[dim] = []
                    dimensions_data[dim].append(score)

        # 计算维度间的相关性
        dimension_pairs = [
            ("language_expression", "logical_thinking"),
            ("professional_knowledge", "problem_solving"),
            ("communication_collaboration", "adaptability"),
            ("overall_quality", "language_expression"),
        ]

        for dim1, dim2 in dimension_pairs:
            if dim1 in dimensions_data and dim2 in dimensions_data:
                data1 = dimensions_data[dim1]
                data2 = dimensions_data[dim2]

                # 确保长度一致
                min_len = min(len(data1), len(data2))
                if min_len < 5:
                    continue

                data1 = data1[:min_len]
                data2 = data2[:min_len]

                corr = self._calculate_correlation(data1, data2)
                relationship, strength = self._interpret_correlation(corr)

                correlations.append(CorrelationData(
                    variable1=dim1,
                    variable2=dim2,
                    correlation_coefficient=round(corr, 3),
                    relationship=relationship,
                    strength=strength
                ))

        return correlations

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """计算皮尔逊相关系数"""
        n = len(x)
        if n < 2:
            return 0.0

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))

        sum_sq_x = sum((x[i] - x_mean) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - y_mean) ** 2 for i in range(n))

        denominator = math.sqrt(sum_sq_x * sum_sq_y)

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _interpret_correlation(self, corr: float) -> Tuple[str, str]:
        """解释相关系数"""
        # 关系方向
        if corr > 0.1:
            relationship = "positive"
        elif corr < -0.1:
            relationship = "negative"
        else:
            relationship = "none"

        # 强度
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            strength = "strong"
        elif abs_corr >= 0.3:
            strength = "moderate"
        else:
            strength = "weak"

        return relationship, strength

    # =========================================================================
    # Summary Generation
    # =========================================================================

    def _generate_statistical_summary(self,
                                      descriptive_stats: DescriptiveStatistics,
                                      distribution_analysis: DistributionAnalysis,
                                      comparative_analysis: Optional[ComparativeAnalysis],
                                      trend_statistics: TrendStatistics) -> str:
        """生成统计摘要"""
        parts = []

        # 基本统计
        if descriptive_stats.count > 0:
            parts.append(
                f"基于{descriptive_stats.count}次会话的统计分析： "
                f"平均分{descriptive_stats.mean}分，标准差{descriptive_stats.std_dev}。"
            )

        # 分布特征
        dist_desc = {
            DistributionType.NORMAL: "接近正态分布",
            DistributionType.SKEWED_LEFT: "左偏分布",
            DistributionType.SKEWED_RIGHT: "右偏分布",
            DistributionType.UNIFORM: "均匀分布",
            DistributionType.BIMODAL: "双峰分布",
        }
        parts.append(f"分数分布{dist_desc.get(distribution_analysis.type, '未知')}。")

        # 异常值
        if distribution_analysis.outliers_count > 0:
            parts.append(
                f"检测到{distribution_analysis.outliers_count}个异常值，"
                f"可能代表超常发挥或发挥失常的情况。"
            )

        # 对比分析
        if comparative_analysis:
            parts.append(comparative_analysis.comparison_summary)

        # 趋势
        trend_desc = {
            "upward": "上升趋势",
            "downward": "下降趋势",
            "stable": "稳定",
        }
        strength_desc = {
            "strong": "强烈",
            "moderate": "中等",
            "weak": "微弱",
        }
        parts.append(
            f"表现呈{strength_desc.get(trend_statistics.trend_strength, '')}的"
            f"{trend_desc.get(trend_statistics.trend_direction, '稳定')}趋势。"
        )

        return " ".join(parts)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def to_dict(self, report: StatisticalReport) -> Dict[str, Any]:
        """将 StatisticalReport 转换为字典"""
        return {
            "user_id": report.user_id,
            "generated_at": report.generated_at.isoformat(),
            "period_days": report.period_days,
            "descriptive_stats": {
                "count": report.descriptive_stats.count,
                "mean": report.descriptive_stats.mean,
                "median": report.descriptive_stats.median,
                "mode": report.descriptive_stats.mode,
                "std_dev": report.descriptive_stats.std_dev,
                "variance": report.descriptive_stats.variance,
                "min": report.descriptive_stats.min_value,
                "max": report.descriptive_stats.max_value,
                "range": report.descriptive_stats.range_value,
                "q1": report.descriptive_stats.q1,
                "q3": report.descriptive_stats.q3,
                "iqr": report.descriptive_stats.iqr,
            },
            "percentile_data": {
                "p10": report.percentile_data.p10,
                "p25": report.percentile_data.p25,
                "p50": report.percentile_data.p50,
                "p75": report.percentile_data.p75,
                "p90": report.percentile_data.p90,
                "p95": report.percentile_data.p95,
                "p99": report.percentile_data.p99,
            },
            "distribution_analysis": {
                "type": report.distribution_analysis.type.value,
                "skewness": report.distribution_analysis.skewness,
                "kurtosis": report.distribution_analysis.kurtosis,
                "is_normal": report.distribution_analysis.is_normal,
                "outliers_count": report.distribution_analysis.outliers_count,
                "outliers_values": report.distribution_analysis.outliers_values,
            },
            "comparative_analysis": {
                "user_score": report.comparative_analysis.user_score,
                "population_mean": report.comparative_analysis.population_mean,
                "population_std": report.comparative_analysis.population_std,
                "percentile_rank": report.comparative_analysis.percentile_rank,
                "z_score": report.comparative_analysis.z_score,
                "t_score": report.comparative_analysis.t_score,
                "performance_level": report.comparative_analysis.performance_level,
                "comparison_summary": report.comparative_analysis.comparison_summary,
            } if report.comparative_analysis else None,
            "trend_statistics": {
                "slope": report.trend_statistics.slope,
                "r_squared": report.trend_statistics.r_squared,
                "trend_direction": report.trend_statistics.trend_direction,
                "trend_strength": report.trend_statistics.trend_strength,
                "predicted_next_value": report.trend_statistics.predicted_next_value,
                "confidence_interval": report.trend_statistics.confidence_interval,
            },
            "correlations": [
                {
                    "variable1": c.variable1,
                    "variable2": c.variable2,
                    "correlation_coefficient": c.correlation_coefficient,
                    "relationship": c.relationship,
                    "strength": c.strength,
                }
                for c in report.correlations
            ],
            "summary": report.summary,
        }

    def clear_cache(self):
        """清除缓存"""
        self._population_cache.clear()
