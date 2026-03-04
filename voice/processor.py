"""
Audio Processing Module

音频处理模块

This module provides audio processing utilities with:
- Audio format conversion
- Noise reduction
- Volume normalization
- Audio file management

版本：v0.8.0
"""

import logging
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import time
import io

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"
    PCM = "pcm"
    WEBM = "webm"


class NoiseReductionLevel(Enum):
    """Noise reduction intensity levels."""
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXTREME = "extreme"


@dataclass
class AudioInfo:
    """Audio file information."""
    file_path: str
    format: AudioFormat
    duration: float  # seconds
    sample_rate: int  # Hz
    channels: int
    bit_depth: int  # bits
    file_size: int  # bytes
    bitrate: int  # bits per second
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "format": self.format.value,
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "file_size": self.file_size,
            "bitrate": self.bitrate
        }


@dataclass
class ProcessingResult:
    """Result of audio processing operation."""
    success: bool
    output_file: Optional[str] = None
    output_data: Optional[bytes] = None
    processing_time: float = 0.0
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NoiseReductionConfig:
    """Configuration for noise reduction."""
    level: NoiseReductionLevel = NoiseReductionLevel.MODERATE
    profile_samples: int = 10  # Number of samples for noise profiling
    reduction_amount: float = 0.75  # 0.0 to 1.0
    frequency_smoothing: float = 0.5  # 0.0 to 1.0
    residual_suppression: bool = True


@dataclass
class NormalizationConfig:
    """Configuration for volume normalization."""
    target_level: float = -20.0  # dBFS
    max_gain: float = 10.0  # Maximum gain in dB
    prevent_clipping: bool = True
    rms_window: float = 0.1  # seconds


@dataclass
class ConversionConfig:
    """Configuration for audio format conversion."""
    target_format: AudioFormat = AudioFormat.WAV
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_depth: Optional[int] = None
    bitrate: Optional[int] = None  # For lossy formats
    quality: str = "high"  # low/medium/high


