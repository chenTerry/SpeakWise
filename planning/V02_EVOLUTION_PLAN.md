# v0.2 演进计划 - 基础面试场景

## 📋 版本概述

| 项目 | 内容 |
|------|------|
| **版本号** | v0.2 |
| **目标** | 实现基础面试场景 MVP |
| **预计完成** | 2024-03-17 |
| **依赖** | v0.1 核心框架 |

---

## 🎯 核心目标

在 v0.1 核心框架基础上，实现完整的面试场景功能：

1. **面试场景定义** - 场景基类和面试场景实现
2. **面试官 Agent 增强** - 集成 AgentScope，支持多种面试风格
3. **问题库系统** - 结构化面试问题管理
4. **用户代理接口** - 处理用户输入和上下文
5. **基础评估指标** - 3 维度评分系统

---

## 🏗️ 架构扩展

### 新增模块结构

```
project/
├── core/                      # v0.1 已有
│   ├── config.py
│   ├── agent.py
│   └── dialogue_manager.py
├── scenes/                    # v0.2 新增
│   ├── __init__.py
│   ├── base.py              # 场景基类
│   └── interview/           # 面试场景
│       ├── __init__.py
│       ├── scene.py         # 面试场景实现
│       ├── interviewer.py   # 增强面试官
│       └── questions.yaml   # 问题库
├── evaluation/                # v0.2 新增
│   ├── __init__.py
│   └── basic_evaluator.py   # 基础评估器
└── examples/
    └── interview_demo.py    # 面试场景示例
```

---

## 📦 模块详细设计

### 1. 场景系统 (`scenes/`)

#### 1.1 场景抽象基类

```python
# scenes/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core import Config, BaseAgent, DialogueManager

class BaseScene(ABC):
    """场景抽象基类"""
    
    def __init__(self, name: str, config: Config):
        self.name = name
        self.config = config
        self.agents: List[BaseAgent] = []
        self.manager: Optional[DialogueManager] = None
    
    @abstractmethod
    def initialize(self) -> None:
        """初始化场景"""
        pass
    
    @abstractmethod
    def get_agents(self) -> List[BaseAgent]:
        """获取场景所需的所有 Agent"""
        pass
    
    @abstractmethod
    def on_dialogue_start(self) -> None:
        """对话开始回调"""
        pass
    
    @abstractmethod
    def on_dialogue_end(self, history: List) -> None:
        """对话结束回调"""
        pass
    
    def create_manager(self) -> DialogueManager:
        """创建对话管理器"""
        return DialogueManager(
            agents=self.get_agents(),
            config=self.config
        )
```

#### 1.2 面试场景实现

```python
# scenes/interview/scene.py
from scenes.base import BaseScene
from scenes.interview.interviewer import AdvancedInterviewerAgent
from evaluation.basic_evaluator import BasicEvaluatorAgent

class InterviewScene(BaseScene):
    """面试场景"""
    
    def __init__(self, config: Config):
        super().__init__("interview", config)
        self.style = config.get("agent.interviewer.style", "friendly")
        self.domain = config.get("agent.interviewer.domain", "general")
    
    def initialize(self) -> None:
        # 创建面试官
        interviewer = AdvancedInterviewerAgent(
            name=self.config.get("agent.interviewer.name", "面试官"),
            config=self.config,
            style=self.style,
            domain=self.domain,
        )
        
        # 创建评估员
        evaluator = BasicEvaluatorAgent(
            name="AI 评估员",
            config=self.config,
        )
        
        self.agents = [interviewer, evaluator]
    
    def get_agents(self) -> List[BaseAgent]:
        return self.agents
    
    def on_dialogue_start(self) -> None:
        print(f"🎯 {self.name} 场景开始")
        print(f"面试官风格：{self.style}")
        print(f"面试领域：{self.domain}")
    
    def on_dialogue_end(self, history: List) -> None:
        print(f"✅ 面试结束，共 {len(history)} 轮对话")
```

