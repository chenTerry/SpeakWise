# AgentScope AI Interview

> AI 模拟对话平台 - 基于 AgentScope 框架的多智能体对话模拟系统

**当前版本**: v0.4.0

## 📋 项目概述

AgentScope AI Interview 是一个专业的 AI 对话模拟训练平台，通过多智能体协作模拟真实职场对话场景，帮助用户提升沟通技能、面试技巧和社交能力。

### ✨ v0.4 新增特性 (User Interface)

- 💻 **CLI 命令行界面** - 基于 Rich 库的增强终端 UI，支持 5 种主题
- 🌐 **Web 网页界面** - 基于 FastAPI 的响应式 Web 应用，支持移动端
- 🎨 **主题系统** - 暗色/亮色/蓝色/绿色/Monokai 5 种主题
- 📊 **可视化反馈** - 图表化评估报告，支持 JSON/Markdown 导出
- 🔌 **RESTful API** - 完整的 API 接口，支持 WebSocket 实时通信

### v0.2 特性

- 🎭 **场景系统** - 可插拔的场景架构，支持多种面试场景
- 🎯 **增强面试官** - 3 种面试风格 (友好/严格/压力)，5 大领域支持
- 📚 **问题库** - 78+ 预置技术问题，按领域/难度/类型分类
- 📊 **三维度评估** - 内容质量、表达清晰度、专业知识全面评估

### 核心特性

- 🤖 **多 Agent 协作** - 支持面试官、观察者、评估员等多种角色
- 📝 **配置驱动** - YAML 配置文件定义场景和 Agent 行为
- 🔌 **可扩展架构** - 基于抽象基类，轻松扩展新场景和 Agent 类型
- 📊 **智能评估** - 多维度对话质量评估和反馈
- 💬 **双界面支持** - CLI 和 Web 两种交互方式

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
├─────────────────────────────────────────────────────────┤
│                  Scene System (v0.2)                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│   │InterviewScene│  │  BaseScene  │  │SceneRegistry│    │
│   └─────────────┘  └─────────────┘  └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│   EnhancedInterviewerAgent  │  QuestionBank  │  Evaluator│
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
│   ├── __init__.py           # 模块导出 (v0.2 更新)
│   ├── config.py             # 配置系统
│   ├── agent.py              # Agent 基类和实现
│   └── dialogue_manager.py   # 对话管理器
├── scenes/                    # v0.2 新增
│   ├── __init__.py
│   ├── base.py               # 场景基类
│   ├── registry.py           # 场景注册中心
│   └── interview/
│       ├── __init__.py
│       ├── scene.py          # 面试场景实现
│       ├── interviewer.py    # 增强面试官 Agent
│       └── questions.yaml    # 问题库 (78+ 问题)
├── evaluation/                # v0.2 新增
│   ├── __init__.py
│   └── basic_evaluator.py    # 三维度评估器
├── cli/                       # v0.4 新增
│   ├── __init__.py
│   ├── app.py                # CLI 主应用程序
│   ├── menus.py              # 菜单系统
│   ├── themes.py             # 主题管理
│   └── widgets.py            # UI 组件
├── web/                       # v0.4 新增
│   ├── __init__.py
│   ├── app.py                # FastAPI 应用
│   ├── config.py             # 配置管理
│   ├── routes/
│   │   ├── scenes.py         # 场景 API
│   │   ├── dialogue.py       # 对话 API
│   │   └── feedback.py       # 反馈 API
│   ├── static/
│   │   ├── css/main.css      # 样式表
│   │   └── js/app.js         # 前端逻辑
│   └── templates/            # HTML 模板
├── examples/
│   ├── basic_conversation.py # v0.1 CLI 测试
│   ├── interview_demo.py     # v0.2 面试演示
│   ├── cli_demo.py           # v0.4 CLI 演示
│   └── web_demo.py           # v0.4 Web 演示
├── tests/
│   └── test_v04_implementation.py  # v0.4 测试
├── docs/
│   ├── PRD.md                # 产品需求文档
│   ├── DETAILED_PRD.md       # 详细需求
│   └── V0_4_IMPLEMENTATION.md # v0.4 实现文档
├── planning/
│   ├── VERSION_PLAN.md       # 版本路线图
│   ├── TASK_STATUS.md        # 任务状态
│   └── V0_4_SUMMARY.md       # v0.4 总结
├── requirements.txt
└── README.md
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
# 安装所有依赖（包括 v0.4 Web 界面）
pip install -r requirements.txt

