"""
Advanced Evaluator - 高级评估器 (v0.3)

实现 7 维度评估模型，基于 AgentScope LLM 进行智能评估：

7 个核心维度:
1. content_quality (内容质量): 相关性、准确性、深度
2. expression_clarity (表达清晰度): 逻辑性、简洁性、条理性
3. professional_knowledge (专业知识): 技术深度、经验、解决问题能力
4. adaptability (应变能力): 处理意外问题、灵活应对
5. communication_skills (沟通技巧): 倾听、表达、互动质量
6. confidence_level (自信程度): 语气、确定性、自我展示
7. innovative_thinking (创新思维): 独特见解、创造性解决方案

设计原则:
- 单一职责：专注于 LLM 驱动的评估逻辑
- 开闭原则：支持通过配置扩展新的评估维度
- 依赖倒置：依赖 AgentScope 抽象而非具体 LLM 实现
- 配置驱动：评估权重、阈值、提示词均可配置

Attributes:
    config: 配置对象
    model_agent: AgentScope ModelAgent 实例
    weights: 维度权重配置
    thresholds: 评级阈值配置
"""

import logging
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.agent import Message
from core.config import Config

logger = logging.getLogger(__name__)


class EvaluationDimension7(Enum):
    """
    7 维度评估枚举

    定义七个核心评估维度，覆盖面试评估的关键方面
    """
    CONTENT_QUALITY = "content_quality"           # 内容质量
    EXPRESSION_CLARITY = "expression_clarity"      # 表达清晰度
    PROFESSIONAL_KNOWLEDGE = "professional_knowledge"  # 专业知识
    ADAPTABILITY = "adaptability"                  # 应变能力
    COMMUNICATION_SKILLS = "communication_skills"  # 沟通技巧
    CONFIDENCE_LEVEL = "confidence_level"          # 自信程度
    INNOVATIVE_THINKING = "innovative_thinking"    # 创新思维


@dataclass
class DimensionScore7:
    """
    7 维度评分数据类

    封装单个维度的评分详情，支持子维度分解

    Attributes:
        dimension: 评估维度
        score: 维度得分 (0-5)
        weight: 权重 (0-1)
        sub_scores: 子维度得分字典
        comments: 评语
        evidence: 评分依据（引用原文）
        improvement_suggestions: 改进建议
    """
    dimension: EvaluationDimension7
    score: float = 0.0
    weight: float = 1.0
    sub_scores: Dict[str, float] = field(default_factory=dict)
    comments: str = ""
    evidence: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)

    def weighted_score(self) -> float:
        """计算加权得分"""
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 2),
            "weight": round(self.weight, 3),
            "sub_scores": {k: round(v, 2) for k, v in self.sub_scores.items()},
            "comments": self.comments,
            "evidence": self.evidence,
            "improvement_suggestions": self.improvement_suggestions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DimensionScore7":
        """从字典创建"""
        return cls(
            dimension=EvaluationDimension7(data["dimension"]),
            score=data.get("score", 0.0),
            weight=data.get("weight", 1.0),
            sub_scores=data.get("sub_scores", {}),
            comments=data.get("comments", ""),
            evidence=data.get("evidence", []),
            improvement_suggestions=data.get("improvement_suggestions", []),
        )


