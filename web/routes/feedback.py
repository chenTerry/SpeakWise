"""
Feedback Routes - 反馈 API 路由

提供评估反馈相关的 RESTful API。
"""

import json
import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


# ============== Models ==============

class DimensionScore(BaseModel):
    """维度评分"""
    name: str
    score: float = Field(ge=0, le=5)
    weight: float = 1.0
    comment: str = ""
    sub_dimensions: Dict[str, float] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    """评估结果"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    overall_score: float = Field(ge=0, le=5)
    rating: str  # S, A, B, C, D
    dimensions: List[DimensionScore] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    summary: str = ""
    created_at: float = Field(default_factory=time.time)


class FeedbackReport(BaseModel):
    """反馈报告"""
    evaluation: EvaluationResult
    scene_info: Dict[str, Any]
    candidate_info: Optional[Dict[str, Any]] = None
    charts_data: Dict[str, Any] = Field(default_factory=dict)


# ============== In-Memory Storage ==============

EVALUATIONS_DB: Dict[str, EvaluationResult] = {}


# ============== Helper Functions ==============

def generate_evaluation(session_id: str, messages: List[Dict]) -> EvaluationResult:
    """
    生成评估结果

    这里应该调用真实的评估模型，暂时使用模拟数据。
    """
    # 根据消息数量和内容生成模拟评分
    message_count = len(messages)

    # 基础分数
    base_score = min(3.0 + (message_count * 0.1), 4.5)

    # 维度评分
    dimensions = [
        DimensionScore(
            name="内容质量",
            score=min(base_score + 0.2, 5.0),
            weight=0.35,
            comment="回答内容较为准确，能够切中要点",
            sub_dimensions={
                "相关性": min(base_score + 0.3, 5.0),
                "准确性": min(base_score + 0.1, 5.0),
                "深度": min(base_score, 5.0),
            },
        ),
        DimensionScore(
            name="表达清晰度",
            score=min(base_score - 0.1, 5.0),
            weight=0.30,
            comment="表达流畅，逻辑性有待提高",
            sub_dimensions={
                "逻辑性": min(base_score - 0.2, 5.0),
                "简洁性": min(base_score, 5.0),
                "条理性": min(base_score, 5.0),
            },
        ),
        DimensionScore(
            name="专业知识",
            score=min(base_score + 0.1, 5.0),
            weight=0.35,
            comment="技术基础扎实，展现了良好的专业素养",
            sub_dimensions={
                "技术深度": min(base_score + 0.2, 5.0),
                "经验": min(base_score, 5.0),
                "解决问题能力": min(base_score + 0.1, 5.0),
            },
        ),
        DimensionScore(
            name="应变能力",
            score=min(base_score, 5.0),
            weight=0.15,
            comment="能够应对突发问题，表现稳定",
            sub_dimensions={
                "反应速度": min(base_score + 0.1, 5.0),
                "灵活应对": min(base_score - 0.1, 5.0),
            },
        ),
        DimensionScore(
            name="沟通技巧",
            score=min(base_score + 0.1, 5.0),
            weight=0.15,
            comment="沟通顺畅，能够清晰表达想法",
            sub_dimensions={
                "倾听": min(base_score, 5.0),
                "表达": min(base_score + 0.2, 5.0),
                "互动": min(base_score, 5.0),
            },
        ),
    ]

    # 计算总体分数
    weighted_score = sum(d.score * d.weight for d in dimensions) / sum(d.weight for d in dimensions)
    overall_score = min(max(weighted_score, 0), 5.0)

    # 确定评级
    if overall_score >= 4.5:
        rating = "S"
    elif overall_score >= 4.0:
        rating = "A"
    elif overall_score >= 3.0:
        rating = "B"
    elif overall_score >= 2.0:
        rating = "C"
    else:
        rating = "D"

    # 生成优势和建议
    strengths = [
        "技术基础扎实，能够准确回答技术问题",
        "表达清晰，逻辑性较好",
        "态度积极，展现了良好的学习意愿",
    ]

    suggestions = [
        "可以更多地使用具体例子来支撑观点",
        "在回答复杂问题时，可以先阐述整体思路",
        "注意控制回答的节奏，避免过于匆忙",
        "多展示解决问题的思考过程",
        "加强对新技术的学习和了解",
    ]

    # 生成总结
    summary = (
        f"本次面试整体表现{rating}级。"
        f"在技术知识和表达能力方面表现良好，"
        f"建议在问题分析和深度思考方面继续提升。"
        f"继续保持学习热情，相信会有更好的发展。"
    )

    return EvaluationResult(
        session_id=session_id,
        overall_score=overall_score,
        rating=rating,
        dimensions=dimensions,
        strengths=strengths,
        suggestions=suggestions,
        summary=summary,
    )


def get_evaluation(evaluation_id: str) -> Optional[EvaluationResult]:
    """获取评估结果"""
    return EVALUATIONS_DB.get(evaluation_id)


# ============== Routes ==============

@router.post("/generate", response_model=EvaluationResult)
async def generate_feedback(
    session_id: str,
    messages: Optional[List[Dict]] = None,
) -> EvaluationResult:
    """生成评估反馈"""
    messages = messages or []
    evaluation = generate_evaluation(session_id, messages)

    # 保存评估结果
    EVALUATIONS_DB[evaluation.id] = evaluation

    return evaluation


@router.get("/{evaluation_id}", response_model=EvaluationResult)
async def get_feedback(evaluation_id: str) -> EvaluationResult:
    """获取评估结果"""
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估结果不存在")
    return evaluation


@router.get("/session/{session_id}", response_model=FeedbackReport)
async def get_session_feedback(session_id: str) -> FeedbackReport:
    """获取会话的反馈报告"""
    # 查找会话相关的评估
    evaluation = None
    for eval_result in EVALUATIONS_DB.values():
        if eval_result.session_id == session_id:
            evaluation = eval_result
            break

    if not evaluation:
        # 生成新的评估
        evaluation = generate_evaluation(session_id, [])
        EVALUATIONS_DB[evaluation.id] = evaluation

    # 生成图表数据
    charts_data = {
        "radar": {
            "labels": [d.name for d in evaluation.dimensions],
            "scores": [d.score for d in evaluation.dimensions],
            "max_score": 5.0,
        },
        "bar": {
            "labels": [d.name for d in evaluation.dimensions],
            "scores": [d.score for d in evaluation.dimensions],
            "weights": [d.weight for d in evaluation.dimensions],
        },
        "gauge": {
            "value": evaluation.overall_score,
            "max": 5.0,
            "rating": evaluation.rating,
        },
    }

    return FeedbackReport(
        evaluation=evaluation,
        scene_info={"name": "面试场景", "id": session_id},
        charts_data=charts_data,
    )


@router.get("/{evaluation_id}/export/json")
async def export_feedback_json(evaluation_id: str) -> Dict[str, Any]:
    """导出 JSON 格式评估报告"""
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估结果不存在")

    return evaluation.dict()


@router.get("/{evaluation_id}/export/markdown")
async def export_feedback_markdown(evaluation_id: str) -> Response:
    """导出 Markdown 格式评估报告"""
    evaluation = get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="评估结果不存在")

    from datetime import datetime

    markdown = f"""# 面试评估报告

