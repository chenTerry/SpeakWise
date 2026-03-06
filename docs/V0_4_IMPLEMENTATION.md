# v0.4 用户界面实现文档 (User Interface Implementation)

## 概述

v0.4 版本完成了完整的用户界面实现，包括 **CLI 命令行界面** 和 **Web 网页界面** 两种交互方式。

---

## 1. CLI 模块 (cli/)

### 1.1 架构设计

```
cli/
├── __init__.py          # 模块导出
├── app.py               # 主应用程序入口
├── menus.py             # 菜单系统
├── themes.py            # 主题管理
└── widgets.py           # UI 组件库
```

### 1.2 核心组件

#### Theme 主题系统

支持 5 种预定义主题：

| 主题名称 | 类型 | 描述 |
|---------|------|------|
| `dark` | Dark | 暗色主题，适合长时间使用 |
| `light` | Light | 亮色主题，适合明亮环境 |
| `blue` | Blue Ocean | 蓝色海洋，舒适护眼 |
| `green` | Green Terminal | 绿色终端，经典风格 |
| `monokai` | Monokai | 流行编辑器主题 |

**使用示例：**
```python
from cli.themes import ThemeManager

manager = ThemeManager(default_theme="dark")
console = manager.create_console()
```

#### Widgets UI 组件

| 组件 | 描述 | 使用场景 |
|-----|------|---------|
| `Header` | 页头组件 | 页面标题和状态 |
| `Footer` | 页脚组件 | 帮助提示和快捷键 |
| `MessageBubble` | 消息气泡 | 对话消息展示 |
| `TypingIndicator` | 打字指示器 | AI 思考动画 |
| `ProgressBar` | 进度条 | 任务进度展示 |
| `Spinner` | 旋转加载器 | 加载动画 |
| `Panel` | 面板容器 | 内容分组 |
| `Menu` | 菜单列表 | 可选项列表 |
| `Divider` | 分隔线 | 视觉分隔 |
| `StatusBadge` | 状态徽章 | 状态指示 |

#### Menus 菜单系统

| 菜单类 | 描述 |
|-------|------|
| `MainMenu` | 主入口菜单 |
| `SceneMenu` | 场景选择菜单 |
| `DialogueMenu` | 对话操作菜单 |
| `FeedbackMenu` | 反馈展示菜单 |
| `SettingsMenu` | 设置菜单 |
| `HelpPanel` | 帮助面板 |

### 1.3 使用示例

```python
from cli.app import CLIApplication

# 创建应用
app = CLIApplication(theme_name="dark")

# 运行
app.run()
```

**快捷命令：**
- `/help` - 显示帮助
- `/quit` - 退出程序
- `/theme` - 切换主题
- `/history` - 查看历史
- `/clear` - 清屏

---

## 2. Web 模块 (web/)

### 2.1 架构设计

```
web/
├── __init__.py          # 模块导出
├── app.py               # FastAPI 应用
├── config.py            # 配置管理
├── routes/
│   ├── __init__.py
│   ├── scenes.py        # 场景 API
│   ├── dialogue.py      # 对话 API
│   └── feedback.py      # 反馈 API
├── static/
│   ├── css/
│   │   └── main.css     # 主样式表
│   └── js/
│       └── app.js       # 前端逻辑
└── templates/
    ├── base.html        # 基础模板
    ├── index.html       # 首页
    ├── scene_selection.html  # 场景选择
    ├── dialogue.html    # 对话页面
    └── feedback.html    # 反馈页面
```

### 2.2 API 端点

#### 场景 API (`/api/scenes`)

| 方法 | 端点 | 描述 |
|-----|------|------|
| GET | `/api/scenes` | 获取场景列表 |
| GET | `/api/scenes/{id}` | 获取场景详情 |
| POST | `/api/scenes/{id}/start` | 开始场景 |
| GET | `/api/scenes/domains` | 获取领域列表 |
| GET | `/api/scenes/styles` | 获取风格列表 |

#### 对话 API (`/api/dialogue`)

| 方法 | 端点 | 描述 |
|-----|------|------|
| POST | `/api/dialogue/sessions` | 创建会话 |
| GET | `/api/dialogue/sessions/{id}` | 获取会话 |
| POST | `/api/dialogue/sessions/{id}/messages` | 发送消息 |
| POST | `/api/dialogue/sessions/{id}/complete` | 完成会话 |
| WebSocket | `/api/dialogue/ws/{id}` | 实时对话 |

#### 反馈 API (`/api/feedback`)

| 方法 | 端点 | 描述 |
|-----|------|------|
| POST | `/api/feedback/generate` | 生成反馈 |
| GET | `/api/feedback/{id}` | 获取反馈 |
| GET | `/api/feedback/{id}/export/json` | 导出 JSON |
| GET | `/api/feedback/{id}/export/markdown` | 导出 Markdown |

### 2.3 前端功能

#### JavaScript 模块

| 模块 | 描述 |
|-----|------|
| `API` | API 请求封装 |
| `ThemeManager` | 主题切换 |
| `UI` | UI 工具函数 |
| `SceneSelection` | 场景选择逻辑 |
| `DialoguePage` | 对话页面逻辑 |
| `FeedbackPage` | 反馈页面逻辑 |

