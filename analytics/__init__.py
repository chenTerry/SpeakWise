"""
AgentScope AI Interview - Analytics Module

分析模块提供：
- LearningAnalytics: 学习数据分析系统
- BehaviorTracker: 用户行为追踪系统
- RecommendationEngine: 个性化推荐系统
- StatisticsEngine: 统计分析系统
- InsightsDashboard: 洞察可视化系统
- DataExporter: 数据导出系统

版本：v0.7.0
新增功能:
- 学习模式识别和强弱项分析
- 行为追踪和平台期检测
- 个性化学习路径推荐
- 高级统计分析（百分位数、分布、对比）
- 洞察仪表盘和成就系统
- 多格式数据导出（PDF/Excel/JSON）

依赖:
- pandas (可选，用于高级数据分析)
- numpy (可选，用于数值计算)
- reportlab (可选，用于 PDF 生成)
- openpyxl (可选，用于 Excel 导出)
- matplotlib (可选，用于图表生成)
"""

from .learning import (
    LearningAnalytics,
    LearningProfile,
    LearningStrength,
    LearningWeakness,
    LearningInsight,
    LearningPattern,
    SkillLevel,
)

from .behavior import (
    BehaviorTracker,
    BehaviorReport,
    SessionPattern,
    EngagementMetrics,
    ImprovementPattern,
    PlateauAnalysis,
    EngagementLevel,
    PlateauStatus,
)

from .recommender import (
    RecommendationEngine,
    RecommendationReport,
    TopicRecommendation,
    DifficultyRecommendation,
    LearningPath,
    LearningPathItem,
    PracticeMethodRecommendation,
    DifficultyLevel,
    RecommendationType,
)

from .statistics import (
    StatisticsEngine,
    StatisticalReport,
    DescriptiveStatistics,
    PercentileData,
    DistributionAnalysis,
    ComparativeAnalysis,
    TrendStatistics,
    CorrelationData,
    DistributionType,
)

from .insights import (
    InsightsDashboard,
    DashboardData,
    KeyInsight,
    TrendAnalysis,
    PerformanceCard,
    ActionableRecommendation,
    Achievement,
    InsightCategory,
    InsightPriority,
)

from .export import (
    DataExporter,
    ExportResult,
    ExportFormat,
    ReportType,
    BackupData,
)

__version__ = "0.7.0"

__all__ = [
    # Version
    "__version__",

    # Learning Analytics
    "LearningAnalytics",
    "LearningProfile",
    "LearningStrength",
    "LearningWeakness",
    "LearningInsight",
    "LearningPattern",
    "SkillLevel",

    # Behavior Tracking
    "BehaviorTracker",
    "BehaviorReport",
    "SessionPattern",
    "EngagementMetrics",
    "ImprovementPattern",
    "PlateauAnalysis",
    "EngagementLevel",
    "PlateauStatus",

    # Recommendation Engine
    "RecommendationEngine",
    "RecommendationReport",
    "TopicRecommendation",
    "DifficultyRecommendation",
    "LearningPath",
    "LearningPathItem",
    "PracticeMethodRecommendation",
    "DifficultyLevel",
    "RecommendationType",

    # Statistics Engine
    "StatisticsEngine",
    "StatisticalReport",
    "DescriptiveStatistics",
    "PercentileData",
    "DistributionAnalysis",
    "ComparativeAnalysis",
    "TrendStatistics",
    "CorrelationData",
    "DistributionType",

    # Insights Dashboard
    "InsightsDashboard",
    "DashboardData",
    "KeyInsight",
    "TrendAnalysis",
    "PerformanceCard",
    "ActionableRecommendation",
    "Achievement",
    "InsightCategory",
    "InsightPriority",

    # Data Export
    "DataExporter",
    "ExportResult",
    "ExportFormat",
    "ReportType",
    "BackupData",
]
