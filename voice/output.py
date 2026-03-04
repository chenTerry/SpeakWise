"""
Voice Output Module - Text-to-Speech Conversion

语音输出模块 - 文字转语音转换

This module provides voice output functionality with:
- Text-to-speech (TTS) conversion
- Voice selection and configuration
- Audio playback control
- Multiple TTS engine support

版本：v0.8.0
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import threading
import time
import queue

# Third-party imports
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None

try:
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    AudioSegment = None
    play = None

logger = logging.getLogger(__name__)


class TTSEngine(Enum):
    """Available Text-to-Speech engines."""
    PYTTSX3 = "pyttsx3"  # Offline TTS (system voices)
    GTTS = "gtts"  # Google Text-to-Speech (online)
    EDGE = "edge"  # Microsoft Edge TTS (online)
    MOCK = "mock"  # Mock engine for testing


class VoiceGender(Enum):
    """Voice gender options."""
    MALE = "male"
    FEMALE = "female"
    ANY = "any"


@dataclass
class VoiceInfo:
    """Information about a voice."""
    id: str
    name: str
    language: str
    gender: VoiceGender
    engine: TTSEngine
    sample_rate: int = 22050
    is_default: bool = False
    
    def __str__(self) -> str:
        return f"{self.name} ({self.language}, {self.gender.value})"


@dataclass
class VoiceOutputConfig:
    """Configuration for VoiceOutput."""
    engine: TTSEngine = TTSEngine.PYTTSX3
    language: str = "zh-CN"
    voice_id: Optional[str] = None
    rate: int = 200  # Words per minute
    volume: float = 1.0  # 0.0 to 1.0
    pitch: int = 50  # 0 to 100
    
    # Playback settings
    auto_play: bool = True
    output_device: Optional[int] = None
    
    # Cache settings
    enable_cache: bool = True
    cache_dir: str = "./cache/voice"
    
    # Fallback configuration
    enable_fallback: bool = True
    fallback_engines: List[TTSEngine] = field(default_factory=lambda: [
        TTSEngine.PYTTSX3,
        TTSEngine.GTTS,
        TTSEngine.MOCK
    ])


@dataclass
class SpeechResult:
    """Result of text-to-speech conversion."""
    success: bool
    audio_data: Optional[bytes] = None
    audio_file: Optional[str] = None
    duration: float = 0.0
    engine: str = ""
    voice_id: str = ""
    error_message: str = ""
    timestamp: float = field(default_factory=time.time)


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""
    
    @abstractmethod
    def synthesize(self, text: str, config: VoiceOutputConfig) -> SpeechResult:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            config: Configuration
            
        Returns:
            Speech result
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available."""
        pass
    
    @abstractmethod
    def get_voices(self, language: Optional[str] = None) -> List[VoiceInfo]:
        """
        Get available voices.
        
        Args:
            language: Filter by language code
            
        Returns:
            List of available voices
        """
        pass


