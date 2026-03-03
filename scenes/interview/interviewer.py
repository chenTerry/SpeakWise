"""
Enhanced Interviewer Agent - 增强的面试官 Agent

扩展基础 InterviewerAgent，提供：
- 3 种面试风格支持 (friendly/strict/pressure)
- 领域特定问题生成 (frontend/backend/system_design/HR)
- 基于回答的智能追问
- AgentScope ModelAgent 集成

设计原则:
- 单一职责：专注于面试问题生成和回答评估
- 开放封闭：通过配置扩展新风格和领域
- 依赖倒置：通过抽象接口与 LLM 交互
"""

import logging
import random
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from core.config import Config
from core.agent import BaseAgent, Message, DialogueContext, MessageType

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """
    面试领域枚举

    定义不同的技术/专业领域
    """
    TECH = "tech"                 # 综合技术
    FRONTEND = "frontend"         # 前端开发
    BACKEND = "backend"           # 后端开发
    SYSTEM_DESIGN = "system_design"  # 系统设计
    HR = "hr"                     # HR 面试


class InterviewStyle(Enum):
    """
    面试风格枚举
    """
    FRIENDLY = "friendly"     # 友好鼓励型
    STRICT = "strict"         # 严格专业型
    PRESSURE = "pressure"     # 压力测试型


class QuestionType(Enum):
    """
    问题类型枚举
    """
    CONCEPTUAL = "conceptual"    # 概念理解
    EXPERIENCE = "experience"    # 经验相关
    BEHAVIORAL = "behavioral"    # 行为面试
    TECHNICAL = "technical"      # 技术细节
    SCENARIO = "scenario"        # 场景题


