"""
Voice Quality Assessment Module

语音质量评估模块

This module provides voice quality evaluation with:
- Pronunciation clarity assessment
- Speaking pace and rhythm analysis
- Filler word detection (um, ah, etc.)
- Voice improvement suggestions

版本：v0.8.0
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Quality assessment levels."""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 75-89
    FAIR = "fair"  # 60-74
    NEEDS_IMPROVEMENT = "needs_improvement"  # 40-59
    POOR = "poor"  # 0-39


class PaceLevel(Enum):
    """Speaking pace levels."""
    TOO_SLOW = "too_slow"
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"
    TOO_FAST = "too_fast"


@dataclass
class PronunciationScore:
    """Pronunciation assessment scores."""
    clarity: float = 0.0  # 0-100, how clear the pronunciation is
    accuracy: float = 0.0  # 0-100, how accurate compared to standard
    completeness: float = 0.0  # 0-100, how complete words are pronounced
    overall: float = 0.0  # Weighted average
    
    def calculate_overall(self):
        """Calculate overall pronunciation score."""
        self.overall = (self.clarity * 0.4 + 
                       self.accuracy * 0.4 + 
                       self.completeness * 0.2)
        return self.overall


@dataclass
class PaceAnalysis:
    """Speaking pace analysis results."""
    wpm: float = 0.0  # Words per minute
    level: PaceLevel = PaceLevel.NORMAL
    consistency: float = 0.0  # 0-100, how consistent the pace is
    pauses: List[Dict[str, Any]] = field(default_factory=list)
    avg_pause_duration: float = 0.0
    pause_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "wpm": self.wpm,
            "level": self.level.value,
            "consistency": self.consistency,
            "avg_pause_duration": self.avg_pause_duration,
            "pause_count": self.pause_count
        }


@dataclass
class FillerWord:
    """Detected filler word."""
    word: str
    position: int  # Position in text
    count: int = 1
    category: str = ""  # hesitation, uncertainty, thinking, etc.


@dataclass
class FillerAnalysis:
    """Filler word analysis results."""
    total_count: int = 0
    fillers_per_minute: float = 0.0
    filler_words: List[FillerWord] = field(default_factory=list)
    categories: Dict[str, int] = field(default_factory=dict)
    severity: QualityLevel = QualityLevel.EXCELLENT
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_count": self.total_count,
            "fillers_per_minute": self.fillers_per_minute,
            "categories": self.categories,
            "severity": self.severity.value,
            "common_fillers": [
                {"word": f.word, "count": f.count}
                for f in sorted(self.filler_words, key=lambda x: x.count, reverse=True)[:5]
            ]
        }


@dataclass
class RhythmAnalysis:
    """Speech rhythm analysis results."""
    regularity: float = 0.0  # 0-100, how regular the rhythm is
    stress_pattern: str = "unknown"  # Description of stress pattern
    intonation: float = 0.0  # 0-100, variety in pitch
    flow: float = 0.0  # 0-100, overall flow quality
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "regularity": self.regularity,
            "stress_pattern": self.stress_pattern,
            "intonation": self.intonation,
            "flow": self.flow
        }


