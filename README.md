# AgentScope AI Interview

> AI 模拟对话平台 - 基于 AgentScope 框架的多智能体对话模拟系统

**当前版本**: v0.7.0

## 📋 项目概述

AgentScope AI Interview 是一个专业的 AI 对话模拟训练平台，通过多智能体协作模拟真实职场对话场景，帮助用户提升沟通技能、面试技巧和社交能力。

### ✨ v0.7 新增特性 (Data Tracking & Insights)

- 📊 **学习分析系统** - 学习模式识别、强弱项分析、技能水平评估
- 🔍 **行为追踪** - 会话频率追踪、改进模式监控、平台期检测
- 🎯 **推荐引擎** - 个性化主题推荐、难度推荐、学习路径生成
- 📈 **统计引擎** - 高级统计指标、百分位数分析、用户对比（匿名化）
- 💡 **洞察仪表盘** - 关键洞察展示、趋势分析、成就系统
- 📤 **数据导出** - PDF/Excel/JSON 多格式导出、数据备份与恢复
- 🔒 **隐私保护** - 匿名化对比数据、配置驱动的隐私设置

### v0.6 特性 (User System & Progress Tracking)

- 👤 **用户系统** - 完整的用户管理、认证系统（JWT + Session）
- 📊 **进度追踪** - 学习进度跟踪、七维度评估、改进率计算
- 📈 **数据可视化** - 雷达图、趋势图（ASCII/SVG 双格式）
- 📼 **历史回放** - 会话回放、步骤导航、笔记标注
- 🖥️ **用户仪表盘** - CLI/Web 双界面仪表盘、进度报告导出
- 💾 **SQLite 数据库** - 用户数据、会话记录、进度数据存储

### v0.5 特性 (Multi-Scene Support)

- 🎭 **沙龙场景** - 多角色对话模拟，支持主持人/演讲者/观众/观察者 4 种角色
- 🏢 **会议场景** - 多种会议类型支持（站会/需求评审/冲突解决/项目启动/复盘会）
- 🔄 **场景管理器** - 支持场景切换和上下文保持，状态序列化
- 📊 **场景评估** - 沙龙/会议专用评估器，5 维度评估模型
- 🎯 **配置驱动** - 灵活的配置系统，支持自定义场景参数

### v0.4 特性 (User Interface)

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

#### v0.7 数据分析演示

```bash
# 数据分析完整演示（包含所有 v0.7 功能）
python examples/analytics_demo.py

# 生成的文件:
# - exports/analytics_report_demo_user_001.json (JSON 报告)
# - exports/analytics_report_demo_user_001.xlsx (Excel 报告)
# - exports/analytics_report_demo_user_001.pdf (PDF 报告)
# - exports/sessions_demo_user_001.csv (会话数据)
# - exports/backup_demo_user_001.json (数据备份)
```

#### v0.7 核心功能使用

```bash
# 用户系统完整演示（包含所有 v0.6 功能）
python examples/user_system_demo.py

# 生成的文件:
# - data/demo_users.db (SQLite 数据库)
# - examples/radar_chart.svg (雷达图)
# - examples/session_replay.md (会话回放)
# - examples/progress_report.md (进度报告)
```

#### v0.5 多场景演示

```bash
# 沙龙场景演示
python examples/salon_demo.py

# 会议场景演示
python examples/meeting_demo.py

# 场景管理器演示（场景切换）
python examples/scene_manager_demo.py
```

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

### Analytics Module - 数据分析模块 (v0.7 新增)

#### LearningAnalytics - 学习分析器

```python
from analytics import LearningAnalytics

# 创建学习分析器
analytics = LearningAnalytics()

# 生成学习画像
profile = analytics.generate_learning_profile(user_id, sessions)

print(f"技能水平：{profile.skill_level.value}")  # beginner/intermediate/advanced/expert
print(f"学习模式：{profile.learning_pattern.value}")  # consistent/burst/gradual/irregular/declining

# 分析优势
for strength in profile.strengths:
    print(f"优势：{strength.dimension} - {strength.score:.1f}分")

# 分析弱点
for weakness in profile.weaknesses:
    print(f"弱点：{weakness.dimension} - {weakness.score:.1f}分 (优先级：{weakness.priority})")
    for suggestion in weakness.improvement_suggestions:
        print(f"  建议：{suggestion}")

# 生成洞察
for insight in profile.insights:
    print(f"[{insight.insight_type}] {insight.title}: {insight.description}")
```

#### BehaviorTracker - 行为追踪器

