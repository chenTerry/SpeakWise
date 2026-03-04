"""
Voice Settings Module

语音设置模块

This module provides voice configuration interface with:
- CLI voice settings panel
- Web voice settings page
- Voice profile management
- Configuration persistence

版本：v0.8.0
"""

import logging
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
import time

logger = logging.getLogger(__name__)


@dataclass
class VoiceProfile:
    """Voice configuration profile."""
    id: str
    name: str
    created_at: float
    
    # Input settings (STT)
    input_language: str = "zh-CN"
    input_engine: str = "google"
    input_sample_rate: int = 16000
    vad_aggressiveness: int = 2
    
    # Output settings (TTS)
    output_engine: str = "pyttsx3"
    output_language: str = "zh-CN"
    output_voice_id: Optional[str] = None
    output_rate: int = 200
    output_volume: float = 1.0
    output_pitch: int = 50
    
    # Processing settings
    noise_reduction: bool = True
    noise_reduction_level: str = "moderate"
    auto_normalize: bool = False
    
    # Replay settings
    default_speed: float = 1.0
    auto_save_replays: bool = True
    
    # UI settings
    show_waveform: bool = True
    show_transcript: bool = True
    theme: str = "default"
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        return cls(**data)


@dataclass
class VoiceSettings:
    """Complete voice settings."""
    # Active profile
    active_profile_id: str = "default"
    
    # Global settings
    enable_voice_input: bool = True
    enable_voice_output: bool = True
    enable_quality_assessment: bool = True
    
    # Device settings
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    
    # Privacy settings
    local_processing_only: bool = False
    save_recordings: bool = True
    recording_retention_days: int = 30
    
    # Performance settings
    enable_caching: bool = True
    cache_size_mb: int = 500
    
    # Advanced settings
    debug_mode: bool = False
    log_audio_events: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceSettings':
        return cls(**data)