## 基本信息

- **评估 ID**: {evaluation.id}
- **会话 ID**: {evaluation.session_id}
- **生成时间**: {datetime.fromtimestamp(evaluation.created_at).strftime('%Y-%m-%d %H:%M:%S')}
- **总体评分**: {evaluation.overall_score:.1f}/5.0
- **评级**: {evaluation.rating}

## 维度评分

| 维度 | 分数 | 权重 | 评语 |
|------|------|------|------|
"""

    for dim in evaluation.dimensions:
        markdown += f"| {dim.name} | {dim.score:.1f} | {dim.weight*100:.0f}% | {dim.comment} |\n"

    markdown += "\n## 优势\n\n"
    for i, strength in enumerate(evaluation.strengths, 1):
        markdown += f"{i}. {strength}\n"

    markdown += "\n## 改进建议\n\n"
    for i, suggestion in enumerate(evaluation.suggestions, 1):
        markdown += f"{i}. {suggestion}\n"

    markdown += f"\n## 总结\n\n{evaluation.summary}\n"

    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename=evaluation_{evaluation_id}.md"
        },
    )


@router.get("/history")
async def get_evaluation_history(
    limit: int = 10,
    offset: int = 0,
) -> Dict[str, Any]:
    """获取评估历史"""
    evaluations = list(EVALUATIONS_DB.values())
    evaluations.sort(key=lambda x: x.created_at, reverse=True)

    # 分页
    paginated = evaluations[offset:offset + limit]

    return {
        "evaluations": [
            {
                "id": e.id,
                "session_id": e.session_id,
                "overall_score": e.overall_score,
                "rating": e.rating,
                "created_at": e.created_at,
            }
            for e in paginated
        ],
        "total": len(evaluations),
        "limit": limit,
        "offset": offset,
    }


@router.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """获取统计信息"""
    evaluations = list(EVALUATIONS_DB.values())

    if not evaluations:
        return {
            "total": 0,
            "average_score": 0,
            "rating_distribution": {},
        }

    # 计算平均分
    avg_score = sum(e.overall_score for e in evaluations) / len(evaluations)

    # 评级分布
    rating_dist = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
    for e in evaluations:
        rating_dist[e.rating] = rating_dist.get(e.rating, 0) + 1

    # 维度平均分
    dim_scores = {}
    for e in evaluations:
        for dim in e.dimensions:
            if dim.name not in dim_scores:
                dim_scores[dim.name] = []
            dim_scores[dim.name].append(dim.score)

    dim_averages = {
        name: sum(scores) / len(scores)
        for name, scores in dim_scores.items()
    }

    return {
        "total": len(evaluations),
        "average_score": round(avg_score, 2),
        "rating_distribution": rating_dist,
        "dimension_averages": dim_averages,
    }
