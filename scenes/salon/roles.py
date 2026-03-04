"""
Salon Roles Module - 沙龙角色模块

定义沙龙场景中的各种角色类型和职责。

沙龙场景支持以下角色:
- Host (主持人): 引导讨论、控制节奏、介绍话题
- Speaker (演讲者): 分享知识、展示观点、回答问题
- Audience (观众): 提问、参与讨论、提供反馈
- Observer (观察者): 记录关键点、提供总结

设计原则:
- 单一职责：每个角色有明确的职责边界
- 开放封闭：通过枚举扩展新角色
- 类型安全：使用 Enum 确保角色类型安全
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class SalonRoleType(Enum):
    """
    沙龙角色类型枚举

    定义沙龙中可用的所有角色类型
    """
    HOST = "host"           # 主持人：掌控全场节奏
    SPEAKER = "speaker"     # 演讲者：分享专业知识
    AUDIENCE = "audience"   # 观众：参与互动讨论
    OBSERVER = "observer"   # 观察者：记录和总结


@dataclass
class RoleConfig:
    """
    角色配置数据类

    封装角色相关的配置参数

    Attributes:
        role_type: 角色类型
        name: 角色显示名称
        description: 角色描述
        system_prompt: 角色系统提示词
        max_turns: 最大发言次数
        priority: 发言优先级 (1-10)
        settings: 角色特定设置
    """
    role_type: SalonRoleType
    name: str = ""
    description: str = ""
    system_prompt: str = ""
    max_turns: int = 10
    priority: int = 5
    settings: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create_host(cls, **kwargs) -> "RoleConfig":
        """
        创建主持人角色配置

        Returns:
            主持人角色配置
        """
        default_config = cls(
            role_type=SalonRoleType.HOST,
            name="主持人",
            description="沙龙活动的主持人，负责引导讨论和控制节奏",
            system_prompt="""你是一个专业的沙龙主持人。你的职责包括:
1. 开场介绍沙龙主题和演讲者
2. 引导讨论方向，确保话题不偏离
3. 控制发言时间，平衡各角色参与度
4. 总结关键观点和结论
5. 营造友好、开放的讨论氛围

你的风格应该：
- 专业但不失亲和力
- 善于倾听和总结
- 能够巧妙引导话题
- 照顾到所有参与者""",
            max_turns=15,
            priority=10,  # 主持人优先级最高
            settings={
                "opening_duration": 2,  # 开场发言轮数
                "summarize_interval": 5,  # 每 N 轮总结一次
                "transition_style": "smooth",  # 转场风格
            },
        )

        # 合并用户提供的配置
        for key, value in kwargs.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)

        return default_config

    @classmethod
    def create_speaker(cls, topic: str = "技术分享", **kwargs) -> "RoleConfig":
        """
        创建演讲者角色配置

        Args:
            topic: 演讲主题

        Returns:
            演讲者角色配置
        """
        default_config = cls(
            role_type=SalonRoleType.SPEAKER,
            name="演讲嘉宾",
            description=f"分享'{topic}'相关知识的专家",
            system_prompt=f"""你是一位在'{topic}'领域有深厚造诣的专家。你的职责包括:
1. 分享专业知识和独到见解
2. 回答观众的提问
3. 用通俗易懂的方式解释复杂概念
4. 提供实际案例和经验分享

你的风格应该：
- 专业权威但不傲慢
- 善于用例子说明问题
- 耐心解答疑问
- 鼓励互动和讨论""",
            max_turns=12,
            priority=8,
            settings={
                "topic": topic,
                "expertise_level": "expert",
                "presentation_style": "interactive",
            },
        )

        for key, value in kwargs.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)

        return default_config

    @classmethod
    def create_audience(cls, **kwargs) -> "RoleConfig":
        """
        创建观众角色配置

        Returns:
            观众角色配置
        """
        default_config = cls(
            role_type=SalonRoleType.AUDIENCE,
            name="观众",
            description="积极参与讨论的沙龙观众",
            system_prompt="""你是沙龙的观众，对讨论话题有浓厚兴趣。你的职责包括:
1. 提出有深度的问题
2. 分享自己的观点和经验
3. 与其他观众互动讨论
4. 给予演讲者积极反馈

你的风格应该：
- 积极但不抢话
- 提问有针对性和深度
- 尊重他人观点
- 乐于分享和学习""",
            max_turns=8,
            priority=5,
            settings={
                "engagement_level": "active",
                "question_style": "thoughtful",
                "background": "practitioner",
            },
        )

        for key, value in kwargs.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)

        return default_config

    @classmethod
    def create_observer(cls, **kwargs) -> "RoleConfig":
        """
        创建观察者角色配置

        Returns:
            观察者角色配置
        """
        default_config = cls(
            role_type=SalonRoleType.OBSERVER,
            name="观察员",
            description="记录沙龙讨论要点并提供总结",
            system_prompt="""你是沙龙的观察员，负责记录和总结。你的职责包括:
1. 记录讨论中的关键观点
2. 识别共识和分歧点
3. 在适当时机提供阶段性总结
4. 整理讨论成果和建议