class VoiceSettingsManager:
    """
    Voice Settings Manager
    
    语音设置管理器
    
    Features:
    - Profile management (create, update, delete, switch)
    - Settings persistence
    - Validation and sanitization
    - Import/Export
    
    功能:
    - 配置文件管理
    - 设置持久化
    - 验证和清理
    - 导入导出
    """
    
    def __init__(self, config_dir: str = "./config"):
        """
        Initialize VoiceSettingsManager.
        
        Args:
            config_dir: Configuration directory
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_dir / "voice_settings.json"
        self.profiles_file = self.config_dir / "voice_profiles.json"
        
        # Load settings
        self.settings = self._load_settings()
        self.profiles = self._load_profiles()
        
        # Ensure default profile exists
        if "default" not in self.profiles:
            self._create_default_profile()
        
        logger.info(f"VoiceSettingsManager initialized: {self.config_dir}")
    
    def get_settings(self) -> VoiceSettings:
        """Get current settings."""
        return self.settings
    
    def update_settings(self, updates: Dict[str, Any]) -> VoiceSettings:
        """
        Update settings.
        
        更新设置
        
        Args:
            updates: Settings to update
            
        Returns:
            Updated settings
        """
        for key, value in updates.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        self._save_settings()
        logger.info(f"Updated settings: {list(updates.keys())}")
        return self.settings
    
    def get_active_profile(self) -> VoiceProfile:
        """Get active voice profile."""
        profile_id = self.settings.active_profile_id
        return self.profiles.get(profile_id, self.profiles.get("default"))
    
    def get_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Get profile by ID."""
        return self.profiles.get(profile_id)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "created_at": p.created_at,
                "is_active": p.id == self.settings.active_profile_id
            }
            for p in self.profiles.values()
        ]
    
    def create_profile(self, 
                      name: str,
                      base_profile_id: Optional[str] = None) -> VoiceProfile:
        """
        Create new voice profile.
        
        创建新的语音配置
        
        Args:
            name: Profile name
            base_profile_id: Optional base profile to copy from
            
        Returns:
            Created profile
        """
        profile_id = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copy from base or create default
        if base_profile_id and base_profile_id in self.profiles:
            base = self.profiles[base_profile_id]
            profile_dict = base.to_dict()
            profile_dict["id"] = profile_id
            profile_dict["name"] = name
            profile_dict["created_at"] = time.time()
            profile = VoiceProfile.from_dict(profile_dict)
        else:
            profile = VoiceProfile(
                id=profile_id,
                name=name,
                created_at=time.time()
            )
        
        self.profiles[profile_id] = profile
        self._save_profiles()
        
        logger.info(f"Created profile: {profile_id} - {name}")
        return profile
    
    def update_profile(self, 
                      profile_id: str,
                      updates: Dict[str, Any]) -> Optional[VoiceProfile]:
        """
        Update profile settings.
        
        更新配置文件设置
        
        Args:
            profile_id: Profile ID
            updates: Settings to update
            
        Returns:
            Updated profile
        """
        if profile_id not in self.profiles:
            logger.warning(f"Profile not found: {profile_id}")
            return None
        
        profile = self.profiles[profile_id]
        profile_dict = profile.to_dict()
        profile_dict.update(updates)
        
        # Ensure ID doesn't change
        profile_dict["id"] = profile_id
        
        self.profiles[profile_id] = VoiceProfile.from_dict(profile_dict)
        self._save_profiles()
        
        logger.info(f"Updated profile: {profile_id}")
        return self.profiles[profile_id]
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete profile.
        
        删除配置文件
        
        Args:
            profile_id: Profile ID
            
        Returns:
            True if deleted
        """
        if profile_id == "default":
            logger.warning("Cannot delete default profile")
            return False
        
        if profile_id not in self.profiles:
            return False
        
        del self.profiles[profile_id]
        self._save_profiles()
        
        # Switch to default if active profile was deleted
        if self.settings.active_profile_id == profile_id:
            self.settings.active_profile_id = "default"
            self._save_settings()
        
        logger.info(f"Deleted profile: {profile_id}")
        return True
    
    def switch_profile(self, profile_id: str) -> bool:
        """
        Switch active profile.
        
        切换活动配置
        
        Args:
            profile_id: Profile ID
            
        Returns:
            True if switched
        """
        if profile_id not in self.profiles:
            logger.warning(f"Profile not found: {profile_id}")
            return False
        
        self.settings.active_profile_id = profile_id
        self._save_settings()
        
        logger.info(f"Switched to profile: {profile_id}")
        return True
    
    def export_settings(self, output_path: str) -> bool:
        """
        Export settings to file.
        
        导出设置到文件
        
        Args:
            output_path: Output file path
            
        Returns:
            True if exported
        """
        try:
            output = Path(output_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "settings": self.settings.to_dict(),
                "profiles": {k: v.to_dict() for k, v in self.profiles.items()}
            }
            
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Exported settings to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from file.
        
        从文件导入设置
        
        Args:
            file_path: Settings file path
            
        Returns:
            True if imported
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if "settings" in data:
                self.settings = VoiceSettings.from_dict(data["settings"])
                self._save_settings()
            
            if "profiles" in data:
                for profile_id, profile_dict in data["profiles"].items():
                    self.profiles[profile_id] = VoiceProfile.from_dict(profile_dict)
                self._save_profiles()
            
            logger.info(f"Imported settings from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = VoiceSettings()
        self._create_default_profile()
        self._save_settings()
        self._save_profiles()
        logger.info("Settings reset to defaults")
    
    def validate_settings(self) -> List[str]:
        """
        Validate current settings.
        
        验证当前设置
        
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check profile exists
        if self.settings.active_profile_id not in self.profiles:
            warnings.append(f"Active profile not found: {self.settings.active_profile_id}")
        
        # Check profile settings
        profile = self.get_active_profile()
        if profile:
            if not 0.5 <= profile.default_speed <= 2.0:
                warnings.append(f"Invalid default speed: {profile.default_speed}")
            
            if not 0.0 <= profile.output_volume <= 1.0:
                warnings.append(f"Invalid output volume: {profile.output_volume}")
            
            if profile.vad_aggressiveness not in [0, 1, 2, 3]:
                warnings.append(f"Invalid VAD aggressiveness: {profile.vad_aggressiveness}")
        
        # Check global settings
        if self.settings.cache_size_mb < 10 or self.settings.cache_size_mb > 10000:
            warnings.append(f"Unusual cache size: {self.settings.cache_size_mb}MB")
        
        return warnings
    
    def _load_settings(self) -> VoiceSettings:
        """Load settings from file."""
        if not self.settings_file.exists():
            return VoiceSettings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return VoiceSettings.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
            return VoiceSettings()
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def _load_profiles(self) -> Dict[str, VoiceProfile]:
        """Load profiles from file."""
        if not self.profiles_file.exists():
            return {}
        
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            profiles = {}
            for profile_id, profile_dict in data.items():
                profiles[profile_id] = VoiceProfile.from_dict(profile_dict)
            return profiles
        except Exception as e:
            logger.warning(f"Failed to load profiles: {e}")
            return {}
    
    def _save_profiles(self):
        """Save profiles to file."""
        try:
            data = {k: v.to_dict() for k, v in self.profiles.items()}
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def _create_default_profile(self):
        """Create default voice profile."""
        default_profile = VoiceProfile(
            id="default",
            name="默认配置 (Default)",
            created_at=time.time(),
            input_language="zh-CN",
            input_engine="google",
            output_engine="pyttsx3",
            output_language="zh-CN",
            default_speed=1.0,
            theme="default"
        )
        self.profiles["default"] = default_profile
        self._save_profiles()


