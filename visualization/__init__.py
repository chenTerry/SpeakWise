"""
AgentScope AI Interview - Visualization Module

数据可视化模块提供：
- 图表生成（ASCII for CLI, SVG for Web）
- 雷达图（七维度评估）
- 趋势图（进度趋势）

版本：v0.6.0
"""

from .charts import ChartGenerator, ASCIIChart
from .radar import RadarChart, DimensionRadarChart
from .trends import TrendChart, ProgressTrendChart

__version__ = "0.6.0"

__all__ = [
    "ChartGenerator",
    "ASCIIChart",
    "RadarChart",
    "DimensionRadarChart",
    "TrendChart",
    "ProgressTrendChart",
]
