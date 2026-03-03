# AgentScope AI Interview

> AI 模拟对话平台 - 基于 AgentScope 框架的多智能体对话模拟系统

## 📋 项目概述

AgentScope AI Interview 是一个专业的 AI 对话模拟训练平台，通过多智能体协作模拟真实职场对话场景，帮助用户提升沟通技能、面试技巧和社交能力。

### 核心特性

- 🤖 **多 Agent 协作** - 支持面试官、观察者、评估员等多种角色
- 📝 **配置驱动** - YAML 配置文件定义场景和 Agent 行为
- 🔌 **可扩展架构** - 基于抽象基类，轻松扩展新场景和 Agent 类型
- 📊 **智能评估** - 多维度对话质量评估和反馈

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
├─────────────────────────────────────────────────────────┤
│                  Dialogue Manager                        │
├─────────────────────────────────────────────────────────┤
│   InterviewerAgent  │  ObserverAgent  │  EvaluatorAgent │
├─────────────────────────────────────────────────────────┤
│                  AgentScope Framework                    │
├─────────────────────────────────────────────────────────┤
│                   Model Adapter Layer                    │
└─────────────────────────────────────────────────────────┘
```

## 📦 项目结构

```
agentscope_ai_interview/
├── core/
│   ├── __init__.py           # 模块导出
│   ├── config.py             # 配置系统
│   ├── agent.py              # Agent 基类和实现
│   └── dialogue_manager.py   # 对话管理器
├── examples/
│   ├── basic_conversation.py # CLI 测试示例
│   └── config.example.yaml   # 配置示例
├── requirements.txt          # 依赖列表
└── README.md                 # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行示例

```bash
# 交互模式
python examples/basic_conversation.py

# 自动测试模式
python examples/basic_conversation.py --auto
```

### 配置说明

复制示例配置文件并根据需要修改：

```bash
cp examples/config.example.yaml config.yaml
```

主要配置项：

```yaml
model:
  name: "deepseek-chat"
  temperature: 0.7

dialogue:
  max_turns: 10

agent:
  interviewer:
    style: "friendly"  # friendly/strict/pressure
    domain: "general"
```

## 📚 核心模块

### Config - 配置系统

```python
from core import Config, ConfigLoader

# 从 YAML 加载
config = ConfigLoader.from_yaml("config.yaml")

# 从字典创建
config = ConfigLoader.from_dict({"model": {"name": "deepseek"}})

# 访问配置
model_name = config.get("model.name")
```

### Agent - Agent 模块

```python
from core import InterviewerAgent, ObserverAgent, EvaluatorAgent

# 创建面试官
interviewer = InterviewerAgent(
    name="张面试官",
    style="friendly",
    domain="tech",
)

# 创建观察者
observer = ObserverAgent(
    name="AI 观察者",
    focus_areas=["communication"],
)

# 创建评估员
evaluator = EvaluatorAgent(
    name="AI 评估员",
    dimensions=["content_quality", "expression_clarity"],
)
```

### DialogueManager - 对话管理器

```python
from core import DialogueManager, DialogueManagerBuilder

# 创建管理器
manager = (
    DialogueManagerBuilder()
    .with_config(config)
    .add_agent(interviewer)
    .add_agent(evaluator)
    .build()
)

# 开始对话
result = manager.start("你好，我准备好了")

# 打印历史
manager.print_history()
```

## 🔧 开发指南

### 扩展新 Agent 类型

```python
from core import BaseAgent, Message, DialogueContext

class ModeratorAgent(BaseAgent):
    """主持人 Agent - 用于会议场景"""
    
    def respond(self, message: Message, context: DialogueContext) -> Message:
        # 实现响应逻辑
        return Message(content="...", role=self.name)
    
    def get_role(self) -> str:
        return "会议主持人"
```

### 扩展新场景 (v0.2)

```python
class BaseScene:
    def initialize(self, config: Config) -> None:
        pass
    
    def get_agents(self) -> List[BaseAgent]:
        pass
```

## 📋 版本规划

| 版本 | 状态 | 核心目标 |
|------|------|----------|
| v0.1 | ✅ 完成 | 核心框架搭建 |
| v0.2 | 🔄 计划 | 基础面试场景 |
| v0.3 | 📅 计划 | 智能反馈系统 |
| v0.4 | 📅 计划 | 用户界面 |

## 📝 提交规范

本项目遵循 Conventional Commits 规范：

```
feat(core): 添加新功能
fix(agent): 修复 Agent 响应问题
docs(readme): 更新文档
test(examples): 添加测试示例
```

## 📄 License

MIT License

## 👥 团队

- 技术架构师：Software Architect
- 产品经理：Product Manager
- 开发团队：Development Team

---

**注意**: v0.1 版本为核心框架 MVP，仅提供基础对话功能。完整的面试场景、智能评估等功能将在后续版本中实现。