class Pyttsx3Provider(TTSProvider):
    """pyttsx3 offline TTS provider."""
    
    def __init__(self):
        self._engine = None
        self._engine_lock = threading.Lock()
        self._voices: List[VoiceInfo] = []
        self._initialize()
    
    def _initialize(self):
        """Initialize pyttsx3 engine."""
        if not PYTTSX3_AVAILABLE:
            return
        
        try:
            self._engine = pyttsx3.init()
            self._load_voices()
            logger.info("pyttsx3 engine initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
            self._engine = None
    
    def _load_voices(self):
        """Load available voices."""
        if not self._engine:
            return
        
        try:
            voices = self._engine.getProperty('voices')
            self._voices = []
            
            for i, voice in enumerate(voices):
                # Determine gender from voice name
                gender = VoiceGender.ANY
                if hasattr(voice, 'name'):
                    name_lower = voice.name.lower()
                    if 'male' in name_lower or 'man' in name_lower:
                        gender = VoiceGender.MALE
                    elif 'female' in name_lower or 'woman' in name_lower:
                        gender = VoiceGender.FEMALE
                
                # Determine language
                language = "en-US"
                if hasattr(voice, 'languages') and voice.languages:
                    language = voice.languages[0]
                elif 'zh' in (voice.name if hasattr(voice, 'name') else ''):
                    language = "zh-CN"
                
                voice_info = VoiceInfo(
                    id=voice.id if hasattr(voice, 'id') else str(i),
                    name=voice.name if hasattr(voice, 'name') else f"Voice {i}",
                    language=language,
                    gender=gender,
                    engine=TTSEngine.PYTTSX3,
                    is_default=(i == 0)
                )
                self._voices.append(voice_info)
            
            logger.info(f"Loaded {len(self._voices)} pyttsx3 voices")
        except Exception as e:
            logger.warning(f"Failed to load voices: {e}")
    
    def synthesize(self, text: str, config: VoiceOutputConfig) -> SpeechResult:
        """Synthesize speech using pyttsx3."""
        if not self._engine:
            raise RuntimeError("pyttsx3 engine not initialized")
        
        start_time = time.time()
        
        with self._engine_lock:
            try:
                # Configure engine
                self._engine.setProperty('rate', config.rate)
                self._engine.setProperty('volume', config.volume)
                self._engine.setProperty('pitch', config.pitch)
                
                if config.voice_id:
                    self._engine.setProperty('voice', config.voice_id)
                
                # Create temporary file for audio data
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    temp_path = f.name
                
                # Save to file
                self._engine.save_to_file(text, temp_path)
                self._engine.runAndWait()
                
                # Read audio data
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up
                Path(temp_path).unlink(missing_ok=True)
                
                duration = time.time() - start_time
                
                # Get current voice
                current_voice = self._engine.getProperty('voice')
                
                return SpeechResult(
                    success=True,
                    audio_data=audio_data,
                    duration=duration,
                    engine=TTSEngine.PYTTSX3.value,
                    voice_id=current_voice
                )
                
            except Exception as e:
                logger.error(f"pyttsx3 synthesis error: {e}")
                return SpeechResult(
                    success=False,
                    error_message=str(e),
                    engine=TTSEngine.PYTTSX3.value
                )
    
    def is_available(self) -> bool:
        return PYTTSX3_AVAILABLE and self._engine is not None
    
    def get_voices(self, language: Optional[str] = None) -> List[VoiceInfo]:
        """Get available voices."""
        if language:
            return [v for v in self._voices if language.lower() in v.language.lower()]
        return self._voices


class GTTSProvider(TTSProvider):
    """Google Text-to-Speech provider."""
    
    def __init__(self):
        self._voices: List[VoiceInfo] = []
        self._load_voices()
    
    def _load_voices(self):
        """Load available gTTS voices (languages)."""
        if not GTTS_AVAILABLE:
            return
        
        # Common gTTS languages
        languages = [
            ("zh-CN", "Chinese (Simplified)", VoiceGender.FEMALE),
            ("zh-TW", "Chinese (Traditional)", VoiceGender.FEMALE),
            ("en-US", "English (US)", VoiceGender.FEMALE),
            ("en-GB", "English (UK)", VoiceGender.FEMALE),
            ("ja-JP", "Japanese", VoiceGender.FEMALE),
            ("ko-KR", "Korean", VoiceGender.FEMALE),
            ("fr-FR", "French", VoiceGender.FEMALE),
            ("de-DE", "German", VoiceGender.FEMALE),
            ("es-ES", "Spanish", VoiceGender.FEMALE),
        ]
        
        for lang_code, lang_name, gender in languages:
            self._voices.append(VoiceInfo(
                id=lang_code,
                name=lang_name,
                language=lang_code,
                gender=gender,
                engine=TTSEngine.GTTS,
                is_default=(lang_code == "zh-CN")
            ))
        
        logger.info(f"Loaded {len(self._voices)} gTTS voices")
    
    def synthesize(self, text: str, config: VoiceOutputConfig) -> SpeechResult:
        """Synthesize speech using gTTS."""
        if not GTTS_AVAILABLE:
            raise RuntimeError("gTTS not available")
        
        start_time = time.time()
        
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=config.language, slow=False)
            
            # Save to bytes
            import io
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_data = audio_buffer.read()
            
            duration = time.time() - start_time
            
            return SpeechResult(
                success=True,
                audio_data=audio_data,
                duration=duration,
                engine=TTSEngine.GTTS.value,
                voice_id=config.language
            )
            
        except Exception as e:
            logger.error(f"gTTS synthesis error: {e}")
            return SpeechResult(
                success=False,
                error_message=str(e),
                engine=TTSEngine.GTTS.value
            )
    
    def is_available(self) -> bool:
        return GTTS_AVAILABLE
    
    def get_voices(self, language: Optional[str] = None) -> List[VoiceInfo]:
        """Get available voices."""
        if language:
            return [v for v in self._voices if language.lower() in v.language.lower()]
        return self._voices


