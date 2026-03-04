#!/usr/bin/env python3
"""
Web Demo - Web 界面演示程序

演示如何启动 Web 应用程序。

使用方法:
    python examples/web_demo.py

访问:
    http://127.0.0.1:8000

功能:
- 场景选择页面
- 对话界面
- 反馈报告
- 响应式设计
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from web.app import WebApplication, create_app
from web.config import WebConfig, WebConfigLoader


def demo_basic():
    """基础演示 - 启动 Web 服务器"""
    print("=" * 60)
    print("AgentScope AI Interview - Web Demo")
    print("=" * 60)
    print()
    print("启动 Web 服务器...")
    print()
    print("访问地址:")
    print("  http://127.0.0.1:8000")
    print()
    print("API 文档:")
    print("  http://127.0.0.1:8000/docs")
    print()
    print("按 Ctrl+C 停止服务器")
    print()
    
    # 创建并运行应用
    config = WebConfig(
        host="127.0.0.1",
        port=8000,
        debug=True,
        reload=True,
    )
    
    app = WebApplication(config=config)
    app.run()


def demo_custom_port(port: int = 8080):
    """自定义端口演示"""
    print(f"启动 Web 服务器在端口 {port}...")
    print(f"访问地址：http://127.0.0.1:{port}")
    
    config = WebConfig(
        host="127.0.0.1",
        port=port,
        debug=True,
        reload=False,
    )
    
    app = WebApplication(config=config)
    app.run()


def show_features():
    """展示 Web 功能"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "AgentScope AI Interview Web 功能展示",
        style="bold blue",
    ))
    console.print()
    
    # 功能表格
    table = Table(title="核心功能")
    table.add_column("功能", style="cyan")
    table.add_column("描述", style="white")
    table.add_column("状态", style="green")
    
    table.add_row("场景选择", "卡片式界面，支持筛选", "✓")
    table.add_row("对话界面", "聊天式布局，实时响应", "✓")
    table.add_row("打字动画", "AI 思考指示器", "✓")
    table.add_row("反馈报告", "可视化评分和图表", "✓")
    table.add_row("主题切换", "暗色/亮色主题", "✓")
    table.add_row("响应式", "支持移动端", "✓")
    table.add_row("RESTful API", "完整的 API 接口", "✓")
    table.add_row("WebSocket", "实时双向通信", "✓")
    
    console.print(table)
    console.print()
    
    # API 端点
    console.print(Panel.fit("API 端点", style="bold magenta"))
    console.print()
    
    endpoints = [
        ("GET /api/scenes", "获取场景列表"),
        ("GET /api/scenes/{id}", "获取场景详情"),
        ("POST /api/scenes/{id}/start", "开始场景"),
        ("POST /api/dialogue/sessions", "创建对话会话"),
        ("POST /api/dialogue/sessions/{id}/messages", "发送消息"),
        ("POST /api/feedback/generate", "生成反馈"),
        ("GET /api/feedback/{id}", "获取反馈"),
        ("GET /api/feedback/{id}/export/json", "导出 JSON"),
        ("GET /api/feedback/{id}/export/markdown", "导出 Markdown"),
    ]
    
    for endpoint, desc in endpoints:
        console.print(f"  • [bold cyan]{endpoint}[/bold cyan] - {desc}")
    
    console.print()
    console.print()
    
    # 页面路由
    console.print(Panel.fit("页面路由", style="bold green"))
    console.print()
    
    pages = [
        ("/", "首页"),
        ("/scenes", "场景选择"),
        ("/dialogue/{session_id}", "对话界面"),
        ("/feedback/{evaluation_id}", "反馈报告"),
    ]
    
    for page, desc in pages:
        console.print(f"  • [bold]{page}[/bold] - {desc}")
    
    console.print()
    console.print(Panel.fit(
        "运行 demo: python examples/web_demo.py",
        style="bold green",
    ))
    console.print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Demo - AgentScope AI Interview")
    parser.add_argument(
        "--features",
        action="store_true",
        help="展示 Web 功能",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认：8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="服务器主机 (默认：127.0.0.1)",
    )
    
    args = parser.parse_args()
    
    if args.features:
        show_features()
    else:
        # 设置配置
        config = WebConfig(
            host=args.host,
            port=args.port,
            debug=True,
            reload=True,
        )
        
        print("=" * 60)
        print("AgentScope AI Interview - Web Demo")
        print("=" * 60)
        print()
        print(f"启动 Web 服务器...")
        print()
        print(f"访问地址:")
        print(f"  http://{args.host}:{args.port}")
        print()
        print(f"API 文档:")
        print(f"  http://{args.host}:{args.port}/docs")
        print()
        print("按 Ctrl+C 停止服务器")
        print()
        
        app = WebApplication(config=config)
        app.run()
