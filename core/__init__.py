"""
AgentScope AI Interview - Core Module

核心模块提供基础架构组件：
- Config: 配置管理系统
- BaseAgent: Agent 抽象基类
- DialogueManager: 对话流程管理器
- Message: 统一消息数据结构

版本：v0.2
新增功能:
- 场景系统 (Scenes)
- 增强面试官 Agent
- 三维度评估系统
"""

from .config import Config, ConfigLoader, ConfigError
from .agent import (
    BaseAgent,
    InterviewerAgent,
    ObserverAgent,
    EvaluatorAgent,
    Message,
    MessageType,
    DialogueContext,
    EvaluationResult,
)
from .dialogue_manager import (
    DialogueManager,
    DialogueContext as DMDialogueContext,
    DialogueResult,
    DialogueManagerBuilder,
)

__version__ = "0.2.0"

__all__ = [
    # Version
    "__version__",
    # Config
    "Config",
    "ConfigLoader",
    "ConfigError",
    # Agent
    "BaseAgent",
    "InterviewerAgent",
    "ObserverAgent",
    "EvaluatorAgent",
    "Message",
    "MessageType",
    "DialogueContext",
    "EvaluationResult",
    # Dialogue Manager
    "DialogueManager",
    "DMDialogueContext",
    "DialogueResult",
    "DialogueManagerBuilder",
]

# =============================================================================
# v0.2 扩展模块导出 (延迟导入，避免循环依赖)
# 使用方式：from core import scenes, evaluation
# =============================================================================

def __getattr__(name: str):
    """延迟导入 v0.2 模块"""
    if name == "scenes":
        import scenes
        return scenes
    elif name == "evaluation":
        import evaluation
        return evaluation
    elif name == "SceneRegistry":
        from scenes import SceneRegistry
        return SceneRegistry
    elif name == "InterviewScene":
        from scenes.interview import InterviewScene
        return InterviewScene
    elif name == "EnhancedInterviewerAgent":
        from scenes.interview import EnhancedInterviewerAgent
        return EnhancedInterviewerAgent
    elif name == "QuestionBank":
        from scenes.interview import QuestionBank
        return QuestionBank
    elif name == "BasicEvaluator":
        from evaluation import BasicEvaluator
        return BasicEvaluator
    elif name == "EvaluationReport":
        from evaluation import EvaluationReport
        return EvaluationReport
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
