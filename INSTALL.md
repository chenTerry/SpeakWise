# 📦 AgentScope AI Interview - Installation Guide

**版本**: v1.0.0  
**最后更新**: 2026-03-04

---

## 📋 目录

1. [系统要求](#系统要求)
2. [快速安装](#快速安装)
3. [详细安装步骤](#详细安装步骤)
4. [配置指南](#配置指南)
5. [验证安装](#验证安装)
6. [故障排除](#故障排除)
7. [卸载指南](#卸载指南)

---

## 💻 系统要求

### 最低配置

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 10 / macOS 10.15 / Linux (Ubuntu 18.04+) |
| **Python** | 3.8 或更高版本 |
| **内存** | 4 GB RAM |
| **磁盘空间** | 500 MB 可用空间 |
| **网络** | 宽带互联网连接（用于 API 调用） |

---

### 推荐配置

| 组件 | 要求 |
|------|------|
| **操作系统** | Windows 11 / macOS 12+ / Linux (Ubuntu 22.04+) |
| **Python** | 3.10 或更高版本 |
| **内存** | 8 GB RAM |
| **磁盘空间** | 1 GB 可用空间 |
| **网络** | 高速互联网连接（用于语音功能和 API 调用） |

---

### 可选硬件

| 硬件 | 用途 | 要求 |
|------|------|------|
| **麦克风** | 语音输入（STT） | 任何 USB 或 3.5mm 麦克风 |
| **扬声器/耳机** | 语音输出（TTS） | 任何音频输出设备 |
| **摄像头** | 未来视频功能 | USB 摄像头（预留） |

---

## 🚀 快速安装

### 5 分钟快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/agentscope_ai_interview.git
cd agentscope_ai_interview

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 复制配置文件
cp examples/config.example.yaml config.yaml

# 5. 设置 API 密钥
export DASHSCOPE_API_KEY="your-api-key-here"

# 6. 运行测试
python examples/v1.0_demo.py
```

---

## 📖 详细安装步骤

### 步骤 1: 安装 Python

#### Windows

1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.10+ 安装包
3. 运行安装程序，**勾选 "Add Python to PATH"**
4. 验证安装：
   ```bash
   python --version
   # 应输出：Python 3.10.x
   ```

#### macOS

```bash
# 使用 Homebrew（推荐）
brew install python@3.10

# 验证安装
python3 --version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# 验证安装
python3 --version
```

---

### 步骤 2: 克隆项目

```bash
# 克隆仓库
git clone https://github.com/your-org/agentscope_ai_interview.git

# 进入项目目录
cd agentscope_ai_interview

# 查看项目结构
ls -la
```

**预期输出**:
```
total 80
drwxr-xr-x  15 user user 4096 Mar  4 10:00 .
drwxr-xr-x   5 user user 4096 Mar  4 10:00 ..
drwxr-xr-x   8 user user 4096 Mar  4 10:00 .git
-rw-r--r--   1 user user  150 Mar  4 10:00 .gitignore
-rw-r--r--   1 user user 8500 Mar  4 10:00 README.md
-rw-r--r--   1 user user 5200 Mar  4 10:00 INSTALL.md
-rw-r--r--   1 user user 3800 Mar  4 10:00 QUICKSTART.md
-rw-r--r--   1 user user 9200 Mar  4 10:00 RELEASE_NOTES.md
-rw-r--r--   1 user user 2100 Mar  4 10:00 requirements.txt
drwxr-xr-x   2 user user 4096 Mar  4 10:00 core
drwxr-xr-x   2 user user 4096 Mar  4 10:00 scenes
...
```

---

### 步骤 3: 创建虚拟环境

**强烈建议**使用虚拟环境来隔离项目依赖。

#### Linux/macOS

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证激活（命令行前应有 (venv) 前缀）
which python
# 应输出：/path/to/agentscope_ai_interview/venv/bin/python
```

#### Windows (PowerShell)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\Activate.ps1

# 如果提示权限问题，运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 验证激活
where python
# 应输出：Z:\path\to\agentscope_ai_interview\venv\Scripts\python.exe
```

#### Windows (CMD)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat
```

---

### 步骤 4: 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt
```

**预期输出**（部分）:
```
Collecting agentscope>=0.1.0
  Downloading agentscope-0.1.0-py3-none-any.whl (256 kB)
Collecting pyyaml>=6.0
  Downloading PyYAML-6.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (705 kB)
Collecting rich>=13.7.0
  Downloading rich-13.7.0-py3-none-any.whl (240 kB)
Collecting fastapi>=0.104.0
  Downloading fastapi-0.104.1-py3-none-any.whl (92 kB)
...
Successfully installed agentscope-0.1.0 fastapi-0.104.1 pyyaml-6.0.1 rich-13.7.0 ...
```

---

### 步骤 5: 安装可选依赖

#### 语音功能依赖（推荐）

```bash
# Linux/macOS
pip install speechrecognition pyaudio pyttsx3 gTTS pydub webrtcvad

# Windows (PyAudio 需要预编译二进制)
pip install speechrecognition pyttsx3 gTTS pydub webrtcvad
pip install --only-binary :all: pyaudio
```

#### 数据库迁移工具（开发环境）

```bash
pip install alembic>=1.12.0
```

#### 开发工具（可选）

```bash
pip install pytest pytest-cov black flake8 mypy httpx
```

---

### 步骤 6: 配置环境变量

#### 创建 .env 文件

```bash
# 复制示例文件
cp examples/.env.example .env
```

#### 编辑 .env 文件

```bash
# .env 文件内容示例

# AgentScope 模型配置
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# 可选：其他模型提供商
OPENAI_API_KEY=your_openai_api_key_here

# 数据库配置（可选，默认使用 SQLite）
DATABASE_URL=sqlite:///data/interview.db

# 语音功能配置（可选）
GOOGLE_SPEECH_API_KEY=your_google_speech_api_key_here

# 企业版 SSO 配置（可选）
SSO_CLIENT_ID=your_sso_client_id
SSO_CLIENT_SECRET=your_sso_client_secret
```

#### 获取 API 密钥

1. **DashScope (阿里云)**:
   - 访问：https://dashscope.aliyun.com/
   - 注册/登录账号
   - 创建 API Key
   - 复制 Key 到 .env 文件

2. **OpenAI (可选)**:
   - 访问：https://platform.openai.com/api-keys
   - 创建 API Key
   - 复制 Key 到 .env 文件

---

## ⚙️ 配置指南

### 配置文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| 主配置 | `config.yaml` | 核心配置 |
| 环境变量 | `.env` | API 密钥和敏感信息 |
| 语音配置 | `voice_config.yaml` | 语音功能配置 |
| 企业配置 | `enterprise_config.yaml` | 企业版功能配置 |

---

### 主配置 (config.yaml)

```bash
# 复制示例配置
cp examples/config.example.yaml config.yaml
```

**配置示例**:

```yaml
# =============================================================================
# AgentScope 模型配置
# =============================================================================
agentscope:
  model_configs:
    - model_type: "dashscope"
      config_name: "deepseek"
      model_name: "deepseek-chat"
      api_key: "${DASHSCOPE_API_KEY}"
    
    - model_type: "openai"
      config_name: "gpt4"
      model_name: "gpt-4"
      api_key: "${OPENAI_API_KEY}"

# =============================================================================
# 模型参数
# =============================================================================
model:
  name: "deepseek-chat"           # 默认模型
  temperature: 0.7                 # 创造性 (0.0-1.0)
  max_tokens: 2048                 # 最大 token 数
  top_p: 0.9                       # 核采样参数
  timeout: 30                      # 超时时间（秒）

# =============================================================================
# 对话配置
# =============================================================================
dialogue:
  max_turns: 10                    # 默认最大对话轮数
  session_timeout: 1800            # 会话超时（秒）
  enable_history: true             # 启用历史记录
  history_limit: 100               # 历史记录上限

# =============================================================================
# Agent 配置
# =============================================================================
agent:
  interviewer:
    style: "friendly"              # friendly/strict/pressure
    domain: "tech"                 # tech/frontend/backend/system_design/hr
    enable_followup: true          # 启用追问
    max_followups: 3               # 最大追问次数

# =============================================================================
# 评估配置
# =============================================================================
evaluation:
  enable: true                     # 启用评估
  weights:
    content_quality: 0.35
    expression_clarity: 0.30
    professional_knowledge: 0.35
  thresholds:
    S: 4.5                         # S 级阈值
    A: 4.0                         # A 级阈值
    B: 3.0                         # B 级阈值
    C: 2.0                         # C 级阈值

# =============================================================================
# 语音配置 (v0.8)
# =============================================================================
voice:
  enable: true                     # 启用语音功能
  stt:
    engine: "google"               # google/azure/aws
    language: "zh-CN"              # 语音识别语言
    sample_rate: 16000             # 采样率
  tts:
    engine: "pyttsx3"              # pyttsx3/gTTS
    language: "zh-CN"              # 语音合成语言
    rate: 200                      # 语速
    volume: 1.0                    # 音量

# =============================================================================
# 企业配置 (v0.9)
# =============================================================================
enterprise:
  enable: false                    # 启用企业版功能
  multi_tenant: false              # 多租户模式
  sso:
    enable: false                  # 启用 SSO
    provider: "oauth2"             # oauth2/saml/ldap
```

---

### 语音配置 (voice_config.yaml)

```yaml
# 语音输入配置
input:
  enable: true
  device_index: null               # null=默认麦克风
  sample_rate: 16000
  channels: 1
  vad_aggressiveness: 2            # 0-3，越高越激进
  silence_duration: 0.5            # 静音检测时长（秒）

# 语音输出配置
output:
  enable: true
  device_index: null               # null=默认扬声器
  engine: "pyttsx3"
  voice_id: null                   # null=默认语音
  rate: 200                        # 语速 (words/min)
  volume: 1.0                      # 音量 (0.0-1.0)

# 语音质量评估配置
quality_assessment:
  enable: true
  language: "zh-CN"
  min_duration: 1.0                # 最小评估时长（秒）
  fillers_detection: true          # 填充词检测
  pace_analysis: true              # 语速分析
```

---

## ✅ 验证安装

### 1. 基础验证

```bash
# 检查 Python 版本
python --version
# 应输出：Python 3.10.x

# 检查虚拟环境
which python
# 应指向 venv 目录

# 检查核心依赖
python -c "import agentscope; print(agentscope.__version__)"
python -c "import yaml; print(yaml.__version__)"
python -c "import rich; print(rich.__version__)"
```

---

### 2. 运行示例

```bash
# 运行 v1.0 综合演示
python examples/v1.0_demo.py

# 预期输出:
# ============================================================
# AgentScope AI Interview - v1.0 综合演示
# ============================================================
# ✓ 核心框架版本：1.0.0
# ✓ 场景系统：已加载 3 个场景
# ✓ 评估系统：7 维度评估就绪
# ✓ 语音支持：STT/TTS 就绪
# ✓ 企业功能：多租户/团队协作就绪
# ============================================================
```

---

### 3. 功能测试

#### 测试 CLI 界面

```bash
python examples/cli_demo.py
```

#### 测试 Web 界面

```bash
# 启动 Web 服务器
python examples/web_demo.py

# 访问浏览器
# http://127.0.0.1:8000
```

#### 测试面试场景

```bash
python examples/interview_demo.py --auto
```

#### 测试语音功能

```bash
python examples/voice_demo.py
```

---

### 4. 运行测试套件

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_core.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

**预期输出**:
```
============================= test session starts ==============================
collected 50 items

tests/test_core.py::test_config_loader PASSED                            [  2%]
tests/test_core.py::test_dialogue_manager PASSED                         [  4%]
tests/test_scenes.py::test_interview_scene PASSED                        [  6%]
...
======================== 50 passed in 15.23s =============================
```

---

## 🔧 故障排除

### 常见问题

#### 1. Python 版本错误

**错误**:
```
ImportError: cannot import name 'xxx' from 'typing'
```

**原因**: Python 版本低于 3.8

**解决方案**:
```bash
# 检查版本
python --version

# 升级 Python
# Windows: 从 python.org 下载安装
# macOS: brew install python@3.10
# Linux: sudo apt install python3.10
```

---

#### 2. 依赖安装失败

**错误**:
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**原因**: pip 版本过旧或网络问题

**解决方案**:
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

#### 3. PyAudio 安装失败（Windows）

**错误**:
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**解决方案**:

方法 1: 使用预编译二进制
```bash
pip install --only-binary :all: pyaudio
```

方法 2: 安装 Visual C++ Build Tools
- 访问：https://visualstudio.microsoft.com/visual-cpp-build-tools/
- 下载并安装 Build Tools
- 重新运行 pip install

---

#### 4. API 密钥错误

**错误**:
```
AuthenticationError: Invalid API key
```

**原因**: API 密钥未设置或错误

**解决方案**:
```bash
# 检查 .env 文件
cat .env

# 重新设置 API 密钥
export DASHSCOPE_API_KEY="your-correct-key"

# 验证
python -c "import os; print(os.getenv('DASHSCOPE_API_KEY'))"
```

---

#### 5. 数据库锁定

**错误**:
```
sqlite3.OperationalError: database is locked
```

**原因**: 多个进程同时访问数据库

**解决方案**:
```bash
# 关闭所有运行中的程序
# 删除数据库锁文件
rm data/interview.db-shm
rm data/interview.db-wal

# 或重建数据库
rm data/interview.db
python scripts/init_db.py
```

---

#### 6. 语音设备不可用

**错误**:
```
OSError: [Errno -9996] Invalid input device
```

**原因**: 麦克风/扬声器未连接或权限问题

**解决方案**:

Linux/macOS:
```bash
# 检查音频设备
arecord -l  # Linux
# 或
system_profiler SPAudioDataType  # macOS

# 检查权限（macOS）
# 系统偏好设置 -> 安全性与隐私 -> 隐私 -> 麦克风
```

Windows:
```bash
# 右键点击任务栏音量图标 -> 声音设置
# 确保麦克风已启用
```

---

#### 7. Web 服务器启动失败

**错误**:
```
Address already in use
```

**原因**: 端口 8000 被占用

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# 杀死进程
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# 或使用其他端口
python examples/web_demo.py --port 8080
```

---

### 日志调试

启用详细日志：

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG

# 运行程序
python examples/v1.0_demo.py
```

查看日志文件：

```bash
# 查看最新日志
tail -f logs/app.log

# 搜索错误
grep ERROR logs/app.log
```

---

## 🗑️ 卸载指南

### 完全卸载

```bash
# 1. 停用虚拟环境
deactivate

# 2. 删除项目目录
cd ..
rm -rf agentscope_ai_interview

# 3. 删除全局安装（如有）
pip uninstall agentscope_ai_interview

# 4. 清理缓存
pip cache purge
```

### 保留数据卸载

```bash
# 1. 备份数据
cp -r agentscope_ai_interview/data ~/backup/interview_data

# 2. 备份配置
cp agentscope_ai_interview/config.yaml ~/backup/

# 3. 删除程序
rm -rf agentscope_ai_interview
```

---

## 📞 获取帮助

如果安装过程中遇到问题：

1. **查看文档**: [QUICKSTART.md](QUICKSTART.md)
2. **检查 Issues**: https://github.com/your-org/agentscope_ai_interview/issues
3. **提交 Issue**: 提供错误信息和系统环境
4. **联系支持**: support@agentscope-interview.example.com

---

**安装愉快！** 🎉

如有问题，请参考 [QUICKSTART.md](QUICKSTART.md) 快速开始使用。
