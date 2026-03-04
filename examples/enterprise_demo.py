"""
Enterprise Demo - 企业版功能演示

演示 v0.9 企业版功能：
- 多租户管理
- 团队协作
- 协作会话
- 管理员仪表盘
- 批量操作
- 企业报表
- SSO 集成

Version: v0.9.0
"""

import sys
from datetime import datetime, timedelta

# 导入企业版模块
from enterprise import (
    TenantManager,
    TenantPlan,
    TenantStatus,
    TeamManager,
    TeamRole,
    CollaborationManager,
    CollaborationSession,
    SessionType,
    AdminDashboard,
    BulkOperations,
    EnterpriseReport,
    ReportGenerator,
    ReportType,
    SSOIntegration,
    OAuth2Config,
)


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_tenant_management():
    """演示租户管理"""
    print_section("1. 租户管理 (Tenant Management)")

    # 创建租户管理器
    tenant_manager = TenantManager("data/demo_tenants.json")

    # 创建租户
    print("\n📝 创建新租户...")
    tenant = tenant_manager.create_tenant(
        name="Acme Corporation",
        plan=TenantPlan.PROFESSIONAL,
        contact_email="admin@acme.com",
        trial_days=30,
    )
    print(f"✅ 租户创建成功:")
    print(f"   ID: {tenant.id}")
    print(f"   名称：{tenant.name}")
    print(f"   计划：{tenant.plan.value}")
    print(f"   状态：{tenant.status.value}")
    print(f"   试用剩余：{tenant.days_remaining} 天")

    # 创建另一个租户
    tenant2 = tenant_manager.create_tenant(
        name="Tech Startup Inc",
        plan=TenantPlan.ENTERPRISE,
        contact_email="contact@techstartup.io",
    )
    print(f"\n✅ 创建第二个租户：{tenant2.name}")

    # 列出租户
    print("\n📋 租户列表:")
    tenants = tenant_manager.list_tenants()
    for t in tenants:
        print(f"   - {t.name} ({t.plan.value}, {t.status.value})")

    # 获取统计
    print("\n📊 租户统计:")
    stats = tenant_manager.get_statistics()
    print(f"   总租户数：{stats['total_tenants']}")
    print(f"   活跃租户：{stats['by_status'].get('active', 0)}")
    print(f"   试用租户：{stats['active_trials']}")

    return tenant_manager


def demo_team_management(tenant_manager: TenantManager):
    """演示团队管理"""
    print_section("2. 团队管理 (Team Management)")

    team_manager = TeamManager("data/demo_teams.json")

    # 获取第一个租户
    tenants = tenant_manager.list_tenants()
    if not tenants:
        print("❌ 没有可用租户")
        return

    tenant = tenants[0]

    # 创建团队
    print(f"\n📝 为租户 '{tenant.name}' 创建团队...")
    team = team_manager.create_team(
        tenant_id=tenant.id,
        name="Engineering Team",
        description="Software development team",
        owner_id="user_001",
        max_members=20,
    )
    print(f"✅ 团队创建成功:")
    print(f"   ID: {team.id}")
    print(f"   名称：{team.name}")
    print(f"   成员数：{team.member_count}")

    # 添加成员
    print("\n👥 添加团队成员...")
    for i in range(5):
        user_id = f"user_{i+1:03d}"
        role = TeamRole.ADMIN if i == 0 else TeamRole.MEMBER
        member = team_manager.add_member(team.id, user_id, role=role)
        if member:
            print(f"   ✅ 添加成员：{user_id} ({role.value})")

    # 列出团队
    print("\n📋 团队列表:")
    teams = team_manager.list_teams(tenant_id=tenant.id)
    for t in teams:
        print(f"   - {t.name} ({t.member_count} 成员)")

    # 获取统计
    print("\n📊 团队统计:")
    stats = team_manager.get_statistics(tenant.id)
    print(f"   总团队数：{stats['total_teams']}")
    print(f"   平均团队大小：{stats['avg_team_size']:.1f}")

    return team_manager


def demo_collaboration(team_manager: TeamManager):
    """演示协作会话"""
    print_section("3. 协作会话 (Collaboration Sessions)")

    collaboration_manager = CollaborationManager("data/demo_collaboration.json")

    # 获取第一个团队
    teams = team_manager.list_teams()
    if not teams:
        print("❌ 没有可用团队")
        return

    team = teams[0]

    # 创建协作会话
    print(f"\n📝 为团队 '{team.name}' 创建协作会话...")
    session = collaboration_manager.create_session(
        team_id=team.id,
        session_type=SessionType.TRAINING,
        name="Interview Practice Session",
        description="Group interview practice",
        scene="interview",
        participants=["user_001", "user_002", "user_003"],
    )
    print(f"✅ 会话创建成功:")
    print(f"   ID: {session.id}")
    print(f"   名称：{session.name}")
    print(f"   类型：{session.session_type.value}")
    print(f"   状态：{session.status.value}")
    print(f"   参与者：{len(session.participants)} 人")

    # 开始会话
    print("\n▶️ 开始会话...")
    session = collaboration_manager.start_session(session.id)
    if session:
        print(f"   ✅ 会话已开始")

    # 添加聊天消息
    print("\n💬 发送聊天消息...")
    collaboration_manager.add_chat_message(session.id, "user_001", "大家好，开始练习吧！")
    collaboration_manager.add_chat_message(session.id, "user_002", "好的，我准备好了！")

    # 结束会话
    print("\n⏹️ 结束会话...")
    session = collaboration_manager.end_session(
        session.id,
        results={
            "average_score": 85.5,
            "completion_rate": 100,
            "feedback": "Great job everyone!",
        },
    )
    if session:
        print(f"   ✅ 会话已结束")
        print(f"   时长：{session.duration_minutes} 分钟")

    # 获取统计
    print("\n📊 协作统计:")
    stats = collaboration_manager.get_statistics(team.id)
    print(f"   总会话数：{stats['total_sessions']}")
    print(f"   已完成会话：{stats['completed_sessions']}")
    print(f"   总时长：{stats['total_duration_minutes']} 分钟")

    return collaboration_manager


