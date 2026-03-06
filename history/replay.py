"""
Session Replay

会话回放功能：
- 加载和回放过往会话
- 步骤导航（上一步/下一步）
- 添加注释和笔记

Design Principles:
- 状态管理清晰
- 支持多种回放模式
- 易于扩展
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from users.database import Database
from users.tables import SessionTable


class ReplayMode(str, Enum):
    """回放模式"""
    NORMAL = "normal"           # 正常回放
    STEP_BY_STEP = "step_by_step"  # 单步回放
    AUTO = "auto"               # 自动回放


@dataclass
class ReplayStep:
    """回放步骤"""
    index: int
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        role_display = {
            "user": "👤 用户",
            "assistant": "🤖 AI",
            "system": "⚙️ 系统",
        }
        role_name = role_display.get(self.role, self.role)
        return f"[{role_name}] {self.content[:50]}..."


@dataclass
class ReplayNote:
    """回放笔记"""
    step_index: int
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "step_index": self.step_index,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReplayNote":
        """从字典创建"""
        return cls(
            step_index=data["step_index"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            tags=data.get("tags", []),
        )


@dataclass
class ReplayData:
    """回放数据"""
    session_id: str
    steps: List[ReplayStep] = field(default_factory=list)
    notes: List[ReplayNote] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayState:
    """回放状态"""
    current_step: int = 0
    mode: ReplayMode = ReplayMode.STEP_BY_STEP
    is_playing: bool = False
    speed: float = 1.0  # 播放速度倍率
    total_steps: int = 0
    
    def reset(self) -> None:
        """重置状态"""
        self.current_step = 0
        self.is_playing = False
        self.speed = 1.0


class SessionReplay:
    """
    会话回放器
    
    加载和回放历史会话
    
    Usage:
        replay = SessionReplay(session_id=1)
        replay.load()
        
        # 单步导航
        replay.next_step()
        replay.prev_step()
        
        # 获取当前步骤
        step = replay.get_current_step()
        
        # 添加笔记
        replay.add_note(0, "这个回答很好")
    """
    
    def __init__(self, session_id: Optional[int] = None,
                 db: Optional[Database] = None):
        """
        初始化会话回放器
        
        Args:
            session_id: 会话 ID
            db: 数据库实例（可选）
        """
        self.session_id = session_id
        self.db = db or Database.get_instance()
        
        # 回放数据
        self.steps: List[ReplayStep] = []
        self.notes: List[ReplayNote] = []
        self.state = ReplayState()
        
        # 会话元数据
        self.session_info: Dict[str, Any] = {}
        self.evaluation_result: Dict[str, Any] = {}
        
        # 回调函数
        self._on_step_change: Optional[Callable] = None
    
    def load(self, session_id: Optional[int] = None) -> bool:
        """
        加载会话
        
        Args:
            session_id: 会话 ID（可选，覆盖构造函数的值）
            
        Returns:
            是否加载成功
        """
        if session_id:
            self.session_id = session_id
        
        if self.session_id is None:
            return False
        
        with self.db.get_session() as session:
            session_record = session.get(SessionTable, self.session_id)
            
            if session_record is None:
                return False
            
            # 保存会话信息
            self.session_info = {
                "id": session_record.id,
                "user_id": session_record.user_id,
                "scene_type": session_record.scene_type,
                "scene_id": session_record.scene_id,
                "title": session_record.title,
                "status": session_record.status,
                "started_at": session_record.started_at,
                "ended_at": session_record.ended_at,
                "duration_seconds": session_record.duration_seconds,
            }
            
            # 解析对话历史
            self._parse_dialogue_history(session_record.dialogue_history)
            
            # 解析评估结果
            if session_record.evaluation_result:
                try:
                    self.evaluation_result = json.loads(session_record.evaluation_result)
                except:
                    self.evaluation_result = {}
            
            # 解析笔记（从 metadata 中）
            if session_record.metadata:
                notes_data = session_record.metadata.get("notes", [])
                self.notes = [ReplayNote.from_dict(n) for n in notes_data]
            
            # 初始化状态
            self.state.total_steps = len(self.steps)
            self.state.reset()
            
            return True
    
    def _parse_dialogue_history(self, dialogue_history: Optional[str]) -> None:
        """
        解析对话历史
        
        Args:
            dialogue_history: 对话历史 JSON 字符串
        """
        self.steps = []
        
        if not dialogue_history:
            return
        
        try:
            history = json.loads(dialogue_history)
            
            if isinstance(history, list):
                for i, msg in enumerate(history):
                    step = ReplayStep(
                        index=i,
                        role=msg.get("role", "unknown"),
                        content=msg.get("content", ""),
                        timestamp=msg.get("timestamp"),
                        metadata=msg.get("metadata", {})
                    )
                    self.steps.append(step)
            
        except json.JSONDecodeError:
            pass
    
    # =========================================================================
    # Navigation
    # =========================================================================
    
    def next_step(self) -> Optional[ReplayStep]:
        """
        下一步
        
        Returns:
            下一步的 ReplayStep，如果没有更多步骤则返回 None
        """
        if self.state.current_step >= len(self.steps) - 1:
            return None
        
        self.state.current_step += 1
        self._notify_step_change()
        
        return self.get_current_step()
    
    def prev_step(self) -> Optional[ReplayStep]:
        """
        上一步
        
        Returns:
            上一步的 ReplayStep，如果已经是第一步则返回 None
        """
        if self.state.current_step <= 0:
            return None
        
        self.state.current_step -= 1
        self._notify_step_change()
        
        return self.get_current_step()
    
    def goto_step(self, step_index: int) -> Optional[ReplayStep]:
        """
        跳转到指定步骤
        
        Args:
            step_index: 步骤索引
            
        Returns:
            目标步骤的 ReplayStep，如果索引无效则返回 None
        """
        if step_index < 0 or step_index >= len(self.steps):
            return None
        
        self.state.current_step = step_index
        self._notify_step_change()
        
        return self.get_current_step()
    
    def first_step(self) -> Optional[ReplayStep]:
        """
        第一步
        
        Returns:
            第一步的 ReplayStep
        """
        return self.goto_step(0)
    
    def last_step(self) -> Optional[ReplayStep]:
        """
        最后一步
        
        Returns:
            最后一步的 ReplayStep
        """
        return self.goto_step(len(self.steps) - 1)
    
    def get_current_step(self) -> Optional[ReplayStep]:
        """
        获取当前步骤

        Returns:
            当前步骤的 ReplayStep，如果没有步骤则返回 None
        """
        if not self.steps:
            return None

        if 0 <= self.state.current_step < len(self.steps):
            return self.steps[self.state.current_step]

        return None

    def add_step(self, step: Optional["ReplayStep"] = None, speaker: str = "", content: str = "") -> None:
        """
        添加步骤到回放列表

        Args:
            step: 要添加的步骤（可选）
            speaker: 说话者（可选）
            content: 内容（可选）
        """
        if step is None:
            # Create a step from speaker and content
            step = ReplayStep(
                index=len(self.steps),
                timestamp=datetime.utcnow(),
                role=speaker,  # Use role field
                content=content,
                metadata={},
            )
        self.steps.append(step)
        self.state.total_steps = len(self.steps)

    def get_step_at(self, index: int) -> Optional[ReplayStep]:
        """
        获取指定索引的步骤
        
        Args:
            index: 步骤索引
            
        Returns:
            指定索引的 ReplayStep
        """
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None
    
    def get_all_steps(self) -> List[ReplayStep]:
        """
        获取所有步骤
        
        Returns:
            所有步骤的列表
        """
        return self.steps.copy()
    
    # =========================================================================
    # Playback Control
    # =========================================================================
    
    def play(self, callback: Optional[Callable[[ReplayStep], None]] = None) -> None:
        """
        开始自动播放
        
        Args:
            callback: 每步回调函数
        """
        self.state.is_playing = True
        
        def play_step():
            if not self.state.is_playing:
                return
            
            step = self.next_step()
            if step and callback:
                callback(step)
            
            if self.state.current_step < len(self.steps) - 1:
                # 简单实现，实际应使用异步
                import time
                time.sleep(1.0 / self.state.speed)
                play_step()
            else:
                self.state.is_playing = False
        
        # 注意：这是简化实现，实际应使用异步或线程
        play_step()
    
    def pause(self) -> None:
        """暂停播放"""
        self.state.is_playing = False

    def stop(self) -> None:
        """停止播放并回到开始"""
        self.state.is_playing = False
        self.state.current_step = 0
        self._notify_step_change()

    def start_session(self, session_id: int) -> bool:
        """
        开始会话回放

        Args:
            session_id: 会话 ID

        Returns:
            是否成功加载会话
        """
        return self.load(session_id)

    def set_speed(self, speed: float) -> None:
        """
        设置播放速度
        
        Args:
            speed: 速度倍率（0.5, 1.0, 1.5, 2.0）
        """
        self.state.speed = max(0.25, min(4.0, speed))
    
    # =========================================================================
    # Notes & Annotations
    # =========================================================================
    
    def add_note(self, step_index: int, content: str,
                tags: Optional[List[str]] = None) -> ReplayNote:
        """
        添加笔记
        
        Args:
            step_index: 步骤索引
            content: 笔记内容
            tags: 标签列表
            
        Returns:
            创建的 ReplayNote
        """
        note = ReplayNote(
            step_index=step_index,
            content=content,
            tags=tags or []
        )
        self.notes.append(note)
        
        # 保存到数据库
        self._save_notes()
        
        return note
    
    def get_notes(self, step_index: Optional[int] = None) -> List[ReplayNote]:
        """
        获取笔记
        
        Args:
            step_index: 步骤索引（可选，过滤特定步骤的笔记）
            
        Returns:
            笔记列表
        """
        if step_index is not None:
            return [n for n in self.notes if n.step_index == step_index]
        return self.notes.copy()
    
    def remove_note(self, note_index: int) -> bool:
        """
        删除笔记
        
        Args:
            note_index: 笔记索引
            
        Returns:
            是否成功删除
        """
        if 0 <= note_index < len(self.notes):
            del self.notes[note_index]
            self._save_notes()
            return True
        return False
    
    def _save_notes(self) -> None:
        """保存笔记到数据库"""
        if self.session_id is None:
            return
        
        with self.db.get_session() as session:
            session_record = session.get(SessionTable, self.session_id)
            
            if session_record is None:
                return
            
            # 保存笔记到 metadata
            if session_record.metadata is None:
                session_record.metadata = {}
            
            session_record.metadata["notes"] = [n.to_dict() for n in self.notes]
            session_record.updated_at = datetime.utcnow()
            
            session.commit()
    
    # =========================================================================
    # Export & Import
    # =========================================================================
    
    def export(self, format: str = "json") -> str:
        """
        导出回放数据
        
        Args:
            format: 导出格式（json, markdown）
            
        Returns:
            导出的字符串
        """
        if format == "json":
            return self._export_json()
        elif format == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self) -> str:
        """导出为 JSON"""
        data = {
            "session_info": self.session_info,
            "evaluation_result": self.evaluation_result,
            "steps": [
                {
                    "index": s.index,
                    "role": s.role,
                    "content": s.content,
                    "timestamp": str(s.timestamp) if s.timestamp else None,
                    "metadata": s.metadata,
                }
                for s in self.steps
            ],
            "notes": [n.to_dict() for n in self.notes],
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _export_markdown(self) -> str:
        """导出为 Markdown"""
        lines = []
        
        # 标题
        title = self.session_info.get("title") or f"Session #{self.session_info.get('id')}"
        lines.append(f"# {title}")
        lines.append("")
        
        # 会话信息
        lines.append("## 会话信息")
        lines.append(f"- 场景：{self.session_info.get('scene_type')}")
        lines.append(f"- 状态：{self.session_info.get('status')}")
        lines.append(f"- 时长：{self.session_info.get('duration_seconds', 0)}秒")
        lines.append("")
        
        # 对话历史
        lines.append("## 对话历史")
        lines.append("")
        
        for step in self.steps:
            role_display = {
                "user": "👤 **用户**",
                "assistant": "🤖 **AI**",
                "system": "⚙️ **系统**",
            }
            role_name = role_display.get(step.role, step.role)
            
            lines.append(f"### {role_name}")
            lines.append("")
            lines.append(step.content)
            lines.append("")
            
            # 显示该步骤的笔记
            step_notes = self.get_notes(step.index)
            if step_notes:
                lines.append("> **笔记:**")
                for note in step_notes:
                    lines.append(f"> - {note.content}")
                lines.append("")
        
        # 评估结果
        if self.evaluation_result:
            lines.append("## 评估结果")
            lines.append("")
            
            overall_score = self.evaluation_result.get("overall_score", 0)
            lines.append(f"**总分：{overall_score:.1f}**")
            lines.append("")
            
            # 各维度分数
            lines.append("### 维度评分")
            for key, value in self.evaluation_result.items():
                if key not in ["overall_score", "strengths", "improvements"]:
                    lines.append(f"- {key}: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    # =========================================================================
    # Callbacks
    # =========================================================================
    
    def on_step_change(self, callback: Callable[[ReplayStep], None]) -> None:
        """
        注册步骤变化回调
        
        Args:
            callback: 回调函数
        """
        self._on_step_change = callback
    
    def _notify_step_change(self) -> None:
        """通知步骤变化"""
        if self._on_step_change:
            step = self.get_current_step()
            if step:
                self._on_step_change(step)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_progress(self) -> float:
        """
        获取回放进度
        
        Returns:
            进度百分比 (0-100)
        """
        if not self.steps:
            return 0.0
        
        return (self.state.current_step + 1) / len(self.steps) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取回放摘要

        Returns:
            摘要字典
        """
        return {
            "session_id": self.session_id,
            "scene_type": self.session_info.get("scene_type"),
            "title": self.session_info.get("title"),
            "total_steps": len(self.steps),
            "current_step": self.state.current_step,
            "progress": self.get_progress(),
            "notes_count": len(self.notes),
            "overall_score": self.evaluation_result.get("overall_score", 0),
        }

    def end_session(self) -> None:
        """
        结束会话回放

        标记会话已结束
        """
        self.state.is_playing = False

    def get_replay_data(self) -> "ReplayData":
        """
        获取回放数据

        Returns:
            包含所有回放步骤的数据对象
        """
        return ReplayData(
            session_id=self.session_id or "",
            steps=self.steps,
            notes=self.notes,
            metadata=self.session_info,
        )
