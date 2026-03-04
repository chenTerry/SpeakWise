"""
Trend Chart Generation

趋势图生成：
- 进度趋势折线图
- 多维度趋势对比
- SVG 和 ASCII 格式

Design Principles:
- 清晰展示趋势变化
- 支持多系列对比
- 自适应时间范围
"""

import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TrendPoint:
    """趋势点数据"""
    date: datetime
    value: float
    label: str = ""


@dataclass
class TrendSeries:
    """趋势系列"""
    name: str
    points: List[TrendPoint]
    color: str = "#3498db"


class TrendChart:
    """
    趋势图生成器
    
    生成 SVG 格式的折线趋势图
    """
    
    def __init__(self, width: int = 600, height: int = 350,
                 margin: int = 60):
        """
        初始化趋势图
        
        Args:
            width: 图表宽度
            height: 图表高度
            margin: 边距
        """
        self.width = width
        self.height = height
        self.margin = margin
        self.plot_width = width - 2 * margin
        self.plot_height = height - 2 * margin
    
    def generate(self, series_list: List[TrendSeries],
                title: str = "",
                y_label: str = "",
                show_grid: bool = True) -> str:
        """
        生成趋势图 SVG
        
        Args:
            series_list: 趋势系列列表
            title: 图表标题
            y_label: Y 轴标签
            show_grid: 是否显示网格
            
        Returns:
            SVG 字符串
        """
        if not series_list:
            return "<svg></svg>"
        
        # 收集所有数据点
        all_points = []
        for series in series_list:
            all_points.extend(series.points)
        
        if not all_points:
            return "<svg></svg>"
        
        # 计算 X 轴范围（日期）
        dates = [p.date for p in all_points]
        min_date = min(dates)
        max_date = max(dates)
        
        # 计算 Y 轴范围
        values = [p.value for p in all_points]
        min_value = min(values) * 0.9  # 留 10% 空间
        max_value = max(values) * 1.1
        value_range = max_value - min_value if max_value != min_value else 1
        
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
            svg_parts.append(f'  <text x="{self.width / 2}" y="30" '
                           f'text-anchor="middle" font-family="Arial" '
                           f'font-size="18" font-weight="bold">{title}</text>')
        
        # 绘制网格
        if show_grid:
            self._draw_grid(svg_parts, min_value, max_value, 5)
        
        # 绘制坐标轴
        self._draw_axes(svg_parts, min_value, max_value, y_label)
        
        # 绘制各系列
        for series in series_list:
            self._draw_series(svg_parts, series, min_date, max_date, min_value, max_value)
        
        # 图例
        self._draw_legend(svg_parts, series_list)
        
        # SVG 尾
        svg_parts.append('</svg>')
        
        return "\n".join(svg_parts)
    
    def _draw_grid(self, svg_parts: list, min_value: float, max_value: float,
                  num_lines: int) -> None:
        """绘制网格线"""
        for i in range(num_lines + 1):
            y = self.margin + (self.plot_height * i / num_lines)
            svg_parts.append(f'  <line x1="{self.margin}" y1="{y:.1f}" '
                           f'x2="{self.width - self.margin}" y2="{y:.1f}" '
                           f'stroke="#e8e8e8" stroke-width="1"/>')
    
    def _draw_axes(self, svg_parts: list, min_value: float, max_value: float,
                  y_label: str) -> None:
        """绘制坐标轴"""
        # Y 轴
        svg_parts.append(f'  <line x1="{self.margin}" y1="{self.margin}" '
                        f'x2="{self.margin}" y2="{self.height - self.margin}" '
                        f'stroke="#333" stroke-width="2"/>')
        
        # X 轴
        svg_parts.append(f'  <line x1="{self.margin}" y1="{self.height - self.margin}" '
                        f'x2="{self.width - self.margin}" y2="{self.height - self.margin}" '
                        f'stroke="#333" stroke-width="2"/>')
        
        # Y 轴刻度标签
        for i in range(6):
            value = min_value + (max_value - min_value) * i / 5
            y = self.height - self.margin - (self.plot_height * i / 5)
            svg_parts.append(f'  <text x="{self.margin - 10}" y="{y + 4:.1f}" '
                           f'text-anchor="end" font-family="Arial" font-size="11" '
                           f'fill="#666">{value:.0f}</text>')
        
        # Y 轴标签
        if y_label:
            svg_parts.append(f'  <text x="20" y="{self.height / 2}" '
                           f'text-anchor="middle" font-family="Arial" font-size="13" '
                           f'fill="#333" transform="rotate(-90, 20, {self.height / 2})">{y_label}</text>')
    
    def _draw_series(self, svg_parts: list, series: TrendSeries,
                    min_date: datetime, max_date: datetime,
                    min_value: float, max_value: float) -> None:
        """绘制数据系列"""
        if len(series.points) < 2:
            return
        
        # 计算日期范围（天数）
        date_range = (max_date - min_date).total_seconds()
        if date_range == 0:
            date_range = 1
        
        # 生成路径
        path_parts = []
        for i, point in enumerate(series.points):
            # X 坐标
            if date_range > 0:
                x_offset = (point.date - min_date).total_seconds() / date_range
            else:
                x_offset = i / max(len(series.points) - 1, 1)
            
            x = self.margin + x_offset * self.plot_width
            
            # Y 坐标
            y_offset = (point.value - min_value) / (max_value - min_value)
            y = self.height - self.margin - y_offset * self.plot_height
            
            if i == 0:
                path_parts.append(f"M {x:.1f} {y:.1f}")
            else:
                path_parts.append(f"L {x:.1f} {y:.1f}")
        
        # 绘制折线
        path_d = " ".join(path_parts)
        svg_parts.append(f'  <path d="{path_d}" fill="none" '
                        f'stroke="{series.color}" stroke-width="2.5"/>')
        
        # 绘制数据点
        for point in series.points:
            if date_range > 0:
                x_offset = (point.date - min_date).total_seconds() / date_range
            else:
                x_offset = 0.5
            
            x = self.margin + x_offset * self.plot_width
            y_offset = (point.value - min_value) / (max_value - min_value)
            y = self.height - self.margin - y_offset * self.plot_height
            
            svg_parts.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                           f'fill="{series.color}"/>')
    
    def _draw_legend(self, svg_parts: list, series_list: List[TrendSeries]) -> None:
        """绘制图例"""
        legend_y = self.height - 25
        legend_x = self.margin
        
        for i, series in enumerate(series_list):
            x = legend_x + i * 120
            
            # 颜色块
            svg_parts.append(f'  <rect x="{x}" y="{legend_y}" '
                           f'width="15" height="15" fill="{series.color}"/>')
            
            # 标签
            svg_parts.append(f'  <text x="{x + 20}" y="{legend_y + 12}" '
                           f'font-family="Arial" font-size="12" fill="#333">{series.name}</text>')


