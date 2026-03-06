"""
Agent Module - Agent 模块

定义系统中所有 Agent 类型的基类和具体实现。
遵循 SOLID 原则，支持通过继承扩展新的 Agent 类型。

核心类:
- BaseAgent: 所有 Agent 的抽象基类
- InterviewerAgent: 面试官 Agent
- ObserverAgent: 观察者 Agent  
- EvaluatorAgent: 评估 Agent
- Message: 统一消息数据结构
"""

import uuid
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .config import Config


class MessageType(Enum):
    """消息类型枚举"""
    USER = "user"           # 用户消息
    AGENT = "agent"         # Agent 消息
    SYSTEM = "system"       # 系统消息
    EVALUATION = "evaluation"  # 评估消息


@dataclass
class Message:
    """
    统一消息数据结构
    
    用于在 Agent 之间传递信息，携带完整的元数据。
    
    Attributes:
        content: 消息内容
        role: 发送者角色名
        type: 消息类型
        timestamp: 时间戳
        metadata: 额外元数据
    """
    content: str
    role: str
    type: MessageType = MessageType.AGENT
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建"""
        return cls(
            content=data["content"],
            role=data["role"],
            type=MessageType(data.get("type", "agent")),
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
            id=data.get("id", str(uuid.uuid4())),
        )
    
    def __str__(self) -> str:
        return f"[{self.role}]: {self.content}"


@dataclass
class DialogueContext:
    """
    对话上下文

    保存对话历史和相关状态信息。

    Attributes:
        messages: 消息历史列表
        metadata: 上下文元数据
        session_id: 会话唯一标识
    """
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def add_message(self, message: Message) -> None:
        """添加消息到历史"""
        self.messages.append(message)
    
    def get_history(self, limit: Optional[int] = None) -> List[Message]:
        """
        获取消息历史
        
        Args:
            limit: 限制返回数量，None 表示全部
            
        Returns:
            消息历史列表
        """
        if limit is None:
            return self.messages.copy()
        return self.messages[-limit:]
    
    def get_turn_count(self) -> int:
        """获取对话轮数"""
        return len(self.messages)
    
    def get_last_message(self) -> Optional[Message]:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None
    
    def clear(self) -> None:
        """清空上下文"""
        self.messages.clear()
        self.metadata.clear()
    
    def to_agent_scope_messages(self) -> List[Dict[str, str]]:
        """
        转换为 AgentScope 消息格式
        
        Returns:
            AgentScope 兼容的消息列表
        """
        result = []
        for msg in self.messages:
            if msg.type == MessageType.USER:
                result.append({"role": "user", "content": msg.content})
            else:
                result.append({"role": "assistant", "content": msg.content})
        return result


class BaseAgent(ABC):
    """
    Agent 抽象基类
    
    所有 Agent 类型必须继承此类并实现抽象方法。
    遵循依赖倒置原则，高层模块依赖此抽象而非具体实现。
    
    Attributes:
        name: Agent 名称
        config: 配置对象
    """
    
    def __init__(self, name: str, config: Optional[Config] = None):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
            config: 配置对象
        """
        self.name = name
        self.config = config or Config()
        self._initialized = False
    
    @abstractmethod
    def respond(self, message: Message, context: DialogueContext) -> Message:
        """
        响应消息
        
        Args:
            message: 输入消息
            context: 对话上下文
            
        Returns:
            响应消息
        """
        pass
    
    @abstractmethod
    def get_role(self) -> str:
        """
        获取 Agent 角色描述
        
        Returns:
            角色描述字符串
        """
        pass
    
    def initialize(self) -> None:
        """
        初始化 Agent
        
        子类可重写此方法进行初始化操作
        """
        self._initialized = True
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized
    
    def _build_system_prompt(self) -> str:
        """
        构建系统提示词
        
        子类可重写此方法自定义提示词
        
        Returns:
            系统提示词字符串
        """
        return f"You are {self.name}. {self.get_role()}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class InterviewerAgent(BaseAgent):
    """
    面试官 Agent
    
    模拟面试官行为，负责提问和评估候选人回答。
    
    Attributes:
        style: 面试风格 (friendly/strict/pressure)
        domain: 面试领域 (tech/hr/management)
    """
    
    def __init__(
        self,
        name: str = "面试官",
        config: Optional[Config] = None,
        style: str = "friendly",
        domain: str = "general",
    ):
        super().__init__(name, config)
        self.style = style
        self.domain = domain
    
    def respond(self, message: Message, context: DialogueContext) -> Message:
        """
        响应候选人的回答
        
        根据上下文和候选人回答生成下一个问题或反馈。
        """
        # v0.1 简单实现，v0.2 将集成 AgentScope
        history = context.get_history()
        
        if len(history) == 0:
            # 第一轮：开场白
            content = self._get_opening_question()
        else:
            # 后续轮次：基于回答追问
            content = self._generate_follow_up(message, context)
        
        return Message(
            content=content,
            role=self.name,
            type=MessageType.AGENT,
            metadata={
                "style": self.style,
                "domain": self.domain,
            }
        )
    
    def get_role(self) -> str:
        """获取角色描述"""
        style_descriptions = {
            "friendly": "友好鼓励型",
            "strict": "严格专业型",
            "pressure": "压力测试型",
        }
        style_desc = style_descriptions.get(self.style, "专业型")
        return f"{style_desc}面试官，专注于{self.domain}领域面试"
    
    def generate_question(self, topic: Optional[str] = None) -> str:
        """
        生成面试问题
        
        Args:
            topic: 可选的话题
            
        Returns:
            面试问题
        """
        if topic:
            return f"请谈谈你对{topic}的理解？"
        return "能介绍一下你最近做的项目吗？"
    
    def _get_opening_question(self) -> str:
        """获取开场问题"""
        openings = {
            "friendly": "你好！很高兴今天能和你交流。先简单介绍一下自己吧？",
            "strict": "你好，我是今天的面试官。请直接介绍一下你的技术背景。",
            "pressure": "时间有限，我们直接开始。说说你最有挑战的项目。",
        }
        return openings.get(self.style, openings["friendly"])
    
    def _generate_follow_up(
        self,
        message: Message,
        context: DialogueContext,
    ) -> str:
        """生成追问"""
        # v0.1 简单实现
        follow_ups = [
            "能详细说说吗？",
            "这个方案有什么优缺点？",
            "如果让你重新设计，你会做什么改进？",
            "遇到过什么技术难点？怎么解决的？",
        ]
        import random
        return random.choice(follow_ups)


