"""
Basic Evaluator - 基础评估器

实现三维度评估模型：
1. content_quality (内容质量): 相关性、准确性、深度
2. expression_clarity (表达清晰度): 逻辑性、简洁性、条理性
3. professional_knowledge (专业知识): 专业知识、经验、解决问题能力

设计原则:
- 单一职责：专注于评估逻辑
- 可扩展：支持添加新的评估维度
- 配置驱动：评估权重和阈值可配置
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from core.agent import Message
from core.config import Config

logger = logging.getLogger(__name__)


class EvaluationDimension(Enum):
    """
    评估维度枚举

    定义三个核心评估维度
    """
    CONTENT_QUALITY = "content_quality"       # 内容质量
    EXPRESSION_CLARITY = "expression_clarity"  # 表达清晰度
    PROFESSIONAL_KNOWLEDGE = "professional_knowledge"  # 专业知识


@dataclass
class DimensionScore:
    """
    维度评分数据类

    封装单个维度的评分详情

    Attributes:
        dimension: 评估维度
        score: 维度得分 (0-5)
        weight: 权重 (0-1)
        sub_scores: 子维度得分
        comments: 评语
        evidence: 评分依据
    """
    dimension: EvaluationDimension
    score: float = 0.0
    weight: float = 1.0
    sub_scores: Dict[str, float] = field(default_factory=dict)
    comments: str = ""
    evidence: List[str] = field(default_factory=list)

    def weighted_score(self) -> float:
        """计算加权得分"""
        return self.score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimension": self.dimension.value,
            "score": round(self.score, 2),
            "weight": self.weight,
            "sub_scores": {k: round(v, 2) for k, v in self.sub_scores.items()},
            "comments": self.comments,
            "evidence": self.evidence,
        }


@dataclass
class EvaluationResult:
    """
    评估结果数据类

    封装完整的评估结果

    Attributes:
        overall_score: 总体评分 (0-5)
        dimension_scores: 各维度评分
        level: 评级 (S/A/B/C/D)
        summary: 评估摘要
        strengths: 优势点
        weaknesses: 待改进点
        suggestions: 改进建议
        metadata: 元数据
    """
    overall_score: float = 0.0
    dimension_scores: Dict[EvaluationDimension, DimensionScore] = field(default_factory=dict)
    level: str = "C"
    summary: str = ""
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_score(self, dimension: EvaluationDimension) -> float:
        """获取指定维度得分"""
        if dimension in self.dimension_scores:
            return self.dimension_scores[dimension].score
        return 0.0

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
            "metadata": self.metadata,
        }

    def to_report(self) -> "EvaluationReport":
        """转换为评估报告"""
        return EvaluationReport.from_result(self)


@dataclass
class EvaluationReport:
    """
    评估报告类

    生成格式化的评估报告

    Attributes:
        result: 评估结果
        generated_at: 生成时间
        candidate_info: 候选人信息
        interview_info: 面试信息
    """
    result: EvaluationResult
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    candidate_info: Dict[str, Any] = field(default_factory=dict)
    interview_info: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_result(
        cls,
        result: EvaluationResult,
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> "EvaluationReport":
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
        lines.append("=" * 60)
        lines.append("面试评估报告")
        lines.append("=" * 60)
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
        lines.append(f"  得分：{self.result.overall_score:.2f} / 5.0")
        lines.append(f"  评级：{self.result.level}")
        lines.append("")

        # 维度评分
        lines.append("【维度评分】")
        dimension_names = {
            EvaluationDimension.CONTENT_QUALITY: "内容质量",
            EvaluationDimension.EXPRESSION_CLARITY: "表达清晰度",
            EvaluationDimension.PROFESSIONAL_KNOWLEDGE: "专业知识",
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

        lines.append("=" * 60)

        return "\n".join(lines)

    def generate_json_report(self) -> Dict[str, Any]:
        """
        生成 JSON 格式报告

        Returns:
            报告字典
        """
        return {
            "report_type": "interview_evaluation",
            "generated_at": self.generated_at,
            "candidate_info": self.candidate_info,
            "interview_info": self.interview_info,
            "evaluation": self.result.to_dict(),
        }

    def __str__(self) -> str:
        return self.generate_text_report()


class BasicEvaluator:
    """
    基础评估器

    实现三维度评估模型，支持：
    - 基于规则的评分
    - 基于关键词的分析
    - 可配置的权重和阈值

    Attributes:
        config: 配置对象
        weights: 维度权重配置
        thresholds: 评级阈值配置
    """

    # 默认维度权重
    DEFAULT_WEIGHTS = {
        EvaluationDimension.CONTENT_QUALITY: 0.35,
        EvaluationDimension.EXPRESSION_CLARITY: 0.30,
        EvaluationDimension.PROFESSIONAL_KNOWLEDGE: 0.35,
    }

    # 评级阈值
    LEVEL_THRESHOLDS = {
        "S": 4.5,
        "A": 4.0,
        "B": 3.0,
        "C": 2.0,
        "D": 0.0,
    }

    # 评估关键词库
    KEYWORD_LIBRARY = {
        # 逻辑性关键词
        "logic": ["首先", "其次", "然后", "最后", "第一", "第二", "因此", "所以", "因为", "由于"],
        # 深度关键词
        "depth": ["原理", "机制", "本质", "核心", "底层", "源码", "实现细节", "源码分析"],
        # 经验关键词
        "experience": ["项目", "实践", "经验", "案例", "场景", "生产环境", "实际"],
        # 解决问题关键词
        "problem_solving": ["问题", "解决", "优化", "改进", "方案", "思路", "分析", "排查"],
        # 准确性关键词
        "accuracy": ["准确", "正确", "精确", "严格", "规范", "标准"],
        # 简洁性指标
        "conciseness": ["简洁", "清晰", "明了", "直接", "重点"],
    }

    def __init__(
        self,
        config: Optional[Config] = None,
        weights: Optional[Dict[EvaluationDimension, float]] = None,
    ):
        """
        初始化评估器

        Args:
            config: 配置对象
            weights: 维度权重配置
        """
        self.config = config or Config()

        # 加载权重配置
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # 从配置加载权重（如果存在）
        config_weights = self.config.get("evaluation.weights", {})
        for dim_name, weight in config_weights.items():
            try:
                dim = EvaluationDimension(dim_name)
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
        config_thresholds = self.config.get("evaluation.thresholds", {})
        self.thresholds.update(config_thresholds)

    def evaluate(
        self,
        dialogue_history: List[Message],
        question_answers: Optional[List[Dict[str, str]]] = None,
    ) -> EvaluationResult:
        """
        评估对话历史

        Args:
            dialogue_history: 对话历史消息列表
            question_answers: 问答对列表（可选）

        Returns:
            评估结果
        """
        logger.info(f"开始评估，对话轮数：{len(dialogue_history)}")

        # 提取候选人回答
        answers = self._extract_answers(dialogue_history)

        # 评估各维度
        content_score = self._evaluate_content_quality(answers)
        expression_score = self._evaluate_expression_clarity(answers)
        knowledge_score = self._evaluate_professional_knowledge(answers)

        # 构建评估结果
        result = EvaluationResult(
            dimension_scores={
                EvaluationDimension.CONTENT_QUALITY: content_score,
                EvaluationDimension.EXPRESSION_CLARITY: expression_score,
                EvaluationDimension.PROFESSIONAL_KNOWLEDGE: knowledge_score,
            },
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
            "total_words": sum(len(a) for a in answers),
            "avg_answer_length": sum(len(a) for a in answers) / len(answers) if answers else 0,
        }

        logger.info(f"评估完成，总体评分：{result.overall_score:.2f}, 评级：{result.level}")

        return result

    def evaluate_answer(
        self,
        answer: str,
        question: Optional[str] = None,
        expected_points: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        评估单个回答

        Args:
            answer: 回答内容
            question: 原问题（可选）
            expected_points: 期望要点（可选）

        Returns:
            评估结果字典
        """
        # 内容质量
        content_score = self._score_content_quality(answer, question, expected_points)

        # 表达清晰度
        expression_score = self._score_expression_clarity(answer)

        # 专业知识
        knowledge_score = self._score_professional_knowledge(answer)

        return {
            "content_quality": content_score,
            "expression_clarity": expression_score,
            "professional_knowledge": knowledge_score,
            "overall": (content_score + expression_score + knowledge_score) / 3,
        }

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

    def _evaluate_content_quality(
        self,
        answers: List[str],
    ) -> DimensionScore:
        """评估内容质量维度"""
        if not answers:
            return DimensionScore(
                dimension=EvaluationDimension.CONTENT_QUALITY,
                score=0.0,
                weight=self.weights.get(EvaluationDimension.CONTENT_QUALITY, 0.35),
                comments="无有效回答",
            )

        # 子维度评分
        relevance_scores = []
        accuracy_scores = []
        depth_scores = []

        for answer in answers:
            relevance_scores.append(self._score_relevance(answer))
            accuracy_scores.append(self._score_accuracy(answer))
            depth_scores.append(self._score_depth(answer))

        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        avg_depth = sum(depth_scores) / len(answers)

        # 计算维度总分（加权平均）
        score = avg_relevance * 0.4 + avg_accuracy * 0.3 + avg_depth * 0.3

        # 生成评语
        comments = self._generate_content_comments(avg_relevance, avg_accuracy, avg_depth)

        return DimensionScore(
            dimension=EvaluationDimension.CONTENT_QUALITY,
            score=round(score, 2),
            weight=self.weights.get(EvaluationDimension.CONTENT_QUALITY, 0.35),
            sub_scores={
                "relevance": round(avg_relevance, 2),
                "accuracy": round(avg_accuracy, 2),
                "depth": round(avg_depth, 2),
            },
            comments=comments,
            evidence=[f"分析了 {len(answers)} 个回答"],
        )

    def _evaluate_expression_clarity(
        self,
        answers: List[str],
    ) -> DimensionScore:
        """评估表达清晰度维度"""
        if not answers:
            return DimensionScore(
                dimension=EvaluationDimension.EXPRESSION_CLARITY,
                score=0.0,
                weight=self.weights.get(EvaluationDimension.EXPRESSION_CLARITY, 0.30),
                comments="无有效回答",
            )

        # 子维度评分
        logic_scores = []
        conciseness_scores = []
        organization_scores = []

        for answer in answers:
            logic_scores.append(self._score_logic(answer))
            conciseness_scores.append(self._score_conciseness(answer))
            organization_scores.append(self._score_organization(answer))

        avg_logic = sum(logic_scores) / len(logic_scores)
        avg_conciseness = sum(conciseness_scores) / len(conciseness_scores)
        avg_organization = sum(organization_scores) / len(answers)

        score = avg_logic * 0.4 + avg_conciseness * 0.3 + avg_organization * 0.3

        comments = self._generate_expression_comments(avg_logic, avg_conciseness, avg_organization)

        return DimensionScore(
            dimension=EvaluationDimension.EXPRESSION_CLARITY,
            score=round(score, 2),
            weight=self.weights.get(EvaluationDimension.EXPRESSION_CLARITY, 0.30),
            sub_scores={
                "logic": round(avg_logic, 2),
                "conciseness": round(avg_conciseness, 2),
                "organization": round(avg_organization, 2),
            },
            comments=comments,
        )

    def _evaluate_professional_knowledge(
        self,
        answers: List[str],
    ) -> DimensionScore:
        """评估专业知识维度"""
        if not answers:
            return DimensionScore(
                dimension=EvaluationDimension.PROFESSIONAL_KNOWLEDGE,
                score=0.0,
                weight=self.weights.get(EvaluationDimension.PROFESSIONAL_KNOWLEDGE, 0.35),
                comments="无有效回答",
            )

        # 子维度评分
        knowledge_scores = []
        experience_scores = []
        problem_solving_scores = []

        for answer in answers:
            knowledge_scores.append(self._score_knowledge(answer))
            experience_scores.append(self._score_experience(answer))
            problem_solving_scores.append(self._score_problem_solving(answer))

        avg_knowledge = sum(knowledge_scores) / len(knowledge_scores)
        avg_experience = sum(experience_scores) / len(experience_scores)
        avg_problem_solving = sum(problem_solving_scores) / len(answers)

        score = avg_knowledge * 0.4 + avg_experience * 0.3 + avg_problem_solving * 0.3

        comments = self._generate_knowledge_comments(
            avg_knowledge, avg_experience, avg_problem_solving
        )

        return DimensionScore(
            dimension=EvaluationDimension.PROFESSIONAL_KNOWLEDGE,
            score=round(score, 2),
            weight=self.weights.get(EvaluationDimension.PROFESSIONAL_KNOWLEDGE, 0.35),
            sub_scores={
                "knowledge": round(avg_knowledge, 2),
                "experience": round(avg_experience, 2),
                "problem_solving": round(avg_problem_solving, 2),
            },
            comments=comments,
        )

    # ==================== 内容质量评分方法 ====================

    def _score_relevance(self, answer: str) -> float:
        """评分：回答相关性 (0-5)"""
        score = 3.0  # 基础分

        # 回答长度适中
        if 50 <= len(answer) <= 500:
            score += 0.5
        elif len(answer) < 20:
            score -= 1.0
        elif len(answer) > 1000:
            score -= 0.5

        # 包含问题关键词（如果有上下文）
        # 简单实现：检查是否有实质性内容
        if len(answer.strip()) > 30:
            score += 0.5

        return min(5.0, max(0.0, score))

    def _score_accuracy(self, answer: str) -> float:
        """评分：回答准确性 (0-5)"""
        score = 3.0

        # 检查是否有模糊表述
        vague_words = ["可能", "也许", "大概", "好像", "听说"]
        vague_count = sum(1 for word in vague_words if word in answer)
        score -= vague_count * 0.2

        # 检查是否有确定性表述
        confident_words = ["是", "需要", "应该", "必须", "通常"]
        confident_count = sum(1 for word in confident_words if word in answer)
        if confident_count > 0:
            score += 0.3

        return min(5.0, max(0.0, score))

    def _score_depth(self, answer: str) -> float:
        """评分：回答深度 (0-5)"""
        score = 2.5

        # 检查深度关键词
        depth_keywords = self.KEYWORD_LIBRARY["depth"]
        depth_count = sum(1 for kw in depth_keywords if kw in answer)
        score += min(depth_count * 0.4, 2.0)

        # 检查是否有举例
        if "例如" in answer or "比如" in answer:
            score += 0.3

        # 检查长度
        if len(answer) > 200:
            score += 0.2

        return min(5.0, max(0.0, score))

    def _generate_content_comments(
        self,
        relevance: float,
        accuracy: float,
        depth: float,
    ) -> str:
        """生成内容质量评语"""
        comments = []

        if relevance >= 4.0:
            comments.append("回答切题")
        elif relevance < 2.5:
            comments.append("回答相关性有待提高")

        if accuracy >= 4.0:
            comments.append("表述准确")
        elif accuracy < 2.5:
            comments.append("表述准确性需加强")

        if depth >= 4.0:
            comments.append("分析深入")
        elif depth < 2.5:
            comments.append("可进一步深化分析")

        return "；".join(comments) if comments else "内容质量一般"

    # ==================== 表达清晰度评分方法 ====================

    def _score_logic(self, answer: str) -> float:
        """评分：逻辑性 (0-5)"""
        score = 2.5

        # 检查逻辑连接词
        logic_words = self.KEYWORD_LIBRARY["logic"]
        logic_count = sum(1 for word in logic_words if word in answer)
        score += min(logic_count * 0.3, 2.0)

        return min(5.0, max(0.0, score))

    def _score_conciseness(self, answer: str) -> float:
        """评分：简洁性 (0-5)"""
        score = 3.0

        # 过长扣分
        if len(answer) > 500:
            score -= 0.5
        if len(answer) > 1000:
            score -= 0.5

        # 过短可能不完整
        if len(answer) < 50:
            score -= 0.5

        # 检查冗余表述
        redundant_patterns = ["就是说", "也就是说", "简单来说", "总的来说"]
        redundant_count = sum(1 for pattern in redundant_patterns if pattern in answer)
        if redundant_count > 2:
            score -= 0.3

        return min(5.0, max(0.0, score))

    def _score_organization(self, answer: str) -> float:
        """评分：条理性 (0-5)"""
        score = 2.5

        # 检查结构化表述
        structure_patterns = [
            r"[一二三四五六七八九十][、.]",  # 一、二、三、
            r"[1-9][,.]",  # 1. 2. 3.
            r"首先.*然后",
            r"第一.*第二",
        ]

        for pattern in structure_patterns:
            if re.search(pattern, answer):
                score += 0.5

        # 检查分段
        if "\n" in answer:
            score += 0.3

        return min(5.0, max(0.0, score))

    def _generate_expression_comments(
        self,
        logic: float,
        conciseness: float,
        organization: float,
    ) -> str:
        """生成表达清晰度评语"""
        comments = []

        if logic >= 4.0:
            comments.append("逻辑清晰")
        elif logic < 2.5:
            comments.append("逻辑性需加强")

        if conciseness >= 4.0:
            comments.append("表达简洁")
        elif conciseness < 2.5:
            comments.append("表达可更精炼")

        if organization >= 4.0:
            comments.append("条理分明")
        elif organization < 2.5:
            comments.append("条理性有待提高")

        return "；".join(comments) if comments else "表达清晰度一般"

    # ==================== 专业知识评分方法 ====================

    def _score_knowledge(self, answer: str) -> float:
        """评分：专业知识 (0-5)"""
        score = 2.5

        # 检查专业术语
        technical_indicators = [
            len(answer) > 100,  # 有一定长度
            any(kw in answer for kw in self.KEYWORD_LIBRARY["depth"]),
            any(kw in answer for kw in self.KEYWORD_LIBRARY["accuracy"]),
        ]
        score += sum(technical_indicators) * 0.5

        return min(5.0, max(0.0, score))

    def _score_experience(self, answer: str) -> float:
        """评分：经验体现 (0-5)"""
        score = 2.5

        # 检查经验关键词
        experience_keywords = self.KEYWORD_LIBRARY["experience"]
        exp_count = sum(1 for kw in experience_keywords if kw in answer)
        score += min(exp_count * 0.3, 2.0)

        # 检查是否有具体项目描述
        if "项目" in answer and ("负责" in answer or "主导" in answer):
            score += 0.5

        return min(5.0, max(0.0, score))

    def _score_problem_solving(self, answer: str) -> float:
        """评分：解决问题能力 (0-5)"""
        score = 2.5

        # 检查解决问题关键词
        ps_keywords = self.KEYWORD_LIBRARY["problem_solving"]
        ps_count = sum(1 for kw in ps_keywords if kw in answer)
        score += min(ps_count * 0.3, 2.0)

        # 检查是否有解决方案描述
        solution_patterns = ["方案", "方法", "思路", "步骤", "流程"]
        if any(p in answer for p in solution_patterns):
            score += 0.3

        return min(5.0, max(0.0, score))

    def _generate_knowledge_comments(
        self,
        knowledge: float,
        experience: float,
        problem_solving: float,
    ) -> str:
        """生成专业知识评语"""
        comments = []

        if knowledge >= 4.0:
            comments.append("专业知识扎实")
        elif knowledge < 2.5:
            comments.append("专业知识需加强")

        if experience >= 4.0:
            comments.append("实践经验丰富")
        elif experience < 2.5:
            comments.append("项目经验有待积累")

        if problem_solving >= 4.0:
            comments.append("解决问题能力强")
        elif problem_solving < 2.5:
            comments.append("解决问题能力需提升")

        return "；".join(comments) if comments else "专业知识水平一般"

    # ==================== 综合计算方法 ====================

    def _calculate_overall_score(
        self,
        dimension_scores: Dict[EvaluationDimension, DimensionScore],
    ) -> float:
        """计算总体评分"""
        total_score = 0.0
        total_weight = 0.0

        for dim, score_obj in dimension_scores.items():
            weight = self.weights.get(dim, 1.0)
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

    def _generate_summary(self, result: EvaluationResult) -> str:
        """生成评估摘要"""
        level_descriptions = {
            "S": "表现卓越，远超预期",
            "A": "表现优秀，符合高级职位要求",
            "B": "表现良好，符合职位要求",
            "C": "表现一般，基本符合要求",
            "D": "表现不佳，需要改进",
        }

        base_desc = level_descriptions.get(result.level, "表现一般")

        # 找出最强和最弱维度
        scores = [
            (dim, score.score)
            for dim, score in result.dimension_scores.items()
        ]
        scores.sort(key=lambda x: x[1], reverse=True)

        if scores:
            strongest = scores[0][0].value
            weakest = scores[-1][0].value

            dimension_names = {
                "content_quality": "内容质量",
                "expression_clarity": "表达清晰度",
                "professional_knowledge": "专业知识",
            }

            summary = (
                f"{base_desc}。{dimension_names.get(strongest, strongest)}表现突出，"
                f"{dimension_names.get(weakest, weakest)}有待提升。"
            )
        else:
            summary = base_desc

        return summary

    def _identify_strengths(self, result: EvaluationResult) -> List[str]:
        """识别优势点"""
        strengths = []

        for dim, score_obj in result.dimension_scores.items():
            if score_obj.score >= 4.0:
                if score_obj.sub_scores:
                    for sub_dim, sub_score in score_obj.sub_scores.items():
                        if sub_score >= 4.0:
                            strengths.append(f"{dim.value}.{sub_dim}: {sub_score:.2f}")

        # 如果没有细分优势，添加维度优势
        if not strengths:
            for dim, score_obj in result.dimension_scores.items():
                if score_obj.score >= 4.0:
                    strengths.append(f"{dim.value}: {score_obj.score:.2f}")

        return strengths[:5]  # 最多 5 个优势点

    def _identify_weaknesses(self, result: EvaluationResult) -> List[str]:
        """识别待改进点"""
        weaknesses = []

        for dim, score_obj in result.dimension_scores.items():
            if score_obj.score < 3.0:
                if score_obj.sub_scores:
                    for sub_dim, sub_score in score_obj.sub_scores.items():
                        if sub_score < 3.0:
                            weaknesses.append(f"{dim.value}.{sub_dim}: {sub_score:.2f}")

        if not weaknesses:
            for dim, score_obj in result.dimension_scores.items():
                if score_obj.score < 3.0:
                    weaknesses.append(f"{dim.value}: {score_obj.score:.2f}")

        return weaknesses[:5]

    def _generate_suggestions(self, result: EvaluationResult) -> List[str]:
        """生成改进建议"""
        suggestions = []

        # 基于最弱维度生成建议
        scores = [
            (dim, score.score, score.sub_scores)
            for dim, score in result.dimension_scores.items()
        ]
        scores.sort(key=lambda x: x[1])

        suggestion_templates = {
            EvaluationDimension.CONTENT_QUALITY: [
                "建议加强回答的深度，多从原理层面分析问题",
                "回答时注意结合具体案例，增强说服力",
                "提升回答的准确性，避免模糊表述",
            ],
            EvaluationDimension.EXPRESSION_CLARITY: [
                "建议使用结构化表达，如'首先、其次、最后'",
                "练习简洁表达，避免冗余",
                "注意逻辑连接词的使用，增强条理性",
            ],
            EvaluationDimension.PROFESSIONAL_KNOWLEDGE: [
                "建议深入学习核心技术原理",
                "多参与实际项目，积累实践经验",
                "培养系统性思考和解决问题的能力",
            ],
        }

        # 为最弱的两个维度生成建议
        for dim, score, sub_scores in scores[:2]:
            if score < 3.5:
                templates = suggestion_templates.get(dim, [])
                if templates:
                    suggestions.append(templates[0])

        # 如果没有自动生成，添加通用建议
        if not suggestions:
            suggestions = [
                "继续保持技术学习的热情",
                "多参与技术交流和分享",
                "注重理论与实践结合",
            ]

        return suggestions[:5]
