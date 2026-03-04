"""
Voice Replay Module

语音回放模块

This module provides voice playback functionality with:
- Record and playback sessions
- Segment navigation
- Speed control (0.5x - 2.0x)
- Session management

版本：v0.8.0
"""

import logging
import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Union
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """Playback state."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class ReplayMode(Enum):
    """Replay mode."""
    NORMAL = "normal"
    LOOP = "loop"
    SHUFFLE = "shuffle"
    SINGLE = "single"


@dataclass
class ReplaySegment:
    """A segment of a replay session."""
    id: str
    start_time: float  # seconds from session start
    end_time: float  # seconds from session start
    speaker: str  # "user" or "agent"
    text: str
    audio_file: Optional[str] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "speaker": self.speaker,
            "text": self.text,
            "audio_file": self.audio_file,
            "duration": self.duration,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReplaySegment':
        return cls(**data)


@dataclass
class ReplaySession:
    """A voice replay session."""
    id: str
    name: str
    created_at: float
    duration: float
    segments: List[ReplaySegment]
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "duration": self.duration,
            "segments": [s.to_dict() for s in self.segments],
            "metadata": self.metadata,
            "tags": self.tags,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReplaySession':
        segments = [ReplaySegment.from_dict(s) for s in data.get("segments", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data["created_at"],
            duration=data["duration"],
            segments=segments,
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            notes=data.get("notes", "")
        )


@dataclass
class PlaybackPosition:
    """Current playback position."""
    current_segment_index: int = 0
    current_time: float = 0.0
    total_time: float = 0.0
    speed: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReplayConfig:
    """Configuration for VoiceReplay."""
    auto_save: bool = True
    save_interval: float = 60.0  # seconds
    cache_audio: bool = True
    default_speed: float = 1.0
    min_speed: float = 0.5
    max_speed: float = 2.0
    speed_step: float = 0.1
    storage_dir: str = "./data/replays"
    audio_format: str = "wav"


class VoiceReplay:
    """
    Voice Replay Engine
    
    语音回放引擎
    
    Features:
    - Record and playback voice sessions
    - Segment navigation (previous/next/jump)
    - Speed control (0.5x - 2.0x)
    - Session management and storage
    - Loop and shuffle modes
    
    功能:
    - 录制和回放语音会话
    - 分段导航
    - 速度控制
    - 会话管理和存储
    - 循环和随机播放模式
    """
    
    def __init__(self, config: Optional[ReplayConfig] = None):
        """
        Initialize VoiceReplay.
        
        Args:
            config: Replay configuration
        """
        self.config = config or ReplayConfig()
        
        # Ensure storage directory exists
        self.storage_dir = Path(self.config.storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session
        self._current_session: Optional[ReplaySession] = None
        self._segments: List[ReplaySegment] = []
        
        # Playback state
        self._state = PlaybackState.STOPPED
        self._position = PlaybackPosition()
        self._mode = ReplayMode.NORMAL
        self._speed = self.config.default_speed
        
        # Playback thread
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # Callbacks
        self._on_segment_change: Optional[Callable[[ReplaySegment], None]] = None
        self._on_playback_complete: Optional[Callable[[], None]] = None
        
        # Session storage
        self._sessions: Dict[str, ReplaySession] = {}
        self._load_sessions()
        
        logger.info(f"VoiceReplay initialized, storage: {self.storage_dir}")
    
    def start_session(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new replay session.
        
        开始新的回放会话
        
        Args:
            name: Session name
            metadata: Optional metadata
            
        Returns:
            Session ID
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._current_session = ReplaySession(
            id=session_id,
            name=name,
            created_at=time.time(),
            duration=0.0,
            segments=[],
            metadata=metadata or {},
        )
        self._segments = []
        
        logger.info(f"Started session: {session_id} - {name}")
        return session_id
    
    def add_segment(self,
                   speaker: str,
                   text: str,
                   audio_file: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> ReplaySegment:
        """
        Add a segment to current session.
        
        添加片段到当前会话
        
        Args:
            speaker: Speaker identifier ("user" or "agent")
            text: Transcribed text
            audio_file: Optional audio file path
            metadata: Optional metadata
            
        Returns:
            Created segment
        """
        if not self._current_session:
            raise RuntimeError("No active session. Call start_session() first.")
        
        # Calculate start time
        if self._segments:
            start_time = self._segments[-1].end_time
        else:
            start_time = 0.0
        
        # Calculate duration from audio file or estimate from text
        duration = self._estimate_duration(text, audio_file)
        end_time = start_time + duration
        
        segment = ReplaySegment(
            id=f"segment_{len(self._segments)}",
            start_time=start_time,
            end_time=end_time,
            speaker=speaker,
            text=text,
            audio_file=audio_file,
            duration=duration,
            metadata=metadata or {}
        )
        
        self._segments.append(segment)
        self._current_session.segments = self._segments
        self._current_session.duration = end_time
        
        logger.debug(f"Added segment: {segment.id} ({duration:.2f}s)")
        
        return segment
    
    def end_session(self) -> Optional[ReplaySession]:
        """
        End current session and save.
        
        结束当前会话并保存
        
        Returns:
            Saved session
        """
        if not self._current_session:
            return None
        
        # Stop playback if active
        self.stop()
        
        session = self._current_session
        session.segments = self._segments
        
        # Save session
        if self.config.auto_save:
            self._save_session(session)
        
        self._sessions[session.id] = session
        self._current_session = None
        self._segments = []
        
        logger.info(f"Ended session: {session.id}")
        return session
    
    def play(self, from_segment: Optional[int] = None):
        """
        Start playback.
        
        开始播放
        
        Args:
            from_segment: Optional segment index to start from
        """
        if not self._current_session and not self._segments:
            logger.warning("No session to play")
            return
        
        if self._state == PlaybackState.PLAYING:
            logger.warning("Already playing")
            return
        
        self._state = PlaybackState.PLAYING
        self._pause_event.clear()
        
        if from_segment is not None:
            self._position.current_segment_index = from_segment
        
        self._playback_thread = threading.Thread(
            target=self._playback_loop,
            daemon=True
        )
        self._playback_thread.start()
        
        logger.info(f"Playback started at segment {self._position.current_segment_index}")
    
    def pause(self):
        """Pause playback."""
        if self._state != PlaybackState.PLAYING:
            return
        
        self._state = PlaybackState.PAUSED
        self._pause_event.set()
        logger.info("Playback paused")
    
    def resume(self):
        """Resume paused playback."""
        if self._state != PlaybackState.PAUSED:
            return
        
        self._state = PlaybackState.PLAYING
        self._pause_event.clear()
        logger.info("Playback resumed")
    
    def stop(self):
        """Stop playback."""
        if self._state == PlaybackState.STOPPED:
            return
        
        self._stop_event.set()
        self._pause_event.clear()
        
        if self._playback_thread:
            self._playback_thread.join(timeout=2.0)
            self._playback_thread = None
        
        self._state = PlaybackState.STOPPED
        self._position.current_segment_index = 0
        self._position.current_time = 0.0
        
        logger.info("Playback stopped")
    
    def next_segment(self):
        """Skip to next segment."""
        if not self._segments:
            return
        
        current = self._position.current_segment_index
        if current < len(self._segments) - 1:
            self._position.current_segment_index = current + 1
            self._position.current_time = self._segments[current + 1].start_time
            
            if self._on_segment_change:
                self._on_segment_change(self._segments[current + 1])
            
            logger.debug(f"Skipped to segment {current + 1}")
    
    def previous_segment(self):
        """Skip to previous segment."""
        if not self._segments:
            return
        
        current = self._position.current_segment_index
        if current > 0:
            self._position.current_segment_index = current - 1
            self._position.current_time = self._segments[current - 1].start_time
            
            if self._on_segment_change:
                self._on_segment_change(self._segments[current - 1])
            
            logger.debug(f"Skipped to segment {current - 1}")
    
    def jump_to(self, segment_index: int):
        """
        Jump to specific segment.
        
        跳转到指定片段
        
        Args:
            segment_index: Target segment index
        """
        if not self._segments:
            return
        
        if 0 <= segment_index < len(self._segments):
            self._position.current_segment_index = segment_index
            self._position.current_time = self._segments[segment_index].start_time
            
            if self._on_segment_change:
                self._on_segment_change(self._segments[segment_index])
            
            logger.info(f"Jumped to segment {segment_index}")
    
    def jump_to_time(self, time_seconds: float):
        """
        Jump to specific time.
        
        跳转到指定时间
        
        Args:
            time_seconds: Time in seconds from session start
        """
        if not self._segments:
            return
        
        # Find segment containing this time
        for i, segment in enumerate(self._segments):
            if segment.start_time <= time_seconds <= segment.end_time:
                self.jump_to(i)
                return
        
        # If past all segments, jump to last
        if self._segments:
            self.jump_to(len(self._segments) - 1)
    
    def set_speed(self, speed: float):
        """
        Set playback speed.
        
        设置播放速度
        
        Args:
            speed: Speed multiplier (0.5 - 2.0)
        """
        speed = max(self.config.min_speed, min(self.config.max_speed, speed))
        self._speed = speed
        self._position.speed = speed
        logger.info(f"Playback speed set to {speed}x")
    
    def increase_speed(self):
        """Increase playback speed."""
        new_speed = min(self.config.max_speed, self._speed + self.config.speed_step)
        self.set_speed(new_speed)
    
    def decrease_speed(self):
        """Decrease playback speed."""
        new_speed = max(self.config.min_speed, self._speed - self.config.speed_step)
        self.set_speed(new_speed)
    
    def set_mode(self, mode: ReplayMode):
        """Set replay mode."""
        self._mode = mode
        logger.info(f"Replay mode set to {mode.value}")
    
    def get_position(self) -> PlaybackPosition:
        """Get current playback position."""
        return self._position
    
    def get_current_segment(self) -> Optional[ReplaySegment]:
        """Get current segment."""
        if not self._segments:
            return None
        
        index = self._position.current_segment_index
        if 0 <= index < len(self._segments):
            return self._segments[index]
        return None
    
    def get_segments(self) -> List[ReplaySegment]:
        """Get all segments."""
        return self._segments
    
    def get_session(self, session_id: str) -> Optional[ReplaySession]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions."""
        return [
            {
                "id": s.id,
                "name": s.name,
                "created_at": s.created_at,
                "duration": s.duration,
                "segment_count": len(s.segments),
                "tags": s.tags
            }
            for s in self._sessions.values()
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        删除会话
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted
        """
        if session_id not in self._sessions:
            return False
        
        session = self._sessions[session_id]
        
        # Delete audio files
        for segment in session.segments:
            if segment.audio_file and Path(segment.audio_file).exists():
                try:
                    Path(segment.audio_file).unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete audio file: {e}")
        
        # Delete session file
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
        
        del self._sessions[session_id]
        logger.info(f"Deleted session: {session_id}")
        return True
    
    def export_session(self, session_id: str, output_path: str) -> bool:
        """
        Export session to file.
        
        导出会话到文件
        
        Args:
            session_id: Session ID
            output_path: Output file path
            
        Returns:
            True if exported
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported session {session_id} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    def import_session(self, file_path: str) -> Optional[ReplaySession]:
        """
        Import session from file.
        
        从文件导入会话
        
        Args:
            file_path: Session file path
            
        Returns:
            Imported session
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session = ReplaySession.from_dict(data)
            self._sessions[session.id] = session
            
            logger.info(f"Imported session {session.id} from {file_path}")
            return session
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            return None
    
    def add_note(self, segment_index: int, note: str) -> bool:
        """
        Add note to segment.
        
        添加笔记到片段
        
        Args:
            segment_index: Segment index
            note: Note text
            
        Returns:
            True if added
        """
        if not self._segments or segment_index >= len(self._segments):
            return False
        
        segment = self._segments[segment_index]
        segment.metadata["note"] = note
        segment.metadata["note_time"] = time.time()
        
        logger.debug(f"Added note to segment {segment_index}")
        return True
    
    def get_notes(self) -> List[Dict[str, Any]]:
        """Get all notes from segments."""
        notes = []
        for i, segment in enumerate(self._segments):
            if "note" in segment.metadata:
                notes.append({
                    "segment_index": i,
                    "time": segment.start_time,
                    "text": segment.text[:100],
                    "note": segment.metadata["note"],
                    "note_time": segment.metadata.get("note_time")
                })
        return notes
    
    def set_callbacks(self,
                     on_segment_change: Optional[Callable[[ReplaySegment], None]] = None,
                     on_playback_complete: Optional[Callable[[], None]] = None):
        """
        Set playback callbacks.
        
        设置播放回调
        
        Args:
            on_segment_change: Called when segment changes
            on_playback_complete: Called when playback completes
        """
        self._on_segment_change = on_segment_change
        self._on_playback_complete = on_playback_complete
    
    def _playback_loop(self):
        """Background playback loop."""
        try:
            while not self._stop_event.is_set():
                # Check pause
                if self._pause_event.is_set():
                    time.sleep(0.1)
                    continue
                
                # Get current segment
                if self._position.current_segment_index >= len(self._segments):
                    # End of session
                    if self._mode == ReplayMode.LOOP:
                        self._position.current_segment_index = 0
                        self._position.current_time = 0.0
                        continue
                    elif self._mode == ReplayMode.SHUFFLE:
                        import random
                        self._position.current_segment_index = random.randint(0, len(self._segments) - 1)
                        continue
                    else:
                        break
                
                segment = self._segments[self._position.current_segment_index]
                
                # Notify segment change
                if self._on_segment_change:
                    self._on_segment_change(segment)
                
                # Play audio if available
                if segment.audio_file and Path(segment.audio_file).exists():
                    self._play_audio_file(segment.audio_file)
                else:
                    # Simulate playback duration
                    sleep_time = segment.duration / self._speed
                    elapsed = 0
                    while elapsed < sleep_time and not self._stop_event.is_set():
                        if self._pause_event.is_set():
                            time.sleep(0.1)
                            continue
                        time.sleep(0.1)
                        elapsed += 0.1
                
                # Move to next segment
                self._position.current_segment_index += 1
                self._position.current_time = segment.end_time
            
            # Playback complete
            if self._on_playback_complete and not self._stop_event.is_set():
                self._on_playback_complete()
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
        finally:
            self._state = PlaybackState.STOPPED
            self._stop_event.clear()
    
    def _play_audio_file(self, file_path: str):
        """Play audio file."""
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            
            audio = AudioSegment.from_file(file_path)
            
            # Apply speed change if needed
            if self._speed != 1.0:
                from pydub.effects import speedup
                if self._speed > 1.0:
                    audio = speedup(audio, self._speed, chunk=150)
                else:
                    new_frame_rate = int(audio.frame_rate * self._speed)
                    audio = audio._spawn(
                        audio.raw_data,
                        overrides={'frame_rate': new_frame_rate}
                    )
                    audio = audio.set_frame_rate(audio.frame_rate)
            
            play(audio)
            
        except Exception as e:
            logger.warning(f"Failed to play audio file {file_path}: {e}")
    
    def _estimate_duration(self, text: str, audio_file: Optional[str]) -> float:
        """Estimate speech duration from text or audio file."""
        if audio_file and Path(audio_file).exists():
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_file)
                return len(audio) / 1000.0
            except Exception:
                pass
        
        # Estimate from text (Chinese: ~4 chars/sec, English: ~3 words/sec)
        chinese_chars = len([c for c in text if '\u4e00-\u9fa5' in c])
        if chinese_chars > 0:
            return chinese_chars / 4.0
        
        # English words
        words = len(text.split())
        return words / 3.0
    
    def _save_session(self, session: ReplaySession):
        """Save session to file."""
        session_file = self.storage_dir / f"{session.id}.json"
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Saved session to {session_file}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def _load_sessions(self):
        """Load sessions from storage."""
        if not self.storage_dir.exists():
            return
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                session = self.import_session(str(file_path))
                if session:
                    self._sessions[session.id] = session
            except Exception as e:
                logger.warning(f"Failed to load session {file_path}: {e}")
        
        logger.info(f"Loaded {len(self._sessions)} sessions")
    
    def generate_transcript(self, session_id: Optional[str] = None) -> str:
        """
        Generate transcript for session.
        
        生成会话文字记录
        
        Args:
            session_id: Session ID (uses current session if None)
            
        Returns:
            Transcript text
        """
        if session_id:
            session = self.get_session(session_id)
            if not session:
                return ""
            segments = session.segments
        else:
            segments = self._segments
        
        if not segments:
            return ""
        
        lines = [
            f"会话记录 (Session Transcript)",
            f"会话 ID: {self._current_session.id if self._current_session else session_id}",
            f"会话名称: {self._current_session.name if self._current_session else 'Unknown'}",
            f"时长: {sum(s.duration for s in segments):.1f}秒",
            f"片段数: {len(segments)}",
            "=" * 60,
            ""
        ]
        
        for i, segment in enumerate(segments, 1):
            speaker_label = "用户" if segment.speaker == "user" else "AI"
            timestamp = f"[{segment.start_time:.1f}s]"
            lines.append(f"{timestamp} {speaker_label}: {segment.text}")
            
            if "note" in segment.metadata:
                lines.append(f"  📝 笔记：{segment.metadata['note']}")
            
            lines.append("")
        
        return "\n".join(lines)
