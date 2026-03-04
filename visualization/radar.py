"""
Radar Chart Generation

雷达图生成：
- 七维度评估雷达图
- SVG 格式输出
- ASCII 简化版本

Design Principles:
- 支持多种输出格式
- 可配置的维度和标签
- 美观的可视化效果
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class RadarDimension:
    """雷达图维度"""
    name: str
    value: float  # 0-100
    color: str = "#3498db"


class RadarChart:
    """
    雷达图生成器
    
    生成 SVG 格式的雷达图
    """
    
    def __init__(self, width: int = 400, height: int = 400,
                 margin: int = 50):
        """
        初始化雷达图
        
        Args:
            width: 图表宽度
            height: 图表高度
            margin: 边距
        """
        self.width = width
        self.height = height
        self.margin = margin
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = min(width, height) / 2 - margin
    
    def generate(self, dimensions: List[RadarDimension],
                title: str = "") -> str:
        """
        生成雷达图 SVG
        
        Args:
            dimensions: 维度列表
            title: 图表标题
            
        Returns:
            SVG 字符串
        """
        if not dimensions:
            return "<svg></svg>"
        
        n = len(dimensions)
        angle_step = 2 * math.pi / n
        
        # 计算各顶点坐标
        points = []
        for i, dim in enumerate(dimensions):
            # 从顶部开始（-90 度）
            angle = i * angle_step - math.pi / 2
            # 根据分数计算半径
            r = self.radius * (dim.value / 100)
            x = self.center_x + r * math.cos(angle)
            y = self.center_y + r * math.sin(angle)
            points.append((x, y))
        
        # 生成 SVG
        svg_parts = []
        
        # SVG 头
        svg_parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                        f'width="{self.width}" height="{self.height}" '
                        f'viewBox="0 0 {self.width} {self.height}">')
        
        # 背景
        svg_parts.append(f'  <rect width="{self.width}" height="{self.height}" fill="#ffffff"/>')
        
        # 标题
        if title:
            svg_parts.append(f'  <text x="{self.center_x}" y="30" '
                           f'text-anchor="middle" font-family="Arial" '
                           f'font-size="18" font-weight="bold">{title}</text>')
        
        # 绘制网格（同心多边形）
        for level in range(1, 6):
            level_radius = self.radius * level / 5
            grid_points = []
            for i in range(n):
                angle = i * angle_step - math.pi / 2
                x = self.center_x + level_radius * math.cos(angle)
                y = self.center_y + level_radius * math.sin(angle)
                grid_points.append(f"{x:.1f},{y:.1f}")
            
            svg_parts.append(f'  <polygon points="{" ".join(grid_points)}" '
                           f'fill="none" stroke="#e0e0e0" stroke-width="1"/>')
        
        # 绘制轴线
        for i in range(n):
            angle = i * angle_step - math.pi / 2
            x = self.center_x + self.radius * math.cos(angle)
            y = self.center_y + self.radius * math.sin(angle)
            
            svg_parts.append(f'  <line x1="{self.center_x:.1f}" y1="{self.center_y:.1f}" '
                           f'x2="{x:.1f}" y2="{y:.1f}" '
                           f'stroke="#d0d0d0" stroke-width="1"/>')
        
        # 绘制数据区域
        data_points = [f"{p[0]:.1f},{p[1]:.1f}" for p in points]
        svg_parts.append(f'  <polygon points="{" ".join(data_points)}" '
                        f'fill="{dimensions[0].color}" fill-opacity="0.3" '
                        f'stroke="{dimensions[0].color}" stroke-width="2"/>')
        
        # 绘制数据点
        for x, y in points:
            svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                           f'fill="{dimensions[0].color}"/>')
        
        # 绘制维度标签
        for i, dim in enumerate(dimensions):
            angle = i * angle_step - math.pi / 2
            # 标签位置在轴线外侧
            label_radius = self.radius + 20
            x = self.center_x + label_radius * math.cos(angle)
            y = self.center_y + label_radius * math.sin(angle)
            
            # 调整文本锚点
            text_anchor = "middle"
            if x < self.center_x - 50:
                text_anchor = "end"
            elif x > self.center_x + 50:
                text_anchor = "start"
            
            svg_parts.append(f'  <text x="{x:.1f}" y="{y:.1f}" '
                           f'text-anchor="{text_anchor}" '
                           f'dominant-baseline="middle" '
                           f'font-family="Arial" font-size="12" '
                           f'fill="#333">{dim.name}</text>')
        
        # SVG 尾
        svg_parts.append('</svg>')
        
        return "\n".join(svg_parts)
    
    def generate_multi_series(self, series_list: List[Tuple[str, List[RadarDimension], str]],
                             title: str = "") -> str:
        """
        生成多系列雷达图
        
        Args:
            series_list: 列表，每项为 (系列名，维度列表，颜色)
            title: 图表标题
            
        Returns:
            SVG 字符串
        """
        if not series_list:
            return "<svg></svg>"
        
        # 使用第一个系列的维度数
        n = len(series_list[0][1])
        angle_step = 2 * math.pi / n
        
        # SVG 头
        svg_parts = []
        svg_parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                        f'width="{self.width}" height="{self.height}" '
                        f'viewBox="0 0 {self.width} {self.height}">')
        
        # 背景
        svg_parts.append(f'  <rect width="{self.width}" height="{self.height}" fill="#ffffff"/>')
        
        # 标题
        if title:
            svg_parts.append(f'  <text x="{self.center_x}" y="30" '
                           f'text-anchor="middle" font-family="Arial" '
                           f'font-size="18" font-weight="bold">{title}</text>')
        
        # 绘制网格
        for level in range(1, 6):
            level_radius = self.radius * level / 5
            grid_points = []
            for i in range(n):
                angle = i * angle_step - math.pi / 2
                x = self.center_x + level_radius * math.cos(angle)
                y = self.center_y + level_radius * math.sin(angle)
                grid_points.append(f"{x:.1f},{y:.1f}")
            
            svg_parts.append(f'  <polygon points="{" ".join(grid_points)}" '
                           f'fill="none" stroke="#e0e0e0" stroke-width="1"/>')
        
        # 绘制各系列
        for series_name, dimensions, color in series_list:
            # 计算顶点
            points = []
            for i, dim in enumerate(dimensions):
                angle = i * angle_step - math.pi / 2
                r = self.radius * (dim.value / 100)
                x = self.center_x + r * math.cos(angle)
                y = self.center_y + r * math.sin(angle)
                points.append((x, y))
            
            # 绘制数据区域
            data_points = [f"{p[0]:.1f},{p[1]:.1f}" for p in points]
            svg_parts.append(f'  <polygon points="{" ".join(data_points)}" '
                           f'fill="{color}" fill-opacity="0.2" '
                           f'stroke="{color}" stroke-width="2"/>')
            
            # 绘制数据点
            for x, y in points:
                svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4" '
                               f'fill="{color}"/>')
        
        # 绘制维度标签
        for i, dim in enumerate(series_list[0][1]):
            angle = i * angle_step - math.pi / 2
            label_radius = self.radius + 20
            x = self.center_x + label_radius * math.cos(angle)
            y = self.center_y + label_radius * math.sin(angle)
            
            text_anchor = "middle"
            if x < self.center_x - 50:
                text_anchor = "end"
            elif x > self.center_x + 50:
                text_anchor = "start"
            
            svg_parts.append(f'  <text x="{x:.1f}" y="{y:.1f}" '
                           f'text-anchor="{text_anchor}" '
                           f'dominant-baseline="middle" '
                           f'font-family="Arial" font-size="12" '
                           f'fill="#333">{dim.name}</text>')
        
        # 图例
        legend_y = self.height - 20
        for i, (series_name, _, color) in enumerate(series_list):
            legend_x = 20 + i * 150
            svg_parts.append(f'  <rect x="{legend_x}" y="{legend_y}" '
                           f'width="12" height="12" fill="{color}"/>')
            svg_parts.append(f'  <text x="{legend_x + 18}" y="{legend_y + 10}" '
                           f'font-family="Arial" font-size="11" fill="#333">{series_name}</text>')
        
        # SVG 尾
        svg_parts.append('</svg>')
        
        return "\n".join(svg_parts)


class DimensionRadarChart:
    """
    七维度评估雷达图
    
    专门用于展示七维度评估结果
    """
    
    # 七维度名称（中文）
    DIMENSION_NAMES = {
        "language_expression": "语言表达",
        "logical_thinking": "逻辑思维",
        "professional_knowledge": "专业知识",
        "problem_solving": "问题解决",
        "communication_collaboration": "沟通协作",
        "adaptability": "应变能力",
        "overall_quality": "综合素质",
    }
    
    # 默认颜色
    DEFAULT_COLORS = {
        "excellent": "#27ae60",  # 优秀 (80-100)
        "good": "#3498db",       # 良好 (60-79)
        "fair": "#f39c12",       # 一般 (40-59)
        "poor": "#e74c3c",       # 较差 (0-39)
    }
    
    def __init__(self, width: int = 450, height: int = 450):
        """
        初始化七维度雷达图
        
        Args:
            width: 图表宽度
            height: 图表高度
        """
        self.radar = RadarChart(width, height)
    
    def generate(self, scores: Dict[str, float],
                title: str = "七维度评估") -> str:
        """
        生成七维度雷达图
        
        Args:
            scores: 分数字典，键为维度英文名，值为 0-100 的分数
            title: 图表标题
            
        Returns:
            SVG 字符串
        """
        # 按照固定顺序构建维度
        dimension_order = [
            "language_expression",
            "logical_thinking",
            "professional_knowledge",
            "problem_solving",
            "communication_collaboration",
            "adaptability",
            "overall_quality",
        ]
        
        dimensions = []
        for dim_key in dimension_order:
            score = scores.get(dim_key, 0)
            name = self.DIMENSION_NAMES.get(dim_key, dim_key)
            color = self._get_color_for_score(score)
            
            dimensions.append(RadarDimension(
                name=name,
                value=score,
                color=color
            ))
        
        return self.radar.generate(dimensions, title)
    
    def generate_comparison(self, current_scores: Dict[str, float],
                           previous_scores: Optional[Dict[str, float]] = None,
                           title: str = "能力对比") -> str:
        """
        生成对比雷达图
        
        Args:
            current_scores: 当前分数
            previous_scores: 之前分数（可选）
            title: 图表标题
            
        Returns:
            SVG 字符串
        """
        dimension_order = [
            "language_expression",
            "logical_thinking",
            "professional_knowledge",
            "problem_solving",
            "communication_collaboration",
            "adaptability",
            "overall_quality",
        ]
        
        series_list = []
        
        # 当前（蓝色）
        current_dims = []
        for dim_key in dimension_order:
            score = current_scores.get(dim_key, 0)
            name = self.DIMENSION_NAMES.get(dim_key, dim_key)
            current_dims.append(RadarDimension(name=name, value=score))
        series_list.append(("当前", current_dims, "#3498db"))
        
        # 之前（灰色，如果有）
        if previous_scores:
            previous_dims = []
            for dim_key in dimension_order:
                score = previous_scores.get(dim_key, 0)
                name = self.DIMENSION_NAMES.get(dim_key, dim_key)
                previous_dims.append(RadarDimension(name=name, value=score))
            series_list.append(("之前", previous_dims, "#95a5a6"))
        
        return self.radar.generate_multi_series(series_list, title)
    
    def _get_color_for_score(self, score: float) -> str:
        """
        根据分数获取颜色
        
        Args:
            score: 分数
            
        Returns:
            颜色代码
        """
        if score >= 80:
            return self.DEFAULT_COLORS["excellent"]
        elif score >= 60:
            return self.DEFAULT_COLORS["good"]
        elif score >= 40:
            return self.DEFAULT_COLORS["fair"]
        else:
            return self.DEFAULT_COLORS["poor"]
    
    def generate_ascii(self, scores: Dict[str, float],
                      title: str = "七维度评估") -> str:
        """
        生成 ASCII 版本的雷达图（简化版）
        
        Args:
            scores: 分数字典
            title: 标题
            
        Returns:
            ASCII 字符串
        """
        lines = []
        
        # 标题
        if title:
            lines.append(f"╔{'═' * (len(title) + 2)}╗")
            lines.append(f"║ {title} ║")
            lines.append(f"╚{'═' * (len(title) + 2)}╝")
            lines.append("")
        
        # 显示各维度分数
        dimension_order = [
            "language_expression",
            "logical_thinking",
            "professional_knowledge",
            "problem_solving",
            "communication_collaboration",
            "adaptability",
            "overall_quality",
        ]
        
        for dim_key in dimension_order:
            score = scores.get(dim_key, 0)
            name = self.DIMENSION_NAMES.get(dim_key, dim_key)
            
            # 进度条
            bar_length = int(score / 5)  # 20 个字符满
            bar = "█" * bar_length
            empty = "░" * (20 - bar_length)
            
            lines.append(f"{name:8} │{bar}{empty}│ {score:5.1f}")
        
        # 图例
        lines.append("")
        lines.append("图例：█ 优秀 (80+)  █ 良好 (60-79)  █ 一般 (40-59)  ░ 较差 (<40)")
        
        return "\n".join(lines)
