"""
Interview Demo - 面试场景演示

演示如何使用 v0.2 的面试场景系统进行模拟面试。

功能:
- 创建和配置面试场景
- 运行模拟面试对话
- 使用评估器生成评估报告

使用方式:
    python examples/interview_demo.py              # 交互模式
    python examples/interview_demo.py --auto       # 自动演示模式
    python examples/interview_demo.py --style strict --domain frontend  # 指定风格/领域
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config, ConfigLoader
from core.agent import Message, MessageType, DialogueContext
from scenes import SceneRegistry
from scenes.interview import InterviewScene, InterviewStyle, DomainType
from scenes.base import SceneState
from evaluation import BasicEvaluator, EvaluationReport

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class InterviewDemo:
    """
    面试演示类

    封装完整的面试演示流程
    """

    def __init__(
        self,
        style: str = "friendly",
        domain: str = "tech",
        config: Optional[Config] = None,
        auto_mode: bool = False,
    ):
        """
        初始化演示

        Args:
            style: 面试风格 (friendly/strict/pressure)
            domain: 面试领域 (tech/frontend/backend/system_design/hr)
            config: 配置对象
            auto_mode: 是否自动演示模式
        """
        self.style = style
        self.domain = domain
        self.config = config or Config()
        self.auto_mode = auto_mode

        # 组件
        self.scene: Optional[InterviewScene] = None
        self.evaluator: Optional[BasicEvaluator] = None
        self.context = DialogueContext()

        # 演示用模拟回答
        self._demo_answers = self._get_demo_answers()
        self._answer_index = 0

    def run(self) -> None:
        """运行演示"""
        print("=" * 60)
        print("AgentScope AI Interview - 面试场景演示 v0.2")
        print("=" * 60)
        print(f"面试风格：{self.style}")
        print(f"面试领域：{self.domain}")
        print(f"运行模式：{'自动演示' if self.auto_mode else '交互模式'}")
        print("=" * 60)
        print()

        # 初始化场景
        if not self._init_scene():
            print("场景初始化失败，退出演示")
            return

        # 开始面试
        self._run_interview()

        # 生成评估报告
        self._generate_evaluation()

        # 清理
        self._cleanup()

    def _init_scene(self) -> bool:
        """初始化面试场景"""
        print("正在初始化面试场景...")

        try:
            # 创建场景
            self.scene = InterviewScene(
                style=self.style,
                domain=self.domain,
                global_config=self.config,
            )

            # 初始化
            if not self.scene.initialize():
                print("场景初始化失败")
                return False

            # 创建评估器
            self.evaluator = BasicEvaluator(self.config)

            print("场景初始化成功!")
            print(f"问题库加载了 {self.scene.question_bank.get_question_count() if self.scene.question_bank else 0} 个问题")
            print()
            return True

        except Exception as e:
            logger.error(f"初始化失败：{e}")
            return False

    def _run_interview(self) -> None:
        """运行面试流程"""
        print("-" * 60)
        print("面试开始")
        print("-" * 60)
        print()

        # 获取开场白
        opening = self.scene.start()
        self._print_message(opening)

        # 面试主循环
        max_turns = 10
        turn_count = 0

        while self.scene.is_running() and turn_count < max_turns:
            turn_count += 1

            # 获取用户输入
            if self.auto_mode:
                user_input = self._get_auto_answer()
            else:
                user_input = self._get_user_input()

            if not user_input:
                print("输入为空，继续...")
                continue

            if user_input.lower() in ["quit", "exit", "结束", "退出"]:
                print("用户主动结束面试")
                break

            # 创建消息
            user_message = Message(
                content=user_input,
                role="user",
                type=MessageType.USER,
            )

            # 处理消息
            response = self.scene.handle_message(user_message, self.context)
            self._print_message(response)

            # 检查是否结束
            if self.scene.is_completed():
                break

            # 自动模式添加延迟
            if self.auto_mode:
                time.sleep(1)

        print()
        print("-" * 60)
        print("面试结束")
        print("-" * 60)

    def _generate_evaluation(self) -> None:
        """生成评估报告"""
        print()
        print("=" * 60)
        print("生成评估报告")
        print("=" * 60)
        print()

        if not self.evaluator:
            print("评估器未初始化")
            return

        # 获取对话历史
        history = self.context.get_history()

        if not history:
            print("没有对话历史，无法评估")
            return

        # 执行评估
        result = self.evaluator.evaluate(history)

        # 生成报告
        report = EvaluationReport.from_result(
            result,
            candidate_info={"name": "演示候选人"},
            interview_info={
                "domain": self.domain,
                "style": self.style,
                "duration": len(history),
            },
        )

        # 打印报告
        print(report.generate_text_report())

        # 保存报告到文件
        self._save_report(report)

    def _save_report(self, report: EvaluationReport) -> None:
        """保存报告到文件"""
        try:
            output_dir = Path(__file__).parent.parent / "logs"
            output_dir.mkdir(exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"evaluation_{timestamp}.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report.generate_text_report())

            print(f"\n评估报告已保存至：{output_file}")

        except Exception as e:
            logger.error(f"保存报告失败：{e}")

    def _cleanup(self) -> None:
        """清理资源"""
        if self.scene:
            self.scene.cleanup()
        print()
        print("演示结束，感谢使用!")

    def _print_message(self, message: Message) -> None:
        """打印消息"""
        role_colors = {
            "system": "\033[94m",  # 蓝色
            "interviewer": "\033[92m",  # 绿色
            "user": "\033[93m",  # 黄色
            "evaluator": "\033[95m",  # 紫色
        }
        reset = "\033[0m"

        role = message.role
        color = role_colors.get(role, "")

        print(f"{color}[{role}]{reset} {message.content}")
        print()

    def _get_user_input(self) -> str:
        """获取用户输入"""
        try:
            user_input = input("\033[93m[你]\033[0m ").strip()
            return user_input
        except (EOFError, KeyboardInterrupt):
            return "quit"

    def _get_auto_answer(self) -> str:
        """获取自动演示回答"""
        if self._answer_index >= len(self._demo_answers):
            self._answer_index = 0

        answer = self._demo_answers[self._answer_index]
        self._answer_index += 1

        print(f"\033[93m[你]\033[0m {answer}")
        return answer

    def _get_demo_answers(self) -> List[str]:
        """获取演示用模拟回答"""
        return [
            "你好，我是一名有 5 年经验的全栈工程师，主要负责后端开发和系统架构设计。最近在做的是一个电商平台的重构项目。",
            "在这个项目中，我主要负责订单系统和支付系统的设计与实现。我们使用了微服务架构，将原来的单体应用拆分成多个独立服务。",
            "关于 RESTful API 设计，我认为最重要的是资源命名要清晰，使用合适的 HTTP 动词，状态码要准确反映操作结果。我们项目中遵循了这些原则。",
            "数据库索引方面，我们遇到过慢查询问题。通过分析执行计划，发现是复合索引没有满足最左前缀原则导致的。调整后查询性能提升了 10 倍。",
            "缓存穿透问题我们是通过布隆过滤器解决的。对于热点 key，我们使用了互斥锁来防止缓存击穿。",
            "在微服务通信方面，我们主要使用 gRPC 进行同步调用，消息队列处理异步事件。服务发现用的是 Nacos。",
            "关于分布式事务，我们根据业务场景选择了不同方案。核心交易用 TCC，非核心用最终一致性方案。",
            "性能优化方面，我通常会先通过监控和 profiling 定位瓶颈，然后针对性优化。最近优化了一个接口，从 2 秒降到了 200 毫秒。",
            "代码质量方面，我们团队有严格的 code review 流程，要求单元测试覆盖率达到 80% 以上，使用 CI/CD 自动化部署。",
            "我平时通过技术博客、开源项目和社区交流来学习新技术。最近在学习 Kubernetes 和云原生相关技术。",
        ]


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AgentScope AI Interview - 面试场景演示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python examples/interview_demo.py                    # 交互模式
  python examples/interview_demo.py --auto             # 自动演示
  python examples/interview_demo.py --style strict     # 严格风格
  python examples/interview_demo.py --domain frontend  # 前端领域
        """,
    )

    parser.add_argument(
        "--style",
        type=str,
        default="friendly",
        choices=["friendly", "strict", "pressure"],
        help="面试风格 (默认：friendly)",
    )

    parser.add_argument(
        "--domain",
        type=str,
        default="tech",
        choices=["tech", "frontend", "backend", "system_design", "hr"],
        help="面试领域 (默认：tech)",
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="自动演示模式",
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="配置文件路径 (默认: config.yaml)",
    )

    return parser.parse_args()


def main() -> None:
    """主函数"""
    args = parse_args()

    # 加载配置
    config = Config()
    if args.config:
        try:
            config = ConfigLoader.from_yaml(args.config)
        except Exception as e:
            logger.warning(f"加载配置文件失败：{e}，使用默认配置")

    # 创建并运行演示
    demo = InterviewDemo(
        style=args.style,
        domain=args.domain,
        config=config,
        auto_mode=args.auto,
    )

    demo.run()


if __name__ == "__main__":
    main()