class ObserverAgent(BaseAgent):
    """
    观察者 Agent
    
    观察对话过程，记录关键点和模式，不参与直接对话。
    
    Attributes:
        focus_areas: 关注领域列表
    """
    
    def __init__(
        self,
        name: str = "观察者",
        config: Optional[Config] = None,
        focus_areas: Optional[List[str]] = None,
    ):
        super().__init__(name, config)
        self.focus_areas = focus_areas or ["communication", "technical_depth"]
        self._observations: List[Dict[str, Any]] = []
    
    def respond(self, message: Message, context: DialogueContext) -> Message:
        """
        观察者不直接响应，而是记录观察
        
        Returns:
            空消息或观察摘要
        """
        observation = {
            "turn": context.get_turn_count(),
            "message": message.content[:100],  # 摘要
            "timestamp": message.timestamp,
        }
        self._observations.append(observation)
        
        return Message(
            content="[Observer] 记录观察点",
            role=self.name,
            type=MessageType.SYSTEM,
            metadata={"observation_count": len(self._observations)},
        )
    
    def get_role(self) -> str:
        """获取角色描述"""
        return "对话观察者，记录关键交流模式和技术深度"
    
    def get_observations(self) -> List[Dict[str, Any]]:
        """获取所有观察记录"""
        return self._observations.copy()
    
    def get_summary(self) -> str:
        """获取观察摘要"""
        if not self._observations:
            return "暂无观察记录"
        
        return f"共记录 {len(self._observations)} 个观察点"


class EvaluatorAgent(BaseAgent):
    """
    评估 Agent
    
    对对话过程进行评估，生成反馈报告。
    
    Attributes:
        dimensions: 评估维度列表
    """
    
    def __init__(
        self,
        name: str = "评估员",
        config: Optional[Config] = None,
        dimensions: Optional[List[str]] = None,
    ):
        super().__init__(name, config)
        self.dimensions = dimensions or [
            "content_quality",
            "expression_clarity",
            "professional_knowledge",
        ]
    
    def respond(self, message: Message, context: DialogueContext) -> Message:
        """
        评估 Agent 不直接参与对话
        
        此方法主要用于接口兼容性
        """
        return Message(
            content="[Evaluator] 等待对话结束进行评估",
            role=self.name,
            type=MessageType.SYSTEM,
        )
    
    def get_role(self) -> str:
        """获取角色描述"""
        return f"对话评估员，从{len(self.dimensions)}个维度进行评估"
    
    def evaluate(
        self,
        dialogue_history: List[Message],
    ) -> "EvaluationResult":
        """
        评估对话历史
        
        Args:
            dialogue_history: 完整的对话历史
            
        Returns:
            评估结果对象
        """
        # v0.1 简单实现，v0.3 将实现完整评估逻辑
        scores = {}
        for dim in self.dimensions:
            # 模拟评分
            import random
            scores[dim] = round(random.uniform(3.0, 5.0), 1)
        
        return EvaluationResult(
            scores=scores,
            dialogue_length=len(dialogue_history),
        )


@dataclass
class EvaluationResult:
    """
    评估结果
    
    Attributes:
        scores: 各维度评分
        dialogue_length: 对话长度
        suggestions: 改进建议
    """
    scores: Dict[str, float]
    dialogue_length: int
    suggestions: List[str] = field(default_factory=list)
    
    def get_overall_score(self) -> float:
        """计算总体评分"""
        if not self.scores:
            return 0.0
        return round(sum(self.scores.values()) / len(self.scores), 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "overall_score": self.get_overall_score(),
            "dimension_scores": self.scores,
            "dialogue_length": self.dialogue_length,
            "suggestions": self.suggestions,
        }
    
    def __str__(self) -> str:
        lines = [f"总体评分：{self.get_overall_score()}/5.0"]
        lines.append("维度评分:")
        for dim, score in self.scores.items():
            lines.append(f"  - {dim}: {score}")
        if self.suggestions:
            lines.append("改进建议:")
            for sug in self.suggestions:
                lines.append(f"  - {sug}")
        return "\n".join(lines)
