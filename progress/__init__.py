"""
AgentScope AI Interview - Progress Module

进度追踪模块提供：
- ProgressTracker: 进度追踪器
- Metrics: 进度指标计算
- History: 会话历史管理

版本：v0.6.0
"""

from .tracker import ProgressTracker
from .metrics import ProgressMetricsCalculator, DimensionScore
from .history import SessionHistoryManager

__version__ = "0.6.0"

__all__ = [
    "ProgressTracker",
    "ProgressMetricsCalculator",
    "DimensionScore",
    "SessionHistoryManager",
]