class MockTTSProvider(TTSProvider):
    """Mock TTS provider for testing."""
    
    def synthesize(self, text: str, config: VoiceOutputConfig) -> SpeechResult:
        """Return mock speech result."""
        logger.info(f"Mock TTS: '{text[:50]}...'")
        
        # Generate mock audio data (silent WAV)
        import wave
        import struct
        
        sample_rate = 22050
        duration = 1.0  # 1 second
        n_frames = int(sample_rate * duration)
        
        audio_buffer = io.BytesIO()
        with wave.open(audio_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            for _ in range(n_frames):
                wav_file.writeframes(struct.pack('<h', 0))  # Silent
        
        audio_buffer.seek(0)
        audio_data = audio_buffer.read()
        
        return SpeechResult(
            success=True,
            audio_data=audio_data,
            duration=duration,
            engine=TTSEngine.MOCK.value,
            voice_id="mock-voice"
        )
    
    def is_available(self) -> bool:
        return True
    
    def get_voices(self, language: Optional[str] = None) -> List[VoiceInfo]:
        """Return mock voice."""
        return [VoiceInfo(
            id="mock-voice",
            name="Mock Voice",
            language=language or "en-US",
            gender=VoiceGender.ANY,
            engine=TTSEngine.MOCK,
            is_default=True
        )]


class AudioPlayer:
    """Audio playback handler."""
    
    def __init__(self, config: VoiceOutputConfig):
        self.config = config
        self._is_playing = False
        self._playback_thread: Optional[threading.Thread] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
    
    def play(self, audio_data: bytes, sample_rate: int = 22050):
        """
        Play audio data.
        
        Args:
            audio_data: Raw audio data
            sample_rate: Sample rate in Hz
        """
        if not PYAUDIO_AVAILABLE:
            logger.warning("PyAudio not available, cannot play audio")
            return
        
        self._is_playing = True
        self._playback_thread = threading.Thread(
            target=self._playback_loop,
            args=(audio_data, sample_rate),
            daemon=True
        )
        self._playback_thread.start()
    
    def play_file(self, file_path: str):
        """
        Play audio file.
        
        Args:
            file_path: Path to audio file
        """
        if not PYDUB_AVAILABLE:
            logger.warning("pydub not available, cannot play audio file")
            return
        
        try:
            audio = AudioSegment.from_file(file_path)
            play(audio)
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")
    
    def stop(self):
        """Stop playback."""
        self._stop_event.set()
        self._is_playing = False
    
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._is_playing
    
    def _playback_loop(self, audio_data: bytes, sample_rate: int):
        """Background playback loop."""
        try:
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True,
                output_device_index=self.config.output_device
            )
            
            # Play audio data
            chunk_size = 1024
            for i in range(0, len(audio_data), chunk_size):
                if self._stop_event.is_set():
                    break
                
                chunk = audio_data[i:i + chunk_size]
                stream.write(chunk)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
        except Exception as e:
            logger.error(f"Playback error: {e}")
        finally:
            self._is_playing = False
            self._stop_event.clear()