@dataclass
class AdvancedEvaluationResult:
    """
    高级评估结果数据类

    封装完整的 7 维度评估结果

    Attributes:
        overall_score: 总体评分 (0-5)
        dimension_scores: 各维度评分
        level: 评级 (S/A/B/C/D)
        summary: 评估摘要
        strengths: 优势点列表
        weaknesses: 待改进点列表
        suggestions: 改进建议列表
        detailed_feedback: 详细反馈（按维度组织）
        metadata: 元数据
    """
    overall_score: float = 0.0
    dimension_scores: Dict[EvaluationDimension7, DimensionScore7] = field(default_factory=dict)
    level: str = "C"
    summary: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    detailed_feedback: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_score(self, dimension: EvaluationDimension7) -> float:
        """获取指定维度得分"""
        if dimension in self.dimension_scores:
            return self.dimension_scores[dimension].score
        return 0.0

    def get_top_dimensions(self, n: int = 3) -> List[Tuple[EvaluationDimension7, float]]:
        """获取得分最高的 N 个维度"""
        sorted_dims = sorted(
            self.dimension_scores.items(),
            key=lambda x: x[1].score,
            reverse=True
        )
        return [(dim, score.score) for dim, score in sorted_dims[:n]]

    def get_bottom_dimensions(self, n: int = 3) -> List[Tuple[EvaluationDimension7, float]]:
        """获取得分最低的 N 个维度"""
        sorted_dims = sorted(
            self.dimension_scores.items(),
            key=lambda x: x[1].score
        )
        return [(dim, score.score) for dim, score in sorted_dims[:n]]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "overall_score": round(self.overall_score, 2),
            "level": self.level,
            "dimension_scores": {
                k.value: v.to_dict() for k, v in self.dimension_scores.items()
            },
            "summary": self.summary,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "detailed_feedback": self.detailed_feedback,
            "metadata": self.metadata,
        }

    def to_report(self) -> "AdvancedFeedbackReport":
        """转换为评估报告"""
        return AdvancedFeedbackReport.from_result(self)