class CLIVoiceSettingsPanel:
    """
    CLI Voice Settings Panel
    
    CLI 语音设置面板
    
    Provides interactive CLI interface for voice settings management.
    """
    
    def __init__(self, manager: VoiceSettingsManager):
        """
        Initialize CLI panel.
        
        Args:
            manager: VoiceSettingsManager instance
        """
        self.manager = manager
        
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.form import Form
            self.console = Console()
            self.rich_available = True
        except ImportError:
            self.rich_available = False
            self.console = None
    
    def display(self):
        """Display voice settings panel."""
        if not self.rich_available:
            self._display_text()
            return
        
        settings = self.manager.get_settings()
        profile = self.manager.get_active_profile()
        
        # Create settings table
        table = Table(title="🎤 语音设置 (Voice Settings)")
        
        table.add_column("设置项 (Setting)", style="cyan")
        table.add_column("值 (Value)", style="green")
        table.add_column("说明 (Description)", style="dim")
        
        # Global settings
        table.add_row(
            "语音输入 (Voice Input)",
            "✅ 启用" if settings.enable_voice_input else "❌ 禁用",
            "启用/禁用语音输入功能"
        )
        table.add_row(
            "语音输出 (Voice Output)",
            "✅ 启用" if settings.enable_voice_output else "❌ 禁用",
            "启用/禁用语音输出功能"
        )
        table.add_row(
            "质量评估 (Quality Assessment)",
            "✅ 启用" if settings.enable_quality_assessment else "❌ 禁用",
            "启用/禁用语音质量评估"
        )
        
        # Profile settings
        table.add_row("", "", "")
        table.add_row(
            "活动配置 (Active Profile)",
            profile.name if profile else "N/A",
            f"ID: {profile.id if profile else 'N/A'}"
        )
        table.add_row(
            "输入语言 (Input Language)",
            profile.input_language if profile else "N/A",
            "语音识别语言"
        )
        table.add_row(
            "输出语言 (Output Language)",
            profile.output_language if profile else "N/A",
            "语音合成语言"
        )
        table.add_row(
            "播放速度 (Playback Speed)",
            f"{profile.default_speed if profile else 1.0}x",
            "默认回放速度"
        )
        
        self.console.print(table)
        
        # Quick actions
        actions_panel = Panel(
            "[1] 切换配置  [2] 创建配置  [3] 编辑配置  [4] 删除配置\n"
            "[5] 导入设置  [6] 导出设置  [7] 重置默认  [0] 返回",
            title="⚡ 快速操作 (Quick Actions)",
            border_style="blue"
        )
        self.console.print(actions_panel)
    
    def _display_text(self):
        """Display settings as text (fallback)."""
        settings = self.manager.get_settings()
        profile = self.manager.get_active_profile()
        
        print("\n" + "=" * 60)
        print("🎤 语音设置 (Voice Settings)")
        print("=" * 60)
        print(f"\n全局设置 (Global Settings):")
        print(f"  语音输入：{'启用' if settings.enable_voice_input else '禁用'}")
        print(f"  语音输出：{'启用' if settings.enable_voice_output else '禁用'}")
        print(f"  质量评估：{'启用' if settings.enable_quality_assessment else '禁用'}")
        
        if profile:
            print(f"\n当前配置 (Active Profile): {profile.name}")
            print(f"  输入语言：{profile.input_language}")
            print(f"  输出语言：{profile.output_language}")
            print(f"  播放速度：{profile.default_speed}x")
        
        print("\n" + "=" * 60)
    
    def interactive_menu(self):
        """Run interactive settings menu."""
        while True:
            self.display()
            
            if self.rich_available:
                choice = self.console.input("\n请选择操作 (Select action): ")
            else:
                choice = input("\n请选择操作 (Select action): ")
            
            if choice == "0":
                break
            elif choice == "1":
                self._switch_profile_menu()
            elif choice == "2":
                self._create_profile_menu()
            elif choice == "3":
                self._edit_profile_menu()
            elif choice == "4":
                self._delete_profile_menu()
            elif choice == "5":
                self._import_settings()
            elif choice == "6":
                self._export_settings()
            elif choice == "7":
                self._reset_defaults()
    
    def _switch_profile_menu(self):
        """Profile switching menu."""
        profiles = self.manager.list_profiles()
        
        print("\n可用配置 (Available Profiles):")
        for i, p in enumerate(profiles, 1):
            active = " (当前)" if p["is_active"] else ""
            print(f"  {i}. {p['name']}{active}")
        
        try:
            choice = int(input("选择配置 (Select profile): "))
            if 1 <= choice <= len(profiles):
                profile_id = profiles[choice - 1]["id"]
                self.manager.switch_profile(profile_id)
                print(f"✅ 已切换到：{profiles[choice - 1]['name']}")
        except ValueError:
            pass
    
    def _create_profile_menu(self):
        """Profile creation menu."""
        name = input("配置名称 (Profile name): ")
        if name:
            self.manager.create_profile(name)
            print(f"✅ 已创建配置：{name}")
    
    def _edit_profile_menu(self):
        """Profile editing menu."""
        profiles = self.manager.list_profiles()
        
        print("\n选择要编辑的配置:")
        for i, p in enumerate(profiles, 1):
            print(f"  {i}. {p['name']}")
        
        try:
            choice = int(input("选择配置："))
            if 1 <= choice <= len(profiles):
                profile_id = profiles[choice - 1]["id"]
                self._edit_profile(profile_id)
        except ValueError:
            pass
    
    def _edit_profile(self, profile_id: str):
        """Edit a profile."""
        profile = self.manager.get_profile(profile_id)
        if not profile:
            return
        
        print(f"\n编辑配置：{profile.name}")
        print(f"1. 输入语言：{profile.input_language}")
        print(f"2. 输出语言：{profile.output_language}")
        print(f"3. 播放速度：{profile.default_speed}")
        print(f"4. 降噪：{'启用' if profile.noise_reduction else '禁用'}")
        
        try:
            field_choice = int(input("选择要修改的字段 (0 返回): "))
            
            if field_choice == 1:
                new_val = input("新输入语言 (如 zh-CN, en-US): ")
                self.manager.update_profile(profile_id, {"input_language": new_val})
            elif field_choice == 2:
                new_val = input("新输出语言 (如 zh-CN, en-US): ")
                self.manager.update_profile(profile_id, {"output_language": new_val})
            elif field_choice == 3:
                new_val = float(input("新播放速度 (0.5-2.0): "))
                self.manager.update_profile(profile_id, {"default_speed": new_val})
            elif field_choice == 4:
                new_val = input("启用降噪？(y/n): ").lower() == 'y'
                self.manager.update_profile(profile_id, {"noise_reduction": new_val})
                
        except ValueError:
            pass
    
    def _delete_profile_menu(self):
        """Profile deletion menu."""
        profiles = self.manager.list_profiles()
        
        print("\n选择要删除的配置 (不能删除默认配置):")
        for i, p in enumerate(profiles, 1):
            if p["id"] != "default":
                print(f"  {i}. {p['name']}")
        
        try:
            choice = int(input("选择配置："))
            valid_profiles = [p for p in profiles if p["id"] != "default"]
            if 1 <= choice <= len(valid_profiles):
                profile_id = valid_profiles[choice - 1]["id"]
                if self.manager.delete_profile(profile_id):
                    print(f"✅ 已删除配置")
        except ValueError:
            pass
    
    def _import_settings(self):
        """Import settings."""
        path = input("导入文件路径：")
        if self.manager.import_settings(path):
            print("✅ 设置导入成功")
        else:
            print("❌ 设置导入失败")
    
    def _export_settings(self):
        """Export settings."""
        path = input("导出文件路径：")
        if self.manager.export_settings(path):
            print("✅ 设置导出成功")
        else:
            print("❌ 设置导出失败")
    
    def _reset_defaults(self):
        """Reset to defaults."""
        confirm = input("确认重置为默认设置？(y/n): ")
        if confirm.lower() == 'y':
            self.manager.reset_to_defaults()
            print("✅ 已重置为默认设置")


