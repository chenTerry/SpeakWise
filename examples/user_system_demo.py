#!/usr/bin/env python3
"""
User System Demo

用户系统演示脚本

展示 v0.6 版本的用户管理、进度追踪、数据可视化和历史回放功能

Usage:
    python examples/user_system_demo.py
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from users.database import Database, init_database
from users.service import UserService
from users.models import UserCreate, SessionCreate
from progress.tracker import ProgressTracker
from progress.history import SessionHistoryManager
from visualization.radar import DimensionRadarChart
from visualization.charts import create_bar_chart, create_progress_bar
from dashboard.cli_dashboard import CLIDashboard
from dashboard.report import ReportGenerator


def print_header(title: str) -> None:
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_user_registration(user_service: UserService) -> int:
    """演示用户注册"""
    print_header("1. 用户注册")
    
    # 创建测试用户
    user_data = UserCreate(
        username="demo_user",
        password="demo123",
        email="demo@example.com",
        display_name="演示用户"
    )
    
    try:
        user = user_service.register(user_data)
        print(f"✅ 用户注册成功！")
        print(f"   ID: {user.id}")
        print(f"   用户名：{user.username}")
        print(f"   显示名：{user.display_name}")
        print(f"   创建时间：{user.created_at}")
        return user.id
    except Exception as e:
        print(f"⚠️  用户可能已存在，尝试登录...")
        # 用户已存在，尝试登录获取 ID
        try:
            result = user_service.login("demo_user", "demo123")
            return result["user"]["id"]
        except:
            return 1


def demo_user_login(user_service: UserService) -> tuple[int, str]:
    """演示用户登录"""
    print_header("2. 用户登录")
    
    result = user_service.login("demo_user", "demo123")
    
    print(f"✅ 登录成功！")
    print(f"   Token: {result['token'][:50]}...")
    print(f"   Session ID: {result['session_id']}")
    print(f"   用户：{result['user']['display_name']}")
    
    return result["user"]["id"], result["session_id"]


def demo_session_management(user_service: UserService, user_id: int) -> list:
    """演示会话管理"""
    print_header("3. 会话管理")
    
    session_ids = []
    
    # 创建模拟会话
    scenes = [
        ("technical_interview", "技术面试模拟"),
        ("hr_interview", "HR 面试模拟"),
        ("salon_discussion", "技术沙龙讨论"),
    ]
    
    for scene_type, title in scenes:
        session_data = SessionCreate(
            user_id=user_id,
            scene_type=scene_type,
            title=title
        )
        
        session = user_service.create_session_record(session_data)
        session_ids.append(session.id)
        
        print(f"📝 创建会话：{title} (ID: {session.id})")
    
    # 完成会话（带模拟评估结果）
    print("\n📊 完成会话并记录评估结果...")
    
    evaluation_results = [
        {
            "overall_score": 75.5,
            "language_expression": 78.0,
            "logical_thinking": 82.0,
            "professional_knowledge": 70.0,
            "problem_solving": 75.0,
            "communication_collaboration": 80.0,
            "adaptability": 72.0,
            "overall_quality": 76.0,
            "strengths": ["逻辑思维清晰", "沟通表达流畅"],
            "improvements": ["专业知识需要加强"],
        },
        {
            "overall_score": 82.0,
            "language_expression": 85.0,
            "logical_thinking": 88.0,
            "professional_knowledge": 78.0,
            "problem_solving": 80.0,
            "communication_collaboration": 85.0,
            "adaptability": 79.0,
            "overall_quality": 83.0,
            "strengths": ["表现优秀", "应变能力强"],
            "improvements": ["可以继续提升专业知识"],
        },
        {
            "overall_score": 88.5,
            "language_expression": 90.0,
            "logical_thinking": 92.0,
            "professional_knowledge": 85.0,
            "problem_solving": 88.0,
            "communication_collaboration": 90.0,
            "adaptability": 86.0,
            "overall_quality": 89.0,
            "strengths": ["综合素质优秀", "表达能力突出"],
            "improvements": ["保持练习，追求卓越"],
        },
    ]
    
    for i, session_id in enumerate(session_ids):
        if i < len(evaluation_results):
            # 模拟会话时长
            duration = 1800 + i * 300  # 30-40 分钟
            
            # 完成会话
            user_service.complete_session(
                session_id=session_id,
                evaluation_result=evaluation_results[i]
            )
            
            # 手动更新会话时长（通过 repository）
            from users.database import get_db_session
            from users.repository import SessionRepository
            
            with get_db_session() as session:
                session_repo = SessionRepository(session)
                session_repo.update(session_id, duration_seconds=duration)
                session.commit()
            
            print(f"✅ 完成会话 {session_id}: {evaluation_results[i]['overall_score']}分")
    
    return session_ids


def demo_progress_tracking(user_id: int) -> None:
    """演示进度追踪"""
    print_header("4. 进度追踪")
    
    tracker = ProgressTracker(user_id)
    
    # 获取进度
    progress = tracker.get_progress()
    
    if progress:
        print("📊 进度数据:")
        print(f"   总会话数：{progress.get('total_sessions', 0)}")
        print(f"   平均分数：{progress.get('avg_score', 0):.1f}")
        print(f"   改进率：{progress.get('improvement_rate', 0):+.1f}%")
        print(f"   连续练习：{progress.get('streak_days', 0)} 天")
        
        # 显示维度分数
        print("\n🎯 七维度评估:")
        dimension_scores = progress.get("dimension_scores", {})
        
        dimension_names = {
            "language_expression": "语言表达",
            "logical_thinking": "逻辑思维",
            "professional_knowledge": "专业知识",
            "problem_solving": "问题解决",
            "communication_collaboration": "沟通协作",
            "adaptability": "应变能力",
            "overall_quality": "综合素质",
        }
        
        for dim_key, dim_name in dimension_names.items():
            score = dimension_scores.get(dim_key, 0)
            bar = create_progress_bar(dim_name, score, 100, width=30)
            print(f"   {bar}")
    else:
        print("⚠️  暂无进度数据")


def demo_visualization(user_id: int) -> None:
    """演示数据可视化"""
    print_header("5. 数据可视化")
    
    tracker = ProgressTracker(user_id)
    progress = tracker.get_progress()
    
    if progress and progress.get("dimension_scores"):
        # 雷达图
        print("📊 七维度雷达图 (ASCII):")
        print()
        
        radar = DimensionRadarChart()
        ascii_radar = radar.generate_ascii(progress["dimension_scores"])
        print(ascii_radar)
        
        # SVG 雷达图（保存文件）
        print("\n📁 生成 SVG 雷达图...")
        svg_content = radar.generate(progress["dimension_scores"])
        
        svg_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples",
            "radar_chart.svg"
        )
        
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        
        print(f"✅ SVG 雷达图已保存到：{svg_path}")
    else:
        print("⚠️  暂无可视化数据")


def demo_history_replay(user_id: int, session_ids: list) -> None:
    """演示历史回放"""
    print_header("6. 历史回放")
    
    from history.replay import SessionReplay
    
    if session_ids:
        session_id = session_ids[0]
        
        replay = SessionReplay(session_id)
        
        if replay.load():
            summary = replay.get_summary()
            print(f"📼 回放会话：{summary.get('title', 'N/A')}")
            print(f"   场景：{summary.get('scene_type', 'N/A')}")
            print(f"   总步骤：{summary.get('total_steps', 0)}")
            print(f"   整体分数：{summary.get('overall_score', 0):.1f}")
            
            # 添加笔记
            print("\n📝 添加笔记...")
            note = replay.add_note(0, "这是一个很好的开场回答", tags=["good_start"])
            print(f"   已添加笔记：{note.content}")
            
            # 导出为 Markdown
            print("\n📄 导出回放记录...")
            md_content = replay.export(format="markdown")
            
            md_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "examples",
                "session_replay.md"
            )
            
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content[:2000])  # 只保存前 2000 字符
            
            print(f"✅ 回放记录已保存到：{md_path}")
        else:
            print("⚠️  无法加载会话")
    else:
        print("⚠️  没有可回放的会话")


def demo_dashboard(user_id: int) -> None:
    """演示用户仪表盘"""
    print_header("7. 用户仪表盘")
    
    dashboard = CLIDashboard(user_id)
    dashboard.show_welcome()
    
    input("\n按 Enter 键显示仪表盘...")
    dashboard.display()


def demo_report_generation(user_id: int) -> None:
    """演示报告生成"""
    print_header("8. 进度报告生成")
    
    generator = ReportGenerator(user_id)
    
    # 生成 Markdown 报告
    print("📝 生成 Markdown 报告...")
    
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "examples",
        "progress_report.md"
    )
    
    generator.export_markdown(report_path, period_days=30)
    print(f"✅ 报告已保存到：{report_path}")
    
    # 显示报告预览
    print("\n📋 报告预览（前 1000 字符）:")
    print("-" * 40)
    
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        print(content[:1000])
        print("...")


def main():
    """主函数"""
    print_header("🎯 AgentScope AI Interview v0.6 - 用户系统演示")
    
    # 初始化数据库
    print("📁 初始化数据库...")
    db = init_database("sqlite:///./data/demo_users.db")
    print("✅ 数据库初始化完成")
    
    # 创建用户服务
    user_service = UserService(db)
    
    # 1. 用户注册
    user_id = demo_user_registration(user_service)
    
    # 2. 用户登录
    user_id, session_id = demo_user_login(user_service)
    
    # 3. 会话管理
    session_ids = demo_session_management(user_service, user_id)
    
    # 4. 进度追踪
    demo_progress_tracking(user_id)
    
    # 5. 数据可视化
    demo_visualization(user_id)
    
    # 6. 历史回放
    demo_history_replay(user_id, session_ids)
    
    # 7. 用户仪表盘（交互式）
    # demo_dashboard(user_id)  # 需要用户交互，可选
    
    # 8. 报告生成
    demo_report_generation(user_id)
    
    print_header("✅ 演示完成！")
    print("生成的文件:")
    print("  - examples/radar_chart.svg (雷达图)")
    print("  - examples/session_replay.md (会话回放)")
    print("  - examples/progress_report.md (进度报告)")
    print("\n🚀 感谢使用 AgentScope AI Interview v0.6!")
    print()


if __name__ == "__main__":
    main()
