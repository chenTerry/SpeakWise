"""
Chart Generation Utilities

图表生成工具：
- ASCII 图表（CLI 终端显示）
- SVG 图表（Web 界面）
- 通用图表生成器

Design Principles:
- 支持多种输出格式
- 可配置的样式
- 简单易用的 API
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChartType(str, Enum):
    """图表类型"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    RADAR = "radar"


class ChartStyle:
    """图表样式配置"""
    
    # ASCII 字符
    ASCII_BAR_HORIZONTAL = "█"
    ASCII_BAR_EMPTY = "░"
    ASCII_LINE_POINT = "●"
    ASCII_LINE_CONNECTOR = "─"
    
    # 颜色（用于支持颜色的终端）
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "reset": "\033[0m",
    }


@dataclass
class ChartData:
    """图表数据"""
    labels: List[str]
    values: List[float]
    title: str = ""
    colors: Optional[List[str]] = None


class ASCIIChart:
    """
    ASCII 图表生成器
    
    用于在终端显示简单的图表
    """
    
    def __init__(self, width: int = 60, height: int = 20):
        """
        初始化 ASCII 图表
        
        Args:
            width: 图表宽度（字符数）
            height: 图表高度（行数）
        """
        self.width = width
        self.height = height
    
    def generate_bar_chart(self, data: ChartData, 
                          show_values: bool = True) -> str:
        """
        生成条形图
        
        Args:
            data: 图表数据
            show_values: 是否显示数值
            
        Returns:
            ASCII 条形图字符串
        """
        if not data.labels or not data.values:
            return "No data to display"
        
        lines = []
        
        # 标题
        if data.title:
            lines.append(f"╔{'═' * (len(data.title) + 2)}╗")
            lines.append(f"║ {data.title} ║")
            lines.append(f"╚{'═' * (len(data.title) + 2)}╝")
            lines.append("")
        
        # 找到最大值用于缩放
        max_value = max(data.values) if data.values else 1
        bar_max_width = self.width - 20  # 留出标签空间
        
        # 生成条形
        for i, (label, value) in enumerate(zip(data.labels, data.values)):
            # 计算条形长度
            bar_length = int((value / max_value) * bar_max_width) if max_value > 0 else 0
            bar = ChartStyle.ASCII_BAR_HORIZONTAL * bar_length
            empty = ChartStyle.ASCII_EMPTY * (bar_max_width - bar_length)
            
            # 格式化数值
            value_str = f"{value:.1f}" if show_values else ""
            
            # 组合行
            label_padded = label[:15].ljust(15)
            line = f"{label_padded} │{bar}{empty}│ {value_str}"
            lines.append(line)
        
        # 添加图例
        lines.append("")
        lines.append(f"{' ' * 16}└{'─' * bar_max_width}┘")
        lines.append(f"{' ' * 16} 0{' ' * (bar_max_width - 5)}{max_value:.1f}")
        
        return "\n".join(lines)
    
    def generate_horizontal_bar_chart(self, data: ChartData,
                                     show_values: bool = True) -> str:
        """
        生成水平条形图（更适合长标签）
        
        Args:
            data: 图表数据
            show_values: 是否显示数值
            
        Returns:
            ASCII 水平条形图字符串
        """
        if not data.labels or not data.values:
            return "No data to display"
        
        lines = []
        
        # 标题
        if data.title:
            lines.append(f"╔{'═' * (len(data.title) + 2)}╗")
            lines.append(f"║ {data.title} ║")
            lines.append(f"╚{'═' * (len(data.title) + 2)}╝")
            lines.append("")
        
        # 找到最大值用于缩放
        max_value = max(data.values) if data.values else 1
        bar_max_width = self.width - 30  # 留出标签和数值空间
        
        # 生成条形
        for i, (label, value) in enumerate(zip(data.labels, data.values)):
            # 计算条形长度
            bar_length = int((value / max_value) * bar_max_width) if max_value > 0 else 0
            bar = ChartStyle.ASCII_BAR_HORIZONTAL * bar_length
            
            # 格式化数值
            value_str = f"{value:.1f}" if show_values else ""
            
            # 组合行
            label_padded = label[:12].ljust(12)
            value_padded = value_str.rjust(6)
            line = f"{label_padded} │{bar}│ {value_padded}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def generate_line_chart(self, data: ChartData,
                           show_points: bool = True) -> str:
        """
        生成简单的折线图
        
        Args:
            data: 图表数据
            show_points: 是否显示数据点
            
        Returns:
            ASCII 折线图字符串
        """
        if not data.labels or not data.values:
            return "No data to display"
        
        lines = []
        
        # 标题
        if data.title:
            lines.append(f"╔{'═' * (len(data.title) + 2)}╗")
            lines.append(f"║ {data.title} ║")
            lines.append(f"╚{'═' * (len(data.title) + 2)}╝")
            lines.append("")
        
        # 找到最大最小值
        max_value = max(data.values) if data.values else 1
        min_value = min(data.values) if data.values else 0
        value_range = max_value - min_value if max_value != min_value else 1
        
        # 图表高度
        chart_height = min(self.height - 6, len(data.values))
        
        # 创建网格
        grid = [[" " for _ in range(len(data.values))] for _ in range(chart_height)]
        
        # 填充数据点
        for i, value in enumerate(data.values):
            # 计算行位置（从底部开始）
            normalized = (value - min_value) / value_range
            row = int(normalized * (chart_height - 1))
            row = chart_height - 1 - row  # 翻转
            
            if 0 <= row < chart_height:
                grid[row][i] = ChartStyle.ASCII_LINE_POINT
        
        # 生成输出
        # Y 轴标签
        lines.append(f"{max_value:>8.1f} │" + "".join(grid[0]))
        
        for row in grid[1:-1]:
            lines.append(f"{' ' * 9}│" + "".join(row))
        
        lines.append(f"{min_value:>8.1f} │" + "".join(grid[-1]))
        
        # X 轴
        lines.append(f"{' ' * 9}└" + "─" * len(data.values))
        
        # X 轴标签（简化）
        if len(data.labels) <= 10:
            label_line = " " * 10 + "".join([l[0] if l else " " for l in data.labels])
            lines.append(label_line)
        
        return "\n".join(lines)
    
    def generate_progress_bars(self, items: List[Tuple[str, float, float]],
                              title: str = "Progress") -> str:
        """
        生成进度条（带百分比）
        
        Args:
            items: 列表，每项为 (标签，当前值，最大值)
            title: 标题
            
        Returns:
            ASCII 进度条字符串
        """
        lines = []
        
        # 标题
        if title:
            lines.append(f"╔{'═' * (len(title) + 2)}╗")
            lines.append(f"║ {title} ║")
            lines.append(f"╚{'═' * (title + 2)}╝")
            lines.append("")
        
        bar_width = self.width - 25
        
        for label, current, maximum in items:
            if maximum <= 0:
                percentage = 0
                bar_length = 0
            else:
                percentage = (current / maximum) * 100
                bar_length = int((current / maximum) * bar_width)
            
            bar = ChartStyle.ASCII_BAR_HORIZONTAL * bar_length
            empty = ChartStyle.ASCII_EMPTY * (bar_width - bar_length)
            
            label_padded = label[:12].ljust(12)
            percentage_str = f"{percentage:5.1f}%"
            
            line = f"{label_padded} │{bar}{empty}│ {percentage_str}"
            lines.append(line)
        
        return "\n".join(lines)


