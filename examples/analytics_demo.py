"""
Analytics Module Demo

分析模块演示脚本

展示 v0.7 数据追踪与洞察功能：
- 学习分析 (LearningAnalytics)
- 行为追踪 (BehaviorTracker)
- 推荐引擎 (RecommendationEngine)
- 统计引擎 (StatisticsEngine)
- 洞察仪表盘 (InsightsDashboard)
- 数据导出 (DataExporter)

Usage:
    python examples/analytics_demo.py
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics import (
    LearningAnalytics,
    BehaviorTracker,
    RecommendationEngine,
    StatisticsEngine,
    InsightsDashboard,
    DataExporter,
)


# =============================================================================
# Helper Functions
# =============================================================================

def generate_sample_sessions(user_id: str, count: int = 20) -> List[Dict[str, Any]]:
    """生成模拟会话数据"""
    sessions = []
    base_date = datetime.utcnow() - timedelta(days=count * 2)

    dimensions = [
        "language_expression",
        "logical_thinking",
        "professional_knowledge",
        "problem_solving",
        "communication_collaboration",
        "adaptability",
    ]

    # 基础分数（模拟进步趋势）
    base_scores = {
        "language_expression": 65 + random.uniform(-5, 5),
        "logical_thinking": 60 + random.uniform(-5, 5),
        "professional_knowledge": 55 + random.uniform(-5, 5),
        "problem_solving": 62 + random.uniform(-5, 5),
        "communication_collaboration": 70 + random.uniform(-5, 5),
        "adaptability": 58 + random.uniform(-5, 5),
    }

    scene_types = ["technical_interview", "hr_interview", "project_meeting", "salon"]

    for i in range(count):
        # 时间递增
        session_date = base_date + timedelta(days=i * 1.5 + random.uniform(-0.5, 0.5))

        # 分数逐渐提升
        progress_factor = 1 + (i / count) * 0.3  # 最多提升 30%

        # 生成各维度分数
        eval_result = {}
        for dim in dimensions:
            base = base_scores[dim]
            noise = random.uniform(-8, 8)
            score = min(95, max(40, (base + noise) * progress_factor))
            eval_result[dim] = round(score, 1)

        # 总体分数
        eval_result["overall_quality"] = round(
            sum(eval_result[d] for d in dimensions) / len(dimensions), 1
        )

        session = {
            "session_id": i + 1,
            "user_id": user_id,
            "scene_type": random.choice(scene_types),
            "completed_at": session_date.isoformat(),
            "duration_seconds": random.randint(900, 2700),  # 15-45 分钟
            "status": "completed",
            "evaluation_result": eval_result,
        }

        sessions.append(session)

    return sessions


def print_section(title: str, char: str = "="):
    """打印分隔线"""
    print(f"\n{char * 60}")
    print(f"{title}")
    print(f"{char * 60}")


def print_dict(data: Dict, indent: int = 0):
    """打印字典"""
    prefix = " " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            print_dict(value, indent + 2)
        elif isinstance(value, list):
            print(f"{prefix}{key}: [{len(value)} items]")
            for item in value[:3]:  # 只显示前 3 个
                if isinstance(item, dict):
                    print(f"{prefix}  - {item}")
                else:
                    print(f"{prefix}  - {item}")
            if len(value) > 3:
                print(f"{prefix}  ... and {len(value) - 3} more")
        else:
            print(f"{prefix}{key}: {value}")


# =============================================================================
# Demo Functions
# =============================================================================

def demo_learning_analytics(sessions: List[Dict[str, Any]], user_id: str):
    """演示学习分析功能"""
    print_section("1. Learning Analytics (学习分析)")

    analytics = LearningAnalytics()

    # 生成学习画像
    print("\n生成学习画像...")
    profile = analytics.generate_learning_profile(user_id, sessions)

    print(f"\n用户 ID: {profile.user_id}")
    print(f"技能水平：{profile.skill_level.value}")
    print(f"学习模式：{profile.learning_pattern.value}")
    print(f"总会话数：{profile.total_sessions}")
    print(f"总时长：{profile.total_hours:.2f} 小时")
    print(f"平均分：{profile.avg_score:.2f}")

    print(f"\n优势项 ({len(profile.strengths)}):")
    for strength in profile.strengths:
        print(f"  - {strength.dimension}: {strength.score:.1f}分 "
              f"(置信度：{strength.confidence:.2f}, 趋势：{strength.trend})")

    print(f"\n弱点项 ({len(profile.weaknesses)}):")
    for weakness in profile.weaknesses:
        print(f"  - {weakness.dimension}: {weakness.score:.1f}分 "
              f"(优先级：{weakness.priority})")
        for suggestion in weakness.improvement_suggestions[:2]:
            print(f"      • {suggestion}")

    print(f"\n学习洞察 ({len(profile.insights)}):")
    for insight in profile.insights[:3]:
        print(f"  [{insight.insight_type}] {insight.title}")
        print(f"    {insight.description}")

    return analytics.to_dict(profile)


def demo_behavior_tracking(sessions: List[Dict[str, Any]], user_id: str):
    """演示行为追踪功能"""
    print_section("2. Behavior Tracking (行为追踪)")

    tracker = BehaviorTracker()

    # 分析行为
    print("\n分析用户行为...")
    report = tracker.analyze_behavior(user_id, sessions, period_days=60)

    print(f"\n分析周期：{report.period_days}天")

    # 会话模式
    sp = report.session_pattern
    print(f"\n会话模式:")
    print(f"  平均每周会话数：{sp.avg_sessions_per_week:.2f}")
    print(f"  平均时长：{sp.avg_duration_minutes:.2f}分钟")
    print(f"  偏好时间：{sp.preferred_time_of_day}")
    print(f"  偏好日期：{sp.preferred_days}")
    print(f"  一致性分数：{sp.consistency_score:.2f}")

    # 参与度
    eng = report.engagement
    print(f"\n参与度:")
    print(f"  等级：{eng.level.value}")
    print(f"  总会话数：{eng.total_sessions}")
    print(f"  总时长：{eng.total_hours:.2f}小时")
    print(f"  最近 7 天：{eng.sessions_last_7_days}次")
    print(f"  当前连续：{eng.current_streak}天")
    print(f"  最长连续：{eng.longest_streak}天")

    # 改进模式
    imp = report.improvement_pattern
    print(f"\n改进模式:")
    print(f"  趋势：{imp.overall_trend}")
    print(f"  改进率：{imp.improvement_rate:.2f}%/周")
    print(f"  加速度：{imp.acceleration:.4f}")

    # 平台期
    plat = report.plateau_analysis
    print(f"\n平台期分析:")
    print(f"  状态：{plat.status.value}")
    print(f"  持续天数：{plat.duration_days}")
    if plat.recommendations:
        print(f"  建议:")
        for rec in plat.recommendations[:3]:
            print(f"    • {rec}")

    print(f"\n行为洞察:")
    for insight in report.behavioral_insights[:5]:
        print(f"  • {insight}")

    return tracker.to_dict(report)


def demo_recommendation_engine(sessions: List[Dict[str, Any]], user_id: str,
                               learning_profile: Dict[str, Any],
                               behavior_report: Dict[str, Any]):
    """演示推荐引擎功能"""
    print_section("3. Recommendation Engine (推荐引擎)")

    engine = RecommendationEngine()

    # 生成推荐
    print("\n生成个性化推荐...")
    report = engine.generate_recommendations(
        user_id, sessions, learning_profile, behavior_report
    )

    print(f"\n主题推荐 ({len(report.topic_recommendations)}):")
    for rec in report.topic_recommendations[:5]:
        print(f"  [{rec.priority}] {rec.topic_name}")
        print(f"      维度：{rec.dimension}")
        print(f"      原因：{rec.reason}")
        print(f"      难度：{rec.difficulty.value}")
        print(f"      预计提升：{rec.expected_improvement:.1f}%")

    if report.difficulty_recommendation:
        dr = report.difficulty_recommendation
        print(f"\n难度推荐:")
        print(f"  当前：{dr.current_level.value}")
        print(f"  推荐：{dr.recommended_level.value}")
        print(f"  原因：{dr.reason}")
        print(f"  置信度：{dr.confidence:.2f}")
        print(f"  调整因素：{dr.adjustment_factors}")

    if report.learning_path:
        lp = report.learning_path
        print(f"\n学习路径:")
        print(f"  路径 ID: {lp.path_id}")
        print(f"  持续天数：{lp.duration_days}天")
        print(f"  项目数：{len(lp.items)}")
        print(f"  预期结果:")
        for outcome in lp.expected_outcomes[:3]:
            print(f"    • {outcome}")

    print(f"\n练习方法推荐 ({len(report.practice_methods)}):")
    for method in report.practice_methods[:3]:
        print(f"  {method.method_name}: {method.description}")

    print(f"\n一般建议:")
    for advice in report.general_advice[:5]:
        print(f"  • {advice}")

    return engine.to_dict(report)


def demo_statistics_engine(sessions: List[Dict[str, Any]], user_id: str):
    """演示统计引擎功能"""
    print_section("4. Statistics Engine (统计引擎)")

    engine = StatisticsEngine()

    # 生成统计报告
    print("\n生成统计报告...")
    report = engine.generate_statistical_report(user_id, sessions, period_days=60)

    # 描述性统计
    ds = report.descriptive_stats
    print(f"\n描述性统计:")
    print(f"  样本数：{ds.count}")
    print(f"  平均分：{ds.mean:.2f}")
    print(f"  中位数：{ds.median:.2f}")
    print(f"  标准差：{ds.std_dev:.2f}")
    print(f"  最小值：{ds.min_value:.2f}")
    print(f"  最大值：{ds.max_value:.2f}")
    print(f"  Q1: {ds.q1:.2f}, Q3: {ds.q3:.2f}, IQR: {ds.iqr:.2f}")

    # 百分位数据
    pd = report.percentile_data
    print(f"\n百分位数据:")
    print(f"  P10: {pd.p10:.2f}, P25: {pd.p25:.2f}, P50: {pd.p50:.2f}")
    print(f"  P75: {pd.p75:.2f}, P90: {pd.p90:.2f}, P95: {pd.p95:.2f}")

    # 分布分析
    da = report.distribution_analysis
    print(f"\n分布分析:")
    print(f"  类型：{da.type.value}")
    print(f"  偏度：{da.skewness:.3f}")
    print(f"  峰度：{da.kurtosis:.3f}")
    print(f"  正态分布：{da.is_normal}")
    print(f"  异常值：{da.outliers_count}个")

    # 对比分析
    if report.comparative_analysis:
        ca = report.comparative_analysis
        print(f"\n对比分析:")
        print(f"  用户分数：{ca.user_score:.2f}")
        print(f"  人口平均：{ca.population_mean:.2f}")
        print(f"  百分位排名：{ca.percentile_rank:.1f}%")
        print(f"  Z 分数：{ca.z_score:.2f}")
        print(f"  性能水平：{ca.performance_level}")
        print(f"  {ca.comparison_summary}")

    # 趋势统计
    ts = report.trend_statistics
    print(f"\n趋势统计:")
    print(f"  斜率：{ts.slope:.3f}")
    print(f"  R²: {ts.r_squared:.3f}")
    print(f"  方向：{ts.trend_direction}")
    print(f"  强度：{ts.trend_strength}")
    print(f"  预测值：{ts.predicted_next_value:.2f}")

    print(f"\n统计摘要:")
    print(f"  {report.summary}")

    return engine.to_dict(report)


def demo_insights_dashboard(sessions: List[Dict[str, Any]], user_id: str,
                           learning_profile: Dict[str, Any],
                           behavior_report: Dict[str, Any],
                           statistical_report: Dict[str, Any],
                           recommendation_report: Dict[str, Any]):
    """演示洞察仪表盘功能"""
    print_section("5. Insights Dashboard (洞察仪表盘)")

    dashboard = InsightsDashboard()

    # 生成仪表盘
    print("\n生成洞察仪表盘...")
    data = dashboard.generate_dashboard(
        user_id, sessions, learning_profile, behavior_report,
        statistical_report, recommendation_report, period_days=60
    )

    print(f"\n生成时间：{data.generated_at}")
    print(f"统计周期：{data.period_days}天")

    print(f"\n关键洞察 ({len(data.key_insights)}):")
    for insight in data.key_insights[:5]:
        print(f"  {insight.icon} [{insight.category.value}] {insight.title}")
        print(f"     {insight.description}")
        if insight.actionable_items:
            print(f"     行动：{insight.actionable_items[0]}")

    print(f"\n表现卡片 ({len(data.performance_cards)}):")
    for card in data.performance_cards[:5]:
        change_str = f"+{card.change:.1f}" if card.change > 0 else f"{card.change:.1f}"
        print(f"  {card.dimension_name}: {card.current_score:.1f} "
              f"({change_str}) - {card.level}")

    print(f"\n趋势分析 ({len(data.trend_analyses)}):")
    for trend in data.trend_analyses[:3]:
        print(f"  {trend.metric_name}: {trend.current_value:.2f} "
              f"({trend.trend_direction}, {trend.trend_strength})")

    print(f"\n可操作建议 ({len(data.recommendations)}):")
    for rec in data.recommendations[:3]:
        print(f"  [P{rec.priority}] {rec.title}")
        print(f"     {rec.description}")
        print(f"     时间：{rec.time_required_minutes}分钟")

    print(f"\n成就 ({len(data.achievements)}):")
    for achievement in data.achievements[:5]:
        print(f"  {achievement.icon} {achievement.name}")
        print(f"     {achievement.description}")

    print(f"\n仪表盘摘要:")
    print(f"  {data.summary_text}")

    return dashboard.to_dict(data)


def demo_data_export(sessions: List[Dict[str, Any]], user_id: str,
                    dashboard_data: Dict[str, Any]):
    """演示数据导出功能"""
    print_section("6. Data Export (数据导出)")

    exporter = DataExporter(config={"output_dir": "./exports"})

    print("\n导出 JSON 报告...")
    json_result = exporter.export_to_json(
        dashboard_data,
        filename=f"analytics_report_{user_id}.json"
    )
    print(f"  成功：{json_result.success}")
    print(f"  文件：{json_result.file_path}")
    print(f"  大小：{json_result.file_size_bytes}字节")
    print(f"  消息：{json_result.message}")

    print("\n导出 Excel 报告...")
    excel_result = exporter.export_to_excel(
        dashboard_data,
        filename=f"analytics_report_{user_id}.xlsx"
    )
    print(f"  成功：{excel_result.success}")
    print(f"  文件：{excel_result.file_path}")
    print(f"  大小：{excel_result.file_size_bytes}字节")
    print(f"  消息：{excel_result.message}")

    print("\n导出 PDF 报告...")
    pdf_result = exporter.export_to_pdf(
        dashboard_data,
        filename=f"analytics_report_{user_id}.pdf"
    )
    print(f"  成功：{pdf_result.success}")
    print(f"  文件：{pdf_result.file_path}")
    print(f"  大小：{pdf_result.file_size_bytes}字节")
    print(f"  消息：{pdf_result.message}")

    print("\n导出会话 CSV...")
    csv_result = exporter.export_to_csv(
        sessions,
        filename=f"sessions_{user_id}.csv"
    )
    print(f"  成功：{csv_result.success}")
    print(f"  文件：{csv_result.file_path}")
    print(f"  大小：{csv_result.file_size_bytes}字节")
    print(f"  消息：{csv_result.message}")

    print("\n创建数据备份...")
    backup_result = exporter.create_backup(
        user_id, sessions,
        {"dashboard": dashboard_data},
        filename=f"backup_{user_id}.json"
    )
    print(f"  成功：{backup_result.success}")
    print(f"  文件：{backup_result.file_path}")
    print(f"  大小：{backup_result.file_size_bytes}字节")
    print(f"  消息：{backup_result.message}")

    return {
        "json": json_result,
        "excel": excel_result,
        "pdf": pdf_result,
        "csv": csv_result,
        "backup": backup_result,
    }


# =============================================================================
# Main Demo
# =============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("AgentScope AI Interview - Analytics Module Demo")
    print("分析模块演示 (v0.7.0)")
    print("=" * 60)

    # 用户 ID
    user_id = "demo_user_001"

    # 生成模拟数据
    print("\n生成模拟会话数据...")
    sessions = generate_sample_sessions(user_id, count=20)
    print(f"生成了 {len(sessions)} 次会话")

    # 1. 学习分析
    learning_profile = demo_learning_analytics(sessions, user_id)

    # 2. 行为追踪
    behavior_report = demo_behavior_tracking(sessions, user_id)

    # 3. 推荐引擎
    recommendation_report = demo_recommendation_engine(
        sessions, user_id, learning_profile, behavior_report
    )

    # 4. 统计引擎
    statistical_report = demo_statistics_engine(sessions, user_id)

    # 5. 洞察仪表盘
    dashboard_data = demo_insights_dashboard(
        sessions, user_id, learning_profile, behavior_report,
        statistical_report, recommendation_report
    )

    # 6. 数据导出
    export_results = demo_data_export(sessions, user_id, dashboard_data)

    # 总结
    print_section("Demo Summary (演示总结)", "=")
    print(f"\n✓ 完成所有分析模块演示")
    print(f"✓ 用户：{user_id}")
    print(f"✓ 会话数：{len(sessions)}")
    print(f"✓ 导出文件：")
    for format_name, result in export_results.items():
        status = "✓" if result.success else "✗"
        print(f"  {status} {format_name.upper()}: {result.file_path}")

    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("演示完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
