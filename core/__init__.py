"""
AgentScope AI Interview - Core Module

核心模块提供基础架构组件：
- Config: 配置管理系统
- BaseAgent: Agent 抽象基类
- DialogueManager: 对话流程管理器
- Message: 统一消息数据结构

版本：v0.8.0
新增功能 (v0.8):
- 语音支持模块 (Voice Support) - STT/TTS/语音质量评估/音频处理/语音回放
- VoiceInput: 语音输入 (STT) - 语音转文字，多语言支持，语音活动检测
- VoiceOutput: 语音输出 (TTS) - 文字转语音，多语音支持，播放控制
- VoiceQualityAssessor: 语音质量评估 - 发音/语速/填充词检测
- AudioProcessor: 音频处理 - 格式转换/降噪/音量标准化
- VoiceReplay: 语音回放 - 会话录制/回放/分段导航/速度控制
- VoiceSettings: 语音设置 - CLI/Web 设置界面，配置管理

v0.7 功能:
- 数据分析模块 (Analytics) - 学习分析、行为追踪、推荐引擎
- 统计引擎 (Statistics) - 高级统计、百分位数、分布分析
- 洞察仪表盘 (Insights) - 关键洞察、成就系统
- 数据导出 (Export) - PDF/Excel/JSON 导出、备份恢复

v0.6 功能:
- 用户系统 (Users) - 用户管理、认证
- 进度追踪 (Progress) - 学习进度、指标统计
- 数据可视化 (Visualization) - 雷达图、趋势图
- 历史回放 (History) - 会话回放、笔记
- 用户仪表盘 (Dashboard) - CLI/Web 仪表盘

v0.5 功能:
- 多场景支持 (沙龙、会议)
- 场景管理器 (SceneManager)
- 场景专用评估器
- 场景切换和状态保持

v0.4 功能:
- 场景系统 (Scenes)
- 增强面试官 Agent
- 三维度评估系统
- CLI 界面 (Rich)
- Web 界面 (FastAPI)
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

__version__ = "0.8.0"

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
# v0.7 Analytics Module (Data Tracking & Insights)
# =============================================================================

# =============================================================================
# v0.2 扩展模块导出 (延迟导入，避免循环依赖)
# 使用方式：from core import scenes, evaluation
# =============================================================================

def __getattr__(name: str):
    """延迟导入 v0.2, v0.7 和 v0.8 模块"""
    # v0.8 Voice Module
    if name == "voice":
        import voice
        return voice
    elif name == "VoiceInput":
        from voice import VoiceInput
        return VoiceInput
    elif name == "VoiceOutput":
        from voice import VoiceOutput
        return VoiceOutput
    elif name == "VoiceQualityAssessor":
        from voice import VoiceQualityAssessor
        return VoiceQualityAssessor
    elif name == "AudioProcessor":
        from voice import AudioProcessor
        return AudioProcessor
    elif name == "VoiceReplay":
        from voice import VoiceReplay
        return VoiceReplay
    elif name == "VoiceSettingsManager":
        from voice import VoiceSettingsManager
        return VoiceSettingsManager
    # v0.7 Analytics Module
    elif name == "analytics":
        import analytics
        return analytics
    elif name == "LearningAnalytics":
        from analytics import LearningAnalytics
        return LearningAnalytics
    elif name == "BehaviorTracker":
        from analytics import BehaviorTracker
        return BehaviorTracker
    elif name == "RecommendationEngine":
        from analytics import RecommendationEngine
        return RecommendationEngine
    elif name == "StatisticsEngine":
        from analytics import StatisticsEngine
        return StatisticsEngine
    elif name == "InsightsDashboard":
        from analytics import InsightsDashboard
        return InsightsDashboard
    elif name == "DataExporter":
        from analytics import DataExporter
        return DataExporter
    # v0.2 Scenes and Evaluation Module
    elif name == "scenes":
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
