"""
Meeting Participant Agent - 会议参与者 Agent

负责在会议中扮演不同角色的参与者，包括：
- 产品经理 (Product Manager)
- 技术负责人 (Tech Lead)
- 开发工程师 (Developer)
- 测试工程师 (QA Engineer)
- 项目经理 (Project Manager)
- 敏捷教练 (Scrum Master)
- 等等

参与者根据角色和会议类型，提供符合身份的发言内容。
"""

import logging
import random
from typing import Any, Dict, List, Optional

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

logger = logging.getLogger(__name__)


class MeetingParticipantAgent(BaseAgent):
    """
    会议参与者 Agent

    职责:
    - 根据角色提供专业视角的发言
    - 参与讨论并提出问题
    - 分享相关经验和信息
    - 承诺行动项

    Attributes:
        participant_id: 参与者 ID
        role: 角色类型
        meeting_type: 会议类型
        project_name: 项目名称
    """

    def __init__(
        self,
        name: str = "参与者",
        config: Optional[Config] = None,
        participant_id: int = 0,
        role: str = "participant",
        meeting_type: Any = None,
        project_name: str = "项目 A",
        **kwargs,
    ):
        """
        初始化会议参与者 Agent

        Args:
            name: Agent 名称
            config: 全局配置
            participant_id: 参与者 ID
            role: 角色类型
            meeting_type: 会议类型
            project_name: 项目名称
            **kwargs: 其他参数
        """
        super().__init__(name=name, config=config, **kwargs)

        self.participant_id = participant_id
        self.role = role
        self.meeting_type = meeting_type
        self.project_name = project_name
        self.current_phase = "opening"
        self._turn_count = 0
        self._statements: List[str] = []
        self._questions: List[str] = []
        self._commitments: List[str] = []

    def initialize(self) -> bool:
        """
        初始化 Agent

        Returns:
            初始化是否成功
        """
        try:
            logger.info(
                f"初始化会议参与者 Agent: id={self.participant_id}, "
                f"role={self.role}, type={self.meeting_type}"
            )

            # 构建系统提示词
            self.system_prompt = self._build_system_prompt()

            # 调用父类初始化
            if hasattr(super(), 'initialize') and callable(super().initialize):
                super().initialize()

            self._initialized = True
            logger.info("会议参与者 Agent 初始化成功")
            return True

        except Exception as e:
            logger.error(f"会议参与者 Agent 初始化失败：{e}")
            return False

    def _build_system_prompt(self) -> str:
        """
        构建系统提示词

        Returns:
            系统提示词字符串
        """
        # 延迟导入 MeetingType
        from .scene import MeetingType

        role_descriptions = {
            "product_manager": (
                "你是产品经理，负责产品规划和需求管理。\n"
                "- 关注用户价值和业务目标\n"
                "- 清晰表达需求背景和期望\n"
                "- 平衡业务需求和技术可行性"
            ),
            "tech_lead": (
                "你是技术负责人，负责技术架构和方案决策。\n"
                "- 关注技术可行性和系统稳定性\n"
                "- 评估技术风险和实现难度\n"
                "- 协调技术资源和分工"
            ),
            "developer": (
                "你是开发工程师，负责功能实现。\n"
                "- 关注实现细节和工作量\n"
                "- 提出技术问题和风险\n"
                "- 承诺具体的开发任务"
            ),
            "qa_engineer": (
                "你是测试工程师，负责质量保障。\n"
                "- 关注测试覆盖和质量标准\n"
                "- 识别潜在的质量风险\n"
                "- 规划测试计划和资源"
            ),
            "project_manager": (
                "你是项目经理，负责项目整体管理。\n"
                "- 关注进度、风险和资源\n"
                "- 协调各方利益相关者\n"
                "- 确保项目按时交付"
            ),
            "scrum_master": (
                "你是敏捷教练，负责流程引导。\n"
                "- 关注团队协作和流程改进\n"
                "- 移除团队障碍\n"
                "- 促进持续改进"
            ),
            "product_owner": (
                "你是产品负责人，负责产品愿景和优先级。\n"
                "- 明确产品目标和价值\n"
                "- 决定需求优先级\n"
                "- 代表用户声音"
            ),
            "team_member": (
                "你是团队成员，参与具体工作。\n"
                "- 分享工作进展和问题\n"
                "- 提出改进建议\n"
                "- 承诺具体任务"
            ),
            "mediator": (
                "你是调解人，负责促进沟通。\n"
                "- 保持中立客观\n"
                "- 引导各方表达观点\n"
                "- 寻找共识点"
            ),
            "party_a": (
                "你是当事方 A，有自己的立场和诉求。\n"
                "- 清晰表达自己的观点\n"
                "- 倾听对方意见\n"
                "- 寻求解决方案"
            ),
            "party_b": (
                "你是当事方 B，有自己的立场和诉求。\n"
                "- 清晰表达自己的观点\n"
                "- 倾听对方意见\n"
                "- 寻求解决方案"
            ),
            "observer": (
                "你是观察员，负责记录和观察。\n"
                "- 客观记录讨论内容\n"
                "- 适时提供总结\n"
                "- 不参与争论"
            ),
        }

        role_desc = role_descriptions.get(
            self.role,
            (
                "你是会议参与者。\n"
                "- 积极参与讨论\n"
                "- 分享自己的观点\n"
                "- 承诺力所能及的任务"
            ),
        )

        type_names = {
            MeetingType.REQUIREMENT_REVIEW: "需求评审会",
            MeetingType.STANDUP: "每日站会",
            MeetingType.CONFLICT_RESOLUTION: "冲突解决会",
            MeetingType.PROJECT_KICKOFF: "项目启动会",
            MeetingType.RETROSPECTIVE: "项目复盘会",
        }

        meeting_name = type_names.get(
            self.meeting_type,
            "项目会议",
        ) if hasattr(self.meeting_type, 'value') else "项目会议"

        return f"""你正在参加一场{meeting_name}，项目名称：{self.project_name}。

你的角色：{self.name}
{role_desc}

会议参与原则:
- 聚焦议题，高效发言
- 尊重他人，积极倾听
- 对事不对人
- 承诺可执行的任务
- 关注行动和结果

根据你的角色和会议类型，提供专业、有价值的发言。"""

    def respond(
        self,
        user_message: str,
        context: Optional[DialogueContext] = None,
        phase: str = "discussion",
        agenda_item: str = "讨论",
        **kwargs,
    ) -> str:
        """
        生成响应

        Args:
            user_message: 用户消息
            context: 对话上下文
            phase: 当前阶段
            agenda_item: 当前议程项
            **kwargs: 其他参数

        Returns:
            响应文本
        """
        self._turn_count += 1
        self.current_phase = phase

        # 根据阶段生成不同的响应
        if phase == "round_table":
            return self._respond_round_table(agenda_item)
        elif phase == "discussion":
            return self._respond_discussion(user_message, agenda_item)
        elif phase == "summary":
            return self._respond_summary(user_message)
        elif phase == "action_items":
            return self._respond_action_items(user_message)
        else:
            return self._respond_default(user_message, agenda_item)

    def _respond_round_table(self, agenda_item: str) -> str:
        """回应轮流发言阶段"""
        # 根据会议类型和角色生成发言
        from .scene import MeetingType

        if self.meeting_type == MeetingType.STANDUP:
            return self._generate_standup_update()
        elif self.meeting_type == MeetingType.REQUIREMENT_REVIEW:
            return self._generate_requirement_feedback(agenda_item)
        elif self.meeting_type == MeetingType.RETROSPECTIVE:
            return self._generate_retrospective_input()
        elif self.meeting_type == MeetingType.PROJECT_KICKOFF:
            return self._generate_kickoff_response()
        else:
            return self._generate_general_statement(agenda_item)

    def _respond_discussion(
        self,
        user_message: str,
        agenda_item: str,
    ) -> str:
        """回应讨论阶段"""
        # 根据角色生成专业视角的回应
        responses = {
            "product_manager": (
                "从产品的角度来看，这个问题确实需要考虑。\n\n"
                "我想补充一点用户视角的信息...\n\n"
                "我们是否可以考虑一个平衡的方案？"
            ),
            "tech_lead": (
                "从技术实现的角度，我建议...\n\n"
                "主要考虑因素是：\n"
                "- 系统稳定性\n"
                "- 可维护性\n"
                "- 扩展性\n\n"
                "我的建议是..."
            ),
            "developer": (
                "我理解这个需求，但在实现上有一些考虑...\n\n"
                "具体来说：\n"
                "- 工作量评估...\n"
                "- 技术难点...\n\n"
                "我建议..."
            ),
            "qa_engineer": (
                "从质量保障的角度，我担心...\n\n"
                "我们需要考虑：\n"
                "- 测试覆盖范围\n"
                "- 回归测试成本\n"
                "- 上线风险\n\n"
                "建议..."
            ),
        }

        response = responses.get(
            self.role,
            (
                "我同意刚才的观点，补充一些我的想法...\n\n"
                "从我的角度来看..."
            ),
        )

        self._statements.append(response)
        return response

    def _respond_summary(self, user_message: str) -> str:
        """回应总结阶段"""
        return (
            "我确认一下我的理解：\n\n"
            "今天会议的主要结论是...\n\n"
            "我这边没有其他补充了。"
        )

    def _respond_action_items(self, user_message: str) -> str:
        """回应行动项阶段"""
        # 根据角色承诺任务
        commitments = {
            "product_manager": "我可以负责完善需求文档，预计明天完成。",
            "tech_lead": "我来负责技术方案的设计，后天输出初稿。",
            "developer": "这个功能我来开发，预计需要 3 个工作日。",
            "qa_engineer": "我来准备测试用例，开发完成后立即开始测试。",
            "project_manager": "我来跟踪整体进度，协调需要的资源。",
        }

        commitment = commitments.get(
            self.role,
            "这个任务我可以负责，会按时完成。",
        )

        self._commitments.append(commitment)
        return commitment

    def _respond_default(
        self,
        user_message: str,
        agenda_item: str,
    ) -> str:
        """默认回应"""
        return (
            f"关于{agenda_item}，我的想法是...\n\n"
            "大家有什么建议吗？"
        )

    def _generate_standup_update(self) -> str:
        """生成站会发言"""
        templates = [
            (
                "昨天的工作：\n"
                "- 完成了 XX 功能的开发\n"
                "- 修复了 2 个 bug\n\n"
                "今天的计划：\n"
                "- 继续开发 XX 功能\n"
                "- 参与需求评审\n\n"
                "阻塞问题：\n"
                "- 暂无"
            ),
            (
                "昨天：\n"
                "- 完成了代码审查\n"
                "- 协助测试定位问题\n\n"
                "今天：\n"
                "- 开始新需求的开发\n"
                "- 需要和产品确认需求细节\n\n"
                "问题：\n"
                "- 需要产品确认需求"
            ),
            (
                "昨日进展：\n"
                "- 完成了模块 A 的开发\n"
                "- 正在进行单元测试\n\n"
                "今日计划：\n"
                "- 完成单元测试\n"
                "- 提交代码审查\n\n"
                "需要帮助：\n"
                "- 无"
            ),
        ]

        return random.choice(templates)

    def _generate_requirement_feedback(self, agenda_item: str) -> str:
        """生成需求评审反馈"""
        feedbacks = {
            "product_manager": (
                f"关于{agenda_item}这个需求，我来介绍一下背景...\n\n"
                "用户价值在于...\n\n"
                "期望的完成时间是..."
            ),
            "tech_lead": (
                f"从技术角度评估{agenda_item}...\n\n"
                "实现难度：中等\n"
                "主要风险：...\n"
                "建议排期：..."
            ),
            "developer": (
                f"我看了{agenda_item}的需求，有几个问题想确认...\n\n"
                "1. ...\n"
                "2. ...\n\n"
                "工作量的初步评估是..."
            ),
            "qa_engineer": (
                f"关于{agenda_item}的测试，我需要考虑...\n\n"
                "- 测试场景...\n"
                "- 回归范围...\n\n"
                "建议提前准备测试数据。"
            ),
        }

        return feedbacks.get(
            self.role,
            f"关于{agenda_item}，我没有太多补充。",
        )

    def _generate_retrospective_input(self) -> str:
        """生成复盘会输入"""
        categories = ["做得好的", "需要改进的", "建议"]

        inputs = {
            "做得好的": [
                "我觉得上个迭代我们在...方面做得不错",
                "团队协作效率有明显提升，特别是...",
                "代码质量有所改善，bug 率下降了",
            ],
            "需要改进的": [
                "我觉得在...方面还有改进空间",
                "沟通效率可以进一步提升",
                "需求变更的流程需要优化",
            ],
            "建议": [
                "建议我们可以尝试...",
                "我建议增加...的环节",
                "可以考虑引入...工具",
            ],
        }

        category = random.choice(categories)
        content = random.choice(inputs[category])

        return f"【{category}】\n\n{content}"

    def _generate_kickoff_response(self) -> str:
        """生成启动会回应"""
        responses = {
            "product_manager": (
                "我对这个项目充满期待！\n\n"
                "从产品角度，我们的目标是...\n\n"
                "希望各位通力合作，一起把这个项目做好！"
            ),
            "tech_lead": (
                "技术这边我们已经有了初步的方案...\n\n"
                "主要的技术选型是...\n\n"
                "相信团队能够顺利完成这个项目！"
            ),
            "developer": (
                "我会全力投入这个项目的开发！\n\n"
                "技术上有什么需要预先准备的吗？\n\n"
                "期待和大家一起合作！"
            ),
        }

        return responses.get(
            self.role,
            (
                "很高兴参与这个项目！\n\n"
                "我会尽力完成分配给我的任务。\n\n"
                "期待项目成功！"
            ),
        )

    def _generate_general_statement(self, agenda_item: str) -> str:
        """生成一般性发言"""
        statements = [
            f"关于{agenda_item}，我想说几点...\n\n"
            "首先...\n\n"
            "其次...\n\n"
            "最后...",

            f"我同意刚才的观点，补充一下...\n\n"
            "从实际经验来看...",

            f"这个问题确实值得讨论，我的看法是...\n\n"
            "一方面...\n\n"
            "另一方面...",
        ]

        return random.choice(statements)

    def set_current_phase(self, phase: str) -> None:
        """设置当前阶段"""
        self.current_phase = phase

    def get_statements(self) -> List[str]:
        """获取发言列表"""
        return self._statements.copy()

    def get_questions(self) -> List[str]:
        """获取问题列表"""
        return self._questions.copy()

    def get_commitments(self) -> List[str]:
        """获取承诺列表"""
        return self._commitments.copy()

    def get_turn_count(self) -> int:
        """获取发言次数"""
        return self._turn_count

    def reset(self) -> None:
        """重置状态"""
        self._turn_count = 0
        self._statements.clear()
        self._questions.clear()
        self._commitments.clear()
        self.current_phase = "opening"
