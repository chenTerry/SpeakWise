# v0.3 演进计划 - 智能反馈系统

## 📋 版本概述

| 项目 | 内容 |
|------|------|
| **版本号** | v0.3 |
| **版本名称** | 智能反馈系统 (Intelligent Feedback System) |
| **目标** | 实现 7 维度评估模型和智能反馈生成 |
| **预计完成** | 2026-03-24 |
| **依赖** | v0.2 基础面试场景 |
| **Git 分支** | feature/v0.3 |

---

## 🎯 核心目标

在 v0.2 基础面试场景之上，实现智能化的反馈评估系统：

1. **7 维度评估模型** - 全面评估用户表现
2. **基于 LLM 的智能评估** - 利用大模型进行深度分析
3. **反馈报告生成器** - 结构化、可视化的反馈报告
4. **改进建议库** - 200+ 条针对性改进建议
5. **评估结果存储** - 支持历史查询和成长追踪

---

## 📐 7 维度评估模型

### 评估维度设计

| 维度 | 权重 | 描述 | 评估指标 |
|------|------|------|----------|
| **内容质量** | 20% | 回答内容的相关性和深度 | 相关性、完整性、深度 |
| **表达清晰度** | 15% | 语言表达的清晰程度 | 逻辑性、结构化、流畅度 |
| **专业知识** | 20% | 专业知识掌握程度 | 准确性、深度、广度 |
| **应变能力** | 15% | 面对追问的反应能力 | 反应速度、灵活性、抗压性 |
| **沟通技巧** | 10% | 沟通表达的技巧性 | 倾听、回应、互动 |
| **自信程度** | 10% | 表现出的自信水平 | 语气、措辞、态度 |
| **创新思维** | 10% | 思考的创新性和独特性 | 独特视角、创新方案 |

### 评分标准

| 分数 | 等级 | 描述 |
|------|------|------|
| 5.0 | 优秀 | 超出预期，表现卓越 |
| 4.0-4.9 | 良好 | 达到预期，表现稳定 |
| 3.0-3.9 | 合格 | 基本达标，有提升空间 |
| 2.0-2.9 | 待改进 | 未达预期，需要加强 |
| 1.0-1.9 | 不足 | 明显不足，需要重点训练 |

---

## 🏗️ 架构设计

### 新增模块结构

```
project/
├── core/                      # v0.1/v0.2 已有
│   ├── config.py
│   ├── agent.py
│   └── dialogue_manager.py
├── scenes/                    # v0.2 已有
│   ├── __init__.py
│   ├── base.py
│   └── interview/
├── evaluation/                # v0.3 重点扩展
│   ├── __init__.py
│   ├── basic_evaluator.py   # v0.2 基础评估器
│   ├── advanced_evaluator.py # v0.3 智能评估器
│   ├── dimensions.py         # 7 维度评估模型
│   ├── report_generator.py   # 反馈报告生成器
│   └── suggestion_bank.py    # 改进建议库
├── storage/                   # v0.3 新增
│   ├── __init__.py
│   └── evaluation_store.py   # 评估结果存储
└── examples/
    ├── interview_demo.py
    └── evaluation_demo.py    # v0.3 评估示例
```

---

## 📦 模块详细设计

### 1. 7 维度评估模型 (`evaluation/dimensions.py`)

