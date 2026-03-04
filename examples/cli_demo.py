#!/usr/bin/env python3
"""
CLI Demo - CLI 界面演示程序

演示如何使用 CLI 模块进行模拟面试。

使用方法:
    python examples/cli_demo.py

功能:
- 交互式菜单导航
- 场景选择
- 对话界面
- 反馈报告
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.app import CLIApplication, main


def demo_basic():
    """基础演示 - 启动 CLI 应用"""
    print("=" * 60)
    print("AgentScope AI Interview - CLI Demo")
    print("=" * 60)
    print()
    print("启动 CLI 应用程序...")
    print()
    print("提示:")
    print("  - 使用数字键选择菜单项")
    print("  - 输入 /help 查看帮助")
    print("  - 输入 /quit 退出程序")
    print("  - 输入 /theme 切换主题")
    print()
    
    # 创建并运行应用
    app = CLIApplication(
        config={},
        theme_name="dark",
    )
    app.run()


def demo_with_custom_config():
    """自定义配置演示"""
    config = {
        "theme": "blue",
        "language": "zh-CN",
        "auto_save": True,
    }
    
    app = CLIApplication(
        config=config,
        theme_name="blue",
    )
    app.run()


def show_features():
    """展示 CLI 功能"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    
    console = Console()
    
    console.print()
    console.print(Panel.fit(
        "AgentScope AI Interview CLI 功能展示",
        style="bold blue",
    ))
    console.print()
    
    # 功能表格
    table = Table(title="核心功能")
    table.add_column("功能", style="cyan")
    table.add_column("描述", style="white")
    table.add_column("状态", style="green")
    
    table.add_row("主题系统", "支持 5 种预定义主题", "✓")
    table.add_row("交互式菜单", "数字键快速导航", "✓")
    table.add_row("场景选择", "6 种面试场景", "✓")
    table.add_row("对话界面", "实时消息气泡", "✓")
    table.add_row("打字效果", "AI 响应动画", "✓")
    table.add_row("反馈报告", "多维度评估", "✓")
    table.add_row("快捷命令", "/help, /quit, /theme 等", "✓")
    
    console.print(table)
    console.print()
    
    # 主题展示
    console.print(Panel.fit("可用主题", style="bold magenta"))
    console.print()
    
    themes = [
        ("dark", "暗色主题", "适合长时间使用"),
        ("light", "亮色主题", "适合明亮环境"),
        ("blue", "蓝色海洋", "舒适护眼"),
        ("green", "绿色终端", "经典风格"),
        ("monokai", "Monokai", "流行编辑器主题"),
    ]
    
    for name, title, desc in themes:
        console.print(f"  • [bold]{name}[/bold] - {title}: {desc}")
    
    console.print()
    console.print(Panel.fit(
        "运行 demo: python examples/cli_demo.py",
        style="bold green",
    ))
    console.print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CLI Demo - AgentScope AI Interview")
    parser.add_argument(
        "--features",
        action="store_true",
        help="展示 CLI 功能",
    )
    parser.add_argument(
        "--custom",
        action="store_true",
        help="使用自定义配置启动",
    )
    
    args = parser.parse_args()
    
    if args.features:
        show_features()
    elif args.custom:
        demo_with_custom_config()
    else:
        demo_basic()
