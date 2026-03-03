#!/usr/bin/env python3
"""
Feedback Demo - 智能反馈系统演示 (v0.3)

演示 AgentScope AI Interview v0.3 的 7 维度评估系统功能：
- 7 维度智能评估
- 详细反馈生成
- 评估结果持久化
- 多格式报告导出
- 统计分析

运行方式:
    python examples/feedback_demo.py
"""

import logging
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent import Message, MessageType, DialogueContext
from core.config import Config
from evaluation import (
    AdvancedEvaluator,
    AdvancedEvaluationResult,
    EvaluationStorage,
    FeedbackReportGenerator,
    EvaluationDimension7,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_dialogue() -> list[Message]:
    """
    创建示例对话历史

    模拟一个完整的技术面试场景
    """
    messages = []

    # 开场白
    messages.append(Message(
        content="你好！很高兴今天能和你交流。我是今天的面试官，我们先简单开始吧。能先介绍一下你自己吗？",
        role="面试官",
        type=MessageType.AGENT,
    ))

    messages.append(Message(
        content="""你好！我叫李明，有 5 年后端开发经验。目前就职于某互联网公司，主要负责高并发系统的设计和开发。

技术栈方面，我主要使用 Python 和 Go，对微服务架构、分布式系统有比较深入的实践。在之前的工作中，我主导了一个日活千万级的电商平台重构项目，通过引入事件驱动架构和缓存优化，将系统响应时间降低了 60%。

我对技术有浓厚的兴趣，平时会关注业界最新的技术动态，也参与了一些开源项目的贡献。""",
        role="user",
        type=MessageType.USER,
    ))

    # 技术问题 1 - 系统设计
    messages.append(Message(
        content="很好，听起来你有丰富的实战经验。那我想问一个系统设计的问题：如果要你设计一个秒杀系统，你会考虑哪些关键点？",
        role="面试官",
        type=MessageType.AGENT,
    ))

    messages.append(Message(
        content="""设计秒杀系统，我认为需要重点考虑以下几个关键点：

**第一，流量削峰**。秒杀的核心挑战是瞬时大流量，我会采用以下策略：
- 前端层面：按钮防重复点击、验证码增加门槛
- CDN 缓存：将静态资源和商品详情页缓存到 CDN
- 消息队列：将下单请求异步化，用 Kafka 或 RocketMQ 削峰填谷

**第二，库存扣减**。这是秒杀的核心逻辑，我通常采用：
- Redis 预扣减：利用 Redis 的原子操作预先扣减库存
- 数据库最终一致性：异步同步到数据库
- 超卖防护：使用 Lua 脚本保证原子性

**第三，系统保护**：
- 限流熔断：使用 Sentinel 或自研限流组件
- 服务隔离：秒杀服务独立部署，不影响主站
- 降级策略：非核心功能可以降级

**第四，数据一致性**：
- 最终一致性方案
- 对账机制确保数据准确

在我之前的项目中，我们就是通过这套方案，成功支撑了每秒 10 万 + 的 QPS 峰值。""",
        role="user",
        type=MessageType.USER,
    ))

    # 追问 - 技术深度
    messages.append(Message(
        content="你提到了 Redis 预扣减库存，能详细说说具体的实现方案吗？比如如何保证不超卖？",
        role="面试官",
        type=MessageType.AGENT,
    ))

    messages.append(Message(
        content="""好的，我详细说明一下 Redis 扣减库存的实现方案：

**核心思路**是利用 Redis 的原子操作来保证并发安全。

```lua
-- Lua 脚本保证原子性
local stock = tonumber(redis.call('GET', KEYS[1]))
if stock <= 0 then
    return 0  -- 库存不足
end
redis.call('DECR', KEYS[1])
return 1  -- 扣减成功
```

**具体实现步骤**：

1. **预热阶段**：活动开始前，将库存数量加载到 Redis
   ```python
   redis.set('seckill:stock:1001', 1000)
   ```

2. **扣减阶段**：使用 Lua 脚本执行原子扣减
   ```python
   script = """ + """...""" + """
   result = redis.eval(script, 1, 'seckill:stock:1001')
   if result == 1:
       # 扣减成功，发送消息到队列
       kafka.send('order_queue', {'user_id': uid, 'product_id': 1001})
   ```

3. **防超卖机制**：
   - Lua 脚本的原子性保证不会并发读取同一库存
   - 库存扣减和订单创建在同一事务中
   - 数据库层面增加乐观锁版本号

4. **兜底方案**：
   - 定时对账 Redis 和 DB 库存
   - 异常情况下手动干预

**性能优化**：
- 使用 Redis 集群分片存储不同商品库存
- 本地缓存热点商品库存信息
- 批量扣减减少网络开销

这个方案在我们生产环境运行稳定，没有出现超卖问题。""",
        role="user",
        type=MessageType.USER,
    ))

    # 行为问题
    messages.append(Message(
        content="技术细节很清晰。那我想了解一下，在团队合作中，如果和同事有技术分歧，你会怎么处理？",
        role="面试官",
        type=MessageType.AGENT,
    ))

    messages.append(Message(
        content="""这是一个很好的问题。在团队合作中，技术分歧是很常见的，我的处理方式是：

**首先，保持开放心态**。我认为技术讨论的目的是找到最优解，而不是证明谁对谁错。我会认真倾听对方的观点，理解其背后的考虑。

**其次，用数据和事实说话**。比如在之前一个项目中，我和同事在缓存方案上有分歧：
- 他主张用 Redis Cluster
- 我倾向于用 Codis

我没有直接否定他的方案，而是：
1. 列出了两种方案的对比数据
2. 分析了我们的业务场景特点
3. 做了简单的 POC 测试

**最后，达成共识**。通过数据对比，我们发现：
- 我们的数据量不需要 Redis Cluster 的水平扩展
- Codis 的运维成本更低
- 团队对 Codis 更熟悉

最终我们选择了 Codis，项目运行很稳定。

**总结我的原则**：
1. 对事不对人，聚焦问题本身
2. 用数据和实验支撑观点
3. 考虑团队能力和运维成本
4. 一旦做出决定，全力执行

我认为良好的技术讨论能促进团队成长，关键是要有正确的态度和方法。""",
        role="user",
        type=MessageType.USER,
    ))

    # 压力问题
    messages.append(Message(
        content="最后一个问题：如果你的方案在生产环境出现了严重问题，你会怎么处理？",
        role="面试官",
        type=MessageType.AGENT,
    ))

    messages.append(Message(
        content="""这是一个非常实际的问题。我的处理原则是：**先恢复，再定位，后改进**。

**第一步：紧急恢复（5 分钟内）**
- 立即回滚到上一个稳定版本
- 或者启用降级开关，保证核心功能可用
- 通知相关干系人，包括业务方和技术团队

**第二步：问题定位**
- 收集日志、监控指标、链路追踪数据
- 复现问题（在测试环境）
- 组织相关人员进行问题排查

**第三步：修复和验证**
- 制定修复方案
- 充分测试验证
- 灰度发布，观察效果

**第四步：复盘改进**
这是最重要的环节，我会组织复盘会议：
1. **问题回顾**：时间线、影响范围、处理过程
2. **根因分析**：用 5 Why 方法找到根本原因
3. **改进措施**：
   - 技术层面：增加监控、完善测试、改进架构
   - 流程层面：优化发布流程、增加 Code Review
   - 文档层面：更新 Runbook、完善应急预案

**实际案例**：
之前我们遇到过一次缓存穿透导致数据库压力激增的问题：
- 5 分钟内发现并降级
- 1 小时内定位到是恶意请求
- 当天完成修复并上线
- 复盘后增加了布隆过滤器和限流策略

我认为，生产问题不可避免，关键是要有快速响应能力和持续改进的意识。""",
        role="user",
        type=MessageType.USER,
    ))

    # 面试结束
    messages.append(Message(
        content="很好，今天的交流很愉快。你有什么问题想问我的吗？",
        role="面试官",
        type=MessageType.AGENT,
    ))

    messages.append(Message(
        content="谢谢您的时间。我想了解一下，这个岗位所在团队的技术栈和主要业务方向是什么？另外，团队目前面临的最大技术挑战是什么？",
        role="user",
        type=MessageType.USER,
    ))

    messages.append(Message(
        content="好的，我来介绍一下...（面试结束）",
        role="面试官",
        type=MessageType.AGENT,
    ))

    return messages


def demo_basic_evaluation():
    """演示基础评估功能"""
    print("\n" + "=" * 70)
    print("📋 演示 1: 7 维度智能评估")
    print("=" * 70)

    # 创建对话历史
    dialogue = create_sample_dialogue()
    print(f"\n✅ 创建示例对话，共 {len(dialogue)} 条消息")

    # 创建评估器（不使用 LLM，使用规则基础评估）
    config = Config({
        "evaluation": {
            "v03": {
                "weights": {
                    "content_quality": 0.15,
                    "expression_clarity": 0.13,
                    "professional_knowledge": 0.18,
                    "adaptability": 0.12,
                    "communication_skills": 0.14,
                    "confidence_level": 0.13,
                    "innovative_thinking": 0.15,
                }
            }
        }
    })

    evaluator = AdvancedEvaluator(config=config)
    print("✅ 创建 AdvancedEvaluator（规则基础模式）")

    # 执行评估
    print("\n🔄 开始评估...")
    result = evaluator.evaluate(
        dialogue_history=dialogue,
        candidate_info={"name": "李明", "position": "高级后端工程师"},
        interview_info={"domain": "技术面试", "style": "friendly"},
    )

    print(f"✅ 评估完成!")
    print(f"   总体评分：{result.overall_score:.2f} / 5.0")
    print(f"   评级：{result.level}")
    print(f"   摘要：{result.summary}")

    # 显示各维度评分
    print("\n📊 7 维度评分详情:")
    dimension_names = {
        EvaluationDimension7.CONTENT_QUALITY: "内容质量",
        EvaluationDimension7.EXPRESSION_CLARITY: "表达清晰度",
        EvaluationDimension7.PROFESSIONAL_KNOWLEDGE: "专业知识",
        EvaluationDimension7.ADAPTABILITY: "应变能力",
        EvaluationDimension7.COMMUNICATION_SKILLS: "沟通技巧",
        EvaluationDimension7.CONFIDENCE_LEVEL: "自信程度",
        EvaluationDimension7.INNOVATIVE_THINKING: "创新思维",
    }

    for dim, name in dimension_names.items():
        score = result.get_score(dim)
        bar = "█" * int(score / 0.5) + "░" * (10 - int(score / 0.5))
        print(f"   {name}: [{bar}] {score:.2f}")

    return result, dialogue


def demo_report_generation(result: AdvancedEvaluationResult):
    """演示报告生成功能"""
    print("\n" + "=" * 70)
    print("📄 演示 2: 多格式报告生成")
    print("=" * 70)

    report_gen = FeedbackReportGenerator()
    print("✅ 创建 FeedbackReportGenerator")

    candidate_info = {"name": "李明", "position": "高级后端工程师"}
    interview_info = {"domain": "技术面试", "style": "friendly", "duration": 30}

    # 生成文本报告
    print("\n📝 生成文本格式报告:")
    print("-" * 40)
    text_report = report_gen.generate(
        result, format="text", template="standard",
        candidate_info=candidate_info, interview_info=interview_info,
    )
    print(text_report[:500] + "...")

    # 生成 Markdown 报告
    print("\n📝 生成 Markdown 格式报告 (预览):")
    print("-" * 40)
    md_report = report_gen.generate(
        result, format="markdown", template="detailed",
        candidate_info=candidate_info, interview_info=interview_info,
    )
    print(md_report[:400] + "...")

    # 导出到文件
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # 导出 Markdown
    md_path = output_dir / "evaluation_report.md"
    report_gen.export_to_file(
        result, md_path, format="markdown", template="standard",
        candidate_info=candidate_info, interview_info=interview_info,
    )
    print(f"\n✅ Markdown 报告已导出：{md_path}")

    # 导出 HTML
    html_path = output_dir / "evaluation_report.html"
    report_gen.export_to_file(
        result, html_path, format="html", template="standard",
        candidate_info=candidate_info, interview_info=interview_info,
    )
    print(f"✅ HTML 报告已导出：{html_path}")

    # 导出 JSON
    json_path = output_dir / "evaluation_report.json"
    report_gen.export_to_file(
        result, json_path, format="json", template="standard",
        candidate_info=candidate_info, interview_info=interview_info,
    )
    print(f"✅ JSON 报告已导出：{json_path}")


def demo_storage_and_analytics(result: AdvancedEvaluationResult):
    """演示存储和分析功能"""
    print("\n" + "=" * 70)
    print("💾 演示 3: 评估存储与统计分析")
    print("=" * 70)

    # 创建存储
    db_path = Path(__file__).parent / "output" / "evaluations.db"
    storage = EvaluationStorage(db_path=str(db_path))
    print(f"✅ 创建 EvaluationStorage: {db_path}")

    # 保存评估结果（使用唯一 session_id）
    session_id = f"demo_session_{int(time.time())}"
    record_id = storage.save_evaluation(
        result,
        session_id=session_id,
        candidate_info={"name": "李明", "position": "高级后端工程师"},
        interview_info={"domain": "技术面试", "style": "friendly"},
    )
    print(f"✅ 评估结果已保存，记录 ID: {record_id}")

    # 查询评估记录
    record = storage.get_evaluation_by_session(session_id)
    if record:
        print(f"\n📋 查询评估记录:")
        print(f"   候选人：{record.candidate_name}")
        print(f"   岗位：{record.position}")
        print(f"   总体评分：{record.overall_score:.2f}")
        print(f"   评级：{record.level}")

    # 获取统计数据
    print("\n📊 获取统计数据:")
    stats = storage.get_statistics()
    print(f"   总评估数：{stats.total_evaluations}")
    print(f"   平均分：{stats.avg_score:.2f}")
    print(f"   等级分布：{stats.level_distribution}")
    print(f"   维度平均分：{stats.dimension_averages}")

    # 趋势分析
    print("\n📈 趋势分析:")
    trend = storage.get_trend_analysis(days=30)
    if trend:
        for data in trend:
            print(f"   {data['period']}: 平均分 {data['avg_score']:.2f}, 数量 {data['count']}")
    else:
        print("   暂无足够数据进行趋势分析")

    # 搜索功能
    print("\n🔍 搜索评估记录:")
    results = storage.search_evaluations(min_score=3.0, level="A")
    print(f"   找到 {len(results)} 条符合条件的记录")

    storage.close()
    print("\n✅ 存储演示完成")


def demo_single_answer_evaluation():
    """演示单个回答评估"""
    print("\n" + "=" * 70)
    print("🎯 演示 4: 单个回答评估")
    print("=" * 70)

    config = Config()
    evaluator = AdvancedEvaluator(config=config)

    sample_answer = """
    对于这个问题，我认为需要从三个层面来分析：

    首先，从技术层面，我们需要考虑系统的可扩展性和性能。
    采用微服务架构可以很好地解决这些问题。

    其次，从业务层面，我们需要理解核心业务流程，
    确保技术方案能够支撑业务发展。

    最后，从团队层面，要考虑团队的技术栈和能力，
    选择适合团队的技术方案。
    """

    print(f"\n📝 评估回答:\n{sample_answer[:100]}...")

    # 评估所有维度
    scores = evaluator.evaluate_single_answer(sample_answer)
    print("\n📊 各维度评分:")
    for dim, score in scores.items():
        print(f"   {dim}: {score:.2f}")


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🤖 AgentScope AI Interview v0.3")
    print("   智能反馈系统演示")
    print("=" * 70)

    try:
        # 演示 1: 基础评估
        result, dialogue = demo_basic_evaluation()

        # 演示 2: 报告生成
        demo_report_generation(result)

        # 演示 3: 存储与分析
        demo_storage_and_analytics(result)

        # 演示 4: 单个回答评估
        demo_single_answer_evaluation()

        print("\n" + "=" * 70)
        print("✅ 所有演示完成!")
        print("=" * 70)
        print("\n💡 提示:")
        print("   - 查看生成的报告文件：examples/output/")
        print("   - 要使用 LLM 评估，需要配置 AgentScope ModelAgent")
        print("   - 参考 documentation 了解更多功能")
        print("")

    except Exception as e:
        logger.error(f"演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