---

### 2. 增强面试官 Agent (`scenes/interview/interviewer.py`)

```python
from core import InterviewerAgent, Message, DialogueContext, Config
import agentscope
from agentscope.agents import ModelAgent

class AdvancedInterviewerAgent(InterviewerAgent):
    """
    增强面试官 Agent
    
    集成 AgentScope 框架，支持：
    - 真实 LLM 调用
    - 问题库管理
    - 多风格切换
    """
    
    def __init__(
        self,
        name: str,
        config: Config,
        style: str = "friendly",
        domain: str = "general",
    ):
        super().__init__(name, config, style, domain)
        
        # 加载问题库
        self.question_bank = self._load_question_bank()
        
        # 初始化 AgentScope ModelAgent
        self._model_agent = None
    
    def initialize(self) -> None:
        """初始化 AgentScope 集成"""
        super().initialize()
        
        # 配置 AgentScope
        agentscope.init(
            model_configs=[{
                "model_name": self.config.get("model.name"),
                "temperature": self.config.get("model.temperature", 0.7),
            }]
        )
        
        # 创建内部 Agent
        self._model_agent = ModelAgent(
            name=self.name,
            model_name=self.config.get("model.name"),
            sys_prompt=self._build_system_prompt(),
        )
    
    def respond(self, message: Message, context: DialogueContext) -> Message:
        """使用 AgentScope 生成响应"""
        if not self._model_agent:
            # Fallback 到基础实现
            return super().respond(message, context)
        
        # 转换上下文为 AgentScope 格式
        messages = context.to_agent_scope_messages()
        
        # 调用 AgentScope
        response = self._model_agent(messages)
        
        return Message(
            content=response.content,
            role=self.name,
            metadata={
                "style": self.style,
                "domain": self.domain,
                "source": "agentscope",
            }
        )
    
    def _load_question_bank(self) -> Dict[str, List[str]]:
        """加载问题库"""
        # 从 YAML 文件加载
        # v0.2 实现
        return {}
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        style_prompts = {
            "friendly": "你是一位友好鼓励型的面试官，善于引导候选人展示能力。",
            "strict": "你是一位严格专业的面试官，注重技术深度和准确性。",
            "pressure": "你是一位压力测试型面试官，会挑战候选人的答案。",
        }
        
        return f"""你是一位经验丰富的{self.domain}领域面试官。
{style_prompts.get(self.style, style_prompts['friendly'])}

你的任务：
1. 提出专业且有深度的问题
2. 根据候选人回答进行追问
3. 保持面试流程的专业性和流畅性
4. 在适当时给予反馈和鼓励"""
```

---

### 3. 问题库系统 (`scenes/interview/questions.yaml`)

```yaml
# 技术问题库
technical:
  general:
    - "请介绍一下你最近做的项目？"
    - "你在项目中遇到的最大挑战是什么？"
    - "你是如何解决这个技术难题的？"
  
  system_design:
    - "请设计一个高并发的秒杀系统"
    - "如何设计一个分布式 ID 生成器？"
    - "微服务架构的优缺点是什么？"
  
  coding:
    - "实现一个 LRU Cache"
    - "反转二叉树"
    - "两数之和"

# HR 问题库
hr:
  behavioral:
    - "说说你的优点和缺点"
    - "你为什么选择我们公司？"
    - "你的职业规划是什么？"
  
  situational:
    - "如果和同事意见不合怎么办？"
    - "如何在压力下工作？"
    - "描述一次你领导团队的经历"

# 评估标准
evaluation_criteria:
  content_quality:
    weight: 0.4
    description: "回答内容的相关性和深度"
  
  expression_clarity:
    weight: 0.35
    description: "语言表达的清晰度"
  
  professional_knowledge:
    weight: 0.25
    description: "专业知识掌握程度"
```

---