def demo_admin_dashboard(tenant_manager: TenantManager, team_manager: TeamManager):
    """演示管理员仪表盘"""
    print_section("4. 管理员仪表盘 (Admin Dashboard)")

    dashboard = AdminDashboard(tenant_manager, team_manager)

    # 显示仪表盘
    print("\n📊 显示管理员仪表盘...\n")
    dashboard.display()

    # 显示租户详情
    tenants = tenant_manager.list_tenants()
    if tenants:
        print("\n📝 显示租户详情...")
        dashboard.show_tenant_detail(tenants[0].id)


def demo_bulk_operations():
    """演示批量操作"""
    print_section("5. 批量操作 (Bulk Operations)")

    bulk_ops = BulkOperations()

    # 创建示例 CSV
    import os
    os.makedirs("data", exist_ok=True)

    csv_content = """email,name,role,department
john@example.com,John Doe,member,Engineering
jane@example.com,Jane Smith,admin,Product
bob@example.com,Bob Johnson,member,Design
alice@example.com,Alice Williams,member,Marketing
"""

    csv_path = "data/demo_users.csv"
    with open(csv_path, "w") as f:
        f.write(csv_content)

    print(f"\n📝 创建示例 CSV: {csv_path}")
    print(csv_content)

    # 导入用户（dry run）
    print("\n📥 导入用户 (Dry Run)...")
    result = bulk_ops.import_users_from_csv(
        file_path=csv_path,
        tenant_id="demo_tenant",
        dry_run=True,
    )

    print(f"\n📊 导入结果:")
    print(f"   总行数：{result.total_rows}")
    print(f"   成功：{result.successful}")
    print(f"   失败：{result.failed}")
    print(f"   跳过：{result.skipped}")
    print(f"   成功率：{result.success_rate:.1f}%")
    print(f"   耗时：{result.duration_seconds:.2f} 秒")


def demo_reports(tenant_manager: TenantManager, team_manager: TeamManager):
    """演示企业报表"""
    print_section("6. 企业报表 (Enterprise Reports)")

    report_generator = ReportGenerator(
        tenant_manager=tenant_manager,
        team_manager=team_manager,
    )

    # 获取第一个租户
    tenants = tenant_manager.list_tenants()
    if not tenants:
        print("❌ 没有可用租户")
        return

    tenant = tenants[0]

    # 生成报表
    print(f"\n📝 生成租户摘要报表...")
    report = report_generator.generate_report(
        report_type=ReportType.TENANT_SUMMARY,
        tenant_id=tenant.id,
        title="Monthly Tenant Summary",
        period_days=30,
    )

    print(f"\n✅ 报表生成:")
    print(f"   ID: {report.id}")
    print(f"   标题：{report.title}")
    print(f"   类型：{report.report_type.value}")
    print(f"   状态：{report.status}")
    print(f"   生成时间：{report.generation_time_seconds:.2f} 秒")

    # 导出报表
    print("\n📤 导出报表...")
    file_path = report_generator.export_report(report.id, report.format)
    if file_path:
        print(f"   ✅ 报表已导出：{file_path}")

    # 生成团队表现报表
    print("\n📝 生成团队表现报表...")
    team_report = report_generator.generate_report(
        report_type=ReportType.TEAM_PERFORMANCE,
        tenant_id=tenant.id,
        period_days=7,
    )
    print(f"   ✅ 报表生成：{team_report.title}")


def demo_sso():
    """演示 SSO 集成"""
    print_section("7. SSO 集成 (Single Sign-On)")

    sso = SSOIntegration("data/demo_sso.json")

    # 配置 OAuth2
    print("\n📝 配置 OAuth2...")
    oauth2_config = OAuth2Config(
        client_id="demo_client_id",
        client_secret="demo_client_secret",
        authorization_url="https://example.com/oauth/authorize",
        token_url="https://example.com/oauth/token",
        userinfo_url="https://example.com/oauth/userinfo",
        redirect_uri="http://localhost:8000/admin/auth/callback",
    )

    sso.configure_oauth2("demo_tenant", oauth2_config)
    print("   ✅ OAuth2 配置成功")

    # 创建认证 URL
    print("\n🔗 创建认证 URL...")
    auth_url = sso.create_auth_url("demo_tenant", "oauth2")
    if auth_url:
        print(f"   认证 URL: {auth_url[:80]}...")

    # 获取统计
    print("\n📊 SSO 统计:")
    stats = sso.get_statistics("demo_tenant")
    print(f"   总会话数：{stats['total_sessions']}")
    print(f"   已启用提供商：{stats['enabled_providers']}")


def main():
    """主函数"""
    print("=" * 60)
    print("  AgentScope AI Interview - Enterprise Demo v0.9")
    print("  企业版功能演示")
    print("=" * 60)
    print(f"\n开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. 租户管理
        tenant_manager = demo_tenant_management()

        # 2. 团队管理
        team_manager = demo_team_management(tenant_manager)

        # 3. 协作会话
        demo_collaboration(team_manager)

        # 4. 管理员仪表盘
        demo_admin_dashboard(tenant_manager, team_manager)

        # 5. 批量操作
        demo_bulk_operations()

        # 6. 企业报表
        demo_reports(tenant_manager, team_manager)

        # 7. SSO 集成
        demo_sso()

        print_section("演示完成")
        print("\n✅ 所有企业版功能演示完成！")
        print(f"\n结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\n❌ 演示过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