```python
from analytics import BehaviorTracker

# 创建行为追踪器
tracker = BehaviorTracker()

# 分析用户行为
report = tracker.analyze_behavior(user_id, sessions, period_days=30)

# 会话模式
sp = report.session_pattern
print(f"平均每周会话数：{sp.avg_sessions_per_week:.2f}")
print(f"偏好时间：{sp.preferred_time_of_day}")  # morning/afternoon/evening/night
print(f"一致性分数：{sp.consistency_score:.2f}")  # 0-1

# 参与度
eng = report.engagement
print(f"参与度等级：{eng.level.value}")  # inactive/low/medium/high/very_high
print(f"当前连续天数：{eng.current_streak}")
print(f"最长连续天数：{eng.longest_streak}")

# 改进模式
imp = report.improvement_pattern
print(f"改进趋势：{imp.overall_trend}")  # improving/stable/declining
print(f"改进率：{imp.improvement_rate:.2f}%/周")

# 平台期检测
plat = report.plateau_analysis
print(f"平台期状态：{plat.status.value}")  # none/approaching/in_plateau/breaking_through
if plat.status.value == "in_plateau":
    print(f"平台期持续天数：{plat.duration_days}")
    for rec in plat.recommendations:
        print(f"  建议：{rec}")
```

#### RecommendationEngine - 推荐引擎

```python
from analytics import RecommendationEngine

# 创建推荐引擎
engine = RecommendationEngine()

# 生成推荐
report = engine.generate_recommendations(user_id, sessions, learning_profile, behavior_report)

# 主题推荐
for rec in report.topic_recommendations:
    print(f"[P{rec.priority}] {rec.topic_name}")
    print(f"  维度：{rec.dimension}")
    print(f"  难度：{rec.difficulty.value}")
    print(f"  预期提升：{rec.expected_improvement:.1f}%")

# 难度推荐
dr = report.difficulty_recommendation
print(f"当前难度：{dr.current_level.value}")
print(f"推荐难度：{dr.recommended_level.value}")
print(f"原因：{dr.reason}")

# 学习路径
lp = report.learning_path
print(f"学习路径：{lp.duration_days}天")
for item in lp.items[:5]:
    print(f"  第{item.step}步：{item.description}")

# 练习方法
for method in report.practice_methods:
    print(f"{method.method_name}: {method.description}")
    for step in method.steps[:3]:
        print(f"  - {step}")
```

#### StatisticsEngine - 统计引擎

```python
from analytics import StatisticsEngine

# 创建统计引擎
engine = StatisticsEngine()

# 生成统计报告
report = engine.generate_statistical_report(user_id, sessions, period_days=30)

# 描述性统计
ds = report.descriptive_stats
print(f"平均分：{ds.mean:.2f}")
print(f"中位数：{ds.median:.2f}")
print(f"标准差：{ds.std_dev:.2f}")

# 百分位数据
pd = report.percentile_data
print(f"P50: {pd.p50:.2f}, P75: {pd.p75:.2f}, P90: {pd.p90:.2f}")

# 分布分析
da = report.distribution_analysis
print(f"分布类型：{da.type.value}")  # normal/skewed_left/skewed_right/uniform/bimodal
print(f"偏度：{da.skewness:.3f}")
print(f"异常值：{da.outliers_count}个")

# 对比分析（匿名化）
ca = report.comparative_analysis
print(f"百分位排名：{ca.percentile_rank:.1f}%")
print(f"Z 分数：{ca.z_score:.2f}")
print(f"性能水平：{ca.performance_level}")  # excellent/good/average/below_average/poor
print(f"{ca.comparison_summary}")

# 趋势统计
ts = report.trend_statistics
print(f"趋势方向：{ts.trend_direction}")  # upward/downward/stable
print(f"趋势强度：{ts.trend_strength}")  # strong/moderate/weak
print(f"预测值：{ts.predicted_next_value:.2f}")
```

#### InsightsDashboard - 洞察仪表盘

```python
from analytics import InsightsDashboard

# 创建仪表盘
dashboard = InsightsDashboard()

# 生成仪表盘数据
data = dashboard.generate_dashboard(
    user_id, sessions, learning_profile, behavior_report,
    statistical_report, recommendation_report
)

# 关键洞察
for insight in data.key_insights[:5]:
    print(f"{insight.icon} [{insight.category.value}] {insight.title}")
    print(f"  {insight.description}")
    if insight.actionable_items:
        print(f"  行动：{insight.actionable_items[0]}")

# 表现卡片
for card in data.performance_cards[:5]:
    change_str = f"+{card.change:.1f}" if card.change > 0 else f"{card.change:.1f}"
    print(f"{card.dimension_name}: {card.current_score:.1f} ({change_str})")

# 可操作建议
for rec in data.recommendations[:3]:
    print(f"[P{rec.priority}] {rec.title}: {rec.time_required_minutes}分钟")

# 成就
for achievement in data.achievements:
    print(f"{achievement.icon} {achievement.name}")

# 仪表盘摘要
print(data.summary_text)
```

