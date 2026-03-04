# 🚀 AgentScope AI Interview - Quick Start Guide

**版本**: v1.0.0  
**最后更新**: 2026-03-04  
**预计阅读时间**: 5 分钟

---

## 📋 目录

1. [5 分钟快速开始](#5-分钟快速开始)
2. [基本使用示例](#基本使用示例)
3. [常见场景](#常见场景)
4. [下一步学习](#下一步学习)

---

## ⏱️ 5 分钟快速开始

### 前提条件

- ✅ Python 3.8+ 已安装
- ✅ 已克隆项目代码
- ✅ 已安装依赖 (`pip install -r requirements.txt`)
- ✅ 已配置 API 密钥 (`.env` 文件)

---

### 第 1 分钟：验证安装

```bash
# 进入项目目录
cd agentscope_ai_interview

# 运行版本检查
python -c "from core import __version__; print(f'版本：{__version__}')"
# 输出：版本：1.0.0
```

---

### 第 2 分钟：运行综合演示

```bash
# 运行 v1.0 综合演示
python examples/v1.0_demo.py
```

**预期输出**:
```
============================================================
AgentScope AI Interview - v1.0 综合演示
============================================================
✓ 核心框架版本：1.0.0
✓ 场景系统：已加载 3 个场景
✓ 评估系统：7 维度评估就绪
✓ 语音支持：STT/TTS 就绪
✓ 企业功能：多租户/团队协作就绪
============================================================

[演示] 开始面试场景模拟...
[面试官] 你好，欢迎参加今天的面试。我是张面试官...
```

---

### 第 3 分钟：体验 CLI 界面

```bash
# 启动 CLI 交互界面
python examples/cli_demo.py
```

**CLI 菜单**:
```
╔══════════════════════════════════════════════════════════╗
║       AgentScope AI Interview - 主菜单                    ║
╠══════════════════════════════════════════════════════════╣
║  1. 🎤 面试模拟                                          ║
║  2. 🎭 沙龙讨论                                          ║
║  3. 🏢 项目会议                                          ║
║  4. 📊 我的进度                                          ║
║  5. ⚙️  设置                                             ║
║  0. 退出                                                 ║
╚══════════════════════════════════════════════════════════╝
请选择 [0-5]: 
```

---

### 第 4 分钟：启动 Web 界面

```bash
# 启动 Web 服务器
python examples/web_demo.py
```

**访问浏览器**:
- 主界面：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs

---

### 第 5 分钟：查看评估报告

```bash
# 运行评估演示
python examples/feedback_demo.py
```

**示例输出**:
```
╔══════════════════════════════════════════════════════════╗
║                    评估报告                               ║
╠══════════════════════════════════════════════════════════╣
║  总体评分：4.2/5.0 ⭐⭐⭐⭐                                ║
║                                                          ║
║  维度评分：                                              ║
║  • 内容质量：4.5/5.0                                     ║
║  • 表达清晰度：4.0/5.0                                   ║
║  • 专业知识：4.3/5.0                                     ║
║  • 逻辑思维：4.0/5.0                                     ║
║  • 应变能力：4.2/5.0                                     ║
║  • 沟通技巧：4.1/5.0                                     ║
║  • 职业素养：4.3/5.0                                     ║
║                                                          ║
║  优势：                                                  ║
║  ✓ 技术知识点回答准确                                    ║
║  ✓ 表达条理清晰                                          ║
║                                                          ║
║  改进建议：                                              ║
║  • 可以增加具体项目案例                                  ║
║  • 注意控制回答时长                                      ║
╚══════════════════════════════════════════════════════════╝
```

---

## 💡 基本使用示例

### 示例 1: 技术面试模拟

```bash
# 运行面试演示（交互模式）
python examples/interview_demo.py

# 或指定风格和领域
python examples/interview_demo.py --style strict --domain frontend

# 或自动演示模式
python examples/interview_demo.py --auto
```

**交互示例**:
```
[面试官] 你好，欢迎参加今天的面试。我是张面试官，负责前端开发岗位的面试。
        首先，请你做一个简单的自我介绍。

[你] 你好，我是一名有 3 年经验的前端工程师...

[面试官] 很好。那我问你一个问题：React 中的 useEffect 和 useLayoutEffect 
        有什么区别？

[你] useEffect 是异步执行的，在 DOM 更新后执行...

[面试官] 回答得不错。那我追问一下，如果在 useEffect 中依赖项设置错误，
        可能会导致什么问题？
...
```

---

### 示例 2: 沙龙场景模拟

```bash
# 运行沙龙演示
python examples/salon_demo.py
```

**场景描述**:
- **主题**: AI 技术在开发中的应用
- **角色**: 主持人、演讲者、观众、观察者
- **流程**: 开场 → 主题演讲 → 自由讨论 → 总结

---

### 示例 3: 会议场景模拟

```bash
# 运行会议演示
python examples/meeting_demo.py
```

**支持的会议类型**:
- 📋 每日站会 (Standup)
- 📝 需求评审 (Requirement Review)
- 🔥 冲突解决 (Conflict Resolution)
- 🚀 项目启动 (Project Kickoff)
- 📊 复盘会议 (Retrospective)

---

### 示例 4: 场景切换

```bash
# 运行场景管理器演示
python examples/scene_manager_demo.py
```

**场景切换示例**:
```python
from scenes.manager import SceneManager

# 创建场景管理器
manager = SceneManager()

# 创建多个场景
manager.create_scene("interview", style="friendly")
manager.create_scene("salon", topic="AI 技术")
manager.create_scene("meeting", meeting_type="standup")

# 激活场景
manager.activate_scene("interview")

# 切换到沙龙场景（保持上下文）
manager.switch_scene("salon", preserve_context=True)
```

---

### 示例 5: 查看学习进度

```bash
# 运行用户系统演示
python examples/user_system_demo.py
```

**进度报告示例**:
```
╔══════════════════════════════════════════════════════════╗
║                  学习进度报告                             ║
╠══════════════════════════════════════════════════════════╣
║  用户：demo_user                                         ║
║  注册日期：2026-02-01                                    ║
║  总会话数：15                                            ║
║                                                          ║
║  能力雷达图：                                            ║
║                                                          ║
║              内容质量                                    ║
║                  ● 4.5                                   ║
║                 / \                                      ║
║                /   \                                     ║
║     职业素养 4.3   4.0 表达清晰度                        ║
║              \   /                                       ║
║               \ /                                        ║
║                ● 4.2                                     ║
║              沟通技巧                                    ║
║                                                          ║
║  趋势分析：                                              ║
║  📈 内容质量：+0.3 (上升)                                ║
║  📈 表达清晰度：+0.2 (上升)                              ║
║  ➡️  逻辑思维：0.0 (稳定)                                ║
╚══════════════════════════════════════════════════════════╝
```

---

### 示例 6: 语音对话

```bash
# 运行语音演示
python examples/voice_demo.py
```

**语音功能**:
- 🎤 **语音输入**: 说话自动转文字
- 🔊 **语音输出**: 文字自动朗读
- 📊 **质量评估**: 发音/语速/流畅度分析
- ⏯️ **语音回放**: 录制回放、变速播放

---

### 示例 7: 数据分析报告

```bash
# 运行数据分析演示
python examples/analytics_demo.py
```

**分析报告内容**:
- 📊 学习画像（技能水平、学习模式）
- 📈 行为追踪（会话频率、改进趋势）
- 💡 个性化推荐（主题推荐、学习路径）
- 📉 统计分析（百分位数、分布分析）
- 🏆 成就系统（里程碑、连续天数）

---

### 示例 8: 企业协作

```bash
# 运行企业版演示
python examples/enterprise_demo.py
```

**企业功能**:
- 👥 **多租户管理**: 租户创建/升级/统计
- 🤝 **团队协作**: 团队创建/成员管理/角色权限
- 📊 **管理员仪表盘**: 用户统计、会话分析
- 🔐 **SSO 集成**: OAuth2/SAML/LDAP 登录

---

## 🎯 常见场景

### 场景 1: 面试练习

**目标**: 准备技术面试

```bash
# 1. 选择面试领域
python examples/interview_demo.py --domain frontend

# 2. 选择面试风格
python examples/interview_demo.py --style strict  # 严格风格

# 3. 查看评估报告
python examples/feedback_demo.py

# 4. 针对性改进后再次练习
python examples/interview_demo.py --domain frontend
```

**推荐流程**:
1. 友好风格热身 → 2. 严格风格挑战 → 3. 压力风格实战

---

### 场景 2: 沙龙演讲练习

**目标**: 提升演讲和表达能力

```bash
# 1. 创建沙龙场景
python examples/salon_demo.py

# 2. 选择演讲者角色
# 在菜单中选择"演讲者"

# 3. 进行主题演讲
# 系统会模拟观众提问和互动

# 4. 查看评估报告
# 关注"知识贡献"和"沟通风格"维度
```

---

### 场景 3: 会议主持练习

**目标**: 提升会议主持和协调能力

```bash
# 1. 创建会议场景
python examples/meeting_demo.py

# 2. 选择会议类型
# 推荐：需求评审 或 冲突解决

# 3. 担任主持人角色
# 系统会模拟参会者和突发情况

# 4. 查看评估报告
# 关注"会议效率"和"沟通效果"维度
```

---

### 场景 4: 长期能力提升

**目标**: 系统性地提升沟通能力

```bash
# 第 1 周：基线评估
python examples/interview_demo.py --auto
python examples/feedback_demo.py  # 记录初始分数

# 第 2-4 周：针对性练习
# 每天 15 分钟，选择薄弱环节练习

# 第 4 周：进度评估
python examples/user_system_demo.py  # 查看进度报告
python examples/analytics_demo.py    # 查看详细分析

# 根据推荐继续练习
```

---

### 场景 5: 团队培训

**目标**: 企业团队沟通能力培训

```bash
# 1. 创建团队
python examples/enterprise_demo.py

# 2. 邀请成员加入
# 使用团队邀请码

# 3. 分配练习任务
# 管理员设置练习主题和截止日期

# 4. 查看团队报告
# 管理员仪表盘查看整体进度

# 5. 导出培训报告
python examples/analytics_demo.py --export pdf
```

---

## 📚 下一步学习

### 深入文档

| 文档 | 内容 | 阅读时间 |
|------|------|----------|
| [INSTALL.md](INSTALL.md) | 详细安装指南 | 10 分钟 |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | 版本发布说明 | 15 分钟 |
| [CHANGELOG.md](CHANGELOG.md) | 完整变更日志 | 20 分钟 |
| docs/USER_GUIDE.md | 用户指南 | 30 分钟 |
| docs/DEVELOPER_GUIDE.md | 开发者文档 | 60 分钟 |

---

### 示例代码学习

```bash
# 基础示例
python examples/basic_conversation.py    # 基础对话
python examples/interview_demo.py        # 面试场景

# 进阶示例
python examples/scene_manager_demo.py    # 场景管理
python examples/voice_demo.py            # 语音功能
python examples/analytics_demo.py        # 数据分析

# 企业示例
python examples/enterprise_demo.py       # 企业功能
```

---

### 配置自定义

```bash
# 1. 复制示例配置
cp examples/config.example.yaml config.yaml

# 2. 编辑配置文件
vim config.yaml

# 3. 测试配置
python examples/v1.0_demo.py
```

**常用配置项**:
- 模型选择（deepseek/gpt-4）
- 面试风格（friendly/strict/pressure）
- 评估权重调整
- 语音设置

---

### 加入社区

- **GitHub**: https://github.com/your-org/agentscope_ai_interview
- **Issues**: 报告 Bug 或请求新功能
- **Discussions**: 提问和分享经验
- **Email**: support@agentscope-interview.example.com

---

## 🎓 学习路径推荐

### 初学者路径

```
Day 1: 快速开始 → CLI 界面体验
Day 2: 面试场景练习（友好风格）
Day 3: 查看评估报告，了解评分维度
Day 4-7: 每日练习，尝试不同领域
Week 2: 挑战严格风格，查看进度报告
```

---

### 进阶用户路径

```
Week 1: 多场景体验（面试/沙龙/会议）
Week 2: 语音功能练习
Week 3: 数据分析，识别薄弱环节
Week 4: 针对性强化练习
Month 2: 团队竞赛，互相学习
```

---

### 企业用户路径

```
Day 1: 管理员培训（租户/团队管理）
Day 2: 成员邀请和权限配置
Week 1: 团队练习任务发布
Week 2-4: 持续练习和进度追踪
Month 2: 培训效果评估和报告
```

---

## ❓ 常见问题

### Q: 如何保存我的练习记录？

A: 系统会自动保存所有会话记录。使用 `python examples/user_system_demo.py` 查看历史记录。

---

### Q: 可以自定义面试问题吗？

A: 可以。编辑 `scenes/interview/questions.yaml` 添加自定义问题。

---

### Q: 如何切换不同的 AI 模型？

A: 在 `config.yaml` 中修改 `model.name` 配置项，可选 `deepseek-chat` 或 `gpt-4`。

---

### Q: 语音功能无法使用怎么办？

A: 检查麦克风权限和音频设备配置。参考 [INSTALL.md](INSTALL.md) 故障排除章节。

---

### Q: 如何导出评估报告？

A: 使用 `python examples/analytics_demo.py --export pdf` 导出 PDF 报告。

---

## 🎉 开始你的练习之旅！

现在你已经了解了基础知识，开始练习吧：

```bash
# 开始第一次面试模拟
python examples/interview_demo.py

# 或启动 Web 界面
python examples/web_demo.py
```

**祝你学习愉快！** 🚀

---

*Last updated: 2026-03-04*
