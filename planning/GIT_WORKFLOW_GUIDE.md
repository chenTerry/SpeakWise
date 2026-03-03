# 🌿 Git工作流指南

## 分支策略

```
main        ────●───────────●───────────●───>  # 稳定生产版本
              v0.1        v0.2        v1.0

develop     ────┼───┬───────┼───┬───────┼───>  # 集成分支
                │   │       │   │       │
feature/v0.1  ───┘   │       │   │       │
feature/v0.2  ───────┘       │   │       │
feature/v0.3  ───────────────┘   │       │
...                             │       │
feature/v1.0  ────────────────────────────┘

task/TASK-001 ────●───────>
task/TASK-002 ────────●───────>
```

### 分支说明

| 分支类型 | 用途 | 保护规则 | 合并规则 |
|----------|------|----------|----------|
| **main** | 生产环境代码 | 保护分支，仅允许PR合并 | 仅从develop合并 |
| **develop** | 集成测试环境 | 保护分支，仅允许PR合并 | 从feature分支合并 |
| **feature/vX.Y** | 特定版本开发 | 无需保护 | 任务完成后合并到develop |
| **task/TASK-XXX** | 具体任务开发 | 无需保护 | 完成后合并到feature分支 |

---

## 🌱 分支操作流程

### 1. 初始化项目
```bash
cd /mnt/e/sourcecode/agentscope_ai_interview
git init
git add .
git commit -m "feat: 初始化项目"
git branch -m main  # 将默认分支重命名为main
git checkout -b develop  # 创建develop分支
git remote add origin <repository-url>  # 如果有远程仓库
```

### 2. 开始新版本开发
```bash
# 从develop创建版本分支
git checkout develop
git checkout -b feature/v0.1

git push -u origin feature/v0.1  # 推送到远程
```

### 3. 开始新任务
```bash
# 从feature分支创建任务分支
git checkout feature/v0.1
git checkout -b task/TASK-001-project-structure

# 开发完成后
git add .
git commit -m "feat(core): 创建项目结构 (TASK-001)"
git push origin task/TASK-001-project-structure
```

### 4. 代码审查与合并
```bash
# 创建PR到feature/v0.1分支
# 经过审查后合并
git checkout feature/v0.1
git merge --no-ff task/TASK-001-project-structure
git push origin feature/v0.1

git branch -d task/TASK-001-project-structure  # 删除本地任务分支
git push origin --delete task/TASK-001-project-structure  # 删除远程任务分支
```

### 5. 版本完成与发布
```bash
# 当所有任务完成
git checkout develop
git merge --no-ff feature/v0.1
git push origin develop

# 发布到main
git checkout main
git merge develop
git tag -a v0.1 -m "Release v0.1 - 核心框架搭建"
git push origin v0.1

git checkout develop  # 回到开发分支继续工作
```

---

## 📝 提交规范

### 提交消息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 类型(type)选项
| 类型 | 描述 | 示例 |
|------|------|------|
| **feat** | 新功能 | `feat(core): 添加对话管理器` |
| **fix** | bug修复 | `fix(dialogue): 修复对话历史记录问题` |
| **docs** | 文档变更 | `docs: 更新API文档` |
| **style** | 代码格式调整 | `style: 修复缩进问题` |
| **refactor** | 代码重构 | `refactor: 优化Agent接口` |
| **test** | 测试相关 | `test: 添加对话管理器测试` |
| **chore** | 构建或辅助工具变更 | `chore: 更新依赖` |

### 作用域(scope)建议
- `core`: 核心框架
- `agent`: Agent相关
- `dialogue`: 对话管理
- `scene`: 场景相关
- `evaluation`: 评估系统
- `ui`: 用户界面
- `config`: 配置系统

### 示例提交消息
```
feat(scene): 实现面试场景MVP

- 实现面试场景框架
- 创建面试官Agent支持3种风格
- 构建50+技术问题库
- 添加基础3维度评估系统
- 完成场景集成测试

TASK-008 TASK-009 TASK-010 TASK-011 TASK-012
```

### 重要规则
1. **必须关联任务**：每个提交必须包含相关任务ID（`TASK-XXX`）
2. **原子提交**：每个提交只做一件事
3. **清晰描述**：提交消息要说明"做了什么"和"为什么做"
4. **保持简洁**：subject行不超过50字符