class QuestionData:
    """
    问题数据类

    封装单个问题的所有信息
    """

    def __init__(
        self,
        question_id: str,
        content: str,
        domain: str,
        difficulty: int,
        question_type: str,
        category: str,
        sample_answer: Optional[str] = None,
        evaluation_hints: Optional[List[str]] = None,
        follow_up_suggestions: Optional[List[str]] = None,
    ):
        """
        初始化问题数据

        Args:
            question_id: 问题唯一标识
            content: 问题内容
            domain: 所属领域
            difficulty: 难度等级 (1-5)
            question_type: 问题类型
            category: 分类标签
            sample_answer: 参考回答
            evaluation_hints: 评估提示
            follow_up_suggestions: 追问建议
        """
        self.question_id = question_id
        self.content = content
        self.domain = domain
        self.difficulty = difficulty
        self.question_type = question_type
        self.category = category
        self.sample_answer = sample_answer or ""
        self.evaluation_hints = evaluation_hints or []
        self.follow_up_suggestions = follow_up_suggestions or []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuestionData":
        """从字典创建问题数据"""
        return cls(
            question_id=data.get("id", ""),
            content=data.get("question", ""),
            domain=data.get("domain", "tech"),
            difficulty=int(data.get("difficulty", 3)),
            question_type=data.get("type", "conceptual"),
            category=data.get("category", "general"),
            sample_answer=data.get("sample_answer"),
            evaluation_hints=data.get("evaluation_hints", []),
            follow_up_suggestions=data.get("follow_up_suggestions", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.question_id,
            "question": self.content,
            "domain": self.domain,
            "difficulty": self.difficulty,
            "type": self.question_type,
            "category": self.category,
            "sample_answer": self.sample_answer,
            "evaluation_hints": self.evaluation_hints,
            "follow_up_suggestions": self.follow_up_suggestions,
        }

    def __repr__(self) -> str:
        return f"QuestionData(id='{self.question_id}', difficulty={self.difficulty})"


class QuestionBank:
    """
    问题库管理类

    负责加载、存储和检索面试问题
    支持按领域、难度、类型筛选问题
    """

    def __init__(self):
        """初始化问题库"""
        self._questions: Dict[str, QuestionData] = {}
        self._by_domain: Dict[str, List[str]] = {}
        self._by_difficulty: Dict[int, List[str]] = {}
        self._by_type: Dict[str, List[str]] = {}
        self._by_category: Dict[str, List[str]] = {}
        self._loaded = False

    def load_from_yaml(self, path: Path) -> bool:
        """
        从 YAML 文件加载问题库

        Args:
            path: YAML 文件路径

        Returns:
            加载是否成功
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or "questions" not in data:
                logger.warning(f"问题库文件格式不正确：{path}")
                return False

            questions = data.get("questions", [])
            for q_data in questions:
                question = QuestionData.from_dict(q_data)
                self._add_question(question)

            self._loaded = True
            logger.info(f"成功加载 {len(questions)} 个问题")
            return True

        except Exception as e:
            logger.error(f"加载问题库失败：{e}")
            return False

    def load_default_questions(self) -> None:
        """加载默认问题（当 YAML 文件不存在时使用）"""
        default_questions = self._get_default_questions()
        for q_data in default_questions:
            question = QuestionData.from_dict(q_data)
            self._add_question(question)
        self._loaded = True

    def _add_question(self, question: QuestionData) -> None:
        """添加单个问题到索引"""
        self._questions[question.question_id] = question

        # 按领域索引
        if question.domain not in self._by_domain:
            self._by_domain[question.domain] = []
        self._by_domain[question.domain].append(question.question_id)

        # 按难度索引
        if question.difficulty not in self._by_difficulty:
            self._by_difficulty[question.difficulty] = []
        self._by_difficulty[question.difficulty].append(question.question_id)

        # 按类型索引
        if question.question_type not in self._by_type:
            self._by_type[question.question_type] = []
        self._by_type[question.question_type].append(question.question_id)

        # 按分类索引
        if question.category not in self._by_category:
            self._by_category[question.category] = []
        self._by_category[question.category].append(question.question_id)

    def get_question(
        self,
        question_id: str,
    ) -> Optional[QuestionData]:
        """根据 ID 获取问题"""
        return self._questions.get(question_id)

    def get_questions(
        self,
        domain: Optional[str] = None,
        difficulty: Optional[int] = None,
        question_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[QuestionData]:
        """
        获取符合条件的问题列表

        Args:
            domain: 领域过滤
            difficulty: 难度过滤
            question_type: 类型过滤
            category: 分类过滤
            limit: 返回数量限制

        Returns:
            问题列表
        """
        # 收集所有候选 ID
        candidates: Optional[set] = None

        if domain:
            ids = set(self._by_domain.get(domain, []))
            candidates = ids if candidates is None else candidates & ids

        if difficulty:
            ids = set(self._by_difficulty.get(difficulty, []))
            candidates = ids if candidates is None else candidates & ids

        if question_type:
            ids = set(self._by_type.get(question_type, []))
            candidates = ids if candidates is None else candidates & ids

        if category:
            ids = set(self._by_category.get(category, []))
            candidates = ids if candidates is None else candidates & ids

        # 如果没有过滤条件，返回所有
        if candidates is None:
            candidates = set(self._questions.keys())

        # 转换为问题对象
        questions = [
            self._questions[qid] for qid in candidates
            if qid in self._questions
        ]

        # 随机打乱并限制数量
        random.shuffle(questions)
        if limit:
            questions = questions[:limit]

        return questions

    def get_random_question(
        self,
        domain: Optional[str] = None,
        difficulty_range: Tuple[int, int] = (1, 5),
        question_type: Optional[str] = None,
    ) -> Optional[QuestionData]:
        """
        获取随机问题

        Args:
            domain: 领域过滤
            difficulty_range: 难度范围 (min, max)
            question_type: 类型过滤

        Returns:
            随机问题或 None
        """
        candidates = []

        for diff in range(difficulty_range[0], difficulty_range[1] + 1):
            questions = self.get_questions(
                domain=domain,
                difficulty=diff,
                question_type=question_type,
            )
            candidates.extend(questions)

        if not candidates:
            return None

        return random.choice(candidates)

    def get_question_count(self) -> int:
        """获取问题总数"""
        return len(self._questions)

    def get_domains(self) -> List[str]:
        """获取所有领域"""
        return list(self._by_domain.keys())

    def _get_default_questions(self) -> List[Dict[str, Any]]:
        """获取默认问题列表（精简版）"""
        return [
            {
                "id": "tech_001",
                "question": "请介绍一下你最近做的项目，你在其中负责什么？",
                "domain": "tech",
                "difficulty": 1,
                "type": "experience",
                "category": "project",
            },
            {
                "id": "tech_002",
                "question": "什么是 RESTful API？设计 RESTful API 时需要注意什么？",
                "domain": "backend",
                "difficulty": 2,
                "type": "conceptual",
                "category": "api",
            },
            {
                "id": "fe_001",
                "question": "React 中的虚拟 DOM 是什么？它为什么能提高性能？",
                "domain": "frontend",
                "difficulty": 3,
                "type": "conceptual",
                "category": "framework",
            },
            {
                "id": "be_001",
                "question": "数据库索引的原理是什么？什么情况下索引会失效？",
                "domain": "backend",
                "difficulty": 3,
                "type": "conceptual",
                "category": "database",
            },
            {
                "id": "sd_001",
                "question": "如果要设计一个高并发的秒杀系统，你会考虑哪些方面？",
                "domain": "system_design",
                "difficulty": 4,
                "type": "scenario",
                "category": "architecture",
            },
        ]


class EnhancedInterviewerAgent(BaseAgent):
    """
    增强的面试官 Agent

    在基础 InterviewerAgent 上扩展：
    - 支持 3 种面试风格
    - 领域特定问题生成
    - 智能追问生成
    - AgentScope ModelAgent 集成（可选）

    Attributes:
        style: 面试风格
        domain: 面试领域
        question_bank: 问题库实例
        model_agent: AgentScope ModelAgent（可选）
    """

    # 面试风格提示词模板
    STYLE_PROMPTS = {
        InterviewStyle.FRIENDLY: """你是一位友好鼓励型的面试官。你的特点是：
- 语气温和，善于鼓励候选人
- 即使候选人回答不好，也会给予建设性反馈
- 使用"很好"、"不错"、"能详细说说吗"等鼓励性语言
- 营造轻松的氛围，帮助候选人发挥最佳水平""",

        InterviewStyle.STRICT: """你是一位严格专业型的面试官。你的特点是：
- 语气专业严肃，注重技术深度
- 对模糊或不准确的回答会直接指出
- 追问深入，考察候选人的真实水平
- 保持客观公正，以技术标准评判""",

        InterviewStyle.PRESSURE: """你是一位压力测试型的面试官。你的特点是：
- 语气直接，有时会质疑候选人的回答
- 连续追问，测试候选人的抗压能力
- 设置挑战性场景，观察候选人的反应
- 注意：压力测试不是人身攻击，而是考察应变能力""",
    }

    # 领域特定提示词
    DOMAIN_PROMPTS = {
        DomainType.FRONTEND: """你正在面试前端开发工程师。重点关注：
- HTML/CSS/JavaScript 基础
- 前端框架（React/Vue/Angular）
- 性能优化、浏览器兼容性
- 用户体验意识""",

        DomainType.BACKEND: """你正在面试后端开发工程师。重点关注：
- 编程语言基础（Java/Python/Go 等）
- 数据库设计和优化
- API 设计和微服务架构
- 系统性能和安全""",

        DomainType.SYSTEM_DESIGN: """你正在面试系统设计能力。重点关注：
- 架构设计能力
-  scalability 和可用性考虑
- 技术选型和权衡
- 实际问题解决能力""",

        DomainType.HR: """你正在进行 HR 面试。重点关注：
- 沟通表达能力
- 团队合作意识
- 职业规划和发展意愿
- 文化匹配度""",

        DomainType.TECH: """你正在进行综合技术面试。重点关注：
- 技术基础扎实程度
- 问题解决能力
- 学习能力和技术热情
- 项目经验深度""",
    }

    def __init__(
        self,
        name: str = "面试官",
        config: Optional[Config] = None,
        style: str = "friendly",
        domain: str = "tech",
        question_bank: Optional[QuestionBank] = None,
    ):
        """
        初始化增强的面试官 Agent

        Args:
            name: Agent 名称
            config: 配置对象
            style: 面试风格 (friendly/strict/pressure)
            domain: 面试领域 (tech/frontend/backend/system_design/hr)
            question_bank: 问题库实例
        """
        super().__init__(name, config)

        # 解析枚举
        self.style = InterviewStyle(style.lower()) if isinstance(style, str) else style
        self.domain = DomainType(domain.lower()) if isinstance(domain, str) else domain

        # 组件
        self.question_bank = question_bank or QuestionBank()

        # AgentScope 集成（可选）
        self._model_agent = None
        self._use_agentscope = False

        # 状态跟踪
        self._asked_questions: List[str] = []
        self._current_phase: str = "opening"

    def initialize(self) -> None:
        """初始化 Agent"""
        super().initialize()

        # 尝试初始化 AgentScope ModelAgent
        try:
            self._init_agentscope()
        except Exception as e:
            logger.warning(f"AgentScope 初始化失败，使用备用方案：{e}")
            self._use_agentscope = False

    def _init_agentscope(self) -> None:
        """初始化 AgentScope ModelAgent"""
        try:
            import agentscope
            from agentscope.agents import ModelAgent

            # 检查是否已初始化
            if not agentscope.initialized:
                agentscope.init(
                    model_configs=self.config.get("agentscope.model_configs"),
                )

            self._model_agent = ModelAgent(
                name="InterviewModel",
                model_name=self.config.get("model.name", "deepseek-chat"),
                temperature=self.config.get("model.temperature", 0.7),
            )
            self._use_agentscope = True
            logger.info("AgentScope ModelAgent 初始化成功")

        except ImportError:
            logger.info("AgentScope 未安装，使用内置问题生成")
            self._use_agentscope = False
        except Exception as e:
            logger.warning(f"AgentScope 初始化失败：{e}")
            self._use_agentscope = False

    def respond(self, message: Message, context: DialogueContext) -> Message:
        """
        响应候选人的回答

        Args:
            message: 输入消息
            context: 对话上下文

        Returns:
            响应消息
        """
        # 生成追问或反馈
        response_content = self._generate_response(message, context)

        return Message(
            content=response_content,
            role=self.name,
            type=MessageType.AGENT,
            metadata={
                "style": self.style.value,
                "domain": self.domain.value,
                "phase": self._current_phase,
            },
        )

    def get_role(self) -> str:
        """获取角色描述"""
        style_names = {
            InterviewStyle.FRIENDLY: "友好鼓励型",
            InterviewStyle.STRICT: "严格专业型",
            InterviewStyle.PRESSURE: "压力测试型",
        }
        domain_names = {
            DomainType.TECH: "技术",
            DomainType.FRONTEND: "前端",
            DomainType.BACKEND: "后端",
            DomainType.SYSTEM_DESIGN: "系统设计",
            DomainType.HR: "HR",
        }

        style_name = style_names.get(self.style, "专业")
        domain_name = domain_names.get(self.domain, "综合")

        return f"{style_name}{domain_name}面试官"

    def get_opening_message(self) -> str:
        """
        获取开场白

        Returns:
            开场白字符串
        """
        openings = {
            InterviewStyle.FRIENDLY: [
                "你好！很高兴今天能和你交流。不用紧张，我们就当是一次技术聊天。先简单介绍一下自己吧？",
                "哈喽！我是今天的面试官。放轻松，先做个自我介绍，聊聊你的技术背景？",
            ],
            InterviewStyle.STRICT: [
                "你好，我是今天的面试官。时间有限，请直接介绍一下你的技术背景和相关项目经验。",
                "你好。请用 3 分钟时间介绍你的技术栈和最有代表性的项目。",
            ],
            InterviewStyle.PRESSURE: [
                "你好。我们时间不多，直接说重点。说说你做过最有挑战性的项目，你解决了什么关键问题？",
                "开始吧。我看过你的简历，直接说说你最能体现技术能力的项目。",
            ],
        }

        options = openings.get(self.style, openings[InterviewStyle.FRIENDLY])
        return random.choice(options)

    def get_closing_message(self) -> str:
        """
        获取结束语

        Returns:
            结束语字符串
        """
        closings = {
            InterviewStyle.FRIENDLY: [
                "好的，今天交流得很愉快！你有什么问题想问我的吗？",
                "感谢你的时间！后续 HR 会和你联系。有什么问题现在可以问我。",
            ],
            InterviewStyle.STRICT: [
                "今天的面试到此结束。你有什么问题吗？",
                "面试结束。有问题可以现在问。",
            ],
            InterviewStyle.PRESSURE: [
                "好了，今天就到这里。你有什么要问的吗？",
                "结束。有什么问题？",
            ],
        }

        options = closings.get(self.style, closings[InterviewStyle.FRIENDLY])
        return random.choice(options)

    def generate_question(
        self,
        phase: str = "technical",
        difficulty: int = 3,
        follow_up_context: Optional[str] = None,
    ) -> str:
        """
        生成面试问题

        Args:
            phase: 面试阶段 (opening/technical/behavioral/pressure/closing)
            difficulty: 难度等级 (1-5)
            follow_up_context: 追问上下文

        Returns:
            问题字符串
        """
        self._current_phase = phase

        # 映射阶段到问题类型
        phase_to_type = {
            "technical": QuestionType.TECHNICAL.value,
            "behavioral": QuestionType.BEHAVIORAL.value,
            "pressure": QuestionType.SCENARIO.value,
        }

        question_type = phase_to_type.get(phase, QuestionType.CONCEPTUAL.value)

        # 尝试从问题库获取
        question = self.question_bank.get_random_question(
            domain=self.domain.value,
            difficulty_range=(max(1, difficulty - 1), min(5, difficulty + 1)),
            question_type=question_type,
        )

        if question and question.question_id not in self._asked_questions:
            self._asked_questions.append(question.question_id)
            return self._style_question(question.content)

        # 如果没有问题库或已问完，使用备用生成
        return self._generate_fallback_question(phase, difficulty, follow_up_context)

    def generate_follow_up(
        self,
        answer: str,
        history: Optional[List[Message]] = None,
    ) -> str:
        """
        基于回答生成追问

        Args:
            answer: 候选人的回答
            history: 对话历史

        Returns:
            追问字符串
        """
        # 尝试使用 AgentScope 生成智能追问
        if self._use_agentscope and self._model_agent:
            return self._generate_agentscope_followup(answer, history)

        # 备用方案：基于规则的追问
        return self._generate_rule_based_followup(answer, history)

    def evaluate_answer(
        self,
        answer: str,
        question: str,
        expected_points: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        评估回答质量

        Args:
            answer: 候选人的回答
            question: 原问题
            expected_points: 期望要点

        Returns:
            评估结果字典
        """
        evaluation = {
            "score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
        }

        # 简单实现：基于长度和关键词
        if len(answer) > 200:
            evaluation["score"] += 0.3
            evaluation["strengths"].append("回答详细")

        if len(answer) < 50:
            evaluation["weaknesses"].append("回答过于简短")
            evaluation["suggestions"].append("可以展开更多细节")

        # 检查关键词
        structure_words = ["首先", "然后", "最后", "因为", "所以", "例如"]
        for word in structure_words:
            if word in answer:
                evaluation["strengths"].append(f"使用{word}进行逻辑组织")
                evaluation["score"] += 0.1

        evaluation["score"] = min(1.0, evaluation["score"])

        return evaluation

    def _generate_response(
        self,
        message: Message,
        context: DialogueContext,
    ) -> str:
        """生成响应内容"""
        # 获取历史
        history = context.get_history(limit=5)

        # 生成追问
        follow_up = self.generate_follow_up(message.content, history)

        # 根据风格调整语气
        return self._style_question(follow_up)

    def _style_question(self, question: str) -> str:
        """根据面试风格调整问题语气"""
        prefixes = {
            InterviewStyle.FRIENDLY: ["好的，", "不错，", "嗯，"],
            InterviewStyle.STRICT: ["", "接下来，", "继续，"],
            InterviewStyle.PRESSURE: ["", "说吧，", "直接回答，"],
        }

        suffixes = {
            InterviewStyle.FRIENDLY: ["可以详细说说吗？", "我很有兴趣听听。", "请继续。"],
            InterviewStyle.STRICT: ["请准确回答。", "注意技术细节。", "说重点。"],
            InterviewStyle.PRESSURE: ["别绕弯子。", "直接说核心。", "这就是你的答案？"],
        }

        prefix = random.choice(prefixes.get(self.style, [""]))
        suffix = "" if self.style == InterviewStyle.STRICT else random.choice(
            suffixes.get(self.style, [""])
        )

        return f"{prefix}{question}{suffix}"

    def _generate_fallback_question(
        self,
        phase: str,
        difficulty: int,
        follow_up_context: Optional[str],
    ) -> str:
        """生成备用问题（当问题库为空时）"""
        fallback_questions = {
            "technical": [
                "请谈谈你对这个技术的理解？",
                "在实际项目中，你是如何应用这个技术的？",
                "这个方案有什么优缺点？",
            ],
            "behavioral": [
                "描述一次你遇到技术挑战的经历，你是如何解决的？",
                "你和团队成员有过技术分歧吗？怎么处理的？",
                "你如何学习新技术？最近学了什么？",
            ],
            "pressure": [
                "如果你的方案被质疑，你会怎么回应？",
                "这个方案如果失败了，你有什么备选计划？",
                "为什么你认为这是最优解？有其他选择吗？",
            ],
        }

        questions = fallback_questions.get(phase, fallback_questions["technical"])
        return random.choice(questions)

    def _generate_agentscope_followup(
        self,
        answer: str,
        history: Optional[List[Message]],
    ) -> str:
        """使用 AgentScope 生成追问"""
        if not self._model_agent:
            return self._generate_rule_based_followup(answer, history)

        try:
            # 构建提示词
            prompt = self._build_followup_prompt(answer, history)

            # 调用 ModelAgent
            response = self._model_agent(prompt)

            if isinstance(response, dict):
                return response.get("content", str(response))
            return str(response)

        except Exception as e:
            logger.error(f"AgentScope 追问生成失败：{e}")
            return self._generate_rule_based_followup(answer, history)

    def _generate_rule_based_followup(
        self,
        answer: str,
        history: Optional[List[Message]],
    ) -> str:
        """基于规则生成追问"""
        # 分析回答特征
        answer_lower = answer.lower()

        # 检测回答类型
        if len(answer) < 30:
            return "能详细说说吗？我想听更多细节。"

        # 检查是否有具体例子
        if "例如" not in answer and "比如" not in answer:
            return "能举个具体的例子吗？"

        # 检查是否有技术深度
        technical_keywords = ["原理", "机制", "算法", "架构", "设计"]
        has_depth = any(kw in answer for kw in technical_keywords)

        if not has_depth:
            return "从技术原理角度，能再深入分析一下吗？"

        # 默认追问
        follow_ups = [
            "如果让你重新设计，你会做什么改进？",
            "这个方案有什么潜在风险？",
            "和其他方案相比，你的选择有什么优势？",
        ]

        return random.choice(follow_ups)

    def _build_followup_prompt(
        self,
        answer: str,
        history: Optional[List[Message]],
    ) -> str:
        """构建 AgentScope 追问提示词"""
        style_prompt = self.STYLE_PROMPTS.get(self.style, "")
        domain_prompt = self.DOMAIN_PROMPTS.get(self.domain, "")

        prompt = f"""{style_prompt}

{domain_prompt}

候选人刚刚回答了问题，请生成一个恰当的追问。

候选人回答：
{answer}

请生成一个简洁的追问（不超过 50 字），考察更深入的技术细节或澄清模糊点。"""

        return prompt
