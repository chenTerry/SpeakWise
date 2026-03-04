"""
Voice Module - Voice Support for AgentScope AI Interview

语音模块 - AgentScope AI Interview 语音支持

版本：v0.8.0

功能模块:
- VoiceInput: 语音输入 (STT) - 语音转文字
- VoiceOutput: 语音输出 (TTS) - 文字转语音
- VoiceQualityAssessor: 语音质量评估
- AudioProcessor: 音频处理
- VoiceReplay: 语音回放
- VoiceSettings: 语音设置管理

Dependencies:
- speechrecognition: Speech-to-Text
- pyttsx3/gTTS: Text-to-Speech
- pyaudio: Audio I/O
- pydub: Audio processing
- webrtcvad: Voice Activity Detection
- noisereduce: Noise reduction (optional)
"""

from .input import (
    VoiceInput,
    VoiceInputConfig,
    VoiceRecognitionResult,
    Language,
    STTEngine,
    VoiceActivityDetector,
)

from .output import (
    VoiceOutput,
    VoiceOutputConfig,
    SpeechResult,
    VoiceInfo,
    VoiceGender,
    TTSEngine,
)

from .quality import (
    VoiceQualityAssessor,
    VoiceQualityReport,
    QualityLevel,
    PaceLevel,
    PronunciationScore,
    PaceAnalysis,
    FillerAnalysis,
    RhythmAnalysis,
)

from .processor import (
    AudioProcessor,
    AudioFormat,
    AudioInfo,
    ProcessingResult,
    NoiseReductionConfig,
    NoiseReductionLevel,
    NormalizationConfig,
    ConversionConfig,
)

from .replay import (
    VoiceReplay,
    ReplayConfig,
    ReplaySession,
    ReplaySegment,
    PlaybackState,
    PlaybackPosition,
    ReplayMode,
)

from .settings import (
    VoiceSettingsManager,
    VoiceProfile,
    VoiceSettings,
    CLIVoiceSettingsPanel,
    create_web_settings_router,
)

__version__ = "0.8.0"

__all__ = [
    # Version
    "__version__",
    
    # Input (STT)
    "VoiceInput",
    "VoiceInputConfig",
    "VoiceRecognitionResult",
    "Language",
    "STTEngine",
    "VoiceActivityDetector",
    
    # Output (TTS)
    "VoiceOutput",
    "VoiceOutputConfig",
    "SpeechResult",
    "VoiceInfo",
    "VoiceGender",
    "TTSEngine",
    
    # Quality Assessment
    "VoiceQualityAssessor",
    "VoiceQualityReport",
    "QualityLevel",
    "PaceLevel",
    "PronunciationScore",
    "PaceAnalysis",
    "FillerAnalysis",
    "RhythmAnalysis",
    
    # Audio Processing
    "AudioProcessor",
    "AudioFormat",
    "AudioInfo",
    "ProcessingResult",
    "NoiseReductionConfig",
    "NoiseReductionLevel",
    "NormalizationConfig",
    "ConversionConfig",
    
    # Replay
    "VoiceReplay",
    "ReplayConfig",
    "ReplaySession",
    "ReplaySegment",
    "PlaybackState",
    "PlaybackPosition",
    "ReplayMode",
    
    # Settings
    "VoiceSettingsManager",
    "VoiceProfile",
    "VoiceSettings",
    "CLIVoiceSettingsPanel",
    "create_web_settings_router",
]
