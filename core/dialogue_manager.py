"""
Dialogue Manager - 对话管理器模块

负责管理对话流程、轮次控制、上下文跟踪和 Agent 协调。
是系统的核心编排组件。

核心类:
- DialogueManager: 对话流程管理器
- DialogueContext: 对话上下文
- DialogueResult: 对话结果
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .config import Config
from .agent import (
    BaseAgent,
    Message,
    MessageType,
    DialogueContext,
    EvaluatorAgent,
    EvaluationResult,
)


@dataclass
class DialogueResult:
    """
    对话结果
    
    包含完整的对话历史和评估结果。
    
    Attributes:
        success: 对话是否成功完成
        context: 对话上下文
        evaluation: 评估结果
        metadata: 元数据
    """
    success: bool
    context: DialogueContext
    evaluation: Optional[EvaluationResult] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "message_count": len(self.context.messages),
            "evaluation": self.evaluation.to_dict() if self.evaluation else None,
            "metadata": self.metadata,
        }


class DialogueManager:
    """
    对话管理器
    
    管理完整的对话流程，包括：
    - 初始化 Agent
    - 控制对话轮次
    - 协调 Agent 响应
    - 收集评估结果
    
    Attributes:
        agents: Agent 列表
        config: 配置对象
        context: 当前对话上下文
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        config: Optional[Config] = None,
    ):
        """
        初始化对话管理器
        
        Args:
            agents: 参与对话的 Agent 列表
            config: 配置对象
            
        Example:
            >>> manager = DialogueManager([interviewer, observer])
        """
        self.agents = agents
        self.config = config or Config()
        self.context = DialogueContext()
        self._current_turn = 0
        self._max_turns = config.get("dialogue.max_turns", 10) if config else 10
        self._is_running = False
    
    def add_agent(self, agent: BaseAgent) -> None:
        """
        添加 Agent 到对话
        
        Args:
            agent: 要添加的 Agent
        """
        self.agents.append(agent)
    
    def remove_agent(self, agent_name: str) -> bool:
        """
        移除 Agent
        
        Args:
            agent_name: Agent 名称
            
        Returns:
            是否成功移除
        """
        for i, agent in enumerate(self.agents):
            if agent.name == agent_name:
                self.agents.pop(i)
                return True
        return False
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        根据名称获取 Agent
        
        Args:
            name: Agent 名称
            
        Returns:
            Agent 对象或 None
        """
        for agent in self.agents:
            if agent.name == name:
                return agent
        return None
    
    def initialize(self) -> None:
        """初始化所有 Agent"""
        for agent in self.agents:
            if not agent.is_initialized():
                agent.initialize()
    
    def start(self, user_message: Optional[str] = None) -> DialogueResult:
        """
        开始对话
        
        Args:
            user_message: 可选的初始用户消息
            
        Returns:
            对话结果
            
        Example:
            >>> result = manager.start("你好，我准备好了")
        """
        self._is_running = True
        self._current_turn = 0
        self.context.clear()
        
        # 初始化 Agent
        self.initialize()
        
        # 添加初始消息
        if user_message:
            self.context.add_message(Message(
                content=user_message,
                role="user",
                type=MessageType.USER,
            ))
        
        # 运行对话
        try:
            while self._should_continue():
                self._run_turn()
            
            # 对话结束，生成评估
            evaluation = self._generate_evaluation()
            
            return DialogueResult(
                success=True,
                context=self.context,
                evaluation=evaluation,
                metadata={
                    "total_turns": self._current_turn,
                    "duration_seconds": self._get_duration(),
                }
            )
        
        except Exception as e:
            return DialogueResult(
                success=False,
                context=self.context,
                metadata={"error": str(e)},
            )
        
        finally:
            self._is_running = False
    
    def run_turn(self) -> Tuple[BaseAgent, Message]:
        """
        运行单个对话轮次
        
        Returns:
            (响应 Agent, 响应消息) 的元组
            
        Raises:
            RuntimeError: 对话未开始或已结束
        """
        if not self._is_running:
            raise RuntimeError("Dialogue not started. Call start() first.")
        
        return self._run_turn()
    
    def _run_turn(self) -> Tuple[BaseAgent, Message]:
        """内部轮次运行逻辑"""
        self._current_turn += 1
        
        # 获取最后一条消息
        last_message = self.context.get_last_message()
        if not last_message:
            # 没有历史消息，由面试官开场
            last_message = Message(
                content="",
                role="system",
                type=MessageType.SYSTEM,
            )
        
        # 获取主要响应 Agent（面试官）
        interviewer = self._get_interviewer()
        if not interviewer:
            raise RuntimeError("No interviewer agent found")
        
        # 生成响应
        response = interviewer.respond(last_message, self.context)
        
        # 添加到上下文
        self.context.add_message(response)
        
        # 通知观察者
        self._notify_observers(response)
        
        return interviewer, response
    
    def send_user_message(self, content: str) -> Message:
        """
        发送用户消息
        
        Args:
            content: 用户消息内容
            
        Returns:
            添加的消息对象
        """
        message = Message(
            content=content,
            role="user",
            type=MessageType.USER,
        )
        self.context.add_message(message)
        return message
    
    def get_context(self) -> DialogueContext:
        """获取当前对话上下文"""
        return self.context
    
    def get_turn_count(self) -> int:
        """获取当前轮数"""
        return self._current_turn
    
    def is_running(self) -> bool:
        """检查对话是否正在进行"""
        return self._is_running
    
    def stop(self) -> None:
        """停止对话"""
        self._is_running = False
    
    def _should_continue(self) -> bool:
        """判断是否继续对话"""
        if not self._is_running:
            return False
        
        if self._current_turn >= self._max_turns:
            return False
        
        return True
    
    def _get_interviewer(self) -> Optional[BaseAgent]:
        """获取面试官 Agent"""
        from .agent import InterviewerAgent
        
        for agent in self.agents:
            if isinstance(agent, InterviewerAgent):
                return agent
        
        # 如果没有 InterviewerAgent，返回第一个 Agent
        return self.agents[0] if self.agents else None
    
    def _get_evaluator(self) -> Optional[EvaluatorAgent]:
        """获取评估 Agent"""
        for agent in self.agents:
            if isinstance(agent, EvaluatorAgent):
                return agent
        return None
    
    def _notify_observers(self, message: Message) -> None:
        """通知观察者 Agent"""
        from .agent import ObserverAgent
        
        for agent in self.agents:
            if isinstance(agent, ObserverAgent):
                agent.respond(message, self.context)
    
    def _generate_evaluation(self) -> Optional[EvaluationResult]:
        """生成评估结果"""
        evaluator = self._get_evaluator()
        
        if evaluator:
            return evaluator.evaluate(self.context.get_history())
        
        return None
    
    def _get_duration(self) -> float:
        """获取对话持续时间（秒）"""
        messages = self.context.get_history()
        if len(messages) < 2:
            return 0.0
        
        first_time = messages[0].timestamp
        last_time = messages[-1].timestamp
        
        return round(last_time - first_time, 2)
    
    def print_history(self) -> None:
        """打印对话历史"""
        print("\n" + "=" * 60)
        print("对话历史")
        print("=" * 60)
        
        for msg in self.context.get_history():
            role_display = {
                MessageType.USER: "👤 用户",
                MessageType.AGENT: "🤖 Agent",
                MessageType.SYSTEM: "⚙️ 系统",
                MessageType.EVALUATION: "📊 评估",
            }.get(msg.type, msg.role)
            
            print(f"\n{role_display} ({msg.role}):")
            print(f"  {msg.content}")
        
        print("=" * 60 + "\n")


class DialogueManagerBuilder:
    """
    对话管理器构建器
    
    使用构建器模式创建 DialogueManager，支持流式配置。
    
    Example:
        >>> manager = (DialogueManagerBuilder()
        ...     .with_config(config)
        ...     .add_agent(interviewer)
        ...     .add_agent(evaluator)
        ...     .build())
    """
    
    def __init__(self):
        self._agents: List[BaseAgent] = []
        self._config: Optional[Config] = None
    
    def with_config(self, config: Config) -> "DialogueManagerBuilder":
        """设置配置"""
        self._config = config
        return self
    
    def add_agent(self, agent: BaseAgent) -> "DialogueManagerBuilder":
        """添加 Agent"""
        self._agents.append(agent)
        return self
    
    def add_agents(self, agents: List[BaseAgent]) -> "DialogueManagerBuilder":
        """批量添加 Agent"""
        self._agents.extend(agents)
        return self
    
    def build(self) -> DialogueManager:
        """构建 DialogueManager"""
        return DialogueManager(self._agents, self._config)