```python
# evaluation/dimensions.py
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class EvaluationDimension(Enum):
    """评估维度枚举"""
    CONTENT_QUALITY = "content_quality"       # 内容质量
    EXPRESSION_CLARITY = "expression_clarity" # 表达清晰度
    PROFESSIONAL_KNOWLEDGE = "professional_knowledge"  # 专业知识
    ADAPTABILITY = "adaptability"             # 应变能力
    COMMUNICATION_SKILL = "communication_skill"  # 沟通技巧
    CONFIDENCE_LEVEL = "confidence_level"     # 自信程度
    INNOVATIVE_THINKING = "innovative_thinking"  # 创新思维

@dataclass
class DimensionConfig:
    """维度配置"""
    name: str
    weight: float
    description: str
    indicators: List[str]

@dataclass
class EvaluationResult:
    """评估结果"""
    overall_score: float
    dimension_scores: Dict[str, float]
    level: str  # 优秀/良好/合格/待改进/不足
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    timestamp: str

class SevenDimensionModel:
    """7 维度评估模型"""

    DIMENSION_CONFIGS = {
        EvaluationDimension.CONTENT_QUALITY: DimensionConfig(
            name="内容质量",
            weight=0.20,
            description="回答内容的相关性和深度",
            indicators=["相关性", "完整性", "深度"]
        ),
        EvaluationDimension.EXPRESSION_CLARITY: DimensionConfig(
            name="表达清晰度",
            weight=0.15,
            description="语言表达的清晰程度",
            indicators=["逻辑性", "结构化", "流畅度"]
        ),
        EvaluationDimension.PROFESSIONAL_KNOWLEDGE: DimensionConfig(
            name="专业知识",
            weight=0.20,
            description="专业知识掌握程度",
            indicators=["准确性", "深度", "广度"]
        ),
        EvaluationDimension.ADAPTABILITY: DimensionConfig(
            name="应变能力",
            weight=0.15,
            description="面对追问的反应能力",
            indicators=["反应速度", "灵活性", "抗压性"]
        ),
        EvaluationDimension.COMMUNICATION_SKILL: DimensionConfig(
            name="沟通技巧",
            weight=0.10,
            description="沟通表达的技巧性",
            indicators=["倾听", "回应", "互动"]
        ),
        EvaluationDimension.CONFIDENCE_LEVEL: DimensionConfig(
            name="自信程度",
            weight=0.10,
            description="表现出的自信水平",
            indicators=["语气", "措辞", "态度"]
        ),
        EvaluationDimension.INNOVATIVE_THINKING: DimensionConfig(
            name="创新思维",
            weight=0.10,
            description="思考的创新性和独特性",
            indicators=["独特视角", "创新方案"]
        ),
    }

    def __init__(self):
        self.configs = self.DIMENSION_CONFIGS

    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """计算综合评分"""
        total = 0.0
        for dim, score in dimension_scores.items():
            weight = self.configs[EvaluationDimension(dim)].weight
            total += score * weight
        return round(total, 2)

    def get_level(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 4.5:
            return "优秀"
        elif score >= 4.0:
            return "良好"
        elif score >= 3.0:
            return "合格"
        elif score >= 2.0:
            return "待改进"
        else:
            return "不足"
```

---

### 2. 智能评估器 (`evaluation/advanced_evaluator.py`)

```python
# evaluation/advanced_evaluator.py
from core import EvaluatorAgent, Message, EvaluationResult, DialogueContext
from evaluation.dimensions import SevenDimensionModel, EvaluationDimension
from typing import List, Dict
import agentscope

class AdvancedEvaluatorAgent(EvaluatorAgent):
    """
    智能评估 Agent

    基于 LLM 进行 7 维度深度评估
    """

    def __init__(self, name: str, config=None):
        super().__init__(
            name,
            config,
            dimensions=[dim.value for dim in EvaluationDimension]
        )
        self.model = SevenDimensionModel()
        self._model_agent = None

    def initialize(self) -> None:
        """初始化 AgentScope 集成"""
        agentscope.init(
            model_configs=[{
                "model_name": "deepseek-chat",
                "temperature": 0.3,  # 评估需要更稳定
            }]
        )
        self._model_agent = agentscope.agents.ModelAgent(
            name=self.name,
            model_name="deepseek-chat",
            sys_prompt=self._build_evaluator_prompt(),
        )

    def evaluate(self, dialogue_history: List[Message]) -> EvaluationResult:
        """评估对话"""
        if not self._model_agent:
            self.initialize()

        # 构建评估请求
        eval_prompt = self._build_evaluation_prompt(dialogue_history)

        # 调用 LLM 进行评估
        response = self._model_agent(eval_prompt)

        # 解析评估结果
        dimension_scores = self._parse_dimension_scores(response)
        overall_score = self.model.calculate_overall_score(dimension_scores)
        level = self.model.get_level(overall_score)

        # 生成优势、劣势和建议
        strengths = self._identify_strengths(dimension_scores)
        weaknesses = self._identify_weaknesses(dimension_scores)
        suggestions = self._generate_suggestions(weaknesses)

        return EvaluationResult(
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            level=level,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            timestamp=datetime.now().isoformat()
        )

    def _build_evaluator_prompt(self) -> str:
        """构建评估器系统提示词"""
        return """你是一位专业的面试评估专家，擅长从 7 个维度评估面试表现：

1. 内容质量 (20%) - 回答内容的相关性和深度
2. 表达清晰度 (15%) - 语言表达的清晰程度
3. 专业知识 (20%) - 专业知识掌握程度
4. 应变能力 (15%) - 面对追问的反应能力
5. 沟通技巧 (10%) - 沟通表达的技巧性
6. 自信程度 (10%) - 表现出的自信水平
7. 创新思维 (10%) - 思考的创新性和独特性

请根据对话历史，对每个维度进行 1-5 分的评分，并提供具体的评估理由。
输出格式为 JSON：
{
    "dimension_scores": {
        "content_quality": 4.2,
        "expression_clarity": 3.8,
        ...
    },
    "strengths": ["优势 1", "优势 2"],
    "weaknesses": ["劣势 1", "劣势 2"],
    "suggestions": ["建议 1", "建议 2"]
}"""

    def _build_evaluation_prompt(self, history: List[Message]) -> str:
        """构建评估请求"""
        dialogue_text = "\n".join([
            f"{msg.role}: {msg.content}" for msg in history
        ])
        return f"""请评估以下面试对话：

{dialogue_text}

请按照 7 维度模型进行评分。"""
```

