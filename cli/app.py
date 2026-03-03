"""
CLI Application - CLI 主应用程序模块

提供完整的命令行界面应用程序，整合所有 UI 组件。

核心类:
- CLIApplication: 主应用程序类
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table

from .themes import ThemeManager, get_theme_manager, ThemeType
from .widgets import (
    Header,
    Footer,
    MessageBubble,
    TypingIndicator,
    Spinner,
    Panel,
    Divider,
    StatusBadge,
    Menu as MenuWidget,
)
from .menus import (
    MenuManager,
    MainMenu,
    SceneMenu,
    DialogueMenu,
    FeedbackMenu,
    SettingsMenu,
    HelpPanel,
)


class CLIApplication:
    """
    CLI 主应用程序

    提供完整的命令行界面，包括：
    - 主菜单导航
    - 场景选择
    - 对话界面
    - 反馈展示
    - 设置管理

    Example:
        >>> app = CLIApplication()
        >>> app.run()
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        theme_name: str = "dark",
    ):
        """
        初始化 CLI 应用程序

        Args:
            config: 配置字典
            theme_name: 主题名称
        """
        self.config = config or {}
        self.theme_manager = ThemeManager(default_theme=theme_name)
        self.console = self.theme_manager.create_console()

        # 菜单管理器
        self.menu_manager = MenuManager(
            console=self.console,
            theme=self.theme_manager.current_theme,
        )

        # 应用状态
        self._current_scene: Optional[Dict[str, Any]] = None
        self._dialogue_history: List[Dict[str, Any]] = []
        self._is_running = False
        self._start_time: Optional[float] = None

        # 注册回调
        self._register_callbacks()

    def _register_callbacks(self) -> None:
        """注册菜单回调"""
        self.menu_manager.register_callback("theme", self._toggle_theme)
        self.menu_manager.register_callback("help", self._show_help)
        self.menu_manager.register_callback("quit", self._quit)

    def run(self) -> int:
        """
        运行应用程序主循环

        Returns:
            退出码
        """
        self._is_running = True
        self._start_time = time.time()

        self.console.clear()
        self._show_welcome()

        while self._is_running:
            try:
                self._main_loop()
            except KeyboardInterrupt:
                self._confirm_quit()
            except Exception as e:
                self.console.print(f"[red]错误：{e}[/red]")
                self.console.print("[yellow]按任意键返回主菜单...[/yellow]")
                self.console.input()

        self._show_farewell()
        return 0

    def _main_loop(self) -> None:
        """主循环"""
        # 显示主菜单
        main_menu = MainMenu(theme=self.theme_manager.current_theme)
        footer = Footer(
            hints=["使用数字键选择菜单项", "输入 /help 查看帮助"],
            theme=self.theme_manager.current_theme,
        )

        self.menu_manager.show_menu(
            main_menu,
            header=Header(
                title="AgentScope AI Interview",
                subtitle="AI 模拟面试平台 v0.4",
                theme=self.theme_manager.current_theme,
            ),
            footer=footer,
        )

        # 获取用户选择
        choice = Prompt.ask(
            "\n请选择",
            choices=["0", "1", "2", "3", "4", "5"],
            default="1",
        )

        # 处理选择
        self._handle_main_menu_choice(choice)

    def _handle_main_menu_choice(self, choice: str) -> None:
        """处理主菜单选择"""
        handlers = {
            "1": self._start_interview,
            "2": self._select_scene,
            "3": self._show_history,
            "4": self._show_settings,
            "5": self._show_help,
            "0": self._quit,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
        else:
            self.console.print("[yellow]无效的选择[/yellow]")
            time.sleep(1)

    def _show_welcome(self) -> None:
        """显示欢迎信息"""
        header = Header(
            title="欢迎使用 AgentScope AI Interview",
            subtitle="专业的 AI 模拟面试训练平台",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(header.render())

        welcome_text = """
这是一个专业的 AI 模拟面试训练平台，通过多智能体协作模拟真实职场对话场景。

主要功能:
  • 多种面试场景选择（技术面试、HR 面试等）
  • 智能面试官，支持不同风格
  • 实时对话交互
  • 详细的评估反馈报告

使用提示:
  • 使用数字键选择菜单项
  • 输入 /help 查看帮助
  • 输入 /quit 退出程序
  • 输入 /theme 切换主题

"""
        panel = Panel(
            welcome_text,
            title="使用说明",
            border_style="blue",
        )
        self.console.print(panel)
        self.console.input("\n按 Enter 键继续...")

    def _show_farewell(self) -> None:
        """显示告别信息"""
        duration = time.time() - self._start_time if self._start_time else 0

        text = f"""
感谢使用 AgentScope AI Interview!

本次会话时长：{duration:.0f} 秒
对话轮数：{len(self._dialogue_history)}

期待下次再见！
"""
        panel = Panel(
            text,
            title="再见",
            border_style="green",
        )
        self.console.print(panel)

    def _start_interview(self) -> None:
        """开始面试"""
        # 检查是否已选择场景
        if not self._current_scene:
            self.console.print("[yellow]请先选择一个面试场景[/yellow]")
            time.sleep(1)
            self._select_scene()
            if not self._current_scene:
                return

        # 进入对话界面
        self._run_dialogue()

    def _select_scene(self) -> None:
        """选择场景"""
        self.console.clear()

        # 获取可用场景（从 scenes 模块）
        scenes = self._get_available_scenes()

        scene_menu = SceneMenu(
            scenes=scenes,
            title="选择面试场景",
            theme=self.theme_manager.current_theme,
        )

        header = Header(
            title="场景选择",
            theme=self.theme_manager.current_theme,
        )

        self.menu_manager.show_menu(scene_menu, header=header)

        # 获取用户选择
        choice = Prompt.ask(
            "\n请选择场景编号",
            choices=[str(i) for i in range(1, len(scenes) + 1)],
            default="1",
        )

        # 设置当前场景
        self._current_scene = scene_menu.get_scene_by_index(int(choice))

        if self._current_scene:
            self.console.print(
                f"\n[green]✓ 已选择场景：{self._current_scene.get('name')}[/green]"
            )
            time.sleep(1)

    def _get_available_scenes(self) -> List[Dict[str, Any]]:
        """获取可用场景列表"""
        # 这里应该从 scenes 模块获取真实场景
        # 暂时使用预设场景
        return [
            {
                "name": "技术面试 - 前端开发",
                "description": "模拟前端工程师技术面试，涵盖 HTML/CSS/JavaScript/框架等",
                "difficulty": 3,
                "domain": "frontend",
                "style": "friendly",
            },
            {
                "name": "技术面试 - 后端开发",
                "description": "模拟后端工程师技术面试，涵盖系统设计/数据库/API 等",
                "difficulty": 4,
                "domain": "backend",
                "style": "strict",
            },
            {
                "name": "技术面试 - 系统设计",
                "description": "模拟系统架构师面试，考察系统设计能力",
                "difficulty": 5,
                "domain": "system_design",
                "style": "pressure",
            },
            {
                "name": "HR 面试",
                "description": "模拟人力资源面试，考察软技能和企业文化匹配度",
                "difficulty": 2,
                "domain": "hr",
                "style": "friendly",
            },
            {
                "name": "综合面试",
                "description": "综合技术能力和软技能的全面面试",
                "difficulty": 3,
                "domain": "general",
                "style": "friendly",
            },
        ]

    def _run_dialogue(self) -> None:
        """运行对话界面"""
        self.console.clear()

        # 显示对话界面头部
        header = Header(
            title=f"对话中 - {self._current_scene.get('name', '面试')}",
            subtitle="输入消息与面试官交流，输入 /quit 结束",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(header.render())
        self.console.print()

        # 显示开场白
        self._show_opening_message()

        # 对话循环
        dialogue_menu = DialogueMenu(theme=self.theme_manager.current_theme)
        self.console.print(dialogue_menu.render())
        self.console.print()

        while self._is_running:
            try:
                # 获取用户输入
                user_input = self.console.input("[bold blue]你:[/bold blue] ")

                # 处理特殊命令
                if self._handle_dialogue_command(user_input):
                    continue

                # 发送消息并获取响应
                self._send_message(user_input)

            except KeyboardInterrupt:
                if Confirm.ask("\n确定要结束面试吗？"):
                    break

        # 显示反馈
        self._show_feedback()

    def _show_opening_message(self) -> None:
        """显示开场白"""
        opening = MessageBubble(
            content=f"你好！欢迎参加{self._current_scene.get('name', '面试')}。"
                    f"我是你的面试官，今天将由我来主持这次面试。"
                    f"请放松，展示你最好的一面。我们开始吧！",
            role="interviewer",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(opening.render())
        self.console.print()

        # 添加到历史
        self._dialogue_history.append({
            "role": "interviewer",
            "content": opening.content,
            "timestamp": time.time(),
        })

    def _handle_dialogue_command(self, command: str) -> bool:
        """
        处理对话命令

        Returns:
            是否已处理（跳过正常消息发送）
        """
        command = command.strip().lower()

        if command in ["/quit", "/exit", "/end"]:
            return True

        elif command == "/help":
            help_panel = HelpPanel(theme=self.theme_manager.current_theme)
            self.console.print(help_panel.render())
            self.console.input("\n按 Enter 键继续...")
            return True

        elif command == "/theme":
            self._toggle_theme()
            return True

        elif command == "/history":
            self._show_dialogue_history()
            return True

        elif command == "/clear":
            self.console.clear()
            return True

        return False

    def _send_message(self, content: str) -> None:
        """发送消息并获取响应"""
        if not content.strip():
            return

        # 显示用户消息
        user_msg = MessageBubble(
            content=content,
            role="user",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(user_msg.render())

        # 添加到历史
        self._dialogue_history.append({
            "role": "user",
            "content": content,
            "timestamp": time.time(),
        })

        # 显示打字指示器
        typing_indicator = TypingIndicator(
            message="面试官正在思考",
            theme=self.theme_manager.current_theme,
        )

        with typing_indicator.live(self.console):
            # 模拟 AI 响应延迟
            time.sleep(1.5)

        # 生成 AI 响应（这里应该调用真实的 AI）
        response_content = self._generate_ai_response(content)

        # 显示 AI 响应
        agent_msg = MessageBubble(
            content=response_content,
            role="interviewer",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(agent_msg.render())

        # 添加到历史
        self._dialogue_history.append({
            "role": "interviewer",
            "content": response_content,
            "timestamp": time.time(),
        })

    def _generate_ai_response(self, user_input: str) -> str:
        """
        生成 AI 响应

        这里应该调用真实的 AI 模型，暂时使用预设响应。
        """
        # 简单的关键词匹配响应
        user_input_lower = user_input.lower()

        if "你好" in user_input_lower or "hello" in user_input_lower:
            return "你好！很高兴见到你。能先简单介绍一下你自己吗？"

        elif "介绍" in user_input_lower:
            return "很好！那么请谈谈你最近参与的一个项目，以及你在其中扮演的角色。"

        elif "项目" in user_input_lower or "经验" in user_input_lower:
            return "听起来是个有趣的项目。在这个过程中，你遇到的最大技术挑战是什么？你是如何解决的？"

        elif "挑战" in user_input_lower or "困难" in user_input_lower:
            return "面对困难时的解决能力很重要。那么，你对我们公司和这个职位有什么了解？"

        elif "公司" in user_input_lower or "职位" in user_input_lower:
            return "很好，看得出你做了功课。你有什么问题想问我的吗？"

        elif "问题" in user_input_lower or "疑问" in user_input_lower:
            return "今天的面试差不多了。你表现得不错，我们会在一周内给你反馈。感谢你的时间！"

        else:
            return "明白了。能详细说说你的想法吗？比如具体的实现方案或者考虑因素。"

    def _show_dialogue_history(self) -> None:
        """显示对话历史"""
        self.console.clear()

        header = Header(
            title="对话历史",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(header.render())
        self.console.print()

        if not self._dialogue_history:
            self.console.print("[yellow]暂无对话历史[/yellow]")
        else:
            for msg in self._dialogue_history:
                bubble = MessageBubble(
                    content=msg["content"],
                    role=msg["role"],
                    timestamp=msg.get("timestamp"),
                    theme=self.theme_manager.current_theme,
                )
                self.console.print(bubble.render())
                self.console.print()

        self.console.input("按 Enter 键返回...")

    def _show_feedback(self) -> None:
        """显示反馈"""
        self.console.clear()

        # 生成模拟评估结果
        evaluation_result = self._generate_evaluation()

        feedback_menu = FeedbackMenu(
            evaluation_result=evaluation_result,
            title="面试反馈报告",
            theme=self.theme_manager.current_theme,
        )

        header = Header(
            title="面试结束",
            subtitle="以下是你的评估报告",
            theme=self.theme_manager.current_theme,
        )

        self.menu_manager.show_menu(feedback_menu, header=header)

        # 显示导出选项
        self.console.print()
        if Confirm.ask("是否导出评估报告？"):
            self._export_feedback(evaluation_result)

        self.console.input("\n按 Enter 键返回主菜单...")

    def _generate_evaluation(self) -> Dict[str, Any]:
        """生成模拟评估结果"""
        return {
            "overall_score": 3.8,
            "dimensions": {
                "内容质量": {"score": 4.0, "comment": "回答内容较为准确"},
                "表达清晰度": {"score": 3.5, "comment": "逻辑性有待提高"},
                "专业知识": {"score": 4.0, "comment": "技术基础扎实"},
                "应变能力": {"score": 3.5, "comment": "能应对常见问题"},
                "沟通技巧": {"score": 4.0, "comment": "表达流畅"},
            },
            "suggestions": [
                "可以更多地使用具体例子来支撑观点",
                "在回答技术问题时，可以先阐述整体思路",
                "注意控制回答的节奏，避免过于匆忙",
                "多展示解决问题的思考过程",
            ],
        }

    def _export_feedback(self, evaluation_result: Dict[str, Any]) -> None:
        """导出反馈报告"""
        export_dir = Path("examples/output")
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{timestamp}.json"
        filepath = export_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(evaluation_result, f, ensure_ascii=False, indent=2)

        self.console.print(f"[green]✓ 报告已导出到：{filepath}[/green]")

    def _show_history(self) -> None:
        """显示历史记录"""
        self.console.clear()

        header = Header(
            title="历史记录",
            theme=self.theme_manager.current_theme,
        )
        self.console.print(header.render())
        self.console.print()

        if not self._dialogue_history:
            self.console.print("[yellow]暂无历史记录[/yellow]")
        else:
            # 创建历史表格
            table = Table(title="对话历史摘要")
            table.add_column("序号", style="cyan")
            table.add_column("角色", style="magenta")
            table.add_column("内容", style="white")
            table.add_column("时间", style="green")

            for i, msg in enumerate(self._dialogue_history[:20], 1):
                time_str = datetime.fromtimestamp(msg.get("timestamp", 0)).strftime(
                    "%H:%M:%S"
                )
                table.add_row(
                    str(i),
                    msg["role"],
                    msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"],
                    time_str,
                )

            self.console.print(table)

        self.console.input("\n按 Enter 键返回...")

    def _show_settings(self) -> None:
        """显示设置"""
        self.console.clear()

        settings = {
            "主题": self.theme_manager.current_theme_name,
            "语言": "中文",
            "自动保存": "是",
            "音效": "关",
        }

        settings_menu = SettingsMenu(
            settings=settings,
            title="设置",
            theme=self.theme_manager.current_theme,
        )

        header = Header(
            title="设置",
            theme=self.theme_manager.current_theme,
        )

        self.menu_manager.show_menu(settings_menu, header=header)

        choice = Prompt.ask(
            "\n请选择操作",
            choices=["0", "1", "2"],
            default="0",
        )

        if choice == "1":
            self._toggle_theme()

        self.console.input("\n按 Enter 键返回...")

    def _show_help(self) -> None:
        """显示帮助"""
        self.console.clear()

        help_panel = HelpPanel(theme=self.theme_manager.current_theme)
        header = Header(
            title="帮助",
            theme=self.theme_manager.current_theme,
        )

        self.console.print(header.render())
        self.console.print()
        self.console.print(help_panel.render())

        self.console.input("\n按 Enter 键返回...")

    def _toggle_theme(self) -> None:
        """切换主题"""
        new_theme = self.theme_manager.cycle_theme()
        self.console = self.theme_manager.create_console()
        self.menu_manager.console = self.console
        self.menu_manager.theme = self.theme_manager.current_theme

        self.console.print(f"[green]✓ 已切换到主题：{new_theme}[/green]")
        time.sleep(1)

    def _confirm_quit(self) -> None:
        """确认退出"""
        if Confirm.ask("\n确定要退出吗？"):
            self._is_running = False
        else:
            self.console.clear()

    def _quit(self) -> None:
        """退出程序"""
        if Confirm.ask("确定要退出吗？"):
            self._is_running = False


def main():
    """CLI 应用程序入口点"""
    app = CLIApplication()
    app.run()


if __name__ == "__main__":
    main()