### 4. 基础评估器 (`evaluation/basic_evaluator.py`)

```python
# evaluation/basic_evaluator.py
from core import EvaluatorAgent, Message, EvaluationResult, DialogueContext
from typing import List, Dict

class BasicEvaluatorAgent(EvaluatorAgent):
    """
    基础评估 Agent
    
    实现 3 维度评估：
    - 内容质量 (40%)
    - 表达清晰度 (35%)
    - 专业知识 (25%)
    """
    
    def __init__(self, name: str, config: Config = None):
        super().__init__(
            name,
            config,
            dimensions=[
                "content_quality",
                "expression_clarity",
                "professional_knowledge",
            ]
        )
        
        self.weights = {
            "content_quality": 0.4,
            "expression_clarity": 0.35,
            "professional_knowledge": 0.25,
        }
    
    def evaluate(self, dialogue_history: List[Message]) -> EvaluationResult:
        """评估对话"""
        scores = {}
        suggestions = []
        
        # v0.2 简单实现，v0.3 使用 LLM 评估
        for dim in self.dimensions:
            scores[dim] = self._evaluate_dimension(dim, dialogue_history)
        
        # 生成建议
        if scores["content_quality"] < 3.5:
            suggestions.append("建议增加具体案例支撑观点")
        if scores["expression_clarity"] < 3.5:
            suggestions.append("注意结构化表达，使用 STAR 法则")
        if scores["professional_knowledge"] < 3.5:
            suggestions.append("加强基础知识复习")
        
        return EvaluationResult(
            scores=scores,
            dialogue_length=len(dialogue_history),
            suggestions=suggestions,
        )
    
    def _evaluate_dimension(
        self,
        dimension: str,
        history: List[Message],
    ) -> float:
        """评估单个维度"""
        # v0.2 简单实现
        # v0.3 使用 LLM 进行智能评估
        import random
        return round(random.uniform(3.0, 5.0), 1)
```

---

## 📝 开发任务

| 任务 ID | 任务描述 | 预估工时 | 依赖 |
|--------|----------|----------|------|
| TASK-007 | 设计面试场景结构 | 4h | v0.1 |
| TASK-008 | 实现面试官 Agent 增强 | 12h | TASK-007 |
| TASK-009 | 构建技术问题库 | 8h | TASK-007 |
| TASK-010 | 实现基础评估器 | 10h | TASK-008 |
| TASK-011 | 创建场景切换机制 | 6h | TASK-007 |
| TASK-012 | 集成测试 | 8h | TASK-010 |

---

## 🧪 测试示例

```python
# examples/interview_demo.py
from core import Config, ConfigLoader
from scenes.interview import InterviewScene

# 加载配置
config = ConfigLoader.from_yaml("config.yaml")

# 创建面试场景
scene = InterviewScene(config)
scene.initialize()

# 创建管理器
manager = scene.create_manager()

# 开始面试
scene.on_dialogue_start()
result = manager.start("你好，我准备好了")
scene.on_dialogue_end(result.context.get_history())

# 显示结果
manager.print_history()
print(result.evaluation)
```

---

## 🔄 与 v0.1 的兼容性

v0.2 完全兼容 v0.1 的接口：

- `DialogueManager` 接口不变
- `BaseAgent` 接口不变
- `Config` 接口不变

新增功能通过扩展实现，遵循开闭原则。

---

## 📊 验收标准

1. ✅ 支持 3 种面试风格（friendly/strict/pressure）
2. ✅ 问题库包含 50+ 高质量问题
3. ✅ 支持 10 轮完整对话流程
4. ✅ 评估系统输出 3 维度评分
5. ✅ 代码测试覆盖率 > 80%

---

## 🚀 下一步：v0.3 智能反馈系统

v0.3 将实现：
- 7 维度评估模型
- 基于 LLM 的智能评估
- 反馈报告生成器
- 改进建议库