#### DataExporter - 数据导出器

```python
from analytics import DataExporter, ExportFormat

# 创建导出器
exporter = DataExporter(config={"output_dir": "./exports"})

# 导出 JSON
json_result = exporter.export_to_json(dashboard_data, filename="report.json")
print(f"JSON: {json_result.success} - {json_result.file_path}")

# 导出 Excel
excel_result = exporter.export_to_excel(dashboard_data, filename="report.xlsx")
print(f"Excel: {excel_result.success} - {excel_result.file_path}")

# 导出 PDF
pdf_result = exporter.export_to_pdf(dashboard_data, filename="report.pdf")
print(f"PDF: {pdf_result.success} - {pdf_result.file_path}")

# 导出会话 CSV
csv_result = exporter.export_to_csv(sessions, filename="sessions.csv")
print(f"CSV: {csv_result.success} - {csv_result.file_path}")

# 数据备份
backup_result = exporter.create_backup(user_id, sessions, analytics_data)
print(f"备份：{backup_result.success} - {backup_result.file_path}")

# 恢复备份
restored = exporter.restore_backup(backup_result.file_path)
if restored["success"]:
    print(f"恢复成功：{restored['user_id']}")
```

### SceneManager - 场景管理器 (v0.5 新增)

```python
from scenes.manager import SceneManager
from core import Message, DialogueContext

# 创建场景管理器
manager = SceneManager()

# 创建多个场景
manager.create_scene("interview", scene_key="interview", style="friendly")
manager.create_scene("salon", scene_key="salon", topic="AI 技术")
manager.create_scene("meeting", scene_key="meeting", meeting_type="standup")

# 激活场景
manager.activate_scene("interview")

# 场景切换（保持上下文）
transition = manager.switch_scene("salon", preserve_context=True)
print(transition.message)  # "成功切换到 salon 场景"

# 处理对话
context = manager.get_global_context()
message = Message(content="你好", role="user")
response, transition = manager.handle_message(message, context)

# 场景指令（自动切换）
# 发送 "/switch meeting" 自动切换到会议场景

# 导出/导入状态（支持断点续玩）
state = manager.export_state()
manager.import_state(state)
```

### SalonScene - 沙龙场景 (v0.5 新增)

```python
from scenes.salon import SalonScene, SalonSceneConfig, SalonPhase

# 创建沙龙配置
config = SalonSceneConfig(
    topic="AI 技术在开发中的应用",
    speaker_topic="大模型辅助编程实践",
    discussion_style="casual",  # casual/formal/debate
)

# 创建并初始化场景
scene = SalonScene(config=config)
scene.initialize()

# 启动沙龙
opening = scene.start()
print(opening.content)

# 处理对话
from core import Message, DialogueContext
context = DialogueContext()
message = Message(content="大家对 AI 编程有什么经验？", role="user")
response = scene.handle_message(message, context)

# 获取统计
stats = scene.get_salon_stats()
print(f"阶段：{stats['phase']}, 轮次：{stats['current_turn']}")

# 沙龙角色（4 种 AI Agent）
# - SalonHostAgent: 主持人
# - SalonSpeakerAgent: 演讲者
# - SalonAudienceAgent: 观众（可多个）
# - SalonObserverAgent: 观察者
```

### MeetingScene - 会议场景 (v0.5 新增)

```python
from scenes.meeting import MeetingScene, MeetingType, MeetingPhase

# 创建会议场景
scene = MeetingScene(
    meeting_type=MeetingType.STANDUP,  # 站会
    project_name="电商平台重构",
    agenda=["昨日工作", "今日计划", "阻塞问题"],
)
scene.initialize()

# 启动会议
opening = scene.start()

# 会议类型支持:
# - MeetingType.STANDUP: 每日站会
# - MeetingType.REQUIREMENT_REVIEW: 需求评审
# - MeetingType.CONFLICT_RESOLUTION: 冲突解决
# - MeetingType.PROJECT_KICKOFF: 项目启动
# - MeetingType.RETROSPECTIVE: 复盘会议

# 获取行动项
action_items = scene.get_action_items()
for item in action_items:
    print(f"- {item['content']} (负责人：{item['owner']})")
```

### SalonEvaluator - 沙龙评估器 (v0.5 新增)