def create_web_settings_router(manager: VoiceSettingsManager):
    """
    Create FastAPI router for web settings interface.
    
    创建 Web 设置接口路由
    
    Args:
        manager: VoiceSettingsManager instance
        
    Returns:
        FastAPI APIRouter
    """
    try:
        from fastapi import APIRouter, HTTPException
        from pydantic import BaseModel
    except ImportError:
        logger.warning("FastAPI not available, cannot create web router")
        return None
    
    router = APIRouter(prefix="/api/voice/settings", tags=["voice-settings"])
    
    # Request/Response models
    class SettingsResponse(BaseModel):
        settings: Dict[str, Any]
        profile: Dict[str, Any]
    
    class ProfileResponse(BaseModel):
        id: str
        name: str
        is_active: bool
    
    class UpdateSettingsRequest(BaseModel):
        updates: Dict[str, Any]
    
    class CreateProfileRequest(BaseModel):
        name: str
        base_profile_id: Optional[str] = None
    
    # Routes
    @router.get("", response_model=SettingsResponse)
    async def get_settings():
        """Get current voice settings."""
        settings = manager.get_settings()
        profile = manager.get_active_profile()
        
        return SettingsResponse(
            settings=settings.to_dict(),
            profile=profile.to_dict() if profile else {}
        )
    
    @router.put("", response_model=SettingsResponse)
    async def update_settings(request: UpdateSettingsRequest):
        """Update voice settings."""
        settings = manager.update_settings(request.updates)
        profile = manager.get_active_profile()
        
        return SettingsResponse(
            settings=settings.to_dict(),
            profile=profile.to_dict() if profile else {}
        )
    
    @router.get("/profiles", response_model=List[ProfileResponse])
    async def list_profiles():
        """List all voice profiles."""
        return manager.list_profiles()
    
    @router.post("/profiles", response_model=ProfileResponse)
    async def create_profile(request: CreateProfileRequest):
        """Create new voice profile."""
        profile = manager.create_profile(request.name, request.base_profile_id)
        
        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            is_active=profile.id == manager.settings.active_profile_id
        )
    
    @router.put("/profiles/{profile_id}")
    async def update_profile(profile_id: str, request: UpdateSettingsRequest):
        """Update voice profile."""
        profile = manager.update_profile(profile_id, request.updates)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile.to_dict()
    
    @router.delete("/profiles/{profile_id}")
    async def delete_profile(profile_id: str):
        """Delete voice profile."""
        if not manager.delete_profile(profile_id):
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"success": True}
    
    @router.post("/profiles/{profile_id}/switch")
    async def switch_profile(profile_id: str):
        """Switch active voice profile."""
        if not manager.switch_profile(profile_id):
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"success": True}
    
    @router.get("/export")
    async def export_settings():
        """Export settings to JSON."""
        import tempfile
        from fastapi.responses import FileResponse
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            path = f.name
            manager.export_settings(path)
        
        return FileResponse(
            path,
            media_type='application/json',
            filename='voice_settings.json'
        )
    
    @router.post("/import")
    async def import_settings(file: bytes):
        """Import settings from JSON."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(file)
            path = f.name
        
        if manager.import_settings(path):
            return {"success": True}
        raise HTTPException(status_code=400, detail="Failed to import settings")
    
    @router.post("/reset")
    async def reset_defaults():
        """Reset settings to defaults."""
        manager.reset_to_defaults()
        return {"success": True}
    
    @router.get("/validate")
    async def validate_settings():
        """Validate current settings."""
        warnings = manager.validate_settings()
        return {"valid": len(warnings) == 0, "warnings": warnings}
    
    return router