#### CSS 特性

- **响应式设计** - 支持移动端和桌面端
- **主题切换** - 暗色/亮色主题
- **动画效果** - 打字动画、淡入淡出
- **现代布局** - Flexbox 和 Grid

### 2.4 使用示例

```python
from web.app import WebApplication
from web.config import WebConfig

# 创建配置
config = WebConfig(
    host="127.0.0.1",
    port=8000,
    debug=True,
)

# 启动服务器
app = WebApplication(config=config)
app.run()
```

**访问地址：**
- 首页：http://127.0.0.1:8000
- 场景选择：http://127.0.0.1:8000/scenes
- API 文档：http://127.0.0.1:8000/docs

---

## 3. 配置系统

### 3.1 CLI 配置

CLI 使用主题管理器进行配置：

```python
from cli.themes import ThemeManager

manager = ThemeManager(default_theme="dark")
manager.set_theme("blue")
```

### 3.2 Web 配置

Web 配置支持多种来源：

```python
from web.config import WebConfig, WebConfigLoader

# 从 YAML 加载
config = WebConfigLoader.from_yaml("web_config.yaml")

# 从环境变量加载
config = WebConfigLoader.from_env()

# 自定义配置
config = WebConfig(
    host="0.0.0.0",
    port=8080,
    debug=False,
    secret_key="your-secret-key",
)
```

**环境变量：**
- `WEB_HOST` - 主机地址
- `WEB_PORT` - 端口
- `WEB_DEBUG` - 调试模式
- `WEB_SECRET_KEY` - 密钥
- `WEB_THEME` - 默认主题

---

## 4. 运行示例

### CLI Demo

```bash
# 功能展示
python examples/cli_demo.py --features

# 自定义配置
python examples/cli_demo.py --custom

# 正常运行
python examples/cli_demo.py
```

### Web Demo

```bash
# 功能展示
python examples/web_demo.py --features

# 自定义端口
python examples/web_demo.py --port 8080

# 正常运行
python examples/web_demo.py
```

---

## 5. 依赖安装

```bash
# 安装所有依赖
pip install -r requirements.txt

# 核心依赖
pip install rich>=13.7.0
pip install fastapi>=0.104.0
pip install uvicorn[standard]>=0.24.0
pip install jinja2>=3.1.2
pip install pydantic>=2.0.0
pip install websockets>=12.0
```

---

## 6. 技术亮点

### CLI 模块
- ✅ 基于 Rich 库的彩色终端 UI
- ✅ 完整的主题系统（5 种预定义主题）
- ✅ 交互式菜单导航
- ✅ 实时打字效果动画
- ✅ 消息气泡展示
- ✅ 进度条和加载动画

### Web 模块
- ✅ 基于 FastAPI 的现代 Web 框架
- ✅ RESTful API 设计
- ✅ WebSocket 实时通信
- ✅ 响应式设计（移动端友好）
- ✅ 主题切换（暗色/亮色）
- ✅ 可视化评估报告
- ✅ 导出功能（JSON/Markdown）

---

## 7. 文件清单

### CLI 模块
| 文件 | 行数 | 描述 |
|-----|------|------|
| `cli/__init__.py` | 50+ | 模块导出 |
| `cli/app.py` | 400+ | 主应用程序 |
| `cli/menus.py` | 350+ | 菜单系统 |
| `cli/themes.py` | 200+ | 主题管理 |
| `cli/widgets.py` | 450+ | UI 组件库 |

### Web 模块
| 文件 | 行数 | 描述 |
|-----|------|------|
| `web/__init__.py` | 30+ | 模块导出 |
| `web/app.py` | 150+ | FastAPI 应用 |
| `web/config.py` | 200+ | 配置管理 |
| `web/routes/scenes.py` | 200+ | 场景 API |
| `web/routes/dialogue.py` | 300+ | 对话 API |
| `web/routes/feedback.py` | 300+ | 反馈 API |
| `web/static/css/main.css` | 1000+ | 样式表 |
| `web/static/js/app.js` | 600+ | 前端逻辑 |
| `web/templates/*.html` | 5 个 | HTML 模板 |

---

## 8. 下一步计划 (v0.5)

- [ ] 集成真实的 AgentScope 多智能体
- [ ] 添加更多面试场景
- [ ] 实现用户账户系统
- [ ] 添加对话历史记录存储
- [ ] 改进评估算法
- [ ] 添加语音输入支持

---

## 9. 故障排除

### CLI 问题

**问题：** 颜色显示不正常
```bash
# 确保终端支持真彩色
export COLORTERM=truecolor
```

**问题：** Rich 库版本过低
```bash
pip install --upgrade rich
```

### Web 问题

**问题：** 端口被占用
```bash
# 使用其他端口
python examples/web_demo.py --port 8080
```

**问题：** 模板加载失败
```bash
# 确保模板目录存在
ls web/templates/
```

---

## 10. 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

**代码规范：**
- 使用类型提示
- 添加文档字符串
- 遵循 PEP 8
- 编写测试用例

---

**版本：** v0.4.0  
**更新日期：** 2026-03-31  
**作者：** AgentScope AI Interview Team
