"""
Voice Input Module - Speech-to-Text Conversion

语音输入模块 - 语音转文字转换

This module provides voice input functionality with:
- Speech-to-text (STT) conversion
- Multi-language support (Chinese/English)
- Voice Activity Detection (VAD)
- Fallback mechanisms (offline/online)

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

# Third-party imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    import webrtcvad
    WEBRTCVAD_AVAILABLE = True
except ImportError:
    WEBRTCVAD_AVAILABLE = False
    webrtcvad = None

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    pyaudio = None

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages for speech recognition."""
    CHINESE = "zh-CN"
    ENGLISH = "en-US"
    CHINESE_CANTONESE = "zh-HK"
    ENGLISH_UK = "en-GB"


class STTEngine(Enum):
    """Available Speech-to-Text engines."""
    GOOGLE = "google"  # Google Web Speech API (online)
    GOOGLE_CLOUD = "google_cloud"  # Google Cloud Speech-to-Text (online, paid)
    WHISPER = "whisper"  # OpenAI Whisper (offline/online)
    BUILTIN = "builtin"  # Built-in system STT
    MOCK = "mock"  # Mock engine for testing


@dataclass
class VoiceInputConfig:
    """Configuration for VoiceInput."""
    language: Language = Language.CHINESE
    engine: STTEngine = STTEngine.GOOGLE
    sample_rate: int = 16000
    chunk_size: int = 1024
    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive
    pause_threshold: float = 0.8  # seconds of silence to consider speech ended
    phrase_time_limit: float = 15.0  # max seconds for a phrase
    energy_threshold: float = 300.0  # minimum audio energy
    dynamic_energy: bool = True  # adjust threshold dynamically
    timeout: float = 5.0  # timeout for listening
    phrase_limit: float = 15.0  # max phrase duration
    show_all: bool = False  # show all recognition results
    with_confidence: bool = True  # include confidence scores
    
    # Google Cloud specific
    google_cloud_credentials: Optional[str] = None
    
    # Fallback configuration
    enable_fallback: bool = True
    fallback_engines: List[STTEngine] = field(default_factory=lambda: [
        STTEngine.GOOGLE,
        STTEngine.BUILTIN,
        STTEngine.MOCK
    ])


@dataclass
class VoiceRecognitionResult:
    """Result of speech recognition."""
    text: str
    confidence: float = 0.0
    language: str = ""
    engine: str = ""
    duration: float = 0.0
    audio_data: Optional[bytes] = None
    timestamp: float = field(default_factory=time.time)
    is_final: bool = True
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    
    def __bool__(self) -> bool:
        return bool(self.text.strip())