# 或仅安装 CLI 依赖
pip install rich>=13.7.0

# 或仅安装 Web 依赖
pip install fastapi>=0.104.0 uvicorn[standard]>=0.24.0 jinja2>=3.1.2
```

### 运行示例

#### CLI 模式 (v0.4)

```bash
# CLI 功能展示
python examples/cli_demo.py --features

# CLI 交互模式
python examples/cli_demo.py
```

#### Web 模式 (v0.4)

```bash
# 启动 Web 服务器
python examples/web_demo.py

# 访问浏览器
# http://127.0.0.1:8000
# API 文档：http://127.0.0.1:8000/docs
```

#### v0.2 面试场景演示

```bash
# v0.1 基础对话
python examples/basic_conversation.py

# v0.2 面试场景演示 (交互模式)
python examples/interview_demo.py

# v0.2 面试场景演示 (自动模式)
python examples/interview_demo.py --auto

# 指定面试风格和领域
python examples/interview_demo.py --style strict --domain frontend
```

### 配置说明

复制示例配置文件并根据需要修改：

```bash
cp examples/config.example.yaml config.yaml
```

主要配置项：

```yaml
# AgentScope 模型配置
agentscope:
  model_configs:
    - model_type: "dashscope"
      config_name: "deepseek"
      model_name: "deepseek-chat"
      api_key: "${DASHSCOPE_API_KEY}"

# 模型参数
model:
  name: "deepseek-chat"
  temperature: 0.7
  max_tokens: 2048

# 对话配置
dialogue:
  max_turns: 10

# Agent 配置
agent:
  interviewer:
    style: "friendly"  # friendly/strict/pressure
    domain: "tech"     # tech/frontend/backend/system_design/hr

# 评估配置 (v0.2)
evaluation:
  weights:
    content_quality: 0.35
    expression_clarity: 0.30
    professional_knowledge: 0.35
  thresholds:
    S: 4.5
    A: 4.0
    B: 3.0
    C: 2.0
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

### Scenes - 场景系统 (v0.2 新增)

```python
from scenes import SceneRegistry, InterviewScene

# 获取注册中心
registry = SceneRegistry.get_instance()

# 创建面试场景
scene = InterviewScene(
    style="friendly",
    domain="frontend",
)

# 初始化场景
scene.initialize()

# 开始面试
opening = scene.start()
print(opening.content)

# 处理对话
from core import Message, DialogueContext
user_msg = Message(content="你好", role="user")
response = scene.handle_message(user_msg, scene.get_context())
```

### EnhancedInterviewerAgent - 增强面试官 (v0.2 新增)

```python
from scenes.interview import EnhancedInterviewerAgent, QuestionBank

# 创建问题库
question_bank = QuestionBank()
question_bank.load_from_yaml("scenes/interview/questions.yaml")

# 创建面试官
interviewer = EnhancedInterviewerAgent(
    name="张面试官",
    style="strict",
    domain="backend",
    question_bank=question_bank,
)

# 生成问题
question = interviewer.generate_question(
    phase="technical",
    difficulty=3,
)

# 生成追问
follow_up = interviewer.generate_follow_up(
    answer="候选人回答内容...",
    history=[],
)

# 评估回答
evaluation = interviewer.evaluate_answer(
    answer="回答内容",
    question="原问题",
)
```

### QuestionBank - 问题库 (v0.2 新增)