class ChartGenerator:
    """
    通用图表生成器
    
    根据输出格式自动选择合适的图表类型
    """
    
    def __init__(self, output_format: str = "ascii",
                 width: int = 60, height: int = 20):
        """
        初始化图表生成器
        
        Args:
            output_format: 输出格式（ascii, svg）
            width: 图表宽度
            height: 图表高度
        """
        self.output_format = output_format
        self.width = width
        self.height = height
        self.ascii_chart = ASCIIChart(width, height)
    
    def generate(self, chart_type: ChartType, data: ChartData,
                **kwargs) -> str:
        """
        生成图表
        
        Args:
            chart_type: 图表类型
            data: 图表数据
            **kwargs: 额外参数
            
        Returns:
            图表字符串
        """
        if self.output_format == "ascii":
            return self._generate_ascii(chart_type, data, **kwargs)
        elif self.output_format == "svg":
            return self._generate_svg(chart_type, data, **kwargs)
        else:
            return self._generate_ascii(chart_type, data, **kwargs)
    
    def _generate_ascii(self, chart_type: ChartType, data: ChartData,
                       **kwargs) -> str:
        """
        生成 ASCII 图表
        
        Args:
            chart_type: 图表类型
            data: 图表数据
            **kwargs: 额外参数
            
        Returns:
            ASCII 图表字符串
        """
        if chart_type == ChartType.BAR:
            return self.ascii_chart.generate_horizontal_bar_chart(data, **kwargs)
        elif chart_type == ChartType.LINE:
            return self.ascii_chart.generate_line_chart(data, **kwargs)
        else:
            return f"Unsupported chart type: {chart_type}"
    
    def _generate_svg(self, chart_type: ChartType, data: ChartData,
                     **kwargs) -> str:
        """
        生成 SVG 图表
        
        Args:
            chart_type: 图表类型
            data: 图表数据
            **kwargs: 额外参数
            
        Returns:
            SVG 字符串
        """
        # 简化 SVG 生成，实际项目可使用 matplotlib 或 plotly
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width * 10}" height="{self.height * 20}">',
            f'  <text x="10" y="30" font-family="Arial" font-size="16">{data.title}</text>',
            '</svg>'
        ]
        
        return "\n".join(svg_parts)


def create_bar_chart(labels: List[str], values: List[float],
                    title: str = "", width: int = 60) -> str:
    """
    便捷函数：创建条形图
    
    Args:
        labels: 标签列表
        values: 数值列表
        title: 标题
        width: 图表宽度
        
    Returns:
        ASCII 条形图字符串
    """
    chart = ASCIIChart(width=width)
    data = ChartData(labels=labels, values=values, title=title)
    return chart.generate_horizontal_bar_chart(data)


def create_progress_bar(label: str, current: float, maximum: float,
                       width: int = 40) -> str:
    """
    便捷函数：创建单个进度条
    
    Args:
        label: 标签
        current: 当前值
        maximum: 最大值
        width: 进度条宽度
        
    Returns:
        ASCII 进度条字符串
    """
    if maximum <= 0:
        percentage = 0
        bar_length = 0
    else:
        percentage = (current / maximum) * 100
        bar_length = int((current / maximum) * width)
    
    bar = ChartStyle.ASCII_BAR_HORIZONTAL * bar_length
    empty = ChartStyle.ASCII_EMPTY * (width - bar_length)
    
    return f"{label[:15].ljust(15)} │{bar}{empty}│ {percentage:5.1f}%"
