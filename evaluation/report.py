"""
Feedback Report Generator - 反馈报告生成器 (v0.3)

生成结构化的面试评估反馈报告，支持：
- 多格式报告输出（文本、Markdown、JSON、HTML）
- 可视化友好的文本格式
- 详细反馈和建议
- 导出功能

设计原则:
- 单一职责：专注于报告生成
- 开闭原则：支持扩展新的报告格式
- 依赖倒置：依赖抽象数据结构而非具体实现
- 接口隔离：提供细粒度的报告生成接口

Report Types:
- text: 纯文本格式
- markdown: Markdown 格式
- json: JSON 数据格式
- html: HTML 格式（带样式）
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class ReportTemplate:
    """
    报告模板数据类

    Attributes:
        name: 模板名称
        description: 模板描述
        sections: 报告章节配置
        styles: 样式配置
    """
    name: str
    description: str
    sections: List[str] = field(default_factory=list)
    styles: Dict[str, Any] = field(default_factory=dict)


class FeedbackReportGenerator:
    """
    反馈报告生成器

    生成结构化的面试评估反馈报告

    Attributes:
        config: 配置对象
        templates: 报告模板字典
    """

    # 预定义报告模板
    TEMPLATES = {
        "standard": ReportTemplate(
            name="standard",
            description="标准评估报告",
            sections=[
                "header",
                "overall_score",
                "dimension_scores",
                "summary",
                "strengths",
                "weaknesses",
                "suggestions",
                "footer",
            ],
        ),
        "detailed": ReportTemplate(
            name="detailed",
            description="详细评估报告",
            sections=[
                "header",
                "overall_score",
                "dimension_scores",
                "sub_dimension_breakdown",
                "evidence",
                "summary",
                "strengths",
                "weaknesses",
                "suggestions",
                "improvement_plan",
                "footer",
            ],
        ),
        "executive": ReportTemplate(
            name="executive",
            description="高管摘要报告",
            sections=[
                "header",
                "overall_score",
                "summary",
                "recommendation",
                "footer",
            ],
        ),
        "candidate_feedback": ReportTemplate(
            name="candidate_feedback",
            description="候选人反馈报告",
            sections=[
                "header",
                "overall_score",
                "dimension_scores",
                "strengths",
                "suggestions",
                "encouragement",
                "footer",
            ],
        ),
    }

    def __init__(self, config: Optional[Config] = None):
        """
        初始化报告生成器

        Args:
            config: 配置对象
        """
        self.config = config or Config()
        self.templates = self.TEMPLATES.copy()

        # 从配置加载自定义模板
        custom_templates = self.config.get("report.templates", {})
        for name, template_config in custom_templates.items():
            self.templates[name] = ReportTemplate(
                name=name,
                description=template_config.get("description", ""),
                sections=template_config.get("sections", []),
                styles=template_config.get("styles", {}),
            )

        logger.info("FeedbackReportGenerator 初始化完成")

    def generate(
        self,
        result: Any,
        format: str = "text",
        template: str = "standard",
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成反馈报告

        Args:
            result: AdvancedEvaluationResult 实例
            format: 输出格式 (text/markdown/json/html)
            template: 模板名称
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            格式化的报告字符串
        """
        if format == "text":
            return self.generate_text_report(
                result, template, candidate_info, interview_info
            )
        elif format == "markdown":
            return self.generate_markdown_report(
                result, template, candidate_info, interview_info
            )
        elif format == "json":
            return self.generate_json_report(
                result, template, candidate_info, interview_info
            )
        elif format == "html":
            return self.generate_html_report(
                result, template, candidate_info, interview_info
            )
        else:
            raise ValueError(f"不支持的报告格式：{format}")

    def generate_text_report(
        self,
        result: Any,
        template: str = "standard",
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成文本格式报告

        Args:
            result: 评估结果
            template: 模板名称
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            文本格式报告
        """
        lines = []
        template_obj = self.templates.get(template, self.templates["standard"])

        # 构建报告上下文
        context = self._build_context(result, candidate_info, interview_info)

        for section in template_obj.sections:
            section_content = self._render_text_section(section, context)
            if section_content:
                lines.append(section_content)

        return "\n".join(lines)

    def generate_markdown_report(
        self,
        result: Any,
        template: str = "standard",
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成 Markdown 格式报告

        Args:
            result: 评估结果
            template: 模板名称
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            Markdown 格式报告
        """
        lines = []
        template_obj = self.templates.get(template, self.templates["standard"])
        context = self._build_context(result, candidate_info, interview_info)

        for section in template_obj.sections:
            section_content = self._render_markdown_section(section, context)
            if section_content:
                lines.append(section_content)

        return "\n".join(lines)

    def generate_json_report(
        self,
        result: Any,
        template: str = "standard",
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成 JSON 格式报告

        Args:
            result: 评估结果
            template: 模板名称
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            JSON 格式报告字符串
        """
        context = self._build_context(result, candidate_info, interview_info)

        report_data = {
            "report_type": "interview_evaluation_v0.3",
            "generated_at": datetime.now().isoformat(),
            "template": template,
            "candidate_info": context.get("candidate_info", {}),
            "interview_info": context.get("interview_info", {}),
            "evaluation": {
                "overall_score": round(context["overall_score"], 2),
                "level": context["level"],
                "summary": context["summary"],
                "dimension_scores": context["dimension_scores"],
                "strengths": context["strengths"],
                "weaknesses": context["weaknesses"],
                "suggestions": context["suggestions"],
            },
            "detailed_feedback": context.get("detailed_feedback", {}),
        }

        return json.dumps(report_data, ensure_ascii=False, indent=2)

    def generate_html_report(
        self,
        result: Any,
        template: str = "standard",
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        生成 HTML 格式报告

        Args:
            result: 评估结果
            template: 模板名称
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            HTML 格式报告
        """
        context = self._build_context(result, candidate_info, interview_info)

        html_parts = []

        # HTML 头部
        html_parts.append("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>面试评估报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .report-container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .score-display {
            display: flex;
            align-items: center;
            margin: 20px 0;
        }
        .score-number {
            font-size: 48px;
            font-weight: bold;
            color: #3498db;
            margin-right: 20px;
        }
        .score-bar {
            flex: 1;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            overflow: hidden;
        }
        .score-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            transition: width 0.5s ease;
        }
        .level-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            color: white;
        }
        .level-S { background: #9b59b6; }
        .level-A { background: #2ecc71; }
        .level-B { background: #3498db; }
        .level-C { background: #f39c12; }
        .level-D { background: #e74c3c; }
        .dimension-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .dimension-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #3498db;
        }
        .dimension-name {
            font-weight: bold;
            color: #2c3e50;
        }
        .dimension-score {
            float: right;
            color: #3498db;
            font-weight: bold;
        }
        .suggestion-list {
            background: #e8f6ff;
            border-radius: 8px;
            padding: 15px 20px;
            margin: 10px 0;
        }
        .suggestion-list li {
            margin: 8px 0;
        }
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .info-table td {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }
        .info-table td:first-child {
            font-weight: bold;
            width: 120px;
            color: #7f8c8d;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="report-container">
""")

        # 报告内容
        html_parts.append(self._render_html_header(context))
        html_parts.append(self._render_html_info(context))
        html_parts.append(self._render_html_overall_score(context))
        html_parts.append(self._render_html_dimensions(context))
        html_parts.append(self._render_html_summary(context))
        html_parts.append(self._render_html_strengths(context))
        html_parts.append(self._render_html_weaknesses(context))
        html_parts.append(self._render_html_suggestions(context))

        # HTML 尾部
        html_parts.append(f"""
        <div class="footer">
            <p>Generated by AgentScope AI Interview v0.3</p>
            <p>评估时间：{context.get('generated_at', '')}</p>
        </div>
    </div>
</body>
</html>
""")

        return "".join(html_parts)

    def export_to_file(
        self,
        result: Any,
        output_path: Union[str, Path],
        format: str = "markdown",
        template: str = "standard",
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """
        导出报告到文件

        Args:
            result: 评估结果
            output_path: 输出文件路径
            format: 输出格式
            template: 模板名称
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate(
            result, format, template, candidate_info, interview_info
        )

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"报告已导出到：{output_path}")
            return output_path

        except IOError as e:
            logger.error(f"导出报告失败：{e}")
            raise

    def _build_context(
        self,
        result: Any,
        candidate_info: Optional[Dict[str, Any]],
        interview_info: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """构建报告上下文"""
        # 导入高级评估类
        from .advanced_evaluator import EvaluationDimension7

        dimension_names = {
            EvaluationDimension7.CONTENT_QUALITY: "内容质量",
            EvaluationDimension7.EXPRESSION_CLARITY: "表达清晰度",
            EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识",
            EvaluationDimension7.ADAPTABILITY: "应变能力",
            EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧",
            EvaluationDimension7.CONFIDENCE_LEVEL: "自信程度",
            EvaluationDimension7.INNOVATIVE_THINKING: "创新思维",
        }

        return {
            "overall_score": result.overall_score,
            "level": result.level,
            "summary": result.summary,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "suggestions": result.suggestions,
            "dimension_scores": {
                dimension_names.get(dim, dim.value): {
                    "score": score.score,
                    "weight": score.weight,
                    "comments": score.comments,
                    "sub_scores": score.sub_scores,
                }
                for dim, score in result.dimension_scores.items()
            },
            "detailed_feedback": result.detailed_feedback,
            "candidate_info": candidate_info or {},
            "interview_info": interview_info or {},
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _render_text_section(self, section: str, context: Dict[str, Any]) -> str:
        """渲染文本章节"""
        if section == "header":
            return self._text_header(context)
        elif section == "overall_score":
            return self._text_overall_score(context)
        elif section == "dimension_scores":
            return self._text_dimension_scores(context)
        elif section == "summary":
            return self._text_summary(context)
        elif section == "strengths":
            return self._text_strengths(context)
        elif section == "weaknesses":
            return self._text_weaknesses(context)
        elif section == "suggestions":
            return self._text_suggestions(context)
        elif section == "footer":
            return self._text_footer(context)
        return ""

    def _render_markdown_section(self, section: str, context: Dict[str, Any]) -> str:
        """渲染 Markdown 章节"""
        if section == "header":
            return self._markdown_header(context)
        elif section == "overall_score":
            return self._markdown_overall_score(context)
        elif section == "dimension_scores":
            return self._markdown_dimension_scores(context)
        elif section == "summary":
            return self._markdown_summary(context)
        elif section == "strengths":
            return self._markdown_strengths(context)
        elif section == "weaknesses":
            return self._markdown_weaknesses(context)
        elif section == "suggestions":
            return self._markdown_suggestions(context)
        elif section == "footer":
            return self._markdown_footer(context)
        return ""

    def _render_html_header(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 头部"""
        candidate = context.get("candidate_info", {})
        return f"""
        <h1>📊 面试评估报告</h1>
        <p style="color: #7f8c8d;">AgentScope AI Interview v0.3</p>
"""

    def _render_html_info(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 信息表"""
        candidate = context.get("candidate_info", {})
        interview = context.get("interview_info", {})

        if not candidate and not interview:
            return ""

        rows = []
        if candidate.get("name"):
            rows.append(f"<tr><td>候选人</td><td>{candidate['name']}</td></tr>")
        if candidate.get("position"):
            rows.append(f"<tr><td>面试岗位</td><td>{candidate['position']}</td></tr>")
        if interview.get("domain"):
            rows.append(f"<tr><td>面试领域</td><td>{interview['domain']}</td></tr>")
        if interview.get("style"):
            rows.append(f"<tr><td>面试风格</td><td>{interview['style']}</td></tr>")

        if not rows:
            return ""

        return f"""
        <table class="info-table">
            {''.join(rows)}
        </table>
"""

    def _render_html_overall_score(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 总体评分"""
        score = context["overall_score"]
        level = context["level"]
        percentage = (score / 5.0) * 100

        return f"""
        <h2>总体评分</h2>
        <div class="score-display">
            <span class="score-number">{score:.1f}</span>
            <div class="score-bar">
                <div class="score-fill" style="width: {percentage}%;"></div>
            </div>
            <span class="level-badge level-{level}">{level}级</span>
        </div>
"""

    def _render_html_dimensions(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 维度评分"""
        cards = []
        for dim_name, dim_data in context["dimension_scores"].items():
            score = dim_data["score"]
            percentage = (score / 5.0) * 100
            cards.append(f"""
            <div class="dimension-card">
                <span class="dimension-name">{dim_name}</span>
                <span class="dimension-score">{score:.1f}</span>
                <div class="score-bar" style="margin-top: 10px;">
                    <div class="score-fill" style="width: {percentage}%;"></div>
                </div>
                <p style="margin-top: 8px; color: #7f8c8d; font-size: 14px;">
                    {dim_data.get('comments', '')}
                </p>
            </div>
""")

        return f"""
        <h2>维度评估</h2>
        <div class="dimension-grid">
            {''.join(cards)}
        </div>
"""

    def _render_html_summary(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 摘要"""
        if not context.get("summary"):
            return ""
        return f"""
        <h2>评估摘要</h2>
        <p style="font-size: 16px; line-height: 1.8;">{context['summary']}</p>
"""

    def _render_html_strengths(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 优势"""
        if not context.get("strengths"):
            return ""

        items = "".join(f"<li>{s}</li>" for s in context["strengths"])
        return f"""
        <h2>✨ 优势</h2>
        <ul class="suggestion-list" style="background: #e8f8e8;">
            {items}
        </ul>
"""

    def _render_html_weaknesses(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 待改进"""
        if not context.get("weaknesses"):
            return ""

        items = "".join(f"<li>{w}</li>" for w in context["weaknesses"])
        return f"""
        <h2>⚠️ 待改进</h2>
        <ul class="suggestion-list" style="background: #fff3e0;">
            {items}
        </ul>
"""

    def _render_html_suggestions(self, context: Dict[str, Any]) -> str:
        """渲染 HTML 建议"""
        if not context.get("suggestions"):
            return ""

        items = "".join(f"<li>{s}</li>" for s in context["suggestions"])
        return f"""
        <h2>💡 改进建议</h2>
        <ul class="suggestion-list">
            {items}
        </ul>
"""

    # ==================== 文本格式渲染方法 ====================

    def _text_header(self, context: Dict[str, Any]) -> str:
        """文本头部"""
        lines = []
        lines.append("=" * 70)
        lines.append("📊 AgentScope AI 面试评估报告 (v0.3)")
        lines.append("=" * 70)
        lines.append("")

        # 基本信息
        candidate = context.get("candidate_info", {})
        interview = context.get("interview_info", {})

        if candidate or interview:
            lines.append("【基本信息】")
            if candidate.get("name"):
                lines.append(f"  候选人：{candidate['name']}")
            if candidate.get("position"):
                lines.append(f"  面试岗位：{candidate['position']}")
            if interview.get("domain"):
                lines.append(f"  面试领域：{interview['domain']}")
            if interview.get("style"):
                lines.append(f"  面试风格：{interview['style']}")
            lines.append(f"  评估时间：{context.get('generated_at', '')}")
            lines.append("")

        return "\n".join(lines)

    def _text_overall_score(self, context: Dict[str, Any]) -> str:
        """文本总体评分"""
        lines = []
        score = context["overall_score"]
        level = context["level"]

        lines.append("【总体评分】")
        bar_len = int(score)
        bar = "█" * bar_len + "░" * (5 - bar_len)
        lines.append(f"  得分：[{bar}] {score:.2f} / 5.0")
        lines.append(f"  评级：{level}")
        lines.append("")

        return "\n".join(lines)

    def _text_dimension_scores(self, context: Dict[str, Any]) -> str:
        """文本维度评分"""
        lines = []
        lines.append("【7 维度评估】")

        for dim_name, dim_data in context["dimension_scores"].items():
            score = dim_data["score"]
            bar_len = int(score / 0.5)
            bar = "█" * bar_len + "░" * (10 - bar_len)
            lines.append(f"  {dim_name}: [{bar}] {score:.2f}")
            if dim_data.get("comments"):
                lines.append(f"    评语：{dim_data['comments']}")

        lines.append("")
        return "\n".join(lines)

    def _text_summary(self, context: Dict[str, Any]) -> str:
        """文本摘要"""
        if not context.get("summary"):
            return ""

        lines = []
        lines.append("【评估摘要】")
        lines.append(f"  {context['summary']}")
        lines.append("")

        return "\n".join(lines)

    def _text_strengths(self, context: Dict[str, Any]) -> str:
        """文本优势"""
        if not context.get("strengths"):
            return ""

        lines = []
        lines.append("【优势】")
        for i, strength in enumerate(context["strengths"], 1):
            lines.append(f"  {i}. {strength}")
        lines.append("")

        return "\n".join(lines)

    def _text_weaknesses(self, context: Dict[str, Any]) -> str:
        """文本待改进"""
        if not context.get("weaknesses"):
            return ""

        lines = []
        lines.append("【待改进】")
        for i, weakness in enumerate(context["weaknesses"], 1):
            lines.append(f"  {i}. {weakness}")
        lines.append("")

        return "\n".join(lines)

    def _text_suggestions(self, context: Dict[str, Any]) -> str:
        """文本建议"""
        if not context.get("suggestions"):
            return ""

        lines = []
        lines.append("【改进建议】")
        for i, suggestion in enumerate(context["suggestions"], 1):
            lines.append(f"  {i}. {suggestion}")
        lines.append("")

        return "\n".join(lines)

    def _text_footer(self, context: Dict[str, Any]) -> str:
        """文本尾部"""
        lines = []
        lines.append("=" * 70)
        lines.append("感谢使用 AgentScope AI Interview")
        lines.append("=" * 70)

        return "\n".join(lines)

    # ==================== Markdown 格式渲染方法 ====================

    def _markdown_header(self, context: Dict[str, Any]) -> str:
        """Markdown 头部"""
        lines = []
        lines.append("# 📊 面试评估报告")
        lines.append("")
        lines.append("> AgentScope AI Interview v0.3")
        lines.append("")

        candidate = context.get("candidate_info", {})
        interview = context.get("interview_info", {})

        if candidate or interview:
            lines.append("## 基本信息")
            lines.append("")
            if candidate.get("name"):
                lines.append(f"- **候选人**: {candidate['name']}")
            if candidate.get("position"):
                lines.append(f"- **面试岗位**: {candidate['position']}")
            if interview.get("domain"):
                lines.append(f"- **面试领域**: {interview['domain']}")
            if interview.get("style"):
                lines.append(f"- **面试风格**: {interview['style']}")
            lines.append(f"- **评估时间**: {context.get('generated_at', '')}")
            lines.append("")

        return "\n".join(lines)

    def _markdown_overall_score(self, context: Dict[str, Any]) -> str:
        """Markdown 总体评分"""
        score = context["overall_score"]
        level = context["level"]

        lines = []
        lines.append("## 总体评分")
        lines.append("")

        # 进度条
        filled = int(score)
        bar = "🟩" * filled + "⬜" * (5 - filled)
        lines.append(f"**得分**: {bar} **{score:.2f} / 5.0**")
        lines.append("")
        
        # 确定颜色
        if level in ['S', 'A']:
            color = '#2ecc71'
        elif level == 'B':
            color = '#f39c12'
        else:
            color = '#e74c3c'
        lines.append(f'**评级**: <span style="color: {color}">**{level}级**</span>')
        lines.append("")

        return "\n".join(lines)

    def _markdown_dimension_scores(self, context: Dict[str, Any]) -> str:
        """Markdown 维度评分"""
        lines = []
        lines.append("## 7 维度评估")
        lines.append("")
        lines.append("| 维度 | 评分 | 评语 |")
        lines.append("|------|------|------|")

        for dim_name, dim_data in context["dimension_scores"].items():
            score = dim_data["score"]
            comments = dim_data.get("comments", "-")
            stars = "⭐" * int(score)
            lines.append(f"| {dim_name} | {stars} {score:.2f} | {comments} |")

        lines.append("")
        return "\n".join(lines)

    def _markdown_summary(self, context: Dict[str, Any]) -> str:
        """Markdown 摘要"""
        if not context.get("summary"):
            return ""

        lines = []
        lines.append("## 评估摘要")
        lines.append("")
        lines.append(context["summary"])
        lines.append("")

        return "\n".join(lines)

    def _markdown_strengths(self, context: Dict[str, Any]) -> str:
        """Markdown 优势"""
        if not context.get("strengths"):
            return ""

        lines = []
        lines.append("## ✨ 优势")
        lines.append("")
        for strength in context["strengths"]:
            lines.append(f"- ✅ {strength}")
        lines.append("")

        return "\n".join(lines)

    def _markdown_weaknesses(self, context: Dict[str, Any]) -> str:
        """Markdown 待改进"""
        if not context.get("weaknesses"):
            return ""

        lines = []
        lines.append("## ⚠️ 待改进")
        lines.append("")
        for weakness in context["weaknesses"]:
            lines.append(f"- ⚡ {weakness}")
        lines.append("")

        return "\n".join(lines)

    def _markdown_suggestions(self, context: Dict[str, Any]) -> str:
        """Markdown 建议"""
        if not context.get("suggestions"):
            return ""

        lines = []
        lines.append("## 💡 改进建议")
        lines.append("")
        for i, suggestion in enumerate(context["suggestions"], 1):
            lines.append(f"{i}. {suggestion}")
        lines.append("")

        return "\n".join(lines)

    def _markdown_footer(self, context: Dict[str, Any]) -> str:
        """Markdown 尾部"""
        lines = []
        lines.append("---")
        lines.append("")
        lines.append("*Generated by AgentScope AI Interview v0.3*")
        lines.append("")

        return "\n".join(lines)
