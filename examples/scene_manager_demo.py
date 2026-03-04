"""
Scene Manager Demo - 场景管理器演示示例

演示如何使用场景管理器进行多场景切换和状态管理。

功能展示:
1. 创建和管理多个场景
2. 场景切换和上下文保持
3. 场景状态序列化/反序列化
4. 跨场景对话连续性

运行方式:
    python examples/scene_manager_demo.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scenes.manager import SceneManager, SceneTransition
from core.agent import Message, DialogueContext, MessageType


def demo_basic_scene_management():
    """基础场景管理演示"""
    print("=" * 60)
    print("场景管理器演示 - 基础用法")
    print("=" * 60)
    print()

    # 创建场景管理器
    manager = SceneManager()

    # 创建多个场景
    print("📋 创建场景...")

    # 创建面试场景
    interview_key = manager.create_scene(
        "interview",
        scene_key="my_interview",
        style="friendly",
        domain="tech",
    )
    print(f"✅ 创建面试场景：{interview_key}")

    # 创建沙龙场景
    salon_key = manager.create_scene(
        "salon",
        scene_key="my_salon",
        topic="AI 技术应用",
        discussion_style="casual",
    )
    print(f"✅ 创建沙龙场景：{salon_key}")

    # 创建会议场景
    meeting_key = manager.create_scene(
        "meeting",
        scene_key="my_meeting",
        meeting_type="standup",
        project_name="演示项目",
    )
    print(f"✅ 创建会议场景：{meeting_key}")

    # 列出所有场景
    print("\n📂 已创建的场景:")
    scenes = manager.list_scenes()
    for scene in scenes:
        active_marker = "🟢" if scene["active"] else "⚪"
        print(f"  {active_marker} {scene['key']}: {scene['type']} ({scene['state']})")

    # 激活场景
    print("\n🚀 激活面试场景...")
    manager.activate_scene("my_interview")

    # 获取活跃场景
    active_scene = manager.get_active_scene()
    if active_scene:
        print(f"✅ 当前活跃场景：{active_scene.get_scene_type()}")

    # 清理
    manager.clear()
    print("\n✅ 演示完成")


def demo_scene_switching():
    """场景切换演示"""
    print("\n" + "=" * 60)
    print("场景管理器演示 - 场景切换")
    print("=" * 60)
    print()

    manager = SceneManager()

    # 创建场景
    manager.create_scene("interview", scene_key="interview", style="friendly")
    manager.create_scene("salon", scene_key="salon", topic="技术沙龙")
    manager.create_scene("meeting", scene_key="meeting", meeting_type="standup")

    # 激活初始场景
    manager.activate_scene("interview")
    print("📍 当前场景：interview")

    # 模拟对话
    context = manager.get_global_context()

    print("\n--- 在面试场景中对话 ---")
    message1 = Message(
        content="你好，我想了解一下这个职位的要求。",
        role="user",
        type=MessageType.USER,
    )
    response1, transition1 = manager.handle_message(message1, context)
    print(f"响应：{response1.content[:100]}...")

    # 切换到沙龙场景
    print("\n🔄 切换到沙龙场景...")
    transition = manager.switch_scene("salon")
    print(f"切换结果：{transition.message}")

    print("\n--- 在沙龙场景中对话 ---")
    message2 = Message(
        content="大家对 AI 技术有什么看法？",
        role="user",
        type=MessageType.USER,
    )
    response2, transition2 = manager.handle_message(message2, context)
    print(f"响应：{response2.content[:100]}...")

    # 切换到会议场景
    print("\n🔄 切换到会议场景...")
    transition = manager.switch_scene("meeting")
    print(f"切换结果：{transition.message}")

    print("\n--- 在会议场景中对话 ---")
    message3 = Message(
        content="昨天的工作完成了，今天继续。",
        role="user",
        type=MessageType.USER,
    )
    response3, transition3 = manager.handle_message(message3, context)
    print(f"响应：{response3.content[:100]}...")

    # 查看场景历史
    print("\n📜 场景历史:")
    history = manager.get_scene_history()
    for i, key in enumerate(history, 1):
        print(f"  {i}. {key}")

    # 查看转换历史
    print("\n📊 转换历史:")
    transitions = manager.get_transition_history()
    for t in transitions:
        print(f"  {t.from_scene} -> {t.to_scene}: {t.message}")

    manager.clear()


def demo_context_preservation():
    """上下文保持演示"""
    print("\n" + "=" * 60)
    print("场景管理器演示 - 上下文保持")
    print("=" * 60)
    print()

    manager = SceneManager()

    # 创建场景
    manager.create_scene("interview", scene_key="interview")
    manager.create_scene("salon", scene_key="salon")

    # 在面试场景中对话
    manager.activate_scene("interview")
    context = manager.get_global_context()

    print("📝 在面试场景中对话...")
    for content in ["你好", "我想了解一下职位", "谢谢"]:
        msg = Message(content=content, role="user", type=MessageType.USER)
        manager.handle_message(msg, context)

    # 查看上下文消息数
    print(f"当前上下文消息数：{len(context.messages)}")

    # 切换到沙龙（保持上下文）
    print("\n🔄 切换到沙龙场景（保持上下文）...")
    manager.switch_scene("salon", preserve_context=True)

    # 上下文应该保持不变
    print(f"切换后上下文消息数：{len(context.messages)}")

    # 在沙龙中继续对话
    print("\n📝 在沙龙场景中继续对话...")
    msg = Message(content="这个话题很有意思", role="user", type=MessageType.USER)
    manager.handle_message(msg, context)

    print(f"现在上下文消息数：{len(context.messages)}")

    # 导出状态
    print("\n💾 导出管理器状态...")
    state = manager.export_state()
    print(f"状态大小：{len(str(state))} 字符")
    print(f"活跃场景：{state['active_scene']}")
    print(f"场景历史：{state['history']}")

    manager.clear()


def demo_scene_commands():
    """场景指令演示"""
    print("\n" + "=" * 60)
    print("场景管理器演示 - 场景切换指令")
    print("=" * 60)
    print()

    manager = SceneManager()

    # 创建场景
    manager.create_scene("interview", scene_key="interview")
    manager.create_scene("salon", scene_key="salon")
    manager.create_scene("meeting", scene_key="meeting")

    # 激活初始场景
    manager.activate_scene("interview")
    context = manager.get_global_context()

    print("📍 当前场景：interview")

    # 使用指令切换场景
    commands = [
        "/switch salon",
        "正常对话内容",
        "/scene meeting",
        "另一段对话",
        "/switch interview no_context",
    ]

    for cmd in commands:
        print(f"\n【用户】{cmd}")
        msg = Message(content=cmd, role="user", type=MessageType.USER)
        response, transition = manager.handle_message(msg, context)

        if transition:
            print(f"🔄 场景切换：{transition.message}")
        else:
            print(f"【{response.role}】{response.content[:80]}...")

    manager.clear()


def main():
    """主函数"""
    print("\n" + "🎯" * 30)
    print("AgentScope AI Interview - v0.5 场景管理器演示")
    print("🎯" * 30)

    try:
        # 运行演示
        demo_basic_scene_management()
        demo_scene_switching()
        demo_context_preservation()
        demo_scene_commands()

    except Exception as e:
        print(f"\n❌ 演示出错：{e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("演示结束")
    print("=" * 60)


if __name__ == "__main__":
    main()