---

### 3. 反馈报告生成器 (`evaluation/report_generator.py`)

```python
# evaluation/report_generator.py
from evaluation.dimensions import EvaluationResult
from typing import List
import json

class ReportGenerator:
    """反馈报告生成器"""

    def __init__(self):
        self.template = self._load_template()

    def generate_report(self, result: EvaluationResult) -> str:
        """生成反馈报告"""
        report = {
            "header": self._generate_header(result),
            "overall_assessment": self._generate_overall(result),
            "dimension_analysis": self._generate_dimension_analysis(result),
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "suggestions": result.suggestions,
            "action_plan": self._generate_action_plan(result),
        }
        return self._format_report(report)

    def _generate_header(self, result: EvaluationResult) -> dict:
        """生成报告头部"""
        return {
            "title": "面试表现评估报告",
            "overall_score": result.overall_score,
            "level": result.level,
            "timestamp": result.timestamp,
        }

    def _generate_overall(self, result: EvaluationResult) -> str:
        """生成总体评价"""
        level_comments = {
            "优秀": "表现出色，超出预期！",
            "良好": "表现稳定，达到预期。",
            "合格": "基本达标，仍有提升空间。",
            "待改进": "未达预期，需要加强练习。",
            "不足": "明显不足，建议系统训练。",
        }
        return level_comments.get(result.level, "")

    def _generate_dimension_analysis(self, result: EvaluationResult) -> List[dict]:
        """生成维度分析"""
        analysis = []
        for dim, score in result.dimension_scores.items():
            analysis.append({
                "dimension": dim,
                "score": score,
                "level": SevenDimensionModel().get_level(score),
            })
        return analysis

    def _generate_action_plan(self, result: EvaluationResult) -> List[dict]:
        """生成行动计划"""
        plan = []
        for weakness in result.weaknesses[:3]:  # 最多 3 个重点改进项
            plan.append({
                "focus": weakness,
                "action": f"针对{weakness}进行专项练习",
                "timeline": "1-2 周",
            })
        return plan

    def _format_report(self, report: dict) -> str:
        """格式化报告输出"""
        # 支持多种格式：Markdown、JSON、HTML
        return json.dumps(report, ensure_ascii=False, indent=2)
```

---

### 4. 改进建议库 (`evaluation/suggestion_bank.py`)

```python
# evaluation/suggestion_bank.py
from typing import List, Dict
import yaml

class SuggestionBank:
    """改进建议库"""

    def __init__(self):
        self.suggestions = self._load_suggestions()

    def _load_suggestions(self) -> Dict[str, List[str]]:
        """加载建议库"""
        return {
            "content_quality": [
                "回答时多使用具体案例支撑观点",
                "采用 STAR 法则（情境、任务、行动、结果）组织回答",
                "提前准备常见问题的回答框架",
                "增加行业知识和前沿技术的了解",
                # ... 更多建议
            ],
            "expression_clarity": [
                "练习结构化表达：总 - 分-总",
                "控制语速，确保表达清晰",
                "使用连接词增强逻辑性",
                "录音回听，发现表达问题",
                # ... 更多建议
            ],
            "professional_knowledge": [
                "系统复习专业基础知识",
                "关注行业最新动态和技术趋势",
                "深入理解常用技术方案的原理",
                "准备技术深度问题的回答",
                # ... 更多建议
            ],
            "adaptability": [
                "练习即兴回答能力",
                "模拟压力面试场景",
                "学习快速组织思路的技巧",
                "培养多角度思考问题的习惯",
                # ... 更多建议
            ],
            "communication_skill": [
                "练习主动倾听技巧",
                "学习有效提问的方法",
                "注意非语言沟通（眼神、姿态）",
                "培养互动意识，避免单向输出",
                # ... 更多建议
            ],
            "confidence_level": [
                "充分准备，增强底气",
                "练习积极的自我暗示",
                "模拟面试场景脱敏",
                "关注自身优势，建立自信",
                # ... 更多建议
            ],
            "innovative_thinking": [
                "培养批判性思维习惯",
                "学习设计思维方法",
                "多接触跨领域知识",
                "练习从不同角度分析问题",
                # ... 更多建议
            ],
        }

    def get_suggestions(self, dimension: str, count: int = 3) -> List[str]:
        """获取指定维度的建议"""
        suggestions = self.suggestions.get(dimension, [])
        return suggestions[:count]

    def get_personalized_suggestions(
        self,
        dimension_scores: Dict[str, float],
        threshold: float = 3.5
    ) -> List[dict]:
        """获取个性化建议"""
        suggestions = []
        for dim, score in dimension_scores.items():
            if score < threshold:
                dim_suggestions = self.get_suggestions(dim)
                suggestions.append({
                    "dimension": dim,
                    "score": score,
                    "suggestions": dim_suggestions,
                })
        return suggestions
```