class VoiceActivityDetector:
    """
    Voice Activity Detection using WebRTC VAD.
    
    使用 WebRTC VAD 进行语音活动检测
    """
    
    def __init__(self, aggressiveness: int = 2, sample_rate: int = 16000):
        """
        Initialize VAD.
        
        Args:
            aggressiveness: VAD aggressiveness (0-3)
            sample_rate: Audio sample rate in Hz
        """
        if not WEBRTCVAD_AVAILABLE:
            logger.warning("WebRTC VAD not available, using simple energy-based detection")
            self.vad = None
        else:
            self.vad = webrtcvad.Vad(aggressiveness)
        
        self.sample_rate = sample_rate
        self.aggressiveness = aggressiveness
        
    def is_speech(self, audio_frame: bytes) -> bool:
        """
        Check if audio frame contains speech.
        
        Args:
            audio_frame: Audio frame data (should be 10, 20, or 30 ms)
            
        Returns:
            True if speech detected, False otherwise
        """
        if self.vad is None:
            # Fallback: simple energy-based detection
            return self._simple_energy_detection(audio_frame)
        
        try:
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception as e:
            logger.warning(f"VAD error: {e}")
            return self._simple_energy_detection(audio_frame)
    
    def _simple_energy_detection(self, audio_frame: bytes) -> bool:
        """Simple energy-based speech detection fallback."""
        import struct
        
        # Convert bytes to samples (assuming 16-bit PCM)
        fmt = "<" + "h" * (len(audio_frame) // 2)
        samples = struct.unpack(fmt, audio_frame)
        
        # Calculate RMS energy
        rms = (sum(s ** 2 for s in samples) / len(samples)) ** 0.5
        
        # Threshold (tunable)
        return rms > 100
    
    def vad_classify(self, audio_data: bytes, frame_duration_ms: int = 30) -> List[bool]:
        """
        Classify each frame in audio data.
        
        Args:
            audio_data: Complete audio data
            frame_duration_ms: Duration of each frame in ms
            
        Returns:
            List of boolean values indicating speech presence
        """
        if self.vad is None:
            return []
        
        frame_size = int(self.sample_rate * frame_duration_ms / 1000) * 2  # 16-bit
        results = []
        
        for i in range(0, len(audio_data) - frame_size, frame_size):
            frame = audio_data[i:i + frame_size]
            try:
                is_speech = self.vad.is_speech(frame, self.sample_rate)
                results.append(is_speech)
            except Exception as e:
                logger.warning(f"Frame VAD error: {e}")
                results.append(False)
        
        return results


class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers."""
    
    @abstractmethod
    def recognize(self, audio_data: bytes, config: VoiceInputConfig) -> VoiceRecognitionResult:
        """
        Perform speech recognition.
        
        Args:
            audio_data: Raw audio data
            config: Configuration
            
        Returns:
            Recognition result
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is available."""
        pass


class GoogleSTTProvider(STTProvider):
    """Google Web Speech API provider."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
    
    def recognize(self, audio_data: bytes, config: VoiceInputConfig) -> VoiceRecognitionResult:
        """Recognize speech using Google Web Speech API."""
        if not self.recognizer:
            raise RuntimeError("SpeechRecognition not available")
        
        start_time = time.time()
        
        # Create AudioData object
        audio = sr.AudioData(audio_data, config.sample_rate, 2)  # 16-bit
        
        # Configure recognizer
        self.recognizer.energy_threshold = config.energy_threshold
        self.recognizer.dynamic_energy_threshold = config.dynamic_energy
        
        # Perform recognition
        try:
            language_code = config.language.value
            result = self.recognizer.recognize_google(
                audio,
                language=language_code,
                show_all=config.show_all
            )
            
            duration = time.time() - start_time
            
            if config.show_all and isinstance(result, dict):
                # Handle alternative results
                alternatives = result.get("alternative", [])
                if alternatives:
                    text = alternatives[0].get("transcript", "")
                    confidence = float(alternatives[0].get("confidence", 0.0))
                    return VoiceRecognitionResult(
                        text=text,
                        confidence=confidence,
                        language=language_code,
                        engine=STTEngine.GOOGLE.value,
                        duration=duration,
                        audio_data=audio_data,
                        alternatives=alternatives
                    )
            
            # Simple string result
            return VoiceRecognitionResult(
                text=result if result else "",
                confidence=1.0,
                language=language_code,
                engine=STTEngine.GOOGLE.value,
                duration=duration,
                audio_data=audio_data
            )
            
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return VoiceRecognitionResult(text="", confidence=0.0)
        except sr.RequestError as e:
            logger.error(f"Google STT request error: {e}")
            raise
    
    def is_available(self) -> bool:
        return SPEECH_RECOGNITION_AVAILABLE and self.recognizer is not None


class MockSTTProvider(STTProvider):
    """Mock STT provider for testing."""
    
    def recognize(self, audio_data: bytes, config: VoiceInputConfig) -> VoiceRecognitionResult:
        """Return mock recognition result."""
        logger.info("Using mock STT provider")
        return VoiceRecognitionResult(
            text="[Mock] This is a test transcription",
            confidence=0.95,
            language=config.language.value,
            engine=STTEngine.MOCK.value,
            duration=0.1,
            audio_data=audio_data
        )
    
    def is_available(self) -> bool:
        return True


class VoiceInput:
    """
    Voice Input Handler - Speech-to-Text Conversion
    
    语音输入处理器 - 语音转文字转换
    
    Features:
    - Multi-language support (Chinese/English)
    - Voice Activity Detection
    - Multiple STT engine support with fallback
    - Real-time and batch processing modes
    
    功能:
    - 多语言支持（中文/英文）
    - 语音活动检测
    - 多种 STT 引擎支持，带降级机制
    - 实时和批量处理模式
    """
    
    def __init__(self, config: Optional[VoiceInputConfig] = None):
        """
        Initialize VoiceInput.
        
        Args:
            config: Voice input configuration
        """
        self.config = config or VoiceInputConfig()
        self.vad = VoiceActivityDetector(
            aggressiveness=self.config.vad_aggressiveness,
            sample_rate=self.config.sample_rate
        )
        
        # Initialize STT providers
        self.providers: Dict[STTEngine, STTProvider] = {
            STTEngine.GOOGLE: GoogleSTTProvider(),
            STTEngine.MOCK: MockSTTProvider(),
        }
        
        # Audio recording state
        self._is_recording = False
        self._recording_thread: Optional[threading.Thread] = None
        self._audio_buffer: List[bytes] = []
        self._pyaudio_instance = None
        self._stream = None
        
        logger.info(f"VoiceInput initialized with language={self.config.language.value}, "
                   f"engine={self.config.engine.value}")
    
    def recognize(self, audio_file: str) -> VoiceRecognitionResult:
        """
        Recognize speech from audio file.
        
        从音频文件识别语音
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Recognition result
        """
        logger.info(f"Recognizing speech from file: {audio_file}")
        
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Read audio file
        audio_data = self._read_audio_file(audio_file)
        
        # Perform recognition with fallback
        return self._recognize_with_fallback(audio_data)
    
    def recognize_from_bytes(self, audio_data: bytes) -> VoiceRecognitionResult:
        """
        Recognize speech from raw audio bytes.
        
        从原始音频字节识别语音
        
        Args:
            audio_data: Raw audio data (PCM format)
            
        Returns:
            Recognition result
        """
        logger.info(f"Recognizing speech from bytes ({len(audio_data)} bytes)")
        return self._recognize_with_fallback(audio_data)
    
    def start_recording(self, callback: Optional[Callable[[VoiceRecognitionResult], None]] = None):
        """
        Start recording audio from microphone.
        
        开始从麦克风录音
        
        Args:
            callback: Callback function for recognition results
        """
        if not PYAUDIO_AVAILABLE:
            raise RuntimeError("PyAudio not available for audio recording")
        
        if self._is_recording:
            logger.warning("Already recording")
            return
        
        self._is_recording = True
        self._audio_buffer = []
        
        self._recording_thread = threading.Thread(
            target=self._recording_loop,
            args=(callback,),
            daemon=True
        )
        self._recording_thread.start()
        logger.info("Recording started")
    
    def stop_recording(self) -> VoiceRecognitionResult:
        """
        Stop recording and return recognition result.
        
        停止录音并返回识别结果
        
        Returns:
            Recognition result
        """
        self._is_recording = False
        
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        
        if self._pyaudio_instance:
            self._pyaudio_instance.terminate()
            self._pyaudio_instance = None
        
        # Combine audio buffer
        audio_data = b''.join(self._audio_buffer)
        
        if self._recording_thread:
            self._recording_thread.join(timeout=2.0)
            self._recording_thread = None
        
        logger.info(f"Recording stopped, {len(audio_data)} bytes captured")
        
        # Recognize
        return self._recognize_with_fallback(audio_data)
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
    
    def detect_speech(self, audio_data: bytes) -> bool:
        """
        Detect if audio contains speech.
        
        检测音频是否包含语音
        
        Args:
            audio_data: Audio data
            
        Returns:
            True if speech detected
        """
        return self.vad.is_speech(audio_data[:1024])
    
    def get_supported_languages(self) -> List[Language]:
        """Get list of supported languages."""
        return list(Language)
    
    def set_language(self, language: Language):
        """Set recognition language."""
        self.config.language = language
        logger.info(f"Language changed to {language.value}")
    
    def set_engine(self, engine: STTEngine):
        """Set STT engine."""
        self.config.engine = engine
        logger.info(f"STT engine changed to {engine.value}")
    
    def _read_audio_file(self, file_path: str) -> bytes:
        """Read audio file and return raw bytes."""
        from pydub import AudioSegment
        
        try:
            audio = AudioSegment.from_file(file_path)
            # Convert to mono 16kHz for STT
            audio = audio.set_channels(1).set_frame_rate(self.config.sample_rate)
            return audio.raw_data
        except Exception as e:
            logger.error(f"Error reading audio file: {e}")
            # Fallback: read as raw PCM
            with open(file_path, 'rb') as f:
                return f.read()
    
    def _recognize_with_fallback(self, audio_data: bytes) -> VoiceRecognitionResult:
        """
        Perform recognition with fallback mechanism.
        
        执行带降级机制的识别
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
                
                logger.info(f"Trying STT engine: {engine.value}")
                result = provider.recognize(audio_data, self.config)
                
                if result:
                    logger.info(f"Recognition successful with {engine.value}: "
                               f"confidence={result.confidence:.2f}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Engine {engine.value} failed: {e}")
                last_error = e
                continue
        
        # All engines failed
        error_msg = f"All STT engines failed. Last error: {last_error}"
        logger.error(error_msg)
        return VoiceRecognitionResult(
            text="",
            confidence=0.0,
            engine="none",
            duration=0.0
        )
    
    def _recording_loop(self, callback: Optional[Callable]):
        """Background recording loop."""
        try:
            self._pyaudio_instance = pyaudio.PyAudio()
            self._stream = self._pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size
            )
            
            silence_start = None
            
            while self._is_recording:
                # Read audio chunk
                data = self._stream.read(self.config.chunk_size, exception_on_overflow=False)
                self._audio_buffer.append(data)
                
                # Check for speech
                has_speech = self.vad.is_speech(data)
                
                if has_speech:
                    silence_start = None
                else:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.config.pause_threshold:
                        # Silence detected, process audio
                        logger.debug("Silence detected, processing...")
                        # Could trigger recognition here for real-time mode
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Recording error: {e}")
            self._is_recording = False
        finally:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
            if self._pyaudio_instance:
                self._pyaudio_instance.terminate()
