"""
Report Generator

报告生成器：
- Markdown 格式报告
- PDF 格式报告（通过转换）
- 进度报告导出

Design Principles:
- 模板化设计
- 支持多种格式
- 可定制内容
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from users.database import Database
from progress.tracker import ProgressTracker
from progress.history import SessionHistoryManager
from visualization.radar import DimensionRadarChart


class ReportGenerator:
    """
    报告生成器
    
    生成用户进度报告
    
    Usage:
        generator = ReportGenerator(user_id=1)
        report = generator.generate_markdown()
        generator.export_pdf(report, "report.pdf")
    """
    
    def __init__(self, user_id: int, db: Optional[Database] = None):
        """
        初始化报告生成器
        
        Args:
            user_id: 用户 ID
            db: 数据库实例（可选）
        """
        self.user_id = user_id
        self.db = db or Database.get_instance()
        
        self.progress_tracker = ProgressTracker(user_id, self.db)
        self.history_manager = SessionHistoryManager(user_id, self.db)
    
    def generate_markdown(self, period_days: int = 30,
                         include_history: bool = True) -> str:
        """
        生成 Markdown 格式报告
        
        Args:
            period_days: 统计周期（天）
            include_history: 是否包含历史记录
            
        Returns:
            Markdown 字符串
        """
        # 获取数据
        progress = self.progress_tracker.get_progress()
        report_data = self.progress_tracker.generate_report(period_days)
        milestones = self.progress_tracker.get_milestones()
        
        if include_history:
            history = self.progress_tracker.get_session_history(limit=20)
        else:
            history = []
        
        # 生成报告
        lines = []
        
        # 标题
        lines.append("# 📊 AgentScope AI Interview - 学习进度报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**统计周期**: 最近 {period_days} 天")
        lines.append("")
        
        # 分隔线
        lines.append("---")
        lines.append("")
        
        # 概览
        lines.append("## 📈 概览")
        lines.append("")
        
        if progress:
            lines.append(f"- **总会话数**: {progress.get('total_sessions', 0)}")
            lines.append(f"- **完成会话数**: {progress.get('completed_sessions', 0)}")
            
            # 格式化时长
            total_seconds = progress.get("total_duration_seconds", 0)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            lines.append(f"- **总练习时长**: {hours}小时{minutes}分钟")
            
            lines.append(f"- **平均分数**: {progress.get('avg_score', 0):.1f}")
            lines.append(f"- **改进率**: {progress.get('improvement_rate', 0):+.1f}%")
            lines.append(f"- **连续练习**: {progress.get('streak_days', 0)} 天")
        else:
            lines.append("*暂无数据，开始第一次练习吧！*")
        
        lines.append("")
        
        # 里程碑
        if milestones:
            lines.append("---")
            lines.append("")
            lines.append("## 🏆 里程碑")
            lines.append("")
            
            for milestone in milestones:
                icon = milestone.get("icon", "⭐")
                name = milestone.get("name", "")
                lines.append(f"- {icon} {name}")
            
            lines.append("")
        
        # 七维度评估
        lines.append("---")
        lines.append("")
        lines.append("## 🎯 七维度评估")
        lines.append("")
        
        if progress and progress.get("dimension_scores"):
            dimension_scores = progress["dimension_scores"]
            
            # 表格
            lines.append("| 维度 | 分数 | 等级 |")
            lines.append("|------|------|------|")
            
            dimension_names = {
                "language_expression": "语言表达能力",
                "logical_thinking": "逻辑思维能力",
                "professional_knowledge": "专业知识掌握",
                "problem_solving": "问题解决能力",
                "communication_collaboration": "沟通协作能力",
                "adaptability": "应变能力",
                "overall_quality": "综合素质",
            }
            
            for dim_key, dim_name in dimension_names.items():
                score = dimension_scores.get(dim_key, 0)
                grade = self._get_grade(score)
                lines.append(f"| {dim_name} | {score:.1f} | {grade} |")
            
            lines.append("")
            
            # 雷达图（ASCII 版本）
            lines.append("### 能力雷达图")
            lines.append("")
            radar = DimensionRadarChart()
            lines.append("```")
            lines.append(radar.generate_ascii(dimension_scores))
            lines.append("```")
            lines.append("")
        else:
            lines.append("*暂无评估数据*")
            lines.append("")
        
        # 趋势分析
        lines.append("---")
        lines.append("")
        lines.append("## 📊 趋势分析")
        lines.append("")
        
        if report_data.get("dimension_analysis"):
            lines.append("### 各维度趋势")
            lines.append("")
            
            for dim_key, analysis in report_data["dimension_analysis"].items():
                trend_emoji = {
                    "improving": "📈",
                    "declining": "📉",
                    "stable": "➡️",
                }
                trend = analysis.get("trend", "stable")
                score = analysis.get("avg_score", 0)
                name = analysis.get("name", dim_key)
                
                lines.append(f"- **{name}**: {score:.1f}分 {trend_emoji.get(trend, '')}")
            
            lines.append("")
        
        # 改进建议
        if report_data.get("recommendations"):
            lines.append("### 💡 改进建议")
            lines.append("")
            
            for i, rec in enumerate(report_data["recommendations"], 1):
                lines.append(f"{i}. {rec}")
            
            lines.append("")
        
        # 历史记录
        if history:
            lines.append("---")
            lines.append("")
            lines.append("## 📝 最近会话历史")
            lines.append("")
            
            lines.append("| ID | 场景 | 标题 | 状态 | 分数 |")
            lines.append("|----|------|------|------|------|")
            
            for session in history[:10]:
                session_id = session.get("id", "")
                scene_type = session.get("scene_type", "")
                title = session.get("title") or "-"
                status = session.get("status", "")
                
                # 解析分数
                score_str = "-"
                eval_result = session.get("evaluation_result")
                if eval_result:
                    if isinstance(eval_result, dict):
                        score = eval_result.get("overall_score", 0)
                    else:
                        import json
                        try:
                            result = json.loads(str(eval_result))
                            score = result.get("overall_score", 0)
                        except:
                            score = 0
                    score_str = f"{score:.1f}"
                
                lines.append(f"| {session_id} | {scene_type} | {title} | {status} | {score_str} |")
            
            lines.append("")
        
        # 结尾
        lines.append("---")
        lines.append("")
        lines.append("*报告由 AgentScope AI Interview 系统自动生成*")
        lines.append("")
        lines.append("🚀 继续努力，每天进步一点点！")
        lines.append("")
        
        return "\n".join(lines)
    
    def _get_grade(self, score: float) -> str:
        """
        根据分数获取等级
        
        Args:
            score: 分数
            
        Returns:
            等级字符串
        """
        if score >= 90:
            return "A+ 优秀"
        elif score >= 80:
            return "A 良好"
        elif score >= 70:
            return "B 中等"
        elif score >= 60:
            return "C 及格"
        else:
            return "D 需努力"
    
    def export_markdown(self, output_path: str,
                       period_days: int = 30) -> str:
        """
        导出 Markdown 报告到文件
        
        Args:
            output_path: 输出文件路径
            period_days: 统计周期（天）
            
        Returns:
            输出文件路径
        """
        content = self.generate_markdown(period_days)
        
        # 确保目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_path
    
    def export_pdf(self, output_path: str,
                  period_days: int = 30) -> Optional[str]:
        """
        导出 PDF 报告（需要额外依赖）
        
        Args:
            output_path: 输出文件路径
            period_days: 统计周期（天）
            
        Returns:
            输出文件路径，如果转换失败则返回 None
        """
        # 先生成 Markdown
        md_path = output_path.replace(".pdf", ".md")
        self.export_markdown(md_path, period_days)
        
        # 尝试转换为 PDF
        try:
            # 需要安装 markdown2pdf 或 pandoc
            import subprocess
            
            # 使用 pandoc 转换
            subprocess.run(
                ["pandoc", md_path, "-o", output_path],
                check=True,
                capture_output=True
            )
            
            return output_path
            
        except Exception as e:
            # 转换失败，返回 Markdown 路径
            print(f"PDF 转换失败：{e}")
            return md_path
    
    def generate_html(self, period_days: int = 30) -> str:
        """
        生成 HTML 格式报告
        
        Args:
            period_days: 统计周期（天）
            
        Returns:
            HTML 字符串
        """
        md_content = self.generate_markdown(period_days)
        
        # 简单的 Markdown 转 HTML
        # 实际项目应使用 markdown 库
        html_content = md_content
        
        # 标题转换
        html_content = html_content.replace("# ", "<h1>")
        html_content = html_content.replace("## ", "</h1>\n<h2>")
        html_content = html_content.replace("### ", "</h2>\n<h3>")
        html_content = html_content.replace("#### ", "</h3>\n<h4>")
        
        # 段落
        lines = html_content.split("\n")
        processed_lines = []
        in_list = False
        
        for line in lines:
            if line.startswith("- "):
                if not in_list:
                    processed_lines.append("<ul>")
                    in_list = True
                processed_lines.append(f"<li>{line[2:]}</li>")
            else:
                if in_list:
                    processed_lines.append("</ul>")
                    in_list = False
                processed_lines.append(line)
        
        if in_list:
            processed_lines.append("</ul>")
        
        html_content = "\n".join(processed_lines)
        
        # 完整 HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>学习进度报告</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                h2 {{ color: #764ba2; margin-top: 30px; }}
                h3 {{ color: #333; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #667eea; color: white; }}
                tr:nth-child(even) {{ background: #f5f5f5; }}
                ul {{ line-height: 1.8; }}
                pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return html
    
    def export_html(self, output_path: str,
                   period_days: int = 30) -> str:
        """
        导出 HTML 报告到文件
        
        Args:
            output_path: 输出文件路径
            period_days: 统计周期（天）
            
        Returns:
            输出文件路径
        """
        content = self.generate_html(period_days)
        
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return output_path