---

### 5. 评估结果存储 (`storage/evaluation_store.py`)

```python
# storage/evaluation_store.py
from evaluation.dimensions import EvaluationResult
from typing import List, Optional
import json
import os

class EvaluationStore:
    """评估结果存储"""

    def __init__(self, storage_path: str = "./data/evaluations"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def save(self, user_id: str, result: EvaluationResult) -> str:
        """保存评估结果"""
        filename = f"{user_id}_{result.timestamp}.json"
        filepath = os.path.join(self.storage_path, filename)

        data = {
            "user_id": user_id,
            "overall_score": result.overall_score,
            "level": result.level,
            "dimension_scores": result.dimension_scores,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "suggestions": result.suggestions,
            "timestamp": result.timestamp,
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def load_history(self, user_id: str) -> List[EvaluationResult]:
        """加载用户历史评估"""
        results = []
        for filename in os.listdir(self.storage_path):
            if filename.startswith(user_id):
                filepath = os.path.join(self.storage_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append(EvaluationResult(**data))
        return sorted(results, key=lambda x: x.timestamp, reverse=True)

    def get_progress(self, user_id: str) -> dict:
        """获取用户进步情况"""
        history = self.load_history(user_id)
        if len(history) < 2:
            return {"message": "评估记录不足，无法计算进步情况"}

        first_score = history[-1].overall_score
        latest_score = history[0].overall_score
        improvement = latest_score - first_score

        return {
            "first_score": first_score,
            "latest_score": latest_score,
            "improvement": improvement,
            "trend": "上升" if improvement > 0 else "下降" if improvement < 0 else "持平",
        }
```

---

## 📝 开发任务

| 任务 ID | 任务描述 | 负责人 | 优先级 | 预估工时 | 依赖 |
|--------|----------|--------|--------|----------|------|
| TASK-013 | 定义 7 维度评估模型 | 技术架构师 | 🔴 高 | 4h | v0.2 |
| TASK-014 | 实现内容质量评估 | 研发工程师 | 🔴 高 | 8h | TASK-013 |
| TASK-015 | 实现表达清晰度评估 | 研发工程师 | 🔴 高 | 8h | TASK-013 |
| TASK-016 | 创建反馈报告生成器 | 研发工程师 | 🔴 高 | 6h | TASK-014 |
| TASK-017 | 构建改进建议库 | 产品经理 | 🔴 高 | 8h | TASK-013 |
| TASK-018 | 实现评估结果存储 | 研发工程师 | 🔴 高 | 6h | TASK-016 |

---

## 🧪 测试示例

```python
# examples/evaluation_demo.py
from core import Config, ConfigLoader
from scenes.interview import InterviewScene
from evaluation.advanced_evaluator import AdvancedEvaluatorAgent
from evaluation.report_generator import ReportGenerator
from storage.evaluation_store import EvaluationStore

# 加载配置
config = ConfigLoader.from_yaml("config.yaml")

# 创建面试场景
scene = InterviewScene(config)
scene.initialize()

# 开始面试
manager = scene.create_manager()
scene.on_dialogue_start()
result = manager.start("你好，我准备好了")
scene.on_dialogue_end(result.context.get_history())

# 智能评估
evaluator = AdvancedEvaluatorAgent("AI 评估员", config)
evaluation_result = evaluator.evaluate(result.context.get_history())

# 生成报告
report_gen = ReportGenerator()
report = report_gen.generate_report(evaluation_result)
print(report)

# 存储结果
store = EvaluationStore()
store.save("user_001", evaluation_result)

# 查看进步情况
progress = store.get_progress("user_001")
print(progress)
```

---

## 📊 验收标准

1. ✅ 7 维度评估模型文档完成
2. ✅ 内容质量评估准确率>80%
3. ✅ 表达清晰度评估支持语言分析
4. ✅ 反馈报告生成器输出结构化报告
5. ✅ 改进建议库包含 200+ 建议
6. ✅ 评估结果支持历史查询
7. ✅ 代码测试覆盖率 > 80%

---

## 🔄 与 v0.2 的兼容性

- `EvaluationResult` 接口扩展（新增 7 维度）
- `EvaluatorAgent` 基类保持不变
- 向后兼容 v0.2 的 3 维度评估

---

## 🚀 下一步：v0.4 用户界面

v0.4 将实现：
- CLI 交互流程优化
- Web 框架搭建
- 场景选择 UI
- 对话交互界面
- 反馈报告可视化

---

**最后更新**: 2026-03-03 | **创建人**: Project Coordinator