@dataclass
class AdvancedFeedbackReport:
    """
    高级评估报告类

    生成格式化的 7 维度评估报告

    Attributes:
        result: 评估结果
        generated_at: 生成时间
        candidate_info: 候选人信息
        interview_info: 面试信息
    """
    result: AdvancedEvaluationResult
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    candidate_info: Dict[str, Any] = field(default_factory=dict)
    interview_info: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_result(
        cls,
        result: AdvancedEvaluationResult,
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> "AdvancedFeedbackReport":
        """从评估结果创建报告"""
        return cls(
            result=result,
            candidate_info=candidate_info or {},
            interview_info=interview_info or {},
        )

    def generate_text_report(self) -> str:
        """
        生成文本格式报告

        Returns:
            格式化的文本报告
        """
        lines = []
        lines.append("=" * 70)
        lines.append("📊 AgentScope AI 面试评估报告 (v0.3)")
        lines.append("=" * 70)
        lines.append("")

        # 基本信息
        lines.append("【基本信息】")
        if self.candidate_info:
            lines.append(f"  候选人：{self.candidate_info.get('name', '未知')}")
            lines.append(f"  面试岗位：{self.candidate_info.get('position', '未知')}")
        if self.interview_info:
            lines.append(f"  面试领域：{self.interview_info.get('domain', '未知')}")
            lines.append(f"  面试风格：{self.interview_info.get('style', '未知')}")
            lines.append(f"  面试时长：{self.interview_info.get('duration', '未知')}分钟")
        lines.append(f"  评估时间：{self.generated_at}")
        lines.append("")

        # 总体评分
        lines.append("【总体评分】")
        score_bar = "█" * int(self.result.overall_score) + "░" * (5 - int(self.result.overall_score))
        lines.append(f"  得分：[{score_bar}] {self.result.overall_score:.2f} / 5.0")
        lines.append(f"  评级：{self.result.level}")
        lines.append("")

        # 7 维度评分
        lines.append("【7 维度评估】")
        dimension_names = {
            EvaluationDimension7.CONTENT_QUALITY: "内容质量",
            EvaluationDimension7.EXPRESSION_CLARITY: "表达清晰度",
            EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识",
            EvaluationDimension7.ADAPTABILITY: "应变能力",
            EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧",
            EvaluationDimension7.CONFIDENCE_LEVEL: "自信程度",
            EvaluationDimension7.INNOVATIVE_THINKING: "创新思维",
        }
        for dim, score in self.result.dimension_scores.items():
            name = dimension_names.get(dim, dim.value)
            bar = "█" * int(score.score / 0.5) + "░" * (10 - int(score.score / 0.5))
            lines.append(f"  {name}: [{bar}] {score.score:.2f}")
            if score.comments:
                lines.append(f"    评语：{score.comments}")
        lines.append("")

        # 评估摘要
        lines.append("【评估摘要】")
        lines.append(f"  {self.result.summary}")
        lines.append("")

        # 优势
        if self.result.strengths:
            lines.append("【优势】")
            for i, strength in enumerate(self.result.strengths, 1):
                lines.append(f"  {i}. {strength}")
            lines.append("")

        # 待改进
        if self.result.weaknesses:
            lines.append("【待改进】")
            for i, weakness in enumerate(self.result.weaknesses, 1):
                lines.append(f"  {i}. {weakness}")
            lines.append("")

        # 建议
        if self.result.suggestions:
            lines.append("【改进建议】")
            for i, suggestion in enumerate(self.result.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_json_report(self) -> Dict[str, Any]:
        """
        生成 JSON 格式报告

        Returns:
            报告字典
        """
        return {
            "report_type": "interview_evaluation_v0.3",
            "generated_at": self.generated_at,
            "candidate_info": self.candidate_info,
            "interview_info": self.interview_info,
            "evaluation": self.result.to_dict(),
        }

    def __str__(self) -> str:
        return self.generate_text_report()


class AdvancedEvaluator:
    """
    高级评估器

    基于 AgentScope LLM 的 7 维度智能评估系统，支持：
    - LLM 驱动的深度评估
    - 可配置的权重和阈值
    - 详细的反馈生成
    - 改进建议推荐

    Attributes:
        config: 配置对象
        model_agent: AgentScope ModelAgent 实例
        weights: 维度权重配置
        thresholds: 评级阈值配置
        suggestions_db: 改进建议数据库
    """

    # 默认 7 维度权重
    DEFAULT_WEIGHTS = {
        EvaluationDimension7.CONTENT_QUALITY: 0.15,
        EvaluationDimension7.EXPRESSION_CLARITY: 0.13,
        EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: 0.18,
        EvaluationDimension7.ADAPTABILITY: 0.12,
        EvaluationDimension7.COMMUNICATION_SKILLS: 0.14,
        EvaluationDimension7.CONFIDENCE_LEVEL: 0.13,
        EvaluationDimension7.INNOVATIVE_THINKING: 0.15,
    }

    # 评级阈值
    LEVEL_THRESHOLDS = {
        "S": 4.5,
        "A": 4.0,
        "B": 3.0,
        "C": 2.0,
        "D": 0.0,
    }

    # 7 维度子维度定义
    SUB_DIMENSIONS = {
        EvaluationDimension7.CONTENT_QUALITY: ["相关性", "准确性", "深度"],
        EvaluationDimension7.EXPRESSION_CLARITY: ["逻辑性", "简洁性", "条理性"],
        EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: ["技术深度", "经验", "解决问题能力"],
        EvaluationDimension7.ADAPTABILITY: ["意外问题处理", "灵活应对", "压力管理"],
        EvaluationDimension7.COMMUNICATION_SKILLS: ["倾听", "表达", "互动质量"],
        EvaluationDimension7.CONFIDENCE_LEVEL: ["语气", "确定性", "自我展示"],
        EvaluationDimension7.INNOVATIVE_THINKING: ["独特见解", "创造性", "批判性思维"],
    }

    def __init__(
        self,
        config: Optional[Config] = None,
        model_agent: Optional[Any] = None,
        weights: Optional[Dict[EvaluationDimension7, float]] = None,
    ):
        """
        初始化高级评估器

        Args:
            config: 配置对象
            model_agent: AgentScope ModelAgent 实例（用于 LLM 评估）
            weights: 维度权重配置
        """
        self.config = config or Config()
        self.model_agent = model_agent

        # 加载权重配置
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # 从配置加载权重（如果存在）
        config_weights = self.config.get("evaluation.v03.weights", {})
        for dim_name, weight in config_weights.items():
            try:
                dim = EvaluationDimension7(dim_name)
                self.weights[dim] = weight
            except ValueError:
                logger.warning(f"未知评估维度：{dim_name}")

        # 归一化权重
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            for dim in self.weights:
                self.weights[dim] /= total_weight

        # 加载阈值配置
        self.thresholds = self.LEVEL_THRESHOLDS.copy()
        config_thresholds = self.config.get("evaluation.v03.thresholds", {})
        self.thresholds.update(config_thresholds)

        # 加载改进建议数据库
        self.suggestions_db = self._load_suggestions_db()

        logger.info(f"AdvancedEvaluator 初始化完成，7 维度权重：{self.weights}")

    def _load_suggestions_db(self) -> Dict[str, Any]:
        """加载改进建议数据库"""
        suggestions_path = Path(__file__).parent / "suggestions_db.yaml"
        if suggestions_path.exists():
            try:
                with open(suggestions_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"加载建议数据库失败：{e}")
        return {}

    def evaluate(
        self,
        dialogue_history: List[Message],
        question_answers: Optional[List[Dict[str, str]]] = None,
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> AdvancedEvaluationResult:
        """
        评估对话历史

        Args:
            dialogue_history: 对话历史消息列表
            question_answers: 问答对列表（可选）
            candidate_info: 候选人信息（可选）
            interview_info: 面试信息（可选）

        Returns:
            高级评估结果
        """
        logger.info(f"[v0.3] 开始 7 维度评估，对话轮数：{len(dialogue_history)}")

        # 提取候选人回答
        answers = self._extract_answers(dialogue_history)
        questions = self._extract_questions(dialogue_history)

        # 构建评估上下文
        eval_context = {
            "answers": answers,
            "questions": questions,
            "dialogue_length": len(dialogue_history),
            "candidate_info": candidate_info or {},
            "interview_info": interview_info or {},
        }

        # 使用 LLM 进行评估（如果有 ModelAgent）
        if self.model_agent:
            dimension_scores = self._llm_evaluate_dimensions(eval_context)
        else:
            # 降级到规则基础评估
            logger.warning("未提供 ModelAgent，使用规则基础评估")
            dimension_scores = self._rule_based_evaluate(eval_context)

        # 构建评估结果
        result = AdvancedEvaluationResult(
            dimension_scores=dimension_scores,
        )

        # 计算总体评分
        result.overall_score = self._calculate_overall_score(result.dimension_scores)

        # 确定评级
        result.level = self._determine_level(result.overall_score)

        # 生成摘要和建议
        result.summary = self._generate_summary(result)
        result.strengths = self._identify_strengths(result)
        result.weaknesses = self._identify_weaknesses(result)
        result.suggestions = self._generate_suggestions(result)

        # 添加元数据
        result.metadata = {
            "answer_count": len(answers),
            "question_count": len(questions),
            "total_words": sum(len(a) for a in answers),
            "avg_answer_length": sum(len(a) for a in answers) / len(answers) if answers else 0,
            "evaluation_method": "llm" if self.model_agent else "rule_based",
        }

        # 生成详细反馈
        result.detailed_feedback = self._generate_detailed_feedback(result, eval_context)

        logger.info(f"[v0.3] 评估完成，总体评分：{result.overall_score:.2f}, 评级：{result.level}")

        return result

    def _extract_answers(self, dialogue_history: List[Message]) -> List[str]:
        """从对话历史中提取候选人回答"""
        answers = []
        for msg in dialogue_history:
            # 用户消息视为候选人回答
            if hasattr(msg, 'type') and msg.type.value == "user":
                answers.append(msg.content)
            elif getattr(msg, 'role', '') == 'user':
                answers.append(msg.content)
        return answers

    def _extract_questions(self, dialogue_history: List[Message]) -> List[str]:
        """从对话历史中提取面试官问题"""
        questions = []
        for msg in dialogue_history:
            # Agent 消息视为面试官问题
            if hasattr(msg, 'type') and msg.type.value == "agent":
                questions.append(msg.content)
            elif getattr(msg, 'role', '') in ['assistant', 'interviewer']:
                questions.append(msg.content)
        return questions

    def _llm_evaluate_dimensions(
        self,
        context: Dict[str, Any],
    ) -> Dict[EvaluationDimension7, DimensionScore7]:
        """
        使用 LLM 进行 7 维度评估

        Args:
            context: 评估上下文

        Returns:
            各维度评分
        """
        dimension_scores = {}

        for dimension in EvaluationDimension7:
            # 构建评估提示词
            prompt = self._build_evaluation_prompt(dimension, context)

            try:
                # 调用 LLM 进行评估
                llm_response = self._call_llm_for_evaluation(prompt)

                # 解析 LLM 响应
                score_data = self._parse_llm_evaluation_response(llm_response, dimension)

                # 创建维度评分
                dimension_scores[dimension] = DimensionScore7(
                    dimension=dimension,
                    score=score_data["score"],
                    weight=self.weights.get(dimension, 0.14),
                    sub_scores=score_data.get("sub_scores", {}),
                    comments=score_data.get("comments", ""),
                    evidence=score_data.get("evidence", []),
                    improvement_suggestions=score_data.get("improvement_suggestions", []),
                )

            except Exception as e:
                logger.error(f"LLM 评估维度 {dimension.value} 失败：{e}")
                # 降级处理
                dimension_scores[dimension] = self._fallback_dimension_score(dimension, context)

        return dimension_scores

    def _rule_based_evaluate(
        self,
        context: Dict[str, Any],
    ) -> Dict[EvaluationDimension7, DimensionScore7]:
        """
        规则基础评估（降级方案）

        Args:
            context: 评估上下文

        Returns:
            各维度评分
        """
        dimension_scores = {}
        answers = context.get("answers", [])

        for dimension in EvaluationDimension7:
            score = self._calculate_rule_based_score(dimension, answers, context)
            dimension_scores[dimension] = DimensionScore7(
                dimension=dimension,
                score=score,
                weight=self.weights.get(dimension, 0.14),
                sub_scores=self._calculate_sub_scores(dimension, answers),
                comments=self._generate_rule_based_comments(dimension, score),
            )

        return dimension_scores

    def _build_evaluation_prompt(
        self,
        dimension: EvaluationDimension7,
        context: Dict[str, Any],
    ) -> str:
        """
        构建 LLM 评估提示词

        Args:
            dimension: 评估维度
            context: 评估上下文

        Returns:
            提示词字符串
        """
        dimension_names = {
            EvaluationDimension7.CONTENT_QUALITY: "内容质量",
            EvaluationDimension7.EXPRESSION_CLARITY: "表达清晰度",
            EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识",
            EvaluationDimension7.ADAPTABILITY: "应变能力",
            EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧",
            EvaluationDimension7.CONFIDENCE_LEVEL: "自信程度",
            EvaluationDimension7.INNOVATIVE_THINKING: "创新思维",
        }

        sub_dims = self.SUB_DIMENSIONS.get(dimension, [])
        answers = context.get("answers", [])
        questions = context.get("questions", [])

        # 构建答案文本
        answers_text = "\n\n".join([f"回答{i+1}: {a}" for i, a in enumerate(answers)])
        questions_text = "\n\n".join([f"问题{i+1}: {q}" for i, q in enumerate(questions)])

        prompt = f"""你是一位专业的面试评估专家。请对候选人的"{dimension_names[dimension]}"维度进行评估。

## 评估维度说明
{dimension_names[dimension]}包含以下子维度：{', '.join(sub_dims)}

## 面试问题
{questions_text}

## 候选人回答
{answers_text}

## 评估要求
1. 请对每个子维度进行评分（0-5 分）
2. 给出总体评分（0-5 分）
3. 提供具体评语
4. 引用回答中的具体证据
5. 提供 2-3 条改进建议

## 输出格式（JSON）
{{
    "score": 3.5,
    "sub_scores": {{
        "{sub_dims[0]}": 3.5,
        "{sub_dims[1]}": 4.0,
        "{sub_dims[2]}": 3.0
    }},
    "comments": "具体评语...",
    "evidence": ["引用原文 1", "引用原文 2"],
    "improvement_suggestions": ["建议 1", "建议 2", "建议 3"]
}}

请严格按照 JSON 格式输出，不要添加其他内容。"""

        return prompt

    def _call_llm_for_evaluation(self, prompt: str) -> str:
        """
        调用 LLM 进行评估

        Args:
            prompt: 评估提示词

        Returns:
            LLM 响应文本
        """
        if not self.model_agent:
            raise ValueError("ModelAgent 未配置")

        # 调用 AgentScope ModelAgent
        response = self.model_agent(prompt)

        if hasattr(response, 'content'):
            return response.content
        elif isinstance(response, dict):
            return response.get('content', str(response))
        else:
            return str(response)

    def _parse_llm_evaluation_response(
        self,
        response: str,
        dimension: EvaluationDimension7,
    ) -> Dict[str, Any]:
        """
        解析 LLM 评估响应

        Args:
            response: LLM 响应文本
            dimension: 评估维度

        Returns:
            解析后的评分数据
        """
        import json
        import re

        # 尝试提取 JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return {
                    "score": float(data.get("score", 3.0)),
                    "sub_scores": data.get("sub_scores", {}),
                    "comments": data.get("comments", ""),
                    "evidence": data.get("evidence", []),
                    "improvement_suggestions": data.get("improvement_suggestions", []),
                }
            except json.JSONDecodeError:
                logger.warning(f"JSON 解析失败：{response[:100]}...")

        # 降级处理：返回默认值
        return {
            "score": 3.0,
            "sub_scores": {},
            "comments": "基于 LLM 分析",
            "evidence": [],
            "improvement_suggestions": [],
        }

    def _fallback_dimension_score(
        self,
        dimension: EvaluationDimension7,
        context: Dict[str, Any],
    ) -> DimensionScore7:
        """降级维度评分"""
        answers = context.get("answers", [])
        score = self._calculate_rule_based_score(dimension, answers, context)
        return DimensionScore7(
            dimension=dimension,
            score=score,
            weight=self.weights.get(dimension, 0.14),
            comments="降级评估",
        )

    def _calculate_rule_based_score(
        self,
        dimension: EvaluationDimension7,
        answers: List[str],
        context: Dict[str, Any],
    ) -> float:
        """
        规则基础评分

        Args:
            dimension: 评估维度
            answers: 回答列表
            context: 评估上下文

        Returns:
            评分 (0-5)
        """
        if not answers:
            return 0.0

        # 基础分
        base_score = 3.0

        # 根据维度应用不同规则
        if dimension == EvaluationDimension7.CONTENT_QUALITY:
            # 内容质量：基于长度和关键词
            avg_length = sum(len(a) for a in answers) / len(answers)
            if avg_length > 200:
                base_score += 0.5
            if avg_length < 50:
                base_score -= 0.5

        elif dimension == EvaluationDimension7.EXPRESSION_CLARITY:
            # 表达清晰度：基于结构化表述
            structured_count = sum(1 for a in answers if any(kw in a for kw in ["首先", "其次", "第一", "第二"]))
            base_score += min(structured_count * 0.2, 1.0)

        elif dimension == EvaluationDimension7.PROFESSIONAL_KNOWLEDGE:
            # 专业知识：基于技术术语
            tech_keywords = ["原理", "机制", "架构", "设计模式", "算法", "源码"]
            tech_count = sum(1 for a in answers for kw in tech_keywords if kw in a)
            base_score += min(tech_count * 0.15, 1.5)

        elif dimension == EvaluationDimension7.ADAPTABILITY:
            # 应变能力：基于问题多样性响应
            base_score += 0.3  # 默认加分

        elif dimension == EvaluationDimension7.COMMUNICATION_SKILLS:
            # 沟通技巧：基于互动质量
            base_score += 0.2

        elif dimension == EvaluationDimension7.CONFIDENCE_LEVEL:
            # 自信程度：基于确定性词汇
            confident_words = ["是", "需要", "应该", "必须"]
            confident_count = sum(1 for a in answers for kw in confident_words if kw in a)
            base_score += min(confident_count * 0.1, 0.5)

        elif dimension == EvaluationDimension7.INNOVATIVE_THINKING:
            # 创新思维：基于独特表述
            innovation_keywords = ["创新", "独特", "不同", "改进", "优化"]
            innov_count = sum(1 for a in answers for kw in innovation_keywords if kw in a)
            base_score += min(innov_count * 0.15, 0.8)

        return min(5.0, max(0.0, round(base_score, 2)))

    def _calculate_sub_scores(
        self,
        dimension: EvaluationDimension7,
        answers: List[str],
    ) -> Dict[str, float]:
        """计算子维度评分"""
        sub_dims = self.SUB_DIMENSIONS.get(dimension, [])
        return {sub_dim: 3.0 for sub_dim in sub_dims}

    def _generate_rule_based_comments(
        self,
        dimension: EvaluationDimension7,
        score: float,
    ) -> str:
        """生成规则基础评语"""
        if score >= 4.0:
            return "表现优秀"
        elif score >= 3.0:
            return "表现良好"
        elif score >= 2.0:
            return "表现一般"
        else:
            return "有待提高"

    def _calculate_overall_score(
        self,
        dimension_scores: Dict[EvaluationDimension7, DimensionScore7],
    ) -> float:
        """计算总体评分"""
        total_score = 0.0
        total_weight = 0.0

        for dim, score_obj in dimension_scores.items():
            weight = self.weights.get(dim, 0.14)
            total_score += score_obj.score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return round(total_score / total_weight, 2)

    def _determine_level(self, overall_score: float) -> str:
        """确定评级"""
        for level, threshold in sorted(
            self.thresholds.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            if overall_score >= threshold:
                return level
        return "D"

    def _generate_summary(self, result: AdvancedEvaluationResult) -> str:
        """生成评估摘要"""
        level_descriptions = {
            "S": "表现卓越，远超预期，具备高级/专家级能力",
            "A": "表现优秀，符合高级职位要求，技术扎实",
            "B": "表现良好，符合职位要求，有发展潜力",
            "C": "表现一般，基本符合要求，需要进一步提升",
            "D": "表现不足，与岗位要求有差距",
        }

        base_desc = level_descriptions.get(result.level, "评估完成")

        # 获取最强和最弱维度
        top_dims = result.get_top_dimensions(2)
        bottom_dims = result.get_bottom_dimensions(2)

        dimension_names = {
            EvaluationDimension7.CONTENT_QUALITY: "内容质量",
            EvaluationDimension7.EXPRESSION_CLARITY: "表达清晰度",
            EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识",
            EvaluationDimension7.ADAPTABILITY: "应变能力",
            EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧",
            EvaluationDimension7.CONFIDENCE_LEVEL: "自信程度",
            EvaluationDimension7.INNOVATIVE_THINKING: "创新思维",
        }

        summary_parts = [base_desc]

        if top_dims:
            top_names = [dimension_names.get(d, d.value) for d, _ in top_dims]
            summary_parts.append(f"在{'、'.join(top_names)}方面表现突出")

        if bottom_dims:
            bottom_names = [dimension_names.get(d, d.value) for d, _ in bottom_dims]
            summary_parts.append(f"{'、'.join(bottom_names)}有待提升")

        return "；".join(summary_parts) + "。"

    def _identify_strengths(self, result: AdvancedEvaluationResult) -> List[str]:
        """识别优势点"""
        strengths = []
        top_dims = result.get_top_dimensions(3)

        dimension_comments = {
            EvaluationDimension7.CONTENT_QUALITY: "内容切题且准确",
            EvaluationDimension7.EXPRESSION_CLARITY: "表达清晰有条理",
            EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识扎实",
            EvaluationDimension7.ADAPTABILITY: "应变能力强",
            EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧优秀",
            EvaluationDimension7.CONFIDENCE_LEVEL: "自信从容",
            EvaluationDimension7.INNOVATIVE_THINKING: "创新思维突出",
        }

        for dim, score in top_dims:
            if score >= 3.5:
                comment = dimension_comments.get(dim, "表现优秀")
                strengths.append(f"{comment}（{dim.value}: {score:.2f}）")

        return strengths

    def _identify_weaknesses(self, result: AdvancedEvaluationResult) -> List[str]:
        """识别待改进点"""
        weaknesses = []
        bottom_dims = result.get_bottom_dimensions(3)

        dimension_weaknesses = {
            EvaluationDimension7.CONTENT_QUALITY: "内容深度和准确性需加强",
            EvaluationDimension7.EXPRESSION_CLARITY: "表达逻辑性需提升",
            EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识需进一步积累",
            EvaluationDimension7.ADAPTABILITY: "应变能力需锻炼",
            EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧需改进",
            EvaluationDimension7.CONFIDENCE_LEVEL: "自信心需建立",
            EvaluationDimension7.INNOVATIVE_THINKING: "创新思维需培养",
        }

        for dim, score in bottom_dims:
            if score < 3.0:
                weakness = dimension_weaknesses.get(dim, "需要提升")
                weaknesses.append(f"{weakness}（{dim.value}: {score:.2f}）")

        return weaknesses

    def _generate_suggestions(self, result: AdvancedEvaluationResult) -> List[str]:
        """生成改进建议"""
        suggestions = []
        bottom_dims = result.get_bottom_dimensions(3)

        for dim, score in bottom_dims:
            if score < 3.5:
                # 从建议数据库获取
                dim_suggestions = self._get_suggestions_for_dimension(dim, score)
                suggestions.extend(dim_suggestions[:2])  # 每个维度最多 2 条

        # 如果建议不足，添加通用建议
        if len(suggestions) < 3:
            generic_suggestions = [
                "多参与实际项目，积累实战经验",
                "加强系统性学习，建立完整知识体系",
                "练习结构化表达，提升沟通效率",
            ]
            for sug in generic_suggestions:
                if len(suggestions) >= 5:
                    break
                if sug not in suggestions:
                    suggestions.append(sug)

        return suggestions[:5]  # 最多 5 条建议

    def _get_suggestions_for_dimension(
        self,
        dimension: EvaluationDimension7,
        score: float,
    ) -> List[str]:
        """获取指定维度的改进建议"""
        if not self.suggestions_db:
            return ["建议加强该维度的训练和实践"]

        dim_key = dimension.value
        if dim_key in self.suggestions_db:
            dim_data = self.suggestions_db[dim_key]
            # 根据分数选择建议
            if score < 2.0:
                return dim_data.get("low_score", [])
            elif score < 3.0:
                return dim_data.get("medium_score", [])
            else:
                return dim_data.get("high_score", [])

        return ["建议加强该维度的训练和实践"]

    def _generate_detailed_feedback(
        self,
        result: AdvancedEvaluationResult,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """生成详细反馈"""
        return {
            "evaluation_dimensions": 7,
            "total_answers": len(context.get("answers", [])),
            "total_questions": len(context.get("questions", [])),
            "dimension_breakdown": {
                dim.value: score.to_dict()
                for dim, score in result.dimension_scores.items()
            },
        }

    def evaluate_single_answer(
        self,
        answer: str,
        question: Optional[str] = None,
        dimension: Optional[EvaluationDimension7] = None,
    ) -> Dict[str, Any]:
        """
        评估单个回答

        Args:
            answer: 回答内容
            question: 原问题（可选）
            dimension: 指定评估维度（可选）

        Returns:
            评估结果字典
        """
        context = {
            "answers": [answer],
            "questions": [question] if question else [],
        }

        if dimension:
            # 评估指定维度
            score_obj = self._rule_based_evaluate(context).get(dimension)
            return {
                dimension.value: score_obj.score if score_obj else 0.0,
            }
        else:
            # 评估所有维度
            scores = self._rule_based_evaluate(context)
            return {
                dim.value: score_obj.score
                for dim, score_obj in scores.items()
            }