```python
from scenes.interview import QuestionBank

# 加载问题库
bank = QuestionBank()
bank.load_from_yaml("scenes/interview/questions.yaml")

# 获取随机问题
question = bank.get_random_question(
    domain="frontend",
    difficulty_range=(2, 4),
)

# 按条件筛选
questions = bank.get_questions(
    domain="backend",
    difficulty=3,
    question_type="conceptual",
    limit=5,
)

print(f"问题库共有 {bank.get_question_count()} 个问题")
```

### BasicEvaluator - 评估器 (v0.2 新增)

```python
from evaluation import BasicEvaluator, EvaluationReport
from core import Message

# 创建评估器
evaluator = BasicEvaluator()

# 准备对话历史
history = [
    Message(content="问题 1", role="interviewer", type="agent"),
    Message(content="回答 1", role="user", type="user"),
    # ...
]

# 执行评估
result = evaluator.evaluate(history)

# 生成报告
report = EvaluationReport.from_result(
    result,
    candidate_info={"name": "张三", "position": "后端工程师"},
    interview_info={"domain": "backend", "style": "strict"},
)

# 输出报告
print(report.generate_text_report())

# 保存 JSON 报告
import json
with open("evaluation_report.json", "w") as f:
    json.dump(report.generate_json_report(), f, ensure_ascii=False, indent=2)
```

### 评估维度说明

| 维度 | 权重 | 子维度 |
|------|------|--------|
| **content_quality** (内容质量) | 35% | 相关性、准确性、深度 |
| **expression_clarity** (表达清晰度) | 30% | 逻辑性、简洁性、条理性 |
| **professional_knowledge** (专业知识) | 35% | 专业知识、经验、解决问题能力 |

### 评级标准

| 评级 | 分数范围 | 描述 |
|------|----------|------|
| S | ≥ 4.5 | 表现卓越，远超预期 |
| A | ≥ 4.0 | 表现优秀，符合高级职位要求 |
| B | ≥ 3.0 | 表现良好，符合职位要求 |
| C | ≥ 2.0 | 表现一般，基本符合要求 |
| D | < 2.0 | 表现不佳，需要改进 |

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

### 扩展新场景

```python
from scenes.base import BaseScene, SceneConfig
from core import Config, Message, DialogueContext

class MeetingScene(BaseScene):
    """会议场景示例"""

    def get_scene_type(self) -> str:
        return "meeting"

    def get_description(self) -> str:
        return "模拟团队会议场景"

    def initialize(self) -> bool:
        # 初始化 Agent
        return True

    def handle_message(
        self,
        message: Message,
        context: DialogueContext,
    ) -> Message:
        # 处理消息
        return Message(content="...", role="system")

    def get_agents(self):
        return []

# 注册场景
from scenes import SceneRegistry
registry = SceneRegistry.get_instance()
registry.register("meeting", MeetingScene, config={
    "name": "团队会议",
    "max_turns": 20,
})
```

### 问题库格式

```yaml
questions:
  - id: fe_001
    question: "React 中的虚拟 DOM 是什么？"
    domain: frontend
    difficulty: 3          # 1-5
    type: conceptual       # conceptual/experience/behavioral/technical/scenario
    category: framework
    sample_answer: "虚拟 DOM 是..."
    evaluation_hints:
      - "是否理解 diff 算法"
      - "是否了解性能优化"
    follow_up_suggestions:
      - "React 的 diff 算法有什么优化策略？"
```

## 📋 版本历史

| 版本 | 状态 | 发布日期 | 核心目标 |
|------|------|----------|----------|
| v0.1 | ✅ 完成 | 2024-01 | 核心框架搭建 |
| v0.2 | ✅ 完成 | 2024-03 | 面试场景系统、增强面试官、问题库、评估系统 |
| v0.3 | 📅 计划 | 2024-06 | 智能反馈系统、AgentScope 深度集成 |
| v0.4 | ✅ 完成 | 2024-03 | CLI 和 Web 用户界面 |
| v1.0 | 📅 计划 | 2024-05 | 正式发布、完整功能 |

