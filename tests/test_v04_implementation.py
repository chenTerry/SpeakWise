#!/usr/bin/env python3
"""
v0.4 Implementation Test Script
测试 v0.4 用户界面实现的完整性

使用方法:
    python tests/test_v04_implementation.py

功能:
- 检查所有必需文件是否存在
- 验证模块导入
- 测试基本功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


class Colors:
    """ANSI 颜色代码"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str) -> None:
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text: str) -> None:
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str) -> None:
    """打印错误消息"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str) -> None:
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text: str) -> None:
    """打印信息"""
    print(f"{Colors.BLUE}• {text}{Colors.END}")


class TestResult:
    """测试结果"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_pass(self):
        self.passed += 1

    def add_fail(self):
        self.failed += 1

    def add_warning(self):
        self.warnings += 1

    def summary(self) -> str:
        total = self.passed + self.failed
        return f"通过：{self.passed}/{total}, 警告：{self.warnings}"


# =============================================================================
# Test 1: File Structure Check
# =============================================================================

def test_file_structure(result: TestResult) -> None:
    """测试文件结构完整性"""
    print_header("测试 1: 文件结构检查")

    required_files = [
        # CLI Module
        "cli/__init__.py",
        "cli/app.py",
        "cli/menus.py",
        "cli/themes.py",
        "cli/widgets.py",

        # Web Module
        "web/__init__.py",
        "web/app.py",
        "web/config.py",
        "web/routes/__init__.py",
        "web/routes/scenes.py",
        "web/routes/dialogue.py",
        "web/routes/feedback.py",
        "web/static/css/main.css",
        "web/static/js/app.js",
        "web/templates/base.html",
        "web/templates/index.html",
        "web/templates/scene_selection.html",
        "web/templates/dialogue.html",
        "web/templates/feedback.html",

        # Examples
        "examples/cli_demo.py",
        "examples/web_demo.py",

        # Configuration
        "requirements.txt",
    ]

    for file_path in required_files:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            print_success(f"存在：{file_path}")
            result.add_pass()
        else:
            print_error(f"缺失：{file_path}")
            result.add_fail()


# =============================================================================
# Test 2: Module Import Check
# =============================================================================

def test_module_imports(result: TestResult) -> None:
    """测试模块导入"""
    print_header("测试 2: 模块导入检查")

    imports = [
        # CLI Module
        ("cli", "CLI 主模块"),
        ("cli.app", "CLI 应用"),
        ("cli.menus", "CLI 菜单"),
        ("cli.themes", "CLI 主题"),
        ("cli.widgets", "CLI 组件"),

        # Web Module
        ("web", "Web 主模块"),
        ("web.app", "Web 应用"),
        ("web.config", "Web 配置"),
        ("web.routes", "Web 路由"),
        ("web.routes.scenes", "场景 API"),
        ("web.routes.dialogue", "对话 API"),
        ("web.routes.feedback", "反馈 API"),
    ]

    for module_name, description in imports:
        try:
            __import__(module_name)
            print_success(f"{description} ({module_name})")
            result.add_pass()
        except ImportError as e:
            print_error(f"{description} ({module_name}): {e}")
            result.add_fail()
        except Exception as e:
            print_warning(f"{description} ({module_name}): {e}")
            result.add_warning()


# =============================================================================
# Test 3: CLI Components Check
# =============================================================================

def test_cli_components(result: TestResult) -> None:
    """测试 CLI 组件"""
    print_header("测试 3: CLI 组件检查")

    try:
        from cli.themes import Theme, ThemeManager, ThemeType
        from cli.widgets import (
            UIWidget, Header, Footer, MessageBubble,
            TypingIndicator, ProgressBar, Spinner, Panel, Menu
        )
        from cli.menus import (
            MenuManager, MainMenu, SceneMenu, DialogueMenu,
            FeedbackMenu, SettingsMenu, HelpPanel
        )
        from cli.app import CLIApplication

        # Test Theme
        print_info("测试 Theme...")
        theme = Theme(name="Test", theme_type=ThemeType.DARK)
        rich_theme = theme.to_rich_theme()
        print_success("Theme 创建成功")
        result.add_pass()

        # Test ThemeManager
        print_info("测试 ThemeManager...")
        manager = ThemeManager(default_theme="dark")
        assert manager.current_theme_name == "dark"
        manager.cycle_theme()
        print_success("ThemeManager 工作正常")
        result.add_pass()

        # Test Widgets
        print_info("测试 Widgets...")
        header = Header(title="Test")
        footer = Footer(hints=["Test"])
        bubble = MessageBubble(content="Test", role="user")
        print_success("Widgets 创建成功")
        result.add_pass()

        # Test Menus
        print_info("测试 Menus...")
        main_menu = MainMenu()
        scene_menu = SceneMenu(scenes=[])
        print_success("Menus 创建成功")
        result.add_pass()

        # Test CLIApplication
        print_info("测试 CLIApplication...")
        app = CLIApplication(theme_name="dark")
        assert app.theme_manager is not None
        print_success("CLIApplication 初始化成功")
        result.add_pass()

    except Exception as e:
        print_error(f"CLI 组件测试失败：{e}")
        result.add_fail()