class ProgressTrendChart:
    """
    进度趋势图
    
    专门用于展示学习进度趋势
    """
    
    def __init__(self, width: int = 650, height: int = 400):
        """
        初始化进度趋势图
        
        Args:
            width: 图表宽度
            height: 图表高度
        """
        self.chart = TrendChart(width, height)
    
    def generate(self, session_history: List[Dict[str, Any]],
                title: str = "学习进度趋势",
                days: int = 30) -> str:
        """
        生成进度趋势图
        
        Args:
            session_history: 会话历史列表
            title: 图表标题
            days: 天数范围
            
        Returns:
            SVG 字符串
        """
        if not session_history:
            return "<svg></svg>"
        
        # 过滤时间范围
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_sessions = [
            s for s in session_history
            if s.get("ended_at") and 
               (isinstance(s["ended_at"], datetime) and s["ended_at"] >= cutoff_date or
                datetime.fromisoformat(str(s["ended_at"])) >= cutoff_date)
        ]
        
        if not recent_sessions:
            return "<svg></svg>"
        
        # 构建趋势系列
        score_points = []
        
        for session in sorted(recent_sessions, key=lambda s: s.get("ended_at", datetime.utcnow())):
            # 解析结束时间
            ended_at = session.get("ended_at")
            if isinstance(ended_at, datetime):
                date = ended_at
            else:
                try:
                    date = datetime.fromisoformat(str(ended_at))
                except:
                    continue
            
            # 解析分数
            score = 0.0
            eval_result = session.get("evaluation_result")
            if eval_result:
                if isinstance(eval_result, dict):
                    score = eval_result.get("overall_score", 0.0)
                else:
                    import json
                    try:
                        result = json.loads(str(eval_result))
                        score = result.get("overall_score", 0.0)
                    except:
                        pass
            
            score_points.append(TrendPoint(
                date=date,
                value=score,
                label=session.get("scene_type", "")
            ))
        
        if not score_points:
            return "<svg></svg>"
        
        # 创建系列
        score_series = TrendSeries(
            name="评估分数",
            points=score_points,
            color="#3498db"
        )
        
        # 生成图表
        return self.chart.generate(
            series_list=[score_series],
            title=title,
            y_label="分数"
        )
    
    def generate_with_average(self, session_history: List[Dict[str, Any]],
                             title: str = "学习进度趋势",
                             days: int = 30) -> str:
        """
        生成带平均线的趋势图
        
        Args:
            session_history: 会话历史列表
            title: 图表标题
            days: 天数范围
            
        Returns:
            SVG 字符串
        """
        if not session_history:
            return "<svg></svg>"
        
        # 过滤时间范围
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_sessions = [
            s for s in session_history
            if s.get("ended_at") and 
               (isinstance(s["ended_at"], datetime) and s["ended_at"] >= cutoff_date or
                datetime.fromisoformat(str(s["ended_at"])) >= cutoff_date)
        ]
        
        if not recent_sessions:
            return "<svg></svg>"
        
        # 构建趋势系列
        score_points = []
        total_score = 0.0
        
        for session in sorted(recent_sessions, key=lambda s: s.get("ended_at", datetime.utcnow())):
            ended_at = session.get("ended_at")
            if isinstance(ended_at, datetime):
                date = ended_at
            else:
                try:
                    date = datetime.fromisoformat(str(ended_at))
                except:
                    continue
            
            score = 0.0
            eval_result = session.get("evaluation_result")
            if eval_result:
                if isinstance(eval_result, dict):
                    score = eval_result.get("overall_score", 0.0)
                else:
                    import json
                    try:
                        result = json.loads(str(eval_result))
                        score = result.get("overall_score", 0.0)
                    except:
                        pass
            
            total_score += score
            score_points.append(TrendPoint(date=date, value=score))
        
        if not score_points:
            return "<svg></svg>"
        
        # 计算平均分
        avg_score = total_score / len(score_points)
        
        # 创建系列
        score_series = TrendSeries(
            name="评估分数",
            points=score_points,
            color="#3498db"
        )
        
        # 平均线系列
        avg_series = TrendSeries(
            name=f"平均分 ({avg_score:.1f})",
            points=[
                TrendPoint(date=score_points[0].date, value=avg_score),
                TrendPoint(date=score_points[-1].date, value=avg_score),
            ],
            color="#e74c3c"
        )
        
        # 生成图表
        return self.chart.generate(
            series_list=[score_series, avg_series],
            title=title,
            y_label="分数"
        )
    
    def generate_ascii(self, session_history: List[Dict[str, Any]],
                      title: str = "学习进度趋势",
                      width: int = 60) -> str:
        """
        生成 ASCII 版本的趋势图
        
        Args:
            session_history: 会话历史列表
            title: 图表标题
            width: 图表宽度
            
        Returns:
            ASCII 字符串
        """
        if not session_history:
            return "No data to display"
        
        # 提取分数
        scores = []
        for session in session_history[-20:]:  # 最近 20 次
            eval_result = session.get("evaluation_result")
            if eval_result:
                if isinstance(eval_result, dict):
                    score = eval_result.get("overall_score", 0.0)
                else:
                    import json
                    try:
                        result = json.loads(str(eval_result))
                        score = result.get("overall_score", 0.0)
                    except:
                        score = 0.0
                scores.append(score)
        
        if not scores:
            return "No score data available"
        
        lines = []
        
        # 标题
        if title:
            lines.append(f"╔{'═' * (len(title) + 2)}╗")
            lines.append(f"║ {title} ║")
            lines.append(f"╚{'═' * (len(title) + 2)}╝")
            lines.append("")
        
        # 简单显示分数变化
        max_score = max(scores)
        min_score = min(scores)
        range_score = max_score - min_score if max_score != min_score else 1
        
        chart_height = 10
        chart_width = min(len(scores) * 3, width - 15)
        
        # 创建网格
        grid = [[" " for _ in range(len(scores))] for _ in range(chart_height)]
        
        # 填充数据点
        for i, score in enumerate(scores):
            normalized = (score - min_score) / range_score
            row = int(normalized * (chart_height - 1))
            row = chart_height - 1 - row
            
            if 0 <= row < chart_height:
                grid[row][i] = "●"
        
        # 生成输出
        lines.append(f"{max_score:>7.1f} │" + "".join(grid[0]))
        
        for row in grid[1:-1]:
            lines.append(f"{' ' * 9}│" + "".join(row))
        
        lines.append(f"{min_score:>7.1f} │" + "".join(grid[-1]))
        lines.append(f"{' ' * 9}└" + "─" * len(scores))
        
        # 平均分
        avg_score = sum(scores) / len(scores)
        lines.append(f"\n平均分：{avg_score:.1f}")
        
        return "\n".join(lines)


def create_trend_chart(dates: List[datetime], values: List[float],
                      title: str = "", color: str = "#3498db") -> str:
    """
    便捷函数：创建趋势图
    
    Args:
        dates: 日期列表
        values: 数值列表
        title: 标题
        color: 颜色
        
    Returns:
        SVG 字符串
    """
    chart = TrendChart()
    
    points = [
        TrendPoint(date=d, value=v)
        for d, v in zip(dates, values)
    ]
    
    series = TrendSeries(name="趋势", points=points, color=color)
    
    return chart.generate([series], title=title)