class AudioProcessor:
    """
    Audio Processing Engine
    
    音频处理引擎
    
    Features:
    - Format conversion (WAV, MP3, FLAC, OGG, etc.)
    - Noise reduction using spectral gating
    - Volume normalization (RMS/peak)
    - Audio file management and caching
    
    功能:
    - 格式转换
    - 降噪处理
    - 音量标准化
    - 音频文件管理
    """
    
    def __init__(self, cache_dir: str = "./cache/audio"):
        """
        Initialize AudioProcessor.
        
        Args:
            cache_dir: Directory for cached processed files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._pydub_available = False
        self._noisereduce_available = False
        
        # Check dependencies
        try:
            from pydub import AudioSegment
            self._pydub_available = True
            logger.info("pydub available for audio processing")
        except ImportError:
            logger.warning("pydub not available, limited functionality")
        
        try:
            import noisereduce
            self._noisereduce_available = True
            logger.info("noisereduce available for noise reduction")
        except ImportError:
            logger.warning("noisereduce not available, using basic noise reduction")
    
    def get_audio_info(self, file_path: str) -> AudioInfo:
        """
        Get audio file information.
        
        获取音频文件信息
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Audio information
        """
        logger.info(f"Getting audio info for: {file_path}")
        
        if not self._pydub_available:
            raise RuntimeError("pydub not available")
        
        from pydub import AudioSegment
        
        try:
            audio = AudioSegment.from_file(file_path)
            
            path = Path(file_path)
            file_size = path.stat().st_size
            
            # Determine format
            format_str = path.suffix.lower().lstrip('.')
            try:
                audio_format = AudioFormat(format_str)
            except ValueError:
                audio_format = AudioFormat.WAV
            
            # Calculate bitrate
            duration = len(audio) / 1000.0
            bitrate = int(file_size * 8 / duration) if duration > 0 else 0
            
            return AudioInfo(
                file_path=file_path,
                format=audio_format,
                duration=duration,
                sample_rate=audio.frame_rate,
                channels=audio.channels,
                bit_depth=audio.sample_width * 8,
                file_size=file_size,
                bitrate=bitrate
            )
            
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            raise
    
    def convert(self, 
                file_path: str,
                config: ConversionConfig) -> ProcessingResult:
        """
        Convert audio file to different format.
        
        转换音频文件格式
        
        Args:
            file_path: Source audio file
            config: Conversion configuration
            
        Returns:
            Processing result
        """
        logger.info(f"Converting audio: {file_path} -> {config.target_format.value}")
        
        start_time = time.time()
        
        if not self._pydub_available:
            return ProcessingResult(
                success=False,
                error_message="pydub not available"
            )
        
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Apply conversions
            if config.sample_rate:
                audio = audio.set_frame_rate(config.sample_rate)
            
            if config.channels is not None:
                audio = audio.set_channels(config.channels)
            
            if config.bit_depth:
                # Convert bit depth
                if config.bit_depth == 16:
                    audio = audio.set_sample_width(2)
                elif config.bit_depth == 32:
                    audio = audio.set_sample_width(4)
                elif config.bit_depth == 8:
                    audio = audio.set_sample_width(1)
            
            # Generate output filename
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}_converted.{config.target_format.value}"
            output_path = self.cache_dir / output_filename
            
            # Export
            export_kwargs = {"format": config.target_format.value}
            
            if config.bitrate and config.target_format in [
                AudioFormat.MP3, AudioFormat.OGG, AudioFormat.M4A
            ]:
                export_kwargs["bitrate"] = f"{config.bitrate}k"
            
            audio.export(str(output_path), **export_kwargs)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                output_file=str(output_path),
                processing_time=processing_time,
                metadata={
                    "original_format": self.get_audio_info(file_path).format.value,
                    "target_format": config.target_format.value
                }
            )
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def reduce_noise(self,
                    file_path: str,
                    config: Optional[NoiseReductionConfig] = None) -> ProcessingResult:
        """
        Reduce background noise from audio.
        
        降低音频背景噪音
        
        Args:
            file_path: Source audio file
            config: Noise reduction configuration
            
        Returns:
            Processing result
        """
        logger.info(f"Reducing noise for: {file_path}")
        
        config = config or NoiseReductionConfig()
        start_time = time.time()
        
        if not self._pydub_available:
            return ProcessingResult(
                success=False,
                error_message="pydub not available"
            )
        
        try:
            from pydub import AudioSegment
            import numpy as np
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            if audio.channels > 1:
                samples = samples.reshape((-1, audio.channels))
            
            # Apply noise reduction
            if self._noisereduce_available:
                import noisereduce as nr
                
                # Convert noise reduction level to reduction amount
                reduction_map = {
                    NoiseReductionLevel.NONE: 0.0,
                    NoiseReductionLevel.LIGHT: 0.3,
                    NoiseReductionLevel.MODERATE: 0.6,
                    NoiseReductionLevel.AGGRESSIVE: 0.85,
                    NoiseReductionLevel.EXTREME: 0.95
                }
                
                reduction_amount = reduction_map.get(config.level, 0.6)
                
                # Perform noise reduction
                reduced_samples = nr.reduce_noise(
                    y=samples.astype(np.float32),
                    sr=audio.frame_rate,
                    prop_decrease=reduction_amount,
                    freq_smooth=config.frequency_smoothing,
                    stationary=config.residual_suppression
                )
                
                # Convert back to original dtype
                reduced_samples = reduced_samples.astype(samples.dtype)
            else:
                # Basic noise reduction using spectral gating (simplified)
                reduced_samples = self._basic_noise_reduction(samples, config)
            
            # Convert back to audio
            if audio.channels > 1:
                reduced_samples = reduced_samples.flatten()
            
            reduced_audio = AudioSegment(
                reduced_samples.tobytes(),
                frame_rate=audio.frame_rate,
                sample_width=audio.sample_width,
                channels=audio.channels
            )
            
            # Generate output filename
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}_noise_reduced.wav"
            output_path = self.cache_dir / output_filename
            
            # Export
            reduced_audio.export(str(output_path), format="wav")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                output_file=str(output_path),
                processing_time=processing_time,
                metadata={
                    "noise_reduction_level": config.level.value,
                    "original_duration": len(audio) / 1000.0,
                    "processed_duration": len(reduced_audio) / 1000.0
                }
            )
            
        except Exception as e:
            logger.error(f"Noise reduction error: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def normalize_volume(self,
                        file_path: str,
                        config: Optional[NormalizationConfig] = None) -> ProcessingResult:
        """
        Normalize audio volume.
        
        标准化音频音量
        
        Args:
            file_path: Source audio file
            config: Normalization configuration
            
        Returns:
            Processing result
        """
        logger.info(f"Normalizing volume for: {file_path}")
        
        config = config or NormalizationConfig()
        start_time = time.time()
        
        if not self._pydub_available:
            return ProcessingResult(
                success=False,
                error_message="pydub not available"
            )
        
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Get current RMS level
            rms = audio.rms
            if rms == 0:
                return ProcessingResult(
                    success=False,
                    error_message="Audio is silent"
                )
            
            # Calculate target RMS from dBFS
            import math
            target_rms = int(32767 * (10 ** (config.target_level / 20)))
            
            # Calculate required gain
            gain_ratio = target_rms / rms
            gain_db = 20 * math.log10(gain_ratio)
            
            # Apply max gain limit
            if gain_db > config.max_gain:
                gain_db = config.max_gain
            elif gain_db < -config.max_gain:
                gain_db = -config.max_gain
            
            # Apply gain
            normalized_audio = audio + gain_db
            
            # Prevent clipping if enabled
            if config.prevent_clipping and normalized_audio.max_dBFS > 0:
                normalized_audio = normalized_audio - normalized_audio.max_dBFS
            
            # Generate output filename
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}_normalized.wav"
            output_path = self.cache_dir / output_filename
            
            # Export
            normalized_audio.export(str(output_path), format="wav")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                output_file=str(output_path),
                processing_time=processing_time,
                metadata={
                    "original_rms": rms,
                    "target_rms": target_rms,
                    "applied_gain_db": gain_db,
                    "original_dbfs": audio.dBFS,
                    "normalized_dbfs": normalized_audio.dBFS
                }
            )
            
        except Exception as e:
            logger.error(f"Volume normalization error: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def trim(self,
            file_path: str,
            start: float,
            end: float) -> ProcessingResult:
        """
        Trim audio file.
        
        裁剪音频文件
        
        Args:
            file_path: Source audio file
            start: Start time in seconds
            end: End time in seconds
            
        Returns:
            Processing result
        """
        logger.info(f"Trimming audio: {file_path} [{start}s - {end}s]")
        
        start_time = time.time()
        
        if not self._pydub_available:
            return ProcessingResult(
                success=False,
                error_message="pydub not available"
            )
        
        try:
            from pydub import AudioSegment
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Convert to milliseconds
            start_ms = start * 1000
            end_ms = end * 1000
            
            # Trim
            trimmed_audio = audio[start_ms:end_ms]
            
            # Generate output filename
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}_trimmed.wav"
            output_path = self.cache_dir / output_filename
            
            # Export
            trimmed_audio.export(str(output_path), format="wav")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                output_file=str(output_path),
                processing_time=processing_time,
                metadata={
                    "original_duration": len(audio) / 1000.0,
                    "trimmed_duration": len(trimmed_audio) / 1000.0,
                    "start": start,
                    "end": end
                }
            )
            
        except Exception as e:
            logger.error(f"Trimming error: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def concatenate(self,
                   file_paths: List[str],
                   output_name: str = "concatenated") -> ProcessingResult:
        """
        Concatenate multiple audio files.
        
        拼接多个音频文件
        
        Args:
            file_paths: List of audio file paths
            output_name: Output filename
            
        Returns:
            Processing result
        """
        logger.info(f"Concatenating {len(file_paths)} audio files")
        
        start_time = time.time()
        
        if not self._pydub_available:
            return ProcessingResult(
                success=False,
                error_message="pydub not available"
            )
        
        try:
            from pydub import AudioSegment
            
            # Load and concatenate
            result = None
            for file_path in file_paths:
                audio = AudioSegment.from_file(file_path)
                if result is None:
                    result = audio
                else:
                    result = result + audio
            
            # Generate output filename
            output_filename = f"{output_name}.wav"
            output_path = self.cache_dir / output_filename
            
            # Export
            result.export(str(output_path), format="wav")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                output_file=str(output_path),
                processing_time=processing_time,
                metadata={
                    "input_files": len(file_paths),
                    "total_duration": len(result) / 1000.0
                }
            )
            
        except Exception as e:
            logger.error(f"Concatenation error: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def change_speed(self,
                    file_path: str,
                    speed_factor: float) -> ProcessingResult:
        """
        Change audio playback speed.
        
        改变音频播放速度
        
        Args:
            file_path: Source audio file
            speed_factor: Speed multiplier (0.5 = half speed, 2.0 = double speed)
            
        Returns:
            Processing result
        """
        logger.info(f"Changing speed: {file_path} (x{speed_factor})")
        
        start_time = time.time()
        
        if not self._pydub_available:
            return ProcessingResult(
                success=False,
                error_message="pydub not available"
            )
        
        try:
            from pydub import AudioSegment
            from pydub.effects import speedup
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Apply speed change
            if speed_factor > 1.0:
                # Speed up
                changed_audio = speedup(audio, speed_factor, chunk=150)
            elif speed_factor < 1.0:
                # Slow down (by reducing frame rate)
                new_frame_rate = int(audio.frame_rate * speed_factor)
                changed_audio = audio._spawn(
                    audio.raw_data,
                    overrides={'frame_rate': new_frame_rate}
                )
                # Export at original frame rate
                changed_audio = changed_audio.set_frame_rate(audio.frame_rate)
            else:
                # speed_factor == 1.0, no change
                changed_audio = audio
            
            # Generate output filename
            input_path = Path(file_path)
            output_filename = f"{input_path.stem}_speed_{speed_factor:.2f}x.wav"
            output_path = self.cache_dir / output_filename
            
            # Export
            changed_audio.export(str(output_path), format="wav")
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                output_file=str(output_path),
                processing_time=processing_time,
                metadata={
                    "speed_factor": speed_factor,
                    "original_duration": len(audio) / 1000.0,
                    "changed_duration": len(changed_audio) / 1000.0
                }
            )
            
        except Exception as e:
            logger.error(f"Speed change error: {e}")
            return ProcessingResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def split_silence(self,
                     file_path: str,
                     silence_threshold: float = -40.0,
                     min_silence_duration: float = 0.5) -> List[ProcessingResult]:
        """
        Split audio file at silent sections.
        
        在静音处分割音频文件
        
        Args:
            file_path: Source audio file
            silence_threshold: Silence threshold in dBFS
            min_silence_duration: Minimum silence duration in seconds
            
        Returns:
            List of processing results for each segment
        """
        logger.info(f"Splitting audio at silence: {file_path}")
        
        if not self._pydub_available:
            return []
        
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Split on silence
            segments = split_on_silence(
                audio,
                min_silence_len=int(min_silence_duration * 1000),
                silence_thresh=silence_threshold,
                keep_silence=100  # Keep 100ms of silence
            )
            
            results = []
            for i, segment in enumerate(segments):
                output_filename = f"{Path(file_path).stem}_segment_{i:03d}.wav"
                output_path = self.cache_dir / output_filename
                
                segment.export(str(output_path), format="wav")
                
                results.append(ProcessingResult(
                    success=True,
                    output_file=str(output_path),
                    metadata={
                        "segment_index": i,
                        "duration": len(segment) / 1000.0
                    }
                ))
            
            logger.info(f"Split into {len(results)} segments")
            return results
            
        except Exception as e:
            logger.error(f"Splitting error: {e}")
            return []
    
    def clear_cache(self, older_than: Optional[float] = None):
        """
        Clear cached processed files.
        
        清理缓存的处理文件
        
        Args:
            older_than: Only clear files older than this timestamp
        """
        if not self.cache_dir.exists():
            return
        
        count = 0
        for file_path in self.cache_dir.glob("*"):
            if older_than:
                mtime = file_path.stat().st_mtime
                if mtime >= older_than:
                    continue
            
            file_path.unlink()
            count += 1
        
        logger.info(f"Cleared {count} cached files")
    
    def _basic_noise_reduction(self, 
                               samples: 'np.ndarray',
                               config: NoiseReductionConfig) -> 'np.ndarray':
        """
        Basic noise reduction using spectral gating.
        
        Fallback when noisereduce library is not available.
        """
        import numpy as np
        
        # Simple spectral gating
        # This is a simplified version
        
        # Apply FFT
        fft = np.fft.rfft(samples, axis=0)
        
        # Calculate magnitude
        magnitude = np.abs(fft)
        
        # Estimate noise floor (use lowest 10% of magnitudes)
        noise_floor = np.percentile(magnitude, 10, axis=0)
        
        # Apply gain reduction based on noise floor
        gain = np.maximum(0, 1 - (noise_floor / (magnitude + 1e-10)) * config.reduction_amount)
        
        # Apply gain
        fft = fft * gain
        
        # Inverse FFT
        reduced = np.fft.irfft(fft, axis=0)
        
        return reduced.astype(samples.dtype)
    
    def generate_file_hash(self, file_path: str) -> str:
        """Generate hash for audio file (for caching)."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            hasher.update(buf)
        return hasher.hexdigest()