@dataclass
class VoiceQualityReport:
    """Complete voice quality assessment report."""
    # Scores
    pronunciation: PronunciationScore = field(default_factory=PronunciationScore)
    pace: PaceAnalysis = field(default_factory=PaceAnalysis)
    fillers: FillerAnalysis = field(default_factory=FillerAnalysis)
    rhythm: RhythmAnalysis = field(default_factory=RhythmAnalysis)
    
    # Overall assessment
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.FAIR
    
    # Metadata
    duration: float = 0.0  # Speech duration in seconds
    word_count: int = 0
    language: str = "zh-CN"
    timestamp: float = field(default_factory=time.time)
    
    # Suggestions
    suggestions: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    
    def calculate_overall(self):
        """Calculate overall quality score."""
        weights = {
            "pronunciation": 0.35,
            "pace": 0.25,
            "fillers": 0.20,
            "rhythm": 0.20
        }
        
        pronunciation_score = self.pronunciation.overall
        pace_score = self._calculate_pace_score()
        filler_score = self._calculate_filler_score()
        rhythm_score = (self.rhythm.regularity + self.rhythm.flow) / 2
        
        self.overall_score = (
            pronunciation_score * weights["pronunciation"] +
            pace_score * weights["pace"] +
            filler_score * weights["fillers"] +
            rhythm_score * weights["rhythm"]
        )
        
        # Determine quality level
        if self.overall_score >= 90:
            self.quality_level = QualityLevel.EXCELLENT
        elif self.overall_score >= 75:
            self.quality_level = QualityLevel.GOOD
        elif self.overall_score >= 60:
            self.quality_level = QualityLevel.FAIR
        elif self.overall_score >= 40:
            self.quality_level = QualityLevel.NEEDS_IMPROVEMENT
        else:
            self.quality_level = QualityLevel.POOR
        
        return self.overall_score
    
    def _calculate_pace_score(self) -> float:
        """Calculate pace quality score (0-100)."""
        # Optimal WPM: 140-160 for Chinese, 130-150 for English
        optimal_wpm_min = 130
        optimal_wpm_max = 160
        
        wpm = self.pace.wpm
        
        if optimal_wpm_min <= wpm <= optimal_wpm_max:
            pace_score = 100
        elif wpm < optimal_wpm_min:
            diff = optimal_wpm_min - wpm
            pace_score = max(0, 100 - diff * 1.5)
        else:
            diff = wpm - optimal_wpm_max
            pace_score = max(0, 100 - diff * 1.5)
        
        # Factor in consistency
        consistency_bonus = self.pace.consistency * 0.2
        return min(100, pace_score + consistency_bonus)
    
    def _calculate_filler_score(self) -> float:
        """Calculate filler word score (0-100)."""
        fpm = self.fillers.fillers_per_minute
        
        # Excellent: < 2 per minute
        # Good: 2-5 per minute
        # Fair: 5-10 per minute
        # Needs improvement: 10-15 per minute
        # Poor: > 15 per minute
        
        if fpm <= 2:
            return 100
        elif fpm <= 5:
            return 80 - (fpm - 2) * 5
        elif fpm <= 10:
            return 65 - (fpm - 5) * 5
        elif fpm <= 15:
            return 40 - (fpm - 10) * 5
        else:
            return max(0, 15 - (fpm - 15) * 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "quality_level": self.quality_level.value,
            "duration": self.duration,
            "word_count": self.word_count,
            "language": self.language,
            "pronunciation": {
                "clarity": self.pronunciation.clarity,
                "accuracy": self.pronunciation.accuracy,
                "completeness": self.pronunciation.completeness,
                "overall": self.pronunciation.overall
            },
            "pace": self.pace.to_dict(),
            "fillers": self.fillers.to_dict(),
            "rhythm": self.rhythm.to_dict(),
            "suggestions": self.suggestions,
            "strengths": self.strengths
        }
    
    def generate_text_report(self) -> str:
        """Generate human-readable text report."""
        lines = [
            "=" * 60,
            "语音质量评估报告 (Voice Quality Assessment Report)",
            "=" * 60,
            "",
            f"总体评分 (Overall Score): {self.overall_score:.1f}/100",
            f"质量等级 (Quality Level): {self.quality_level.value.upper()}",
            "",
            f"时长 (Duration): {self.duration:.1f}秒",
            f"词数 (Word Count): {self.word_count}",
            f"语言 (Language): {self.language}",
            "",
            "-" * 60,
            "详细评分 (Detailed Scores)",
            "-" * 60,
            "",
            "1. 发音 (Pronunciation):",
            f"   - 清晰度 (Clarity): {self.pronunciation.clarity:.1f}/100",
            f"   - 准确性 (Accuracy): {self.pronunciation.accuracy:.1f}/100",
            f"   - 完整性 (Completeness): {self.pronunciation.completeness:.1f}/100",
            f"   - 综合 (Overall): {self.pronunciation.overall:.1f}/100",
            "",
            "2. 语速 (Speaking Pace):",
            f"   - 速度 (Speed): {self.pace.wpm:.1f} 词/分钟",
            f"   - 等级 (Level): {self.pace.level.value}",
            f"   - 一致性 (Consistency): {self.pace.consistency:.1f}/100",
            f"   - 停顿次数 (Pause Count): {self.pace.pause_count}",
            f"   - 平均停顿 (Avg Pause): {self.pace.avg_pause_duration:.2f}秒",
            "",
            "3. 填充词 (Filler Words):",
            f"   - 总数 (Total): {self.fillers.total_count}",
            f"   - 频率 (Per Minute): {self.fillers.fillers_per_minute:.1f}",
            f"   - 严重程度 (Severity): {self.fillers.severity.value}",
            "",
            "4. 节奏 (Rhythm):",
            f"   - 规律性 (Regularity): {self.rhythm.regularity:.1f}/100",
            f"   - 语调变化 (Intonation): {self.rhythm.intonation:.1f}/100",
            f"   - 流畅度 (Flow): {self.rhythm.flow:.1f}/100",
            "",
            "-" * 60,
            "优势 (Strengths)",
            "-" * 60,
        ]
        
        for i, strength in enumerate(self.strengths, 1):
            lines.append(f"  {i}. {strength}")
        
        if not self.strengths:
            lines.append("  暂无明显优势 (No obvious strengths identified)")
        
        lines.extend([
            "",
            "-" * 60,
            "改进建议 (Suggestions for Improvement)",
            "-" * 60,
        ])
        
        for i, suggestion in enumerate(self.suggestions, 1):
            lines.append(f"  {i}. {suggestion}")
        
        if not self.suggestions:
            lines.append("  表现优秀，无需特别改进 (Excellent performance, no specific improvements needed)")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Common filler words in Chinese and English