```python
from evaluation import SalonEvaluator

# 创建评估器
evaluator = SalonEvaluator()

# 评估维度:
# 1. participation_quality (参与质量)
# 2. topic_relevance (话题相关性)
# 3. interaction_effectiveness (互动效果)
# 4. knowledge_contribution (知识贡献)
# 5. communication_style (沟通风格)

# 执行评估
result = evaluator.evaluate(
    dialogue_context=context,
    scene_stats=stats,
    user_role="audience",  # host/speaker/audience/observer
)

# 生成报告
report = evaluator.generate_report(result, format="markdown")
print(report)
```

### MeetingEvaluator - 会议评估器 (v0.5 新增)

```python
from evaluation import MeetingEvaluator

# 创建评估器
evaluator = MeetingEvaluator()

# 评估维度:
# 1. meeting_efficiency (会议效率)
# 2. communication_effectiveness (沟通效果)
# 3. collaboration_quality (协作质量)
# 4. problem_solving (问题解决)
# 5. action_orientation (行动导向)

# 执行评估（权重根据会议类型自动调整）
result = evaluator.evaluate(
    dialogue_context=context,
    meeting_stats=stats,
    meeting_type="standup",  # 不同会议类型权重不同
    user_role="participant",
)

# 行动项质量评估
print(f"行动项质量：{result.action_items_quality}")
```

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
| v0.5 | ✅ 完成 | 2024-03 | 多场景支持（沙龙/会议）、场景管理器 |
| v0.6 | ✅ 完成 | 2024-03 | 用户系统、进度追踪、数据可视化 |
| v0.7 | ✅ 完成 | 2024-03 | 数据追踪与洞察、学习分析、推荐引擎 |
| v1.0 | 📅 计划 | 2024-05 | 正式发布、完整功能 |

### v0.7 完成内容

- [x] TASK-037: 学习分析系统
  - `analytics/learning.py` - LearningAnalytics, LearningProfile
  - 学习模式识别（consistent/burst/gradual/irregular/declining）
  - 强弱项分析（基于七维度评估）
  - 学习洞察生成
- [x] TASK-038: 行为追踪系统
  - `analytics/behavior.py` - BehaviorTracker, BehaviorReport
  - 会话模式分析（频率、时长、时间偏好）
  - 参与度计算（inactive/low/medium/high/very_high）
  - 改进模式监控（趋势、加速度）
  - 平台期检测（none/approaching/in_plateau/breaking_through）
- [x] TASK-039: 推荐引擎
  - `analytics/recommender.py` - RecommendationEngine
  - 主题推荐（基于弱点分析）
  - 难度推荐（beginner/intermediate/advanced/expert）
  - 学习路径生成（7/14/21 天计划）
  - 练习方法推荐（刻意练习/间隔重复/场景变换等）
- [x] TASK-040: 统计引擎
  - `analytics/statistics.py` - StatisticsEngine
  - 描述性统计（平均/中位数/标准差/四分位数）
  - 百分位数据（P10/P25/P50/P75/P90/P95/P99）
  - 分布分析（正态/偏态/双峰/均匀）
  - 对比分析（匿名化人口数据、Z 分数、T 分数）
  - 趋势统计（线性回归、R²、预测）
  - 相关分析（皮尔逊相关系数）
- [x] TASK-041: 洞察仪表盘
  - `analytics/insights.py` - InsightsDashboard
  - 关键洞察生成（performance/progress/behavior/recommendation/alert/achievement）
  - 表现卡片（七维度对比）
  - 趋势分析（多指标）
  - 可操作建议（优先级排序）
  - 成就系统（6 种成就徽章）
- [x] TASK-042: 数据导出系统
  - `analytics/export.py` - DataExporter
  - PDF 导出（reportlab/matplotlib 降级方案）
  - Excel 导出（openpyxl，多 sheet）
  - JSON 导出（格式化/元数据）
  - CSV 导出（会话数据）
  - 数据备份与恢复
- [x] TASK-DOC: 示例和文档
  - `examples/analytics_demo.py` - 完整功能演示
  - `analytics/__init__.py` - 模块导出
  - 更新 README 和 core/__init__.py
  - 更新 requirements.txt (pandas, numpy, reportlab, openpyxl)

### v0.6 完成内容

- [x] TASK-031: 用户系统架构设计
  - `users/models.py` - User, UserProfile, SessionModel (Pydantic)
  - `users/auth.py` - AuthService (JWT), SessionManager
  - `users/service.py` - UserService 业务逻辑层
