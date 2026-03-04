"""
AgentScope AI Interview - v1.0 综合演示

本演示脚本展示 v1.0 版本的所有核心功能：
- 核心框架（配置/Agent/对话管理）
- 场景系统（面试/沙龙/会议）
- 评估系统（7 维度评估）
- 用户系统（认证/进度追踪）
- 数据分析（学习分析/行为追踪/推荐）
- 语音支持（STT/TTS/质量评估）
- 企业功能（多租户/团队协作）

使用方式:
    python examples/v1.0_demo.py              # 完整演示
    python examples/v1.0_demo.py --quick      # 快速演示
    python examples/v1.0_demo.py --module core    # 仅演示指定模块

作者：AgentScope AI Interview Team
版本：v1.0.0
日期：2026-03-04
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# =============================================================================
# 演示装饰器和工具函数
# =============================================================================

def demo_section(title: str):
    """打印演示章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_step(step_num: int, description: str):
    """打印演示步骤"""
    print(f"\n[步骤 {step_num}] {description}")
    print("-" * 50)


def demo_success(message: str):
    """打印成功消息"""
    print(f"✓ {message}")


def demo_info(message: str):
    """打印信息消息"""
    print(f"ℹ {message}")


def demo_error(message: str):
    """打印错误消息"""
    print(f"✗ {message}")