CHINESE_FILLERS = {
    "hesitation": ["嗯", "呃", "啊", "哦", "哎", "那个", "嗯..."],
    "uncertainty": ["可能", "也许", "大概", "差不多", "应该说"],
    "thinking": ["让我想想", "我想想", "怎么说呢", "这个嘛"],
    "repetition": ["就是", "然后", "然后然后", "还有"],
}

ENGLISH_FILLERS = {
    "hesitation": ["um", "uh", "er", "ah", "eh"],
    "uncertainty": ["like", "maybe", "perhaps", "sort of", "kind of"],
    "thinking": ["let me see", "you know", "I mean", "well"],
    "repetition": ["and then", "and", "so", "actually", "basically"],
}


class VoiceQualityAssessor:
    """
    Voice Quality Assessment Engine
    
    语音质量评估引擎
    
    Features:
    - Pronunciation clarity assessment
    - Speaking pace and rhythm analysis
    - Filler word detection
    - Personalized improvement suggestions
    
    功能:
    - 发音清晰度评估
    - 语速和节奏分析
    - 填充词检测
    - 个性化改进建议
    """
    
    def __init__(self, language: str = "zh-CN"):
        """
        Initialize VoiceQualityAssessor.
        
        Args:
            language: Language code (zh-CN or en-US)
        """
        self.language = language
        self.filler_patterns = self._load_filler_patterns()
        
        logger.info(f"VoiceQualityAssessor initialized for language: {language}")
    
    def _load_filler_patterns(self) -> Dict[str, List[str]]:
        """Load filler word patterns based on language."""
        if "zh" in self.language:
            fillers = {}
            for category, words in CHINESE_FILLERS.items():
                fillers[category] = words
            return fillers
        else:
            fillers = {}
            for category, words in ENGLISH_FILLERS.items():
                fillers[category] = words
            return fillers
    
    def assess(self, 
               text: str, 
               audio_data: Optional[bytes] = None,
               duration: float = 0.0) -> VoiceQualityReport:
        """
        Perform comprehensive voice quality assessment.
        
        执行全面的语音质量评估
        
        Args:
            text: Transcribed text
            audio_data: Optional audio data for advanced analysis
            duration: Speech duration in seconds
            
        Returns:
            Voice quality report
        """
        logger.info(f"Assessing voice quality for {len(text)} characters")
        
        report = VoiceQualityReport()
        report.language = self.language
        report.duration = duration
        report.word_count = self._count_words(text)
        
        # Analyze pronunciation (simulated without audio)
        report.pronunciation = self._assess_pronunciation(text, audio_data)
        
        # Analyze pace
        report.pace = self._assess_pace(text, duration)
        
        # Analyze filler words
        report.fillers = self._analyze_fillers(text, duration)
        
        # Analyze rhythm
        report.rhythm = self._assess_rhythm(text)
        
        # Calculate overall score
        report.calculate_overall()
        
        # Generate suggestions
        report.suggestions = self._generate_suggestions(report)
        report.strengths = self._identify_strengths(report)
        
        return report
    
    def _assess_pronunciation(self, text: str, 
                             audio_data: Optional[bytes]) -> PronunciationScore:
        """
        Assess pronunciation quality.
        
        Note: Full pronunciation assessment requires audio analysis.
        This implementation provides text-based estimation.
        """
        score = PronunciationScore()
        
        # Text-based heuristics
        if not text.strip():
            score.clarity = 0
            score.accuracy = 0
            score.completeness = 0
            score.calculate_overall()
            return score
        
        # Check for incomplete sentences
        sentence_count = len(re.split(r'[.!?。！？]', text))
        avg_sentence_length = len(text) / max(1, sentence_count)
        
        # Estimate completeness based on sentence structure
        if "zh" in self.language:
            # Chinese: average sentence 15-25 characters
            if 15 <= avg_sentence_length <= 25:
                score.completeness = 90
            elif 10 <= avg_sentence_length < 15 or 25 < avg_sentence_length <= 35:
                score.completeness = 75
            else:
                score.completeness = 60
        else:
            # English: average sentence 15-20 words
            word_count = len(text.split())
            avg_words_per_sentence = word_count / max(1, sentence_count)
            if 15 <= avg_words_per_sentence <= 20:
                score.completeness = 90
            else:
                score.completeness = 75
        
        # Estimate clarity based on text patterns
        # Check for stuttering patterns (repeated characters)
        stutter_pattern = r'(.)\1{2,}'
        stutter_matches = len(re.findall(stutter_pattern, text))
        if stutter_matches == 0:
            score.clarity = 90
        elif stutter_matches <= 2:
            score.clarity = 80
        else:
            score.clarity = max(50, 90 - stutter_matches * 10)
        
        # Estimate accuracy based on vocabulary complexity
        score.accuracy = min(95, 70 + len(set(text)) / max(1, len(text)) * 50)
        
        score.calculate_overall()
        return score
    
    def _assess_pace(self, text: str, duration: float) -> PaceAnalysis:
        """Assess speaking pace."""
        analysis = PaceAnalysis()
        
        if duration <= 0:
            duration = 1.0  # Prevent division by zero
        
        # Calculate WPM
        word_count = self._count_words(text)
        analysis.wpm = (word_count / duration) * 60
        
        # Determine pace level
        if analysis.wpm < 100:
            analysis.level = PaceLevel.TOO_SLOW
        elif analysis.wpm < 130:
            analysis.level = PaceLevel.SLOW
        elif analysis.wpm <= 160:
            analysis.level = PaceLevel.NORMAL
        elif analysis.wpm <= 180:
            analysis.level = PaceLevel.FAST
        else:
            analysis.level = PaceLevel.TOO_FAST
        
        # Analyze pauses (based on punctuation)
        pause_markers = re.findall(r'[,.!?.,:;:,\s]{2,}|[。！？，、；：\s]{2,}', text)
        analysis.pause_count = len(pause_markers)
        analysis.avg_pause_duration = duration / max(1, analysis.pause_count + 1) * 0.5
        
        # Estimate consistency
        sentences = re.split(r'[.!?。！？]', text)
        if len(sentences) > 1:
            lengths = [len(s) for s in sentences if s.strip()]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
                # Lower variance = higher consistency
                analysis.consistency = max(0, min(100, 100 - variance / 10))
        else:
            analysis.consistency = 75
        
        return analysis
    
    def _analyze_fillers(self, text: str, duration: float) -> FillerAnalysis:
        """Analyze filler words."""
        analysis = FillerAnalysis()
        
        text_lower = text.lower()
        
        # Search for filler words
        for category, fillers in self.filler_patterns.items():
            for filler in fillers:
                # Count occurrences
                pattern = re.escape(filler)
                matches = list(re.finditer(pattern, text_lower))
                
                for match in matches:
                    filler_word = FillerWord(
                        word=filler,
                        position=match.start(),
                        category=category
                    )
                    
                    # Check if already counted
                    existing = next(
                        (f for f in analysis.filler_words 
                         if f.word == filler and f.category == category),
                        None
                    )
                    
                    if existing:
                        existing.count += 1
                    else:
                        filler_word.count = 1
                        analysis.filler_words.append(filler_word)
                    
                    # Update category count
                    analysis.categories[category] = analysis.categories.get(category, 0) + 1
        
        # Calculate totals
        analysis.total_count = sum(f.count for f in analysis.filler_words)
        
        if duration > 0:
            analysis.fillers_per_minute = (analysis.total_count / duration) * 60
        
        # Determine severity
        fpm = analysis.fillers_per_minute
        if fpm <= 2:
            analysis.severity = QualityLevel.EXCELLENT
        elif fpm <= 5:
            analysis.severity = QualityLevel.GOOD
        elif fpm <= 10:
            analysis.severity = QualityLevel.FAIR
        elif fpm <= 15:
            analysis.severity = QualityLevel.NEEDS_IMPROVEMENT
        else:
            analysis.severity = QualityLevel.POOR
        
        return analysis
    
    def _assess_rhythm(self, text: str) -> RhythmAnalysis:
        """Assess speech rhythm."""
        analysis = RhythmAnalysis()
        
        # Analyze sentence length variation
        sentences = re.split(r'[.!?。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) > 1:
            lengths = [len(s) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            
            # Regularity: how consistent sentence lengths are
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            analysis.regularity = max(0, min(100, 100 - variance / 20))
            
            # Detect stress pattern (simplified)
            if "zh" in self.language:
                # Chinese: check for 4-character idioms
                idiom_pattern = r'[\u4e00-\u9fa5]{4}'
                idioms = re.findall(idiom_pattern, text)
                if len(idioms) > 3:
                    analysis.stress_pattern = "balanced (成语丰富)"
                else:
                    analysis.stress_pattern = "varied"
            else:
                # English: check for stressed syllables (simplified)
                analysis.stress_pattern = "mixed"
        else:
            analysis.regularity = 50
            analysis.stress_pattern = "single sentence"
        
        # Estimate intonation variety
        # Check for question marks, exclamation marks
        questions = text.count('?') + text.count('？')
        exclamations = text.count('!') + text.count('！')
        total_punctuation = questions + exclamations + text.count('.') + text.count('。')
        
        if total_punctuation > 0:
            analysis.intonation = min(100, (questions + exclamations) / total_punctuation * 100 + 50)
        else:
            analysis.intonation = 50
        
        # Overall flow
        analysis.flow = (analysis.regularity + analysis.intonation) / 2
        
        return analysis
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        if "zh" in self.language:
            # Chinese: count characters (excluding punctuation)
            chinese_chars = re.findall(r'[\u4e00-\u9fa5]', text)
            return len(chinese_chars)
        else:
            # English: count words
            words = re.findall(r'\b\w+\b', text)
            return len(words)
    
    def _generate_suggestions(self, report: VoiceQualityReport) -> List[str]:
        """Generate improvement suggestions based on assessment."""
        suggestions = []
        
        # Pronunciation suggestions
        if report.pronunciation.clarity < 70:
            suggestions.append(
                "发音清晰度有待提高：建议放慢语速，确保每个字音都发完整"
                if "zh" in self.language
                else "Improve pronunciation clarity: Slow down and enunciate each word clearly"
            )
        
        if report.pronunciation.accuracy < 70:
            suggestions.append(
                "发音准确性需要改进：可以多听标准发音并跟读练习"
                if "zh" in self.language
                else "Work on pronunciation accuracy: Listen to native speakers and practice repeating"
            )
        
        # Pace suggestions
        if report.pace.level == PaceLevel.TOO_FAST or report.pace.level == PaceLevel.FAST:
            suggestions.append(
                "语速过快：建议适当放慢语速，给听众更多消化时间"
                if "zh" in self.language
                else "Speaking too fast: Slow down to give your audience time to process"
            )
        elif report.pace.level == PaceLevel.TOO_SLOW or report.pace.level == PaceLevel.SLOW:
            suggestions.append(
                "语速过慢：可以适当加快语速，保持听众注意力"
                if "zh" in self.language
                else "Speaking too slowly: Increase your pace slightly to maintain audience engagement"
            )
        
        # Filler word suggestions
        if report.fillers.fillers_per_minute > 5:
            filler_types = list(report.fillers.categories.keys())
            if filler_types:
                suggestions.append(
                    f"减少填充词使用：检测到较多'{filler_types[0]}'等填充词，建议有意识地控制"
                    if "zh" in self.language
                    else f"Reduce filler words: Detected frequent '{filler_types[0]}', try to be more conscious"
                )
        
        # Rhythm suggestions
        if report.rhythm.regularity < 60:
            suggestions.append(
                "改善节奏感：尝试使用更有变化的句长，避免单调"
                if "zh" in self.language
                else "Improve rhythm: Use more varied sentence lengths to avoid monotony"
            )
        
        if report.rhythm.intonation < 60:
            suggestions.append(
                "增加语调变化：多使用疑问句和感叹句，让表达更生动"
                if "zh" in self.language
                else "Add more intonation variety: Use questions and exclamations to make speech more engaging"
            )
        
        return suggestions
    
    def _identify_strengths(self, report: VoiceQualityReport) -> List[str]:
        """Identify strengths based on assessment."""
        strengths = []
        
        if report.pronunciation.overall >= 80:
            strengths.append(
                "发音清晰准确，易于理解"
                if "zh" in self.language
                else "Clear and accurate pronunciation"
            )
        
        if report.pace.level == PaceLevel.NORMAL:
            strengths.append(
                "语速适中，便于听众接受"
                if "zh" in self.language
                else "Good speaking pace, easy to follow"
            )
        
        if report.fillers.fillers_per_minute <= 2:
            strengths.append(
                "语言表达流畅，填充词使用少"
                if "zh" in self.language
                else "Fluent speech with minimal filler words"
            )
        
        if report.rhythm.regularity >= 80:
            strengths.append(
                "节奏感好，句式变化丰富"
                if "zh" in self.language
                else "Good rhythm with varied sentence structure"
            )
        
        if report.rhythm.intonation >= 80:
            strengths.append(
                "语调生动，富有感染力"
                if "zh" in self.language
                else "Engaging intonation and expression"
            )
        
        return strengths
    
    def assess_from_file(self, 
                        audio_file: str,
                        transcription: Optional[str] = None) -> VoiceQualityReport:
        """
        Assess voice quality from audio file.
        
        从音频文件评估语音质量
        
        Args:
            audio_file: Path to audio file
            transcription: Optional pre-existing transcription
            
        Returns:
            Voice quality report
        """
        from .input import VoiceInput
        
        logger.info(f"Assessing voice quality from file: {audio_file}")
        
        # Read audio file
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_file)
            duration = len(audio) / 1000.0  # Convert to seconds
            audio_data = audio.raw_data
        except Exception as e:
            logger.error(f"Error reading audio file: {e}")
            duration = 0.0
            audio_data = None
        
        # Transcribe if not provided
        if not transcription:
            voice_input = VoiceInput()
            result = voice_input.recognize(audio_file)
            transcription = result.text
        
        # Perform assessment
        return self.assess(transcription, audio_data, duration)