- [x] TASK-032: 用户数据库实现
  - `users/database.py` - Database 单例，SQLite 连接管理
  - `users/tables.py` - SQLAlchemy 表定义 (users, sessions, progress_data)
  - `users/repository.py` - UserRepository, SessionRepository, ProgressRepository
- [x] TASK-033: 进度追踪器
  - `progress/tracker.py` - ProgressTracker 核心类
  - `progress/metrics.py` - ProgressMetricsCalculator, 七维度评估
  - `progress/history.py` - SessionHistoryManager
- [x] TASK-034: 数据可视化
  - `visualization/charts.py` - ASCIIChart, ChartGenerator
  - `visualization/radar.py` - RadarChart, DimensionRadarChart (SVG)
  - `visualization/trends.py` - TrendChart, ProgressTrendChart
- [x] TASK-035: 历史回放
  - `history/replay.py` - SessionReplay, ReplayStep, ReplayNote
  - 步骤导航（上一步/下一步/跳转）
  - 笔记标注和导出（JSON/Markdown）
- [x] TASK-036: 用户仪表盘
  - `dashboard/cli_dashboard.py` - CLIDashboard (Rich UI)
  - `dashboard/web_dashboard.py` - WebDashboardRouter (FastAPI)
  - `dashboard/report.py` - ReportGenerator (Markdown/PDF/HTML)
- [x] TASK-DOC: 示例和文档
  - `examples/user_system_demo.py` - 完整功能演示
  - 更新 README 和 core/__init__.py
  - 更新 requirements.txt (sqlalchemy, PyJWT, matplotlib)

### v0.5 完成内容

- [x] TASK-025: 沙龙场景结构
  - `scenes/salon/scene.py` - SalonScene, SalonSceneConfig
  - `scenes/salon/roles.py` - SalonRoleType, RoleConfig, RoleManager
  - 支持 4+ AI Agent 同时参与
  - `scenes/salon/host.py` - SalonHostAgent (主持人)
  - `scenes/salon/speaker.py` - SalonSpeakerAgent (演讲者)
  - `scenes/salon/audience.py` - SalonAudienceAgent (观众)
  - `scenes/salon/observer.py` - SalonObserverAgent (观察者)
- [x] TASK-027: 会议场景结构
  - `scenes/meeting/scene.py` - MeetingScene, MeetingSceneConfig
  - `scenes/meeting/__init__.py` - MeetingType, MeetingPhase
  - 支持 5 种会议子场景
- [x] TASK-028: 会议场景 Agent
  - `scenes/meeting/manager.py` - MeetingManagerAgent (主持人)
  - `scenes/meeting/participant.py` - MeetingParticipantAgent (参与者)
  - 支持多种角色（产品经理/开发/测试/项目经理等）
- [x] TASK-029: 场景切换机制
  - `scenes/manager.py` - SceneManager, SceneTransition
  - 上下文保持和恢复
  - 场景状态序列化/反序列化
  - 场景指令支持（/switch, /scene）
- [x] TASK-030: 场景评估扩展
  - `evaluation/salon_evaluator.py` - SalonEvaluator (5 维度)
  - `evaluation/meeting_evaluator.py` - MeetingEvaluator (5 维度)
  - 会议类型权重自适应
- [x] TASK-DOC: 示例和文档
  - `examples/salon_demo.py` - 沙龙场景演示
  - `examples/meeting_demo.py` - 会议场景演示
  - `examples/scene_manager_demo.py` - 场景管理器演示
  - 更新 README 和模块文档

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

**v0.6 说明**: 本版本完成了用户系统与进度追踪功能，包括用户管理、认证系统、进度追踪、数据可视化（雷达图/趋势图）、历史回放和用户仪表盘。运行 `python examples/user_system_demo.py` 体验完整功能。

**v0.5 说明**: 本版本完成了多场景支持功能，包括沙龙场景（4 种角色 AI Agent）、会议场景（5 种会议类型）、场景管理器（支持场景切换和上下文保持）、场景专用评估器。运行 `python examples/salon_demo.py`、`python examples/meeting_demo.py` 或 `python examples/scene_manager_demo.py` 体验完整功能。

**v0.4 说明**: 本版本完成了完整的用户界面实现，包括 CLI 命令行界面和 Web 网页界面。CLI 模式提供丰富的终端交互体验，支持 5 种主题；Web 模式提供响应式界面，支持移动端访问。运行 `python examples/cli_demo.py` 或 `python examples/web_demo.py` 体验完整功能。

**v0.2 说明**: 本版本完成了面试场景系统的核心功能，包括场景架构、增强面试官、问题库和评估系统。可以直接运行 `examples/interview_demo.py` 体验完整功能。
