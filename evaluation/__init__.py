"""
Evaluation Module - 评估模块 (v0.3)

提供面试评估功能，包括：

v0.2 (基础评估):
- BasicEvaluator: 三维度评估器
- EvaluationResult: 评估结果数据类
- EvaluationReport: 评估报告生成

v0.3 (高级评估 - 智能反馈系统):
- AdvancedEvaluator: 7 维度智能评估器
- AdvancedEvaluationResult: 高级评估结果
- AdvancedFeedbackReport: 高级反馈报告
- EvaluationStorage: SQLite 持久化存储
- FeedbackReportGenerator: 多格式报告生成器

评估维度 (v0.3 - 7 维度):
1. content_quality (内容质量): 相关性、准确性、深度
2. expression_clarity (表达清晰度): 逻辑性、简洁性、条理性
3. professional_knowledge (专业知识): 技术深度、经验、解决问题能力
4. adaptability (应变能力): 处理意外问题、灵活应对
5. communication_skills (沟通技巧): 倾听、表达、互动质量
6. confidence_level (自信程度): 语气、确定性、自我展示
7. innovative_thinking (创新思维): 独特见解、创造性解决方案

使用示例:
    >>> from evaluation import AdvancedEvaluator, EvaluationStorage, FeedbackReportGenerator
    >>> 
    >>> # 创建评估器
    >>> evaluator = AdvancedEvaluator(model_agent=model_agent)
    >>> 
    >>> # 评估对话
    >>> result = evaluator.evaluate(dialogue_history)
    >>> 
    >>> # 保存结果
    >>> storage = EvaluationStorage()
    >>> storage.save_evaluation(result, session_id="xxx")
    >>> 
    >>> # 生成报告
    >>> report_gen = FeedbackReportGenerator()
    >>> report = report_gen.generate(result, format="markdown")
"""

# v0.2 - Basic Evaluator (保持向后兼容)
from .basic_evaluator import (
    BasicEvaluator,
    EvaluationResult,
    EvaluationReport,
    EvaluationDimension,
    DimensionScore,
)

# v0.3 - Advanced Evaluator
from .advanced_evaluator import (
    AdvancedEvaluator,
    AdvancedEvaluationResult,
    AdvancedFeedbackReport,
    EvaluationDimension7,
    DimensionScore7,
)

# v0.3 - Storage
from .storage import (
    EvaluationStorage,
    EvaluationRecord,
    EvaluationStatistics,
)

# v0.3 - Report Generator
from .report import (
    FeedbackReportGenerator,
    ReportTemplate,
)

# 导出所有内容
__all__ = [
    # v0.2 - Basic
    "BasicEvaluator",
    "EvaluationResult",
    "EvaluationReport",
    "EvaluationDimension",
    "DimensionScore",
    # v0.3 - Advanced
    "AdvancedEvaluator",
    "AdvancedEvaluationResult",
    "AdvancedFeedbackReport",
    "EvaluationDimension7",
    "DimensionScore7",
    # v0.3 - Storage
    "EvaluationStorage",
    "EvaluationRecord",
    "EvaluationStatistics",
    # v0.3 - Report
    "FeedbackReportGenerator",
    "ReportTemplate",
]

# 版本信息
__version__ = "0.3.0"
__author__ = "AgentScope AI Interview Team"


def get_evaluator(version: str = "v0.3", **kwargs):
    """
    工厂函数：获取评估器实例

    Args:
        version: 评估器版本 ("v0.2" 或 "v0.3")
        **kwargs: 传递给评估器构造函数的参数

    Returns:
        评估器实例

    Example:
        >>> evaluator = get_evaluator("v0.3", model_agent=agent)
        >>> evaluator = get_evaluator("v0.2")
    """
    if version == "v0.2":
        return BasicEvaluator(**kwargs)
    elif version == "v0.3":
        return AdvancedEvaluator(**kwargs)
    else:
        raise ValueError(f"不支持的评估器版本：{version}")


def create_storage(db_path: Optional[str] = None, **kwargs):
    """
    工厂函数：创建存储实例

    Args:
        db_path: 数据库路径
        **kwargs: 其他参数

    Returns:
        EvaluationStorage 实例
    """
    return EvaluationStorage(db_path=db_path, **kwargs)


def create_report_generator(**kwargs):
    """
    工厂函数：创建报告生成器实例

    Args:
        **kwargs: 传递给构造函数的参数

    Returns:
        FeedbackReportGenerator 实例
    """
    return FeedbackReportGenerator(**kwargs)


# 延迟导入 Optional 以避免循环导入
from typing import Optional
