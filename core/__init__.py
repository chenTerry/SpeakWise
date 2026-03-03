"""
AgentScope AI Interview - Core Module

核心模块提供基础架构组件：
- Config: 配置管理系统
- BaseAgent: Agent 抽象基类
- DialogueManager: 对话流程管理器
- Message: 统一消息数据结构
"""

from .config import Config, ConfigLoader, ConfigError
from .agent import (
    BaseAgent,
    InterviewerAgent,
    ObserverAgent,
    EvaluatorAgent,
    Message,
    MessageType,
)
from .dialogue_manager import (
    DialogueManager,
    DialogueContext,
    DialogueResult,
)

__version__ = "0.1.0"

__all__ = [
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
    # Dialogue Manager
    "DialogueManager",
    "DialogueContext",
    "DialogueResult",
]
