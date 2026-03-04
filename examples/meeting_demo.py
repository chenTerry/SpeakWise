"""
Meeting Demo - 会议场景演示示例

演示如何使用会议场景进行多种会议类型模拟。

功能展示:
1. 创建和初始化会议场景
2. 支持多种会议类型（站会、需求评审、冲突解决等）
3. 会议流程管理
4. 行动项跟踪
5. 场景评估和反馈

运行方式:
    python examples/meeting_demo.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenes.meeting import (
    MeetingScene,
    MeetingSceneConfig,
    MeetingType,
    MeetingPhase,
)
from core.agent import Message, DialogueContext, MessageType
from evaluation.meeting_evaluator import MeetingEvaluator


def demo_standup_meeting():
    """站会场景演示"""
    print("=" * 60)
    print("会议场景演示 - 每日站会")
    print("=" * 60)
    print()

    # 创建站会配置
    config = MeetingSceneConfig(
        meeting_type=MeetingType.STANDUP,
        project_name="电商平台重构",
        agenda=[
            "昨日完成工作",
            "今日计划",
            "阻塞问题",
        ],
        duration_minutes=15,
        participant_count=4,
    )

    # 创建场景
    scene = MeetingScene(config=config)

    # 初始化场景
    print("📋 初始化站会场景...")
    if not scene.initialize():
        print("❌ 初始化失败")
        return

    print(f"✅ 初始化成功，共{len(scene.get_agents())}个 Agent")
    print()

    # 启动场景
    print("🚀 开始站会...")
    opening = scene.start()
    print(f"\n【{opening.role}】{opening.content}")
    print()

    # 模拟站会发言
    context = DialogueContext()
    standup_updates = [
        "昨天完成了用户模块的重构，今天开始订单模块，没有阻塞。",
        "昨天修复了 3 个 bug，今天继续测试，需要产品确认一个需求细节。",
        "昨天完成了接口文档，今天开始实现，暂无问题。",
        "昨天参与了需求评审，今天准备测试用例，需要等开发完成。",
    ]

    for i, content in enumerate(standup_updates, 1):
        print(f"\n--- 参与者{i}发言 ---")
        print(f"\n【用户】{content}")

        message = Message(
            content=content,
            role="user",
            type=MessageType.USER,
        )

        response = scene.handle_message(message, context)
        print(f"\n【{response.role}】{response.content[:150]}...")

    # 获取统计信息
    stats = scene.get_meeting_stats()
    print("\n📈 会议统计:")
    print(f"  - 阶段：{stats['phase']}")
    print(f"  - 轮次：{stats['current_turn']}")
    print(f"  - 议程进度：{stats['current_agenda_item']}/{stats['agenda_total']}")
    print(f"  - 行动项：{stats['action_items_count']}个")
    print(f"  - 决策：{stats['decisions_count']}个")

    # 获取行动项
    action_items = scene.get_action_items()
    if action_items:
        print("\n📝 行动项:")
        for item in action_items:
            print(f"  - {item.get('content', '')}")

    # 清理
    scene.cleanup()
    print("\n✅ 站会演示完成")


def demo_requirement_review():
    """需求评审会演示"""
    print("\n" + "=" * 60)
    print("会议场景演示 - 需求评审会")
    print("=" * 60)
    print()

    config = MeetingSceneConfig(
        meeting_type=MeetingType.REQUIREMENT_REVIEW,
        project_name="智能推荐系统",
        agenda=[
            "需求背景介绍",
            "功能点评审",
            "技术可行性讨论",
            "风险评估",
        ],
        duration_minutes=45,
    )

    scene = MeetingScene(config=config)

    if not scene.initialize():
        return

    # 启动
    opening = scene.start()
    print(f"【{opening.role}】{opening.content[:100]}...")

    # 模拟需求讨论
    context = DialogueContext()
    discussions = [
        "这个推荐算法的需求，从技术角度看实现难度如何？",
        "用户反馈的实时性要求，我们能否满足？",
        "建议先做 A/B 测试验证效果。",
    ]

    for content in discussions:
        print(f"\n【用户】{content}")
        message = Message(content=content, role="user", type=MessageType.USER)
        response = scene.handle_message(message, context)
        print(f"\n【{response.role}】{response.content[:150]}...")

    # 评估
    stats = scene.get_meeting_stats()
    stats["session_id"] = "requirement_review_001"

    print("\n📊 生成评估报告...")
    evaluator = MeetingEvaluator()
    result = evaluator.evaluate(
        context, stats,
        meeting_type="requirement_review",
        user_role="tech_lead",
    )

    report = evaluator.generate_report(result, format="text")
    print("\n" + report)

    scene.cleanup()


def demo_conflict_resolution():
    """冲突解决会演示"""
    print("\n" + "=" * 60)
    print("会议场景演示 - 冲突解决会")
    print("=" * 60)
    print()

    config = MeetingSceneConfig(
        meeting_type=MeetingType.CONFLICT_RESOLUTION,
        project_name="团队协作改进",
        agenda=[
            "问题陈述",
            "各方观点",
            "寻找共识",
            "解决方案",
        ],
        duration_minutes=30,
    )

    scene = MeetingScene(config=config)

    if not scene.initialize():
        return

    # 启动
    opening = scene.start()
    print(f"【{opening.role}】{opening.content[:100]}...")

    # 模拟冲突讨论
    context = DialogueContext()
    discussions = [
        "我觉得在代码审查流程上我们有不同看法，我想说说我的观点。",
        "我理解你的顾虑，但从项目进度角度...",
        "或许我们可以找一个平衡点，既保证质量又不影响进度。",
    ]

    for content in discussions:
        print(f"\n【用户】{content}")
        message = Message(content=content, role="user", type=MessageType.USER)
        response = scene.handle_message(message, context)
        print(f"\n【{response.role}】{response.content[:150]}...")

    scene.cleanup()
    print("\n✅ 冲突解决会演示完成")


def demo_meeting_phases():
    """演示会议各阶段"""
    print("\n" + "=" * 60)
    print("会议场景演示 - 阶段展示")
    print("=" * 60)
    print()

    config = MeetingSceneConfig(
        meeting_type=MeetingType.PROJECT_KICKOFF,
        project_name="演示项目",
        agenda=["项目介绍", "分工讨论", "时间计划"],
    )
    scene = MeetingScene(config=config)

    if not scene.initialize():
        return

    # 启动
    scene.start()
    print(f"当前阶段：{scene.get_current_phase().value}")

    context = DialogueContext()

    # 遍历各阶段
    phases = [
        MeetingPhase.OPENING,
        MeetingPhase.ROUND_TABLE,
        MeetingPhase.DISCUSSION,
        MeetingPhase.SUMMARY,
        MeetingPhase.ACTION_ITEMS,
        MeetingPhase.CLOSING,
    ]

    for phase in phases:
        scene.switch_phase(phase)
        print(f"\n📍 阶段：{phase.value}")

        message = Message(
            content=f"{phase.value}阶段测试消息",
            role="user",
            type=MessageType.USER,
        )
        response = scene.handle_message(message, context)
        print(f"响应角色：{response.role}")

    scene.cleanup()


def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("AgentScope AI Interview - v0.5 会议场景演示")
    print("🎯" * 30)

    try:
        # 运行演示
        demo_standup_meeting()
        demo_requirement_review()
        demo_conflict_resolution()
        # demo_meeting_phases()  # 可选：展示阶段切换

    except Exception as e:
        print(f"\n❌ 演示出错：{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("演示结束")
    print("=" * 60)


if __name__ == "__main__":
    main()
