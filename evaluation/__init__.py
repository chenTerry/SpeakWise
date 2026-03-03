"""
Evaluation Module - 评估模块

提供面试评估功能，包括：
- BasicEvaluator: 三维度评估器
- EvaluationResult: 评估结果数据类
- EvaluationReport: 评估报告生成

评估维度:
1. content_quality (内容质量): 相关性、准确性、深度
2. expression_clarity (表达清晰度): 逻辑性、简洁性、条理性
3. professional_knowledge (专业知识): 专业知识、经验、解决问题能力
"""

from .basic_evaluator import (
    BasicEvaluator,
    EvaluationResult,
    EvaluationReport,
    EvaluationDimension,
    DimensionScore,
)

__all__ = [
    "BasicEvaluator",
    "EvaluationResult",
    "EvaluationReport",
    "EvaluationDimension",
    "DimensionScore",
]