---

## 🔍 代码审查要求

### 审查清单
- [ ] 代码是否符合编码规范？
- [ ] 是否有必要的单元测试？
- [ ] 文档是否同步更新？
- [ ] 是否解决了关联任务的所有需求？
- [ ] 是否有潜在的性能问题？
- [ ] 是否有安全风险？
- [ ] 提交消息是否符合规范？

### 审查流程
1. 开发者完成任务并提交PR
2. 指定至少1名审查人（通常是相关模块负责人）
3. 审查人在24小时内提供反馈
4. 开发者根据反馈修改
5. 审查通过后合并

### 审查意见模板
```
### 总体评价
[整体评价]

### 需要修改
- [ ] [具体问题1]
- [ ] [具体问题2]

### 建议改进
- [ ] [可选建议1]
- [ ] [可选建议2]

### LGTM
[如果无需修改]
```

---

## 🚀 版本发布流程

### 发布前检查
- [ ] 所有任务已完成并合并到develop
- [ ] 通过所有自动化测试
- [ ] 文档已更新
- [ ] 性能测试达标
- [ ] 安全扫描无高危漏洞

### 发布步骤
1. **创建发布分支**：
   ```bash
git checkout develop
git checkout -b release/v0.1
```

2. **最终测试**：
   - 在发布分支上进行最终测试
   - 修复发现的最后问题

3. **合并到main**：
   ```bash
git checkout main
git merge --no-ff release/v0.1
git push origin main
```

4. **创建标签**：
   ```bash
git tag -a v0.1 -m "Release v0.1 - 核心框架搭建"
git push origin v0.1
```

5. **更新文档**：
   - 更新`VERSION_PLAN.md`中的版本状态
   - 更新`TASK_STATUS.md`
   - 更新用户文档

6. **通知相关方**：
   - 邮件通知团队
   - 更新项目看板
   - 发布更新日志

---

## 🛠️ 常见问题解决

### 合并冲突
1. 拉取最新代码：`git pull origin develop`
2. 解决冲突文件
3. 标记已解决：`git add <resolved-files>`
4. 完成合并：`git commit`

### 回滚变更
```bash
# 查看历史提交
git log

# 回滚到特定提交
git revert <commit-hash>

# 或硬重置（谨慎使用）
git reset --hard <commit-hash>
```

### 恢复已删除分支
```bash
# 查看引用日志
git reflog

# 恢复分支
git branch <branch-name> <commit-hash>
```

---

## 📊 分支管理最佳实践

### 1. 分支生命周期
- **长期分支**：main, develop
- **中期分支**：feature/vX.Y (持续1-4周)
- **短期分支**：task/TASK-XXX (持续1-5天)

### 2. 分支清理
- 完成合并后立即删除任务分支
- 版本发布后可归档feature分支
- 定期清理陈旧分支

### 3. 分支命名规范
- 版本分支：`feature/vX.Y`
- 任务分支：`task/TASK-XXX-description`
- 修复分支：`hotfix/issue-description`

---

## 📌 版本提交示例

### v0.1 版本提交
```
feat(core): 初始化项目框架

- 集成AgentScope基础框架
- 实现基础Agent接口
- 创建对话管理器
- 添加配置加载系统
- 实现命令行测试接口

TASK-001 TASK-002 TASK-003 TASK-004 TASK-005 TASK-006

Signed-off-by: Project Manager <pm@example.com>
```

### v0.2 版本提交
```
feat(scene): 添加面试场景MVP

- 实现面试场景框架
- 创建面试官Agent支持3种风格
- 构建50+技术问题库
- 添加基础3维度评估系统
- 完成场景集成测试

TASK-007 TASK-008 TASK-009 TASK-010 TASK-011 TASK-012

Signed-off-by: Project Manager <pm@example.com>
```

---

**项目经理备注**：
> 严格遵守本工作流指南，确保代码质量和版本控制清晰。  
> **关键原则**：
> - 每个提交都应该是可工作的
> - 保持分支短生命周期
> - 提交消息要清晰有意义
> - 任务与提交严格关联
> 
> 良好的版本控制是团队协作的基础，让我们一起维护好我们的代码库！