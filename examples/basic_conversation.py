#!/usr/bin/env python3
"""
Basic Conversation Example - 基础对话示例

这是一个命令行测试接口，演示如何使用 AgentScope AI Interview 核心框架。

使用方法:
    python examples/basic_conversation.py

功能:
    - 创建面试官和评估员 Agent
    - 运行多轮对话
    - 显示对话历史和评估结果
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    Config,
    ConfigLoader,
    InterviewerAgent,
    ObserverAgent,
    EvaluatorAgent,
    DialogueManager,
    DialogueManagerBuilder,
    Message,
)


def create_default_config() -> Config:
    """创建默认配置"""
    return ConfigLoader.from_dict({
        "model": {
            "name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        "dialogue": {
            "max_turns": 5,  # v0.1 测试用较少轮数
            "timeout_seconds": 300,
        },
        "agent": {
            "interviewer": {
                "style": "friendly",
                "domain": "general",
            },
        },
    })


def create_agents(config: Config):
    """创建 Agent 列表"""
    interviewer = InterviewerAgent(
        name="张面试官",
        config=config,
        style="friendly",
        domain="general",
    )
    
    observer = ObserverAgent(
        name="AI 观察者",
        config=config,
        focus_areas=["communication", "technical_depth"],
    )
    
    evaluator = EvaluatorAgent(
        name="AI 评估员",
        config=config,
        dimensions=[
            "content_quality",
            "expression_clarity",
            "professional_knowledge",
        ],
    )
    
    return [interviewer, observer, evaluator]


def run_interactive_mode(manager: DialogueManager):
    """运行交互式对话模式"""
    print("\n" + "=" * 60)
    print("🎯 AgentScope AI Interview - 模拟面试系统 v0.1")
    print("=" * 60)
    print("\n欢迎来到模拟面试！我是今天的面试官。")
    print("输入 'quit' 或 'exit' 结束对话")
    print("输入 'eval' 查看当前评估")
    print("-" * 60)
    
    # 面试官开场
    opening_message = Message(
        content="你好！很高兴今天能和你交流。先简单介绍一下自己吧？",
        role="张面试官",
    )
    manager.get_context().add_message(opening_message)
    print(f"\n🤖 {opening_message.role}: {opening_message.content}")
    
    turn_count = 0
    max_turns = manager._max_turns
    
    while turn_count < max_turns:
        try:
            # 获取用户输入
            user_input = input("\n👤 你：").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\n💬 感谢参与，对话已结束。")
                break
            
            if user_input.lower() == "eval":
                print("\n📊 当前对话评估:")
                print(f"   已进行 {turn_count} 轮对话")
                continue
            
            # 添加用户消息
            manager.send_user_message(user_input)
            print(f"   (记录中...)")
            
            # 获取面试官响应
            agent, response = manager.run_turn()
            turn_count += 1
            
            print(f"\n🤖 {response.role}: {response.content}")
            
            # 检查是否达到最大轮数
            if turn_count >= max_turns:
                print(f"\n⏰ 已达到最大对话轮数 ({max_turns})")
                break
        
        except KeyboardInterrupt:
            print("\n\n⚠️  对话被用户中断")
            break
        except Exception as e:
            print(f"\n❌ 发生错误：{e}")
            break
    
    return turn_count


def run_auto_mode(manager: DialogueManager):
    """运行自动对话模式（用于测试）"""
    print("\n🤖 自动对话模式启动...")
    
    # 模拟用户回答
    auto_responses = [
        "你好，我是一名有 3 年经验的后端工程师，主要负责 Python 和 Go 开发。",
        "最近我做的项目是一个微服务架构的电商平台，我负责订单模块的设计。",
        "在项目中遇到的主要挑战是高并发场景下的数据一致性问题。",
        "我们通过引入消息队列和分布式事务解决了这个问题。",
        "如果重新设计，我会更早考虑服务治理和监控体系。",
    ]
    
    for i, response in enumerate(auto_responses):
        print(f"\n--- 第 {i + 1} 轮 ---")
        
        # 获取面试官问题
        agent, message = manager.run_turn()
        print(f"🤖 {message.role}: {message.content}")
        
        # 模拟用户回答
        if i < len(auto_responses):
            user_msg = manager.send_user_message(response)
            print(f"👤 你：{response}")
    
    print("\n✅ 自动对话完成")


def main():
    """主函数"""
    print("🚀 初始化 AgentScope AI Interview 系统...\n")
    
    # 1. 加载配置
    config = create_default_config()
    print("✓ 配置加载完成")
    print(f"  - 模型：{config.get('model.name')}")
    print(f"  - 最大轮数：{config.get('dialogue.max_turns')}")
    
    # 2. 创建 Agent
    agents = create_agents(config)
    print(f"✓ 已创建 {len(agents)} 个 Agent:")
    for agent in agents:
        print(f"  - {agent.name}: {agent.get_role()}")
    
    # 3. 创建对话管理器
    manager = (
        DialogueManagerBuilder()
        .with_config(config)
        .add_agents(agents)
        .build()
    )
    print("✓ 对话管理器初始化完成\n")
    
    # 4. 选择运行模式
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        # 自动模式
        manager.start()
        run_auto_mode(manager)
    else:
        # 交互模式
        manager.start()
        run_interactive_mode(manager)
    
    # 5. 显示结果
    print("\n" + "=" * 60)
    print("📊 对话结果")
    print("=" * 60)
    
    context = manager.get_context()
    print(f"总轮数：{context.get_turn_count()}")
    print(f"消息数：{len(context.get_history())}")
    
    # 打印对话历史
    manager.print_history()
    
    # 生成评估
    print("\n📈 评估报告")
    print("-" * 60)
    
    evaluator = manager._get_evaluator()
    if evaluator:
        evaluation = evaluator.evaluate(context.get_history())
        print(evaluation)
    else:
        print("暂无评估员")
    
    print("\n✅ 程序执行完成\n")


if __name__ == "__main__":
    main()
