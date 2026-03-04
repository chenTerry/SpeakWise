#!/usr/bin/env python3
"""
Voice Demo - Voice Support Module Demonstration

语音支持模块演示

This demo showcases all voice module features:
- Speech-to-Text (STT)
- Text-to-Speech (TTS)
- Voice Quality Assessment
- Audio Processing
- Voice Replay
- Voice Settings Management

版本：v0.8.0
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from voice import (
    VoiceInput,
    VoiceOutput,
    VoiceQualityAssessor,
    AudioProcessor,
    VoiceReplay,
    VoiceSettingsManager,
    CLIVoiceSettingsPanel,
    Language,
    STTEngine,
    TTSEngine,
    QualityLevel,
    AudioFormat,
    NoiseReductionLevel,
)


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_voice_input():
    """Demonstrate voice input (STT) functionality."""
    print_header("🎤 语音输入演示 (Voice Input Demo)")
    
    # Create VoiceInput with configuration
    from voice.input import VoiceInputConfig
    
    config = VoiceInputConfig(
        language=Language.CHINESE,
        engine=STTEngine.GOOGLE,
        sample_rate=16000,
        vad_aggressiveness=2,
        enable_fallback=True
    )
    
    voice_input = VoiceInput(config)
    
    print("✅ VoiceInput 初始化成功")
    print(f"   - 语言 (Language): {config.language.value}")
    print(f"   - 引擎 (Engine): {config.engine.value}")
    print(f"   - 采样率 (Sample Rate): {config.sample_rate} Hz")
    print(f"   - VAD 灵敏度 (VAD Aggressiveness): {config.vad_aggressiveness}")
    
    # Show supported languages
    languages = voice_input.get_supported_languages()
    print(f"\n支持的语言 (Supported Languages):")
    for lang in languages:
        print(f"   - {lang.value}")
    
    # Demo: Recognize from file (if exists)
    test_audio = Path(__file__).parent / "test_audio.wav"
    if test_audio.exists():
        print(f"\n📂 从文件识别 (Recognize from file): {test_audio}")
        result = voice_input.recognize(str(test_audio))
        print(f"   - 识别文本 (Text): {result.text}")
        print(f"   - 置信度 (Confidence): {result.confidence:.2f}")
        print(f"   - 引擎 (Engine): {result.engine}")
        print(f"   - 耗时 (Duration): {result.duration:.2f}s")
    else:
        print(f"\n⚠️  测试音频文件不存在：{test_audio}")
        print(f"   跳过文件识别演示 (Skipping file recognition demo)")
    
    # Demo: Speech detection
    print(f"\n🔍 语音活动检测 (Voice Activity Detection):")
    mock_audio = b'\x00' * 1024  # Silent audio
    has_speech = voice_input.detect_speech(mock_audio)
    print(f"   - 静音检测 (Silence Detection): {'有语音' if has_speech else '无语音'}")
    
    return voice_input


def demo_voice_output():
    """Demonstrate voice output (TTS) functionality."""
    print_header("🔊 语音输出演示 (Voice Output Demo)")
    
    # Create VoiceOutput with configuration
    from voice.output import VoiceOutputConfig
    
    config = VoiceOutputConfig(
        engine=TTSEngine.PYTTSX3,
        language="zh-CN",
        rate=200,
        volume=1.0,
        auto_play=False,  # Don't auto-play in demo
        enable_cache=True
    )
    
    voice_output = VoiceOutput(config)
    
    print("✅ VoiceOutput 初始化成功")
    print(f"   - 引擎 (Engine): {config.engine.value}")
    print(f"   - 语言 (Language): {config.language}")
    print(f"   - 语速 (Rate): {config.rate} WPM")
    print(f"   - 音量 (Volume): {config.volume * 100:.0f}%")
    
    # Get available voices
    voices = voice_output.get_voices()
    print(f"\n可用语音 (Available Voices): {len(voices)}个")
    for i, voice in enumerate(voices[:5], 1):  # Show first 5
        print(f"   {i}. {voice.name} ({voice.language}, {voice.gender.value})")
    if len(voices) > 5:
        print(f"   ... 还有 {len(voices) - 5} 个语音")
    
    # Demo: Synthesize text
    test_texts = [
        "你好，欢迎使用语音支持模块。",
        "Hello, welcome to the voice support module.",
        "这是一个文字转语音的演示。",
    ]
    
    print(f"\n📝 文字转语音演示 (Text-to-Speech Demo):")
    for i, text in enumerate(test_texts, 1):
        print(f"\n   文本 {i}: {text}")
        result = voice_output.synthesize(text)
        
        if result.success:
            print(f"   ✅ 合成成功")
            print(f"      - 引擎 (Engine): {result.engine}")
            print(f"      - 音频大小 (Size): {len(result.audio_data) if result.audio_data else 0} bytes")
            print(f"      - 耗时 (Time): {result.duration:.2f}s")
            
            # Save to file
            output_file = Path(__file__).parent / "output" / f"tts_demo_{i}.wav"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            save_result = voice_output.save_to_file(text, str(output_file))
            if save_result.success:
                print(f"      - 已保存到：{output_file}")
        else:
            print(f"   ❌ 合成失败：{result.error_message}")
    
    return voice_output


def demo_voice_quality_assessment():
    """Demonstrate voice quality assessment."""
    print_header("📊 语音质量评估演示 (Voice Quality Assessment Demo)")
    
    assessor = VoiceQualityAssessor(language="zh-CN")
    
    # Test texts with different quality levels
    test_cases = [
        {
            "name": "优秀表现 (Excellent)",
            "text": "人工智能是当今科技发展的前沿领域，它正在深刻地改变着我们的生活方式和工作模式。",
            "duration": 5.0
        },
        {
            "name": "一般表现 (Fair)",
            "text": "嗯...那个...人工智能就是...呃...让电脑变得更聪明的技术吧。",
            "duration": 6.0
        },
        {
            "name": "需要改进 (Needs Improvement)",
            "text": "就是...那个...嗯...AI 嘛...啊...我也不知道怎么说...可能...大概...也许...",
            "duration": 8.0
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 测试案例：{case['name']}")
        print(f"   文本：{case['text']}")
        print(f"   时长：{case['duration']}秒")
        
        report = assessor.assess(
            text=case["text"],
            duration=case["duration"]
        )
        
        print(f"\n   📈 评估结果:")
        print(f"      - 总体评分 (Overall): {report.overall_score:.1f}/100")
        print(f"      - 质量等级 (Level): {report.quality_level.value.upper()}")
        print(f"      - 发音 (Pronunciation): {report.pronunciation.overall:.1f}/100")
        print(f"      - 语速 (Pace): {report.pace.wpm:.1f} WPM ({report.pace.level.value})")
        print(f"      - 填充词 (Fillers): {report.fillers.total_count}个 ({report.fillers.fillers_per_minute:.1f}/分钟)")
        print(f"      - 节奏 (Rhythm): {report.rhythm.flow:.1f}/100")
        
        if report.suggestions:
            print(f"\n   💡 改进建议:")
            for i, suggestion in enumerate(report.suggestions[:3], 1):
                print(f"      {i}. {suggestion}")
        
        if report.strengths:
            print(f"\n   ✨ 优势:")
            for i, strength in enumerate(report.strengths[:2], 1):
                print(f"      {i}. {strength}")
    
    return assessor


def demo_audio_processor():
    """Demonstrate audio processing functionality."""
    print_header("🔧 音频处理演示 (Audio Processor Demo)")
    
    processor = AudioProcessor()
    
    print("✅ AudioProcessor 初始化成功")
    print(f"   - 缓存目录 (Cache Dir): {processor.cache_dir}")
    print(f"   - pydub 可用：{processor._pydub_available}")
    print(f"   - noisereduce 可用：{processor._noisereduce_available}")
    
    # Demo: Check audio info (if test file exists)
    test_audio = Path(__file__).parent / "test_audio.wav"
    if test_audio.exists() and processor._pydub_available:
        print(f"\n📂 音频文件信息 (Audio File Info): {test_audio}")
        
        try:
            info = processor.get_audio_info(str(test_audio))
            print(f"   - 格式 (Format): {info.format.value}")
            print(f"   - 时长 (Duration): {info.duration:.2f}s")
            print(f"   - 采样率 (Sample Rate): {info.sample_rate} Hz")
            print(f"   - 声道 (Channels): {info.channels}")
            print(f"   - 位深 (Bit Depth): {info.bit_depth} bits")
            print(f"   - 文件大小 (Size): {info.file_size / 1024:.1f} KB")
            print(f"   - 比特率 (Bitrate): {info.bitrate / 1000:.1f} kbps")
        except Exception as e:
            print(f"   ⚠️ 无法读取音频文件：{e}")
    else:
        print(f"\n⚠️  测试音频文件不存在或 pydub 不可用")
    
    # Demo: Format conversion options
    print(f"\n🔄 支持的音频格式 (Supported Formats):")
    for fmt in AudioFormat:
        print(f"   - {fmt.value}")
    
    # Demo: Noise reduction levels
    print(f"\n🔇 降噪级别 (Noise Reduction Levels):")
    for level in NoiseReductionLevel:
        print(f"   - {level.value}")
    
    return processor


def demo_voice_replay():
    """Demonstrate voice replay functionality."""
    print_header("⏯️  语音回放演示 (Voice Replay Demo)")
    
    replay = VoiceReplay()
    
    print("✅ VoiceReplay 初始化成功")
    print(f"   - 存储目录 (Storage Dir): {replay.storage_dir}")
    
    # Demo: Create a session
    print(f"\n📼 创建回放会话 (Create Replay Session):")
    session_id = replay.start_session(
        name="面试模拟 Session 1",
        metadata={"scene": "interview", "candidate": "张三"}
    )
    print(f"   - 会话 ID: {session_id}")
    
    # Add segments
    segments_data = [
        ("user", "你好，我是来面试的。", 2.0),
        ("agent", "你好，欢迎参加今天的面试。请先做个自我介绍吧。", 4.0),
        ("user", "好的，我叫张三，毕业于北京大学计算机专业。", 3.5),
        ("agent", "很好，能介绍一下你的项目经验吗？", 3.0),
        ("user", "当然，我参与过多个 Web 开发项目...", 5.0),
    ]
    
    print(f"\n📝 添加会话片段 (Add Segments):")
    for speaker, text, duration in segments_data:
        segment = replay.add_segment(
            speaker=speaker,
            text=text,
            metadata={"estimated_duration": duration}
        )
        print(f"   - [{segment.start_time:.1f}s - {segment.end_time:.1f}s] "
              f"{speaker}: {text[:30]}...")
    
    # End session
    session = replay.end_session()
    print(f"\n✅ 会话结束 (Session Ended)")
    print(f"   - 总时长 (Total Duration): {session.duration:.1f}s")
    print(f"   - 片段数 (Segments): {len(session.segments)}")
    
    # Demo: Playback controls
    print(f"\n▶️  播放控制演示 (Playback Controls Demo):")
    print(f"   - 设置速度 (Set Speed): 1.5x")
    replay.set_speed(1.5)
    print(f"   - 当前速度 (Current Speed): {replay._speed}x")
    
    print(f"   - 跳转到片段 2 (Jump to Segment 2)")
    replay.jump_to(2)
    pos = replay.get_position()
    print(f"   - 当前位置 (Position): 片段 {pos.current_segment_index}, "
          f"时间 {pos.current_time:.1f}s")
    
    print(f"   - 下一个片段 (Next Segment)")
    replay.next_segment()
    print(f"   - 当前位置 (Position): 片段 {replay.get_position().current_segment_index}")
    
    # Demo: Generate transcript
    print(f"\n📄 生成文字记录 (Generate Transcript):")
    transcript = replay.generate_transcript(session_id)
    lines = transcript.split('\n')[:10]  # Show first 10 lines
    for line in lines:
        print(f"   {line}")
    print(f"   ...")
    
    # Demo: List sessions
    print(f"\n📋 会话列表 (Session List):")
    sessions = replay.list_sessions()
    for s in sessions:
        print(f"   - {s['name']} ({s['duration']:.1f}s, {s['segment_count']}个片段)")
    
    return replay


def demo_voice_settings():
    """Demonstrate voice settings management."""
    print_header("⚙️  语音设置演示 (Voice Settings Demo)")
    
    manager = VoiceSettingsManager()
    
    print("✅ VoiceSettingsManager 初始化成功")
    print(f"   - 配置目录 (Config Dir): {manager.config_dir}")
    
    # Get current settings
    settings = manager.get_settings()
    print(f"\n📋 当前设置 (Current Settings):")
    print(f"   - 语音输入 (Voice Input): {'启用' if settings.enable_voice_input else '禁用'}")
    print(f"   - 语音输出 (Voice Output): {'启用' if settings.enable_voice_output else '禁用'}")
    print(f"   - 质量评估 (Quality Assessment): {'启用' if settings.enable_quality_assessment else '禁用'}")
    print(f"   - 本地处理 (Local Processing): {'是' if settings.local_processing_only else '否'}")
    
    # Get active profile
    profile = manager.get_active_profile()
    print(f"\n🎯 活动配置 (Active Profile):")
    print(f"   - 名称 (Name): {profile.name}")
    print(f"   - 输入语言 (Input Language): {profile.input_language}")
    print(f"   - 输出语言 (Output Language): {profile.output_language}")
    print(f"   - 播放速度 (Playback Speed): {profile.default_speed}x")
    print(f"   - 降噪 (Noise Reduction): {'启用' if profile.noise_reduction else '禁用'}")
    
    # Demo: Create new profile
    print(f"\n➕ 创建新配置 (Create New Profile):")
    new_profile = manager.create_profile(
        name="面试练习配置",
        base_profile_id="default"
    )
    print(f"   - 已创建：{new_profile.name} (ID: {new_profile.id})")
    
    # Demo: Update profile
    print(f"\n✏️  更新配置 (Update Profile):")
    manager.update_profile(new_profile.id, {
        "input_language": "en-US",
        "default_speed": 1.2,
        "noise_reduction": True
    })
    updated = manager.get_profile(new_profile.id)
    print(f"   - 输入语言：{updated.input_language}")
    print(f"   - 播放速度：{updated.default_speed}x")
    print(f"   - 降噪：{'启用' if updated.noise_reduction else '禁用'}")
    
    # Demo: List profiles
    print(f"\n📋 配置列表 (Profile List):")
    profiles = manager.list_profiles()
    for p in profiles:
        active = " (当前)" if p["is_active"] else ""
        print(f"   - {p['name']}{active}")
    
    # Demo: Switch profile
    print(f"\n🔄 切换配置 (Switch Profile):")
    manager.switch_profile(new_profile.id)
    current = manager.get_active_profile()
    print(f"   - 已切换到：{current.name}")
    
    # Demo: Validate settings
    print(f"\n✅ 验证设置 (Validate Settings):")
    warnings = manager.validate_settings()
    if warnings:
        print(f"   ⚠️  发现 {len(warnings)} 个问题:")
        for w in warnings:
            print(f"      - {w}")
    else:
        print(f"   ✅ 设置验证通过")
    
    # Demo: Export settings
    print(f"\n💾 导出设置 (Export Settings):")
    export_path = Path(__file__).parent / "output" / "voice_settings.json"
    export_path.parent.mkdir(parents=True, exist_ok=True)
    if manager.export_settings(str(export_path)):
        print(f"   ✅ 已导出到：{export_path}")
    
    return manager


def run_all_demos():
    """Run all voice module demos."""
    print("\n" + "🎙️  " * 20)
    print(" AgentScope AI Interview - Voice Module Demo")
    print(" 语音支持模块演示 (v0.8.0)")
    print("🎙️  " * 20)
    
    start_time = time.time()
    
    try:
        # Run demos
        demo_voice_input()
        demo_voice_output()
        demo_voice_quality_assessment()
        demo_audio_processor()
        demo_voice_replay()
        demo_voice_settings()
        
        elapsed = time.time() - start_time
        
        print_header("✅ 演示完成 (Demo Complete)")
        print(f"   总耗时 (Total Time): {elapsed:.2f}秒")
        print(f"\n   所有语音模块功能演示完毕！")
        print(f"   All voice module features demonstrated successfully!")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误 (Error during demo): {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Voice Module Demo")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run interactive CLI settings panel"
    )
    parser.add_argument(
        "--demo",
        choices=["input", "output", "quality", "processor", "replay", "settings", "all"],
        default="all",
        help="Run specific demo"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        # Run interactive CLI panel
        manager = VoiceSettingsManager()
        panel = CLIVoiceSettingsPanel(manager)
        panel.interactive_menu()
    else:
        # Run demos
        if args.demo == "all":
            run_all_demos()
        elif args.demo == "input":
            demo_voice_input()
        elif args.demo == "output":
            demo_voice_output()
        elif args.demo == "quality":
            demo_voice_quality_assessment()
        elif args.demo == "processor":
            demo_audio_processor()
        elif args.demo == "replay":
            demo_voice_replay()
        elif args.demo == "settings":
            demo_voice_settings()


if __name__ == "__main__":
    main()