def print_header():
    """打印演示头部"""
    print("=" * 70)
    print("  AgentScope AI Interview - v1.0 综合演示")
    print("  Production Ready Release")
    print("=" * 70)
    print(f"  演示时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


# =============================================================================
# 模块 1: 核心框架演示
# =============================================================================

def demo_core_framework(quick_mode: bool = False):
    """
    演示核心框架功能
    
    展示:
    - 配置系统加载
    - Agent 创建和初始化
    - 对话管理器使用
    """
    demo_section("模块 1: 核心框架演示")
    
    try:
        # 步骤 1: 配置系统
        demo_step(1, "配置系统加载")
        from core import Config, ConfigLoader
        
        # 从字典创建配置
        config_dict = {
            "model": {
                "name": "deepseek-chat",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            "dialogue": {
                "max_turns": 10,
            },
            "agent": {
                "interviewer": {
                    "style": "friendly",
                    "domain": "tech",
                }
            }
        }
        config = ConfigLoader.from_dict(config_dict)
        demo_success(f"配置加载成功 - 模型：{config.get('model.name')}")
        
        # 步骤 2: Agent 创建
        demo_step(2, "Agent 创建和初始化")
        from core.agent import Message, DialogueContext
        
        # 创建消息
        user_msg = Message(content="你好，我准备开始面试练习", role="user")
        demo_success(f"消息创建成功 - 角色：{user_msg.role}")
        
        # 创建对话上下文
        context = DialogueContext()
        demo_success(f"对话上下文创建成功 - ID: {context.session_id}")
        
        # 步骤 3: 对话管理器
        demo_step(3, "对话管理器使用")
        from core import DialogueManager, DialogueManagerBuilder
        
        # 使用构建器创建对话管理器
        manager = (DialogueManagerBuilder()
                   .with_config(config)
                   .with_context(context)
                   .build())
        demo_success("对话管理器创建成功")
        
        if not quick_mode:
            # 模拟对话流程
            demo_step(4, "模拟对话流程")
            print("对话流程:")
            print(f"  用户：{user_msg.content}")
            print(f"  系统：[AI 响应] 你好！欢迎参加今天的面试练习...")
            demo_success("对话流程演示完成")
        
        return True
        
    except Exception as e:
        demo_error(f"核心框架演示失败：{str(e)}")
        logger.exception("Core framework demo failed")
        return False


# =============================================================================
# 模块 2: 场景系统演示
# =============================================================================

def demo_scene_system(quick_mode: bool = False):
    """
    演示场景系统功能
    
    展示:
    - 面试场景
    - 沙龙场景
    - 会议场景
    - 场景管理器
    """
    demo_section("模块 2: 场景系统演示")
    
    try:
        # 步骤 1: 面试场景
        demo_step(1, "面试场景")
        from scenes.interview import InterviewScene, InterviewStyle, DomainType
        
        interview_scene = InterviewScene(
            style=InterviewStyle.FRIENDLY,
            domain=DomainType.TECH,
        )
        interview_scene.initialize()
        demo_success("面试场景初始化成功")
        
        if not quick_mode:
            opening = interview_scene.start()
            print(f"开场白：{opening.content[:100]}...")
        
        # 步骤 2: 沙龙场景
        demo_step(2, "沙龙场景")
        from scenes.salon import SalonScene, SalonSceneConfig
        
        salon_config = SalonSceneConfig(
            topic="AI 技术在开发中的应用",
            speaker_topic="大模型辅助编程实践",
            discussion_style="casual",
        )
        salon_scene = SalonScene(config=salon_config)
        salon_scene.initialize()
        demo_success("沙龙场景初始化成功")
        
        # 步骤 3: 会议场景
        demo_step(3, "会议场景")
        from scenes.meeting import MeetingScene, MeetingType
        
        meeting_scene = MeetingScene(
            meeting_type=MeetingType.STANDUP,
            project_name="电商平台重构",
        )
        meeting_scene.initialize()
        demo_success("会议场景初始化成功")
        
        # 步骤 4: 场景管理器
        demo_step(4, "场景管理器")
        from scenes.manager import SceneManager
        
        manager = SceneManager()
        manager.create_scene("interview", scene_key="interview", style="friendly")
        manager.create_scene("salon", scene_key="salon", topic="AI 技术")
        manager.create_scene("meeting", scene_key="meeting", meeting_type="standup")
        
        # 场景切换
        manager.activate_scene("interview")
        transition = manager.switch_scene("salon", preserve_context=True)
        demo_success(f"场景切换成功 - {transition.message}")
        
        demo_info(f"已加载场景数：{len(manager.list_scenes())}")
        
        return True
        
    except Exception as e:
        demo_error(f"场景系统演示失败：{str(e)}")
        logger.exception("Scene system demo failed")
        return False


# =============================================================================
# 模块 3: 评估系统演示
# =============================================================================

def demo_evaluation_system(quick_mode: bool = False):
    """
    演示评估系统功能
    
    展示:
    - 7 维度评估模型
    - 评估报告生成
    - 改进建议
    """
    demo_section("模块 3: 评估系统演示")
    
    try:
        # 步骤 1: 基础评估器
        demo_step(1, "7 维度评估模型")
        from evaluation import BasicEvaluator
        from core import DialogueContext, Message
        
        evaluator = BasicEvaluator()
        
        # 创建模拟对话上下文
        context = DialogueContext()
        context.add_message(Message(content="请介绍一下你自己", role="assistant"))
        context.add_message(Message(content="你好，我是一名有 3 年经验的前端工程师...", role="user"))
        context.add_message(Message(content="很好，那 React 中的 useEffect 有什么作用？", role="assistant"))
        context.add_message(Message(content="useEffect 是 React 的副作用处理钩子...", role="user"))
        
        demo_success("模拟对话创建成功")
        
        # 步骤 2: 执行评估
        demo_step(2, "执行评估")
        result = evaluator.evaluate(context)
        
        print("\n评估结果:")
        print(f"  总体评分：{result.overall_score:.1f}/5.0")
        print(f"  评级：{result.grade}")
        
        # 步骤 3: 维度详情
        demo_step(3, "7 维度详情")
        dimensions = result.dimensions
        for dim_name, score in dimensions.items():
            bar = "█" * int(score * 2) + "░" * (10 - int(score * 2))
            print(f"  {dim_name}: [{bar}] {score:.1f}")
        
        # 步骤 4: 生成报告
        demo_step(4, "生成评估报告")
        report = evaluator.generate_report(result, format="markdown")
        demo_success(f"评估报告生成成功 - {len(report)} 字符")
        
        if not quick_mode:
            print("\n报告摘要:")
            print(report[:500] + "...")
        
        return True
        
    except Exception as e:
        demo_error(f"评估系统演示失败：{str(e)}")
        logger.exception("Evaluation system demo failed")
        return False


# =============================================================================
# 模块 4: 用户系统演示
# =============================================================================

def demo_user_system(quick_mode: bool = False):
    """
    演示用户系统功能
    
    展示:
    - 用户认证
    - 进度追踪
    - 数据可视化
    - 历史回放
    """
    demo_section("模块 4: 用户系统演示")
    
    try:
        # 步骤 1: 用户管理
        demo_step(1, "用户管理")
        from users import UserManager
        
        user_manager = UserManager(db_path=":memory:")  # 使用内存数据库演示
        
        # 创建演示用户
        user_id = user_manager.create_user(
            username="demo_user",
            email="demo@example.com",
            password="demo_password123",
        )
        demo_success(f"用户创建成功 - ID: {user_id}")
        
        # 用户登录
        token = user_manager.login("demo_user", "demo_password123")
        demo_success(f"用户登录成功 - Token: {token[:20]}...")
        
        # 步骤 2: 进度追踪
        demo_step(2, "进度追踪")
        from users import ProgressTracker
        
        tracker = ProgressTracker()
        
        # 模拟会话记录
        from users.database import SessionRecord
        sessions = []
        for i in range(5):
            session = SessionRecord(
                user_id=user_id,
                scene_type="interview",
                score=3.5 + i * 0.2,
                duration=600 + i * 60,
            )
            sessions.append(session)
        
        progress = tracker.calculate_progress(user_id, sessions)
        demo_success(f"进度计算成功 - 会话数：{progress.total_sessions}")
        
        print(f"\n进度指标:")
        print(f"  总会话数：{progress.total_sessions}")
        print(f"  平均分：{progress.average_score:.1f}")
        print(f"  改进率：{progress.improvement_rate:.1f}%")
        
        # 步骤 3: 数据可视化
        demo_step(3, "数据可视化")
        from users import DataVisualizer
        
        visualizer = DataVisualizer()
        
        # 生成雷达图数据
        radar_data = {
            "内容质量": 4.2,
            "表达清晰度": 3.8,
            "专业知识": 4.0,
            "逻辑思维": 3.9,
            "应变能力": 4.1,
            "沟通技巧": 3.7,
            "职业素养": 4.3,
        }
        radar_svg = visualizer.generate_radar_chart(radar_data, output_format="svg")
        demo_success(f"雷达图生成成功 - {len(radar_svg)} 字符")
        
        # 步骤 4: 历史回放
        demo_step(4, "历史回放")
        from history import SessionReplay
        
        replay = SessionReplay()
        replay.start_session("演示会话")
        replay.add_step(speaker="user", content="你好")
        replay.add_step(speaker="assistant", content="你好，欢迎参加面试")
        replay.end_session()
        
        replay_data = replay.get_replay_data()
        demo_success(f"历史回放创建成功 - 步骤数：{len(replay_data.steps)}")
        
        return True
        
    except Exception as e:
        demo_error(f"用户系统演示失败：{str(e)}")
        logger.exception("User system demo failed")
        return False


# =============================================================================
# 模块 5: 数据分析演示
# =============================================================================

def demo_analytics(quick_mode: bool = False):
    """
    演示数据分析功能
    
    展示:
    - 学习分析
    - 行为追踪
    - 推荐引擎
    - 统计引擎
    - 洞察仪表盘
    - 数据导出
    """
    demo_section("模块 5: 数据分析演示")
    
    try:
        user_id = "demo_user_001"
        
        # 步骤 1: 学习分析
        demo_step(1, "学习分析")
        from analytics import LearningAnalytics
        
        analytics = LearningAnalytics()
        
        # 模拟会话数据
        sessions = [
            {"score": 3.5, "date": "2026-02-01", "duration": 600},
            {"score": 3.7, "date": "2026-02-05", "duration": 650},
            {"score": 4.0, "date": "2026-02-10", "duration": 700},
            {"score": 4.2, "date": "2026-02-15", "duration": 720},
            {"score": 4.5, "date": "2026-02-20", "duration": 750},
        ]
        
        profile = analytics.generate_learning_profile(user_id, sessions)
        demo_success(f"学习画像生成成功 - 技能水平：{profile.skill_level}")
        
        print(f"\n学习画像:")
        print(f"  技能水平：{profile.skill_level.value}")
        print(f"  学习模式：{profile.learning_pattern.value}")
        print(f"  优势维度：{profile.strengths[0].dimension if profile.strengths else 'N/A'}")
        
        # 步骤 2: 行为追踪
        demo_step(2, "行为追踪")
        from analytics import BehaviorTracker
        
        tracker = BehaviorTracker()
        behavior_report = tracker.analyze_behavior(user_id, sessions, period_days=30)
        demo_success(f"行为分析完成 - 参与度：{behavior_report.engagement.level.value}")
        
        # 步骤 3: 推荐引擎
        demo_step(3, "推荐引擎")
        from analytics import RecommendationEngine
        
        engine = RecommendationEngine()
        recommendations = engine.generate_recommendations(user_id, sessions, profile, behavior_report)
        demo_success(f"推荐生成成功 - 推荐数：{len(recommendations.topic_recommendations)}")
        
        if recommendations.topic_recommendations:
            print(f"\n推荐主题:")
            for rec in recommendations.topic_recommendations[:3]:
                print(f"  - {rec.topic_name} (优先级：{rec.priority})")
        
        # 步骤 4: 统计引擎
        demo_step(4, "统计引擎")
        from analytics import StatisticsEngine
        
        stats_engine = StatisticsEngine()
        stats_report = stats_engine.generate_statistical_report(user_id, sessions, period_days=30)
        demo_success(f"统计报告生成成功 - 百分位排名：{stats_report.comparative_analysis.percentile_rank:.1f}%")
        
        # 步骤 5: 洞察仪表盘
        demo_step(5, "洞察仪表盘")
        from analytics import InsightsDashboard
        
        dashboard = InsightsDashboard()
        dashboard_data = dashboard.generate_dashboard(
            user_id, sessions, profile, behavior_report,
            stats_report, recommendations
        )
        demo_success(f"仪表盘生成成功 - 关键洞察：{len(dashboard_data.key_insights)} 条")
        
        # 步骤 6: 数据导出
        demo_step(6, "数据导出")
        from analytics import DataExporter, ExportFormat
        
        exporter = DataExporter(config={"output_dir": "./examples/output"})
        
        # 导出 JSON
        json_result = exporter.export_to_json(dashboard_data, filename="v1_demo_report.json")
        demo_success(f"JSON 导出成功 - {json_result.file_path}")
        
        return True
        
    except Exception as e:
        demo_error(f"数据分析演示失败：{str(e)}")
        logger.exception("Analytics demo failed")
        return False


# =============================================================================
# 模块 6: 语音支持演示
# =============================================================================

def demo_voice_support(quick_mode: bool = False):
    """
    演示语音支持功能
    
    展示:
    - 语音输入 (STT)
    - 语音输出 (TTS)
    - 语音质量评估
    - 音频处理
    - 语音回放
    """
    demo_section("模块 6: 语音支持演示")
    
    try:
        # 步骤 1: 语音输入配置
        demo_step(1, "语音输入配置 (STT)")
        from voice import VoiceInput, VoiceInputConfig, Language, STTEngine
        
        stt_config = VoiceInputConfig(
            language=Language.CHINESE,
            engine=STTEngine.GOOGLE,
            sample_rate=16000,
            vad_aggressiveness=2,
        )
        demo_success(f"STT 配置创建成功 - 语言：{stt_config.language.value}")
        
        # 步骤 2: 语音输出配置
        demo_step(2, "语音输出配置 (TTS)")
        from voice import VoiceOutput, VoiceOutputConfig, TTSEngine
        
        tts_config = VoiceOutputConfig(
            engine=TTSEngine.PYTTSX3,
            language="zh-CN",
            rate=200,
            volume=1.0,
        )
        demo_success(f"TTS 配置创建成功 - 引擎：{tts_config.engine.value}")
        
        # 步骤 3: 语音质量评估
        demo_step(3, "语音质量评估")
        from voice import VoiceQualityAssessor
        
        assessor = VoiceQualityAssessor(language="zh-CN")
        
        # 模拟评估
        report = assessor.assess(
            text="你好，我是来面试的，我是一名有三年经验的工程师",
            duration=5.0,
        )
        demo_success(f"语音评估完成 - 总体评分：{report.overall_score:.1f}/100")
        
        print(f"\n语音质量报告:")
        print(f"  发音清晰度：{report.pronunciation.overall:.1f}/100")
        print(f"  语速：{report.pace.wpm:.1f} WPM ({report.pace.level.value})")
        print(f"  填充词数量：{report.fillers.total_count}")
        
        # 步骤 4: 音频处理
        demo_step(4, "音频处理")
        from voice import AudioProcessor
        
        processor = AudioProcessor()
        demo_info("音频处理器初始化成功")
        demo_info("支持格式：WAV, MP3, FLAC, OGG, M4A")
        demo_info("支持操作：格式转换、降噪、音量标准化、变速")
        
        # 步骤 5: 语音回放
        demo_step(5, "语音回放")
        from voice import VoiceReplay
        
        replay = VoiceReplay()
        session_id = replay.start_session("演示 Session")
        replay.add_segment(speaker="user", text="你好")
        replay.add_segment(speaker="agent", text="你好，欢迎参加面试")
        replay.end_session()
        
        demo_success(f"语音回放创建成功 - 片段数：{len(replay.get_segments())}")
        
        # 步骤 6: 语音设置
        demo_step(6, "语音设置管理")
        from voice import VoiceSettingsManager
        
        settings_manager = VoiceSettingsManager()
        settings = settings_manager.get_settings()
        demo_success(f"语音设置加载成功 - 输入：{'启用' if settings.enable_voice_input else '禁用'}")
        
        return True
        
    except Exception as e:
        demo_error(f"语音支持演示失败：{str(e)}")
        logger.exception("Voice support demo failed")
        return False


# =============================================================================
# 模块 7: 企业功能演示
# =============================================================================

def demo_enterprise_features(quick_mode: bool = False):
    """
    演示企业版功能
    
    展示:
    - 多租户管理
    - 团队管理
    - 协作会话
    - 管理员仪表盘
    - 批量操作
    - 企业报表
    """
    demo_section("模块 7: 企业版功能演示")
    
    try:
        # 步骤 1: 多租户管理
        demo_step(1, "多租户管理")
        from enterprise import TenantManager
        
        tenant_manager = TenantManager(db_path=":memory:")
        
        # 创建租户
        tenant_id = tenant_manager.create_tenant(
            name="演示企业",
            plan="enterprise",
            max_users=100,
        )
        demo_success(f"租户创建成功 - ID: {tenant_id}")
        
        # 获取租户统计
        stats = tenant_manager.get_tenant_stats(tenant_id)
        demo_info(f"租户统计：用户数 {stats.user_count}/{stats.max_users}")
        
        # 步骤 2: 团队管理
        demo_step(2, "团队管理")
        from enterprise import TeamManager
        
        team_manager = TeamManager(db_path=":memory:")
        
        # 创建团队
        team_id = team_manager.create_team(
            tenant_id=tenant_id,
            name="研发团队",
            description="前端和后端开发团队",
        )
        demo_success(f"团队创建成功 - ID: {team_id}")
        
        # 添加成员
        team_manager.add_member(team_id, user_id="user_001", role="member")
        team_manager.add_member(team_id, user_id="user_002", role="admin")
        demo_info(f"团队成员数：{team_manager.get_team_size(team_id)}")
        
        # 步骤 3: 协作会话
        demo_step(3, "协作会话")
        from enterprise import CollaborationManager
        
        collab_manager = CollaborationManager()
        
        # 创建练习会话
        session_id = collab_manager.create_practice_session(
            team_id=team_id,
            topic="技术面试练习",
            max_participants=10,
        )
        demo_success(f"练习会话创建成功 - ID: {session_id}")
        
        # 步骤 4: 管理员仪表盘
        demo_step(4, "管理员仪表盘")
        from enterprise import AdminDashboard
        
        dashboard = AdminDashboard()
        
        # 获取仪表数据
        dashboard_data = dashboard.get_dashboard_data(tenant_id)
        demo_success(f"仪表盘数据获取成功")
        
        print(f"\n仪表盘摘要:")
        print(f"  总会话数：{dashboard_data.get('total_sessions', 0)}")
        print(f"  活跃用户：{dashboard_data.get('active_users', 0)}")
        print(f"  平均评分：{dashboard_data.get('average_score', 0):.1f}")
        
        # 步骤 5: 批量操作
        demo_step(5, "批量操作")
        from enterprise import BulkOperations
        
        bulk_ops = BulkOperations()
        
        # 模拟批量导入数据
        import_data = [
            {"username": "user1", "email": "user1@example.com"},
            {"username": "user2", "email": "user2@example.com"},
            {"username": "user3", "email": "user3@example.com"},
        ]
        
        result = bulk_ops.import_users(tenant_id, import_data)
        demo_success(f"批量导入成功 - 成功：{result['success_count']}, 失败：{result['failure_count']}")
        
        # 步骤 6: 企业报表
        demo_step(6, "企业报表")
        from enterprise import ReportGenerator
        
        report_gen = ReportGenerator()
        
        # 生成团队报表
        report = report_gen.generate_team_report(team_id, period_days=30)
        demo_success(f"团队报表生成成功 - {len(report.sections)} 个章节")
        
        return True
        
    except Exception as e:
        demo_error(f"企业功能演示失败：{str(e)}")
        logger.exception("Enterprise features demo failed")
        return False


# =============================================================================
# 主演示流程
# =============================================================================

def run_full_demo(quick_mode: bool = False, specific_module: Optional[str] = None):
    """
    运行完整演示
    
    Args:
        quick_mode: 是否快速模式（跳过详细输出）
        specific_module: 指定演示的模块名称
    """
    print_header()
    
    # 定义所有演示模块
    modules = [
        ("core_framework", "核心框架", demo_core_framework),
        ("scene_system", "场景系统", demo_scene_system),
        ("evaluation_system", "评估系统", demo_evaluation_system),
        ("user_system", "用户系统", demo_user_system),
        ("analytics", "数据分析", demo_analytics),
        ("voice_support", "语音支持", demo_voice_support),
        ("enterprise_features", "企业功能", demo_enterprise_features),
    ]
    
    # 如果指定了模块，只演示该模块
    if specific_module:
        modules = [m for m in modules if m[0] == specific_module]
        if not modules:
            print(f"\n错误：未找到模块 '{specific_module}'")
            print(f"可用模块：{', '.join([m[0] for m in modules])}")
            return False
    
    # 运行演示
    results = []
    start_time = time.time()
    
    for module_id, module_name, demo_func in modules:
        if specific_module:
            print(f"\n演示模块：{module_name}")
        
        success = demo_func(quick_mode=quick_mode)
        results.append((module_name, success))
        
        if not quick_mode and not specific_module:
            time.sleep(0.5)  # 短暂停顿，便于阅读
    
    # 打印总结
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("  演示总结")
    print("=" * 70)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for module_name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {module_name}")
    
    print("-" * 70)
    print(f"  总耗时：{elapsed_time:.1f}秒")
    print(f"  成功率：{success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
    print("=" * 70)
    
    if success_count == total_count:
        print("\n🎉 所有演示模块运行成功！v1.0 功能就绪！\n")
        return True
    else:
        print(f"\n⚠️  {total_count - success_count} 个模块演示失败，请检查日志\n")
        return False


# =============================================================================
# 命令行入口
# =============================================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="AgentScope AI Interview - v1.0 综合演示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python examples/v1.0_demo.py              # 完整演示
  python examples/v1.0_demo.py --quick      # 快速演示
  python examples/v1.0_demo.py --module core_framework  # 仅演示核心框架
        """,
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速演示模式（跳过详细输出）",
    )
    
    parser.add_argument(
        "--module",
        type=str,
        choices=[
            "core_framework",
            "scene_system",
            "evaluation_system",
            "user_system",
            "analytics",
            "voice_support",
            "enterprise_features",
        ],
        help="指定演示的模块",
    )
    
    args = parser.parse_args()
    
    # 运行演示
    success = run_full_demo(
        quick_mode=args.quick,
        specific_module=args.module,
    )
    
    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
