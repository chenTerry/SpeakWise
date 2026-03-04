"""
Salon Demo - 沙龙场景演示示例

演示如何使用沙龙场景进行多角色对话模拟。

功能展示:
1. 创建和初始化沙龙场景
2. 配置沙龙主题和风格
3. 多轮对话交互
4. 场景评估和反馈

运行方式:
    python examples/salon_demo.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenes.salon import (
    SalonScene,
    SalonSceneConfig,
    SalonPhase,
)
from core.agent import Message, DialogueContext, MessageType
from evaluation.salon_evaluator import SalonEvaluator


def demo_basic_salon():
    """基础沙龙场景演示"""
    print("=" * 60)
    print("沙龙场景演示 - 基础用法")
    print("=" * 60)
    print()

    # 创建沙龙配置
    config = SalonSceneConfig(
        topic="AI 技术在开发中的应用",
        speaker_topic="大模型辅助编程实践",
        discussion_style="casual",
    )

    # 创建场景
    scene = SalonScene(config=config)

    # 初始化场景
    print("📋 初始化沙龙场景...")
    if not scene.initialize():
        print("❌ 初始化失败")
        return

    print(f"✅ 初始化成功，共{len(scene.get_agents())}个 Agent")
    print()

    # 启动场景
    print("🚀 启动沙龙...")
    opening = scene.start()
    print(f"\n【{opening.role}】{opening.content}")
    print()

    # 模拟对话
    context = DialogueContext()
    user_messages = [
        "大家好，我对 AI 辅助编程很感兴趣，想听听大家的经验。",
        "刚才提到的代码生成工具，在实际项目中准确率如何？",
        "我担心过度依赖 AI 会影响自己的编程能力，大家怎么看？",
        "感谢分享，收获很大！",
    ]

    for i, content in enumerate(user_messages, 1):
        print(f"\n--- 第{i}轮对话 ---")
        print(f"\n【用户】{content}")

        message = Message(
            content=content,
            role="user",
            type=MessageType.USER,
        )

        response = scene.handle_message(message, context)
        print(f"\n【{response.role}】{response.content[:200]}...")

        # 检查场景状态
        if scene.is_completed():
            print("\n📊 沙龙已结束")
            break

    # 获取统计信息
    stats = scene.get_salon_stats()
    print("\n📈 沙龙统计:")
    print(f"  - 阶段：{stats['phase']}")
    print(f"  - 轮次：{stats['current_turn']}")
    print(f"  - 关键点：{stats['key_points_count']}个")
    print(f"  - 问题：{stats['questions_count']}个")

    # 清理
    scene.cleanup()
    print("\n✅ 演示完成")


def demo_salon_with_evaluation():
    """带评估的沙龙场景演示"""
    print("\n" + "=" * 60)
    print("沙龙场景演示 - 带评估反馈")
    print("=" * 60)
    print()

    # 创建场景
    config = SalonSceneConfig(
        topic="技术团队管理",
        speaker_topic="敏捷团队的建设与实践",
        discussion_style="formal",
    )
    scene = SalonScene(config=config)

    if not scene.initialize():
        print("❌ 初始化失败")
        return

    # 启动场景
    opening = scene.start()
    print(f"【{opening.role}】{opening.content[:100]}...")

    # 模拟对话
    context = DialogueContext()
    messages = [
        "作为技术管理者，如何平衡业务压力和技术债务？",
        "在推行敏捷实践时遇到的最大挑战是什么？",
    ]

    for content in messages:
        message = Message(content=content, role="user", type=MessageType.USER)
        response = scene.handle_message(message, context)
        print(f"\n【{response.role}】{response.content[:150]}...")

    # 获取统计
    stats = scene.get_salon_stats()
    stats["session_id"] = "demo_001"

    # 评估表现
    print("\n📊 生成评估报告...")
    evaluator = SalonEvaluator()
    result = evaluator.evaluate(context, stats, user_role="audience")

    # 打印报告
    report = evaluator.generate_report(result, format="text")
    print("\n" + report)

    # 清理
    scene.cleanup()


def demo_salon_phases():
    """演示沙龙各阶段"""
    print("\n" + "=" * 60)
    print("沙龙场景演示 - 阶段展示")
    print("=" * 60)
    print()

    config = SalonSceneConfig(
        topic="云计算技术",
        speaker_topic="容器化部署最佳实践",
        discussion_style="casual",
    )
    scene = SalonScene(config=config)

    if not scene.initialize():
        return

    # 启动
    scene.start()
    print(f"当前阶段：{scene.get_current_phase().value}")

    # 手动切换阶段展示
    from scenes.salon import SalonPhase

    phases = [
        SalonPhase.OPENING,
        SalonPhase.PRESENTATION,
        SalonPhase.Q_AND_A,
        SalonPhase.DISCUSSION,
        SalonPhase.SUMMARY,
        SalonPhase.CLOSING,
    ]

    context = DialogueContext()

    for phase in phases:
        scene.switch_phase(phase)
        print(f"\n📍 切换到阶段：{phase.value}")

        message = Message(
            content=f"这是{phase.value}阶段的测试消息",
            role="user",
            type=MessageType.USER,
        )
        response = scene.handle_message(message, context)
        print(f"响应角色：{response.role}")

    scene.cleanup()


def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("AgentScope AI Interview - v0.5 沙龙场景演示")
    print("🎯" * 30)

    try:
        # 运行演示
        demo_basic_salon()
        demo_salon_with_evaluation()
        # demo_salon_phases()  # 可选：展示阶段切换

    except Exception as e:
        print(f"\n❌ 演示出错：{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("演示结束")
    print("=" * 60)


if __name__ == "__main__":
    main()