class VoiceOutput:
    """
    Voice Output Handler - Text-to-Speech Conversion
    
    语音输出处理器 - 文字转语音转换
    
    Features:
    - Multiple TTS engines (pyttsx3, gTTS)
    - Voice selection and configuration
    - Audio playback control
    - Caching support
    
    功能:
    - 多种 TTS 引擎支持
    - 语音选择和配置
    - 音频播放控制
    - 缓存支持
    """
    
    def __init__(self, config: Optional[VoiceOutputConfig] = None):
        """
        Initialize VoiceOutput.
        
        Args:
            config: Voice output configuration
        """
        self.config = config or VoiceOutputConfig()
        
        # Initialize TTS providers
        self.providers: Dict[TTSEngine, TTSProvider] = {
            TTSEngine.PYTTSX3: Pyttsx3Provider(),
            TTSEngine.GTTS: GTTSProvider(),
            TTSEngine.MOCK: MockTTSProvider(),
        }
        
        # Audio player
        self.player = AudioPlayer(self.config)
        
        # Cache
        self._cache: Dict[str, bytes] = {}
        if self.config.enable_cache:
            Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"VoiceOutput initialized with engine={self.config.engine.value}, "
                   f"language={self.config.language}")
    
    def speak(self, text: str, block: bool = True) -> SpeechResult:
        """
        Convert text to speech and optionally play it.
        
        将文字转换为语音并可选播放
        
        Args:
            text: Text to synthesize
            block: Block until playback completes
            
        Returns:
            Speech result
        """
        logger.info(f"Synthesizing text: '{text[:50]}...'")
        
        # Check cache
        cache_key = f"{text}_{self.config.language}_{self.config.voice_id}"
        if self.config.enable_cache and cache_key in self._cache:
            logger.debug("Using cached audio")
            result = SpeechResult(
                success=True,
                audio_data=self._cache[cache_key],
                engine="cache"
            )
        else:
            # Synthesize with fallback
            result = self._synthesize_with_fallback(text)
            
            # Cache result
            if result.success and self.config.enable_cache:
                self._cache[cache_key] = result.audio_data
        
        # Play audio
        if result.success and self.config.auto_play:
            if result.audio_data:
                self.player.play(result.audio_data)
                if block:
                    # Wait for playback to complete
                    while self.player.is_playing():
                        time.sleep(0.1)
        
        return result
    
    def synthesize(self, text: str) -> SpeechResult:
        """
        Convert text to speech without playing.
        
        将文字转换为语音但不播放
        
        Args:
            text: Text to synthesize
            
        Returns:
            Speech result
        """
        return self._synthesize_with_fallback(text)
    
    def save_to_file(self, text: str, file_path: str) -> SpeechResult:
        """
        Synthesize and save to file.
        
        合成并保存到文件
        
        Args:
            text: Text to synthesize
            file_path: Output file path
            
        Returns:
            Speech result
        """
        result = self._synthesize_with_fallback(text)
        
        if result.success and result.audio_data:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(result.audio_data)
            result.audio_file = file_path
            logger.info(f"Audio saved to {file_path}")
        
        return result
    
    def play(self, audio_file: str):
        """
        Play audio file.
        
        播放音频文件
        
        Args:
            audio_file: Path to audio file
        """
        self.player.play_file(audio_file)
    
    def stop(self):
        """Stop current playback."""
        self.player.stop()
    
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self.player.is_playing()
    
    def get_voices(self, language: Optional[str] = None) -> List[VoiceInfo]:
        """
        Get available voices.
        
        获取可用语音列表
        
        Args:
            language: Filter by language code
            
        Returns:
            List of voices
        """
        provider = self.providers.get(self.config.engine)
        if provider:
            return provider.get_voices(language)
        return []
    
    def set_voice(self, voice_id: str):
        """Set voice by ID."""
        self.config.voice_id = voice_id
        logger.info(f"Voice changed to {voice_id}")
    
    def set_rate(self, rate: int):
        """Set speech rate (words per minute)."""
        self.config.rate = rate
        logger.info(f"Speech rate changed to {rate}")
    
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self.config.volume = max(0.0, min(1.0, volume))
        logger.info(f"Volume changed to {self.config.volume}")
    
    def set_language(self, language: str):
        """Set synthesis language."""
        self.config.language = language
        logger.info(f"Language changed to {language}")
    
    def _synthesize_with_fallback(self, text: str) -> SpeechResult:
        """
        Perform synthesis with fallback mechanism.
        
        执行带降级机制的合成
        """
        engines_to_try = [self.config.engine]
        
        # Add fallback engines
        if self.config.enable_fallback:
            for engine in self.config.fallback_engines:
                if engine not in engines_to_try:
                    engines_to_try.append(engine)
        
        last_error = None
        
        for engine in engines_to_try:
            try:
                provider = self.providers.get(engine)
                if not provider or not provider.is_available():
                    logger.warning(f"Engine {engine.value} not available")
                    continue
                
                logger.info(f"Trying TTS engine: {engine.value}")
                result = provider.synthesize(text, self.config)
                
                if result.success:
                    logger.info(f"Synthesis successful with {engine.value}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Engine {engine.value} failed: {e}")
                last_error = e
                continue
        
        # All engines failed
        error_msg = f"All TTS engines failed. Last error: {last_error}"
        logger.error(error_msg)
        return SpeechResult(
            success=False,
            error_message=error_msg
        )
    
    def clear_cache(self):
        """Clear audio cache."""
        self._cache.clear()
        if self.config.enable_cache:
            cache_path = Path(self.config.cache_dir)
            if cache_path.exists():
                for f in cache_path.glob("*.wav"):
                    f.unlink()
        logger.info("Cache cleared")