# =============================================================================
# Test 4: Web Components Check
# =============================================================================

def test_web_components(result: TestResult) -> None:
    """测试 Web 组件"""
    print_header("测试 4: Web 组件检查")

    try:
        from web.config import WebConfig, WebConfigLoader
        from web.app import create_app, WebApplication

        # Test WebConfig
        print_info("测试 WebConfig...")
        config = WebConfig(
            host="127.0.0.1",
            port=8000,
            debug=True,
        )
        assert config.port == 8000
        print_success("WebConfig 创建成功")
        result.add_pass()

        # Test WebConfigLoader
        print_info("测试 WebConfigLoader...")
        loaded_config = WebConfigLoader.load(use_env=False)
        assert loaded_config is not None
        print_success("WebConfigLoader 工作正常")
        result.add_pass()

        # Test FastAPI App
        print_info("测试 FastAPI 应用...")
        app = create_app(config)
        assert app is not None
        assert app.title == "AgentScope AI Interview"
        print_success("FastAPI 应用创建成功")
        result.add_pass()

        # Test WebApplication
        print_info("测试 WebApplication...")
        web_app = WebApplication(config=config)
        assert web_app.app is not None
        print_success("WebApplication 初始化成功")
        result.add_pass()

    except Exception as e:
        print_error(f"Web 组件测试失败：{e}")
        result.add_fail()


# =============================================================================
# Test 5: API Routes Check
# =============================================================================

def test_api_routes(result: TestResult) -> None:
    """测试 API 路由"""
    print_header("测试 5: API 路由检查")

    try:
        from web.routes.scenes import router as scenes_router
        from web.routes.dialogue import router as dialogue_router
        from web.routes.feedback import router as feedback_router

        # Test Scenes Router
        print_info("测试 Scenes Router...")
        assert len(scenes_router.routes) > 0
        print_success(f"Scenes Router 有 {len(scenes_router.routes)} 个路由")
        result.add_pass()

        # Test Dialogue Router
        print_info("测试 Dialogue Router...")
        assert len(dialogue_router.routes) > 0
        print_success(f"Dialogue Router 有 {len(dialogue_router.routes)} 个路由")
        result.add_pass()

        # Test Feedback Router
        print_info("测试 Feedback Router...")
        assert len(feedback_router.routes) > 0
        print_success(f"Feedback Router 有 {len(feedback_router.routes)} 个路由")
        result.add_pass()

    except Exception as e:
        print_error(f"API 路由测试失败：{e}")
        result.add_fail()


# =============================================================================
# Test 6: Dependencies Check
# =============================================================================

def test_dependencies(result: TestResult) -> None:
    """测试依赖"""
    print_header("测试 6: 依赖检查")

    dependencies = [
        ("rich", "CLI UI 库"),
        ("fastapi", "Web 框架"),
        ("uvicorn", "ASGI 服务器"),
        ("jinja2", "模板引擎"),
        ("pydantic", "数据验证"),
        ("yaml", "YAML 解析"),
    ]

    for package, description in dependencies:
        try:
            __import__(package)
            print_success(f"{description} ({package})")
            result.add_pass()
        except ImportError:
            print_error(f"{description} ({package}) - 未安装")
            result.add_fail()


# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    """运行所有测试"""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{'AgentScope AI Interview v0.4 实现测试':^60}{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}")

    result = TestResult()

    # Run all tests
    test_file_structure(result)
    test_module_imports(result)
    test_cli_components(result)
    test_web_components(result)
    test_api_routes(result)
    test_dependencies(result)

    # Print summary
    print_header("测试总结")
    print(f"{result.summary()}")

    if result.failed > 0:
        print(f"\n{Colors.RED}有 {result.failed} 个测试失败，请检查上述错误。{Colors.END}\n")
        return 1
    elif result.warnings > 0:
        print(f"\n{Colors.YELLOW}所有测试通过，但有 {result.warnings} 个警告。{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.GREEN}✓ 所有测试通过！v0.4 实现完整。{Colors.END}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