你的风格应该：
- 客观中立
- 善于提炼要点
- 逻辑清晰
- 总结精准""",
            max_turns=6,
            priority=6,
            settings={
                "summary_style": "structured",
                "intervention_frequency": "moderate",
                "focus_areas": ["key_points", "consensus", "action_items"],
            },
        )

        for key, value in kwargs.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)

        return default_config

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "role_type": self.role_type.value,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "max_turns": self.max_turns,
            "priority": self.priority,
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleConfig":
        """从字典创建"""
        return cls(
            role_type=SalonRoleType(data.get("role_type", "host")),
            name=data.get("name", ""),
            description=data.get("description", ""),
            system_prompt=data.get("system_prompt", ""),
            max_turns=data.get("max_turns", 10),
            priority=data.get("priority", 5),
            settings=data.get("settings", {}),
        )


@dataclass
class RoleState:
    """
    角色状态数据类

    跟踪角色在沙龙中的状态

    Attributes:
        role_type: 角色类型
        turn_count: 已发言次数
        last_turn: 上次发言轮次
        active: 是否活跃
        notes: 角色笔记/记录
    """
    role_type: SalonRoleType
    turn_count: int = 0
    last_turn: int = 0
    active: bool = True
    notes: List[str] = field(default_factory=list)

    def increment_turn(self, turn_number: int) -> None:
        """增加发言计数"""
        self.turn_count += 1
        self.last_turn = turn_number

    def can_speak(self, max_turns: int) -> bool:
        """检查是否可以发言"""
        return self.active and self.turn_count < max_turns

    def add_note(self, note: str) -> None:
        """添加笔记"""
        self.notes.append(note)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "role_type": self.role_type.value,
            "turn_count": self.turn_count,
            "last_turn": self.last_turn,
            "active": self.active,
            "notes": self.notes,
        }


class RoleManager:
    """
    角色管理器

    管理沙龙中所有角色的状态和配置

    Usage:
        >>> manager = RoleManager()
        >>> manager.add_role(RoleConfig.create_host())
        >>> manager.add_role(RoleConfig.create_speaker(topic="AI"))
        >>> host_config = manager.get_role_config(SalonRoleType.HOST)
    """

    def __init__(self):
        """初始化角色管理器"""
        self._configs: Dict[SalonRoleType, RoleConfig] = {}
        self._states: Dict[SalonRoleType, RoleState] = {}
        self._current_turn: int = 0

    def add_role(
        self,
        config: RoleConfig,
        state: Optional[RoleState] = None,
    ) -> None:
        """
        添加角色

        Args:
            config: 角色配置
            state: 角色状态（可选，默认创建初始状态）
        """
        role_type = config.role_type
        self._configs[role_type] = config

        if state is None:
            state = RoleState(role_type=role_type)
        self._states[role_type] = state

    def get_role_config(self, role_type: SalonRoleType) -> Optional[RoleConfig]:
        """获取角色配置"""
        return self._configs.get(role_type)

    def get_role_state(self, role_type: SalonRoleType) -> Optional[RoleState]:
        """获取角色状态"""
        return self._states.get(role_type)

    def get_all_configs(self) -> List[RoleConfig]:
        """获取所有角色配置"""
        return list(self._configs.values())

    def get_all_states(self) -> List[RoleState]:
        """获取所有角色状态"""
        return list(self._states.values())

    def increment_turn(self, role_type: SalonRoleType) -> None:
        """
        增加角色发言计数

        Args:
            role_type: 角色类型
        """
        self._current_turn += 1
        if role_type in self._states:
            self._states[role_type].increment_turn(self._current_turn)

    def get_current_turn(self) -> int:
        """获取当前轮次"""
        return self._current_turn

    def reset(self) -> None:
        """重置所有角色状态"""
        self._current_turn = 0
        for state in self._states.values():
            state.turn_count = 0
            state.last_turn = 0
            state.active = True
            state.notes.clear()

    def get_active_roles(self) -> List[SalonRoleType]:
        """获取所有活跃角色"""
        return [
            role_type for role_type, state in self._states.items()
            if state.active
        ]

    def deactivate_role(self, role_type: SalonRoleType) -> bool:
        """
        停用角色

        Args:
            role_type: 角色类型

        Returns:
            是否成功停用
        """
        if role_type in self._states:
            self._states[role_type].active = False
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "configs": {
                role_type.value: config.to_dict()
                for role_type, config in self._configs.items()
            },
            "states": {
                role_type.value: state.to_dict()
                for role_type, state in self._states.items()
            },
            "current_turn": self._current_turn,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoleManager":
        """从字典创建"""
        manager = cls()

        # 恢复配置
        configs_data = data.get("configs", {})
        for role_type_str, config_data in configs_data.items():
            config = RoleConfig.from_dict(config_data)
            manager.add_role(config)

        # 恢复状态
        states_data = data.get("states", {})
        for role_type_str, state_data in states_data.items():
            role_type = SalonRoleType(role_type_str)
            state = RoleState(
                role_type=role_type,
                turn_count=state_data.get("turn_count", 0),
                last_turn=state_data.get("last_turn", 0),
                active=state_data.get("active", True),
                notes=state_data.get("notes", []),
            )
            if role_type in manager._states:
                manager._states[role_type] = state

        manager._current_turn = data.get("current_turn", 0)
        return manager