### v0.4 完成内容

- [x] TASK-019: CLI 主应用程序
  - `cli/app.py` - CLIApplication 类
  - 完整的交互式菜单系统
  - 快捷命令支持（/help, /quit, /theme 等）
- [x] TASK-020: CLI 菜单系统
  - `cli/menus.py` - MainMenu, SceneMenu, DialogueMenu, FeedbackMenu
  - MenuManager 菜单管理器
  - SettingsMenu, HelpPanel
- [x] TASK-021: CLI 主题管理
  - `cli/themes.py` - Theme, ThemeManager, ThemeType
  - 5 种预定义主题（dark, light, blue, green, monokai）
  - 主题切换和持久化
- [x] TASK-022: CLI UI 组件
  - `cli/widgets.py` - 10 种 UI 组件
  - Header, Footer, MessageBubble, TypingIndicator
  - ProgressBar, Spinner, Panel, Menu, Divider, StatusBadge
- [x] TASK-023: Web 应用程序
  - `web/app.py` - FastAPI 应用创建
  - `web/config.py` - WebConfig, WebConfigLoader
  - 多来源配置加载（YAML, env, dict）
- [x] TASK-024: Web API 路由
  - `web/routes/scenes.py` - 场景 API（6 个端点）
  - `web/routes/dialogue.py` - 对话 API（8 个端点 + WebSocket）
  - `web/routes/feedback.py` - 反馈 API（8 个端点）
- [x] TASK-025: Web 静态资源
  - `web/static/css/main.css` - 1027 行响应式样式
  - `web/static/js/app.js` - 600+ 行前端逻辑
  - 主题切换、API 封装、页面逻辑
- [x] TASK-026: Web HTML 模板
  - `web/templates/base.html` - 基础模板
  - `web/templates/index.html` - 首页
  - `web/templates/scene_selection.html` - 场景选择
  - `web/templates/dialogue.html` - 对话页面
  - `web/templates/feedback.html` - 反馈页面
- [x] TASK-027: 示例程序
  - `examples/cli_demo.py` - CLI 演示
  - `examples/web_demo.py` - Web 演示
- [x] TASK-028: 依赖配置
  - `requirements.txt` - 更新 Web 依赖

### v0.2 完成内容

- [x] TASK-007: 场景系统架构设计
  - `scenes/base.py` - 场景基类
  - `scenes/registry.py` - 场景注册中心
  - `scenes/interview/scene.py` - 面试场景实现
- [x] TASK-008: 增强面试官 Agent
  - 3 种面试风格支持
  - 5 大领域问题生成
  - 智能追问生成
  - AgentScope ModelAgent 集成
- [x] TASK-009: 问题库建设
  - 78+ 技术问题
  - 按领域/难度/类型分类
  - 参考答案和评估提示
- [x] TASK-010: 基础评估器
  - 三维度评估模型
  - 结构化反馈报告
  - 改进建议生成

## 📝 提交规范

本项目遵循 Conventional Commits 规范：

```
feat(scenes): 添加面试场景系统
feat(evaluator): 实现三维度评估器
fix(interviewer): 修复追问生成逻辑
docs(readme): 更新 v0.2 文档
test(examples): 添加面试演示示例
```

## 📄 License

MIT License

## 👥 团队

- 技术架构师：Software Architect
- 产品经理：Product Manager
- 开发团队：Development Team

---

**v0.4 说明**: 本版本完成了完整的用户界面实现，包括 CLI 命令行界面和 Web 网页界面。CLI 模式提供丰富的终端交互体验，支持 5 种主题；Web 模式提供响应式界面，支持移动端访问。运行 `python examples/cli_demo.py` 或 `python examples/web_demo.py` 体验完整功能。

**v0.2 说明**: 本版本完成了面试场景系统的核心功能，包括场景架构、增强面试官、问题库和评估系统。可以直接运行 `examples/interview_demo.py` 体验完整功能。
