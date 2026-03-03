"""
Web Configuration - Web 配置模块

提供 Web 服务器的配置管理。

核心类:
- WebConfig: Web 配置数据类
- WebConfigLoader: 配置加载器
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class WebConfig:
    """
    Web 服务器配置

    Attributes:
        host: 服务器主机地址
        port: 服务器端口
        debug: 调试模式
        reload: 自动重载
        secret_key: 密钥
        cors_origins: CORS 允许的源
        database_url: 数据库 URL
        static_path: 静态文件路径
        template_path: 模板路径
        max_upload_size: 最大上传大小 (MB)
        session_timeout: 会话超时时间 (分钟)
        theme: 默认主题
        language: 默认语言
    """
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    reload: bool = True
    secret_key: str = "change-me-in-production"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    database_url: str = "sqlite:///./interview.db"
    static_path: str = "web/static"
    template_path: str = "web/templates"
    max_upload_size: int = 10  # MB
    session_timeout: int = 60  # minutes
    theme: str = "dark"
    language: str = "zh-CN"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "reload": self.reload,
            "secret_key": self.secret_key,
            "cors_origins": self.cors_origins,
            "database_url": self.database_url,
            "static_path": self.static_path,
            "template_path": self.template_path,
            "max_upload_size": self.max_upload_size,
            "session_timeout": self.session_timeout,
            "theme": self.theme,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebConfig":
        """从字典创建"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


class WebConfigLoader:
    """
    Web 配置加载器

    支持从多种来源加载配置：
    - YAML 文件
    - 环境变量
    - 字典

    Example:
        >>> config = WebConfigLoader.from_yaml("web_config.yaml")
        >>> config = WebConfigLoader.from_env()
        >>> config = WebConfigLoader.from_dict({...})
    """

    DEFAULT_CONFIG = {
        "host": "127.0.0.1",
        "port": 8000,
        "debug": False,
        "reload": True,
        "secret_key": "change-me-in-production",
        "cors_origins": ["*"],
        "database_url": "sqlite:///./interview.db",
        "static_path": "web/static",
        "template_path": "web/templates",
        "max_upload_size": 10,
        "session_timeout": 60,
        "theme": "dark",
        "language": "zh-CN",
    }

    @classmethod
    def from_yaml(cls, path: str) -> WebConfig:
        """
        从 YAML 文件加载配置

        Args:
            path: YAML 文件路径

        Returns:
            WebConfig 对象
        """
        config_path = Path(path)
        if not config_path.exists():
            return cls.from_dict(cls.DEFAULT_CONFIG)

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data.get("web", cls.DEFAULT_CONFIG))

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WebConfig:
        """
        从字典创建配置

        Args:
            data: 配置字典

        Returns:
            WebConfig 对象
        """
        # 合并默认配置
        merged = {**cls.DEFAULT_CONFIG, **data}
        return WebConfig.from_dict(merged)

    @classmethod
    def from_env(cls) -> WebConfig:
        """
        从环境变量加载配置

        支持的环境变量:
        - WEB_HOST
        - WEB_PORT
        - WEB_DEBUG
        - WEB_SECRET_KEY
        - WEB_DATABASE_URL
        - WEB_THEME

        Returns:
            WebConfig 对象
        """
        data = cls.DEFAULT_CONFIG.copy()

        # 映射环境变量
        env_mapping = {
            "WEB_HOST": "host",
            "WEB_PORT": "port",
            "WEB_DEBUG": "debug",
            "WEB_SECRET_KEY": "secret_key",
            "WEB_DATABASE_URL": "database_url",
            "WEB_THEME": "theme",
            "WEB_LANGUAGE": "language",
        }

        for env_var, config_key in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # 类型转换
                if config_key in ["port", "max_upload_size", "session_timeout"]:
                    data[config_key] = int(value)
                elif config_key in ["debug", "reload"]:
                    data[config_key] = value.lower() in ["true", "1", "yes"]
                else:
                    data[config_key] = value

        return WebConfig.from_dict(data)

    @classmethod
    def load(
        cls,
        yaml_path: Optional[str] = None,
        use_env: bool = True,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> WebConfig:
        """
        加载配置（支持多来源合并）

        优先级：overrides > env > yaml > default

        Args:
            yaml_path: YAML 配置文件路径
            use_env: 是否使用环境变量
            overrides: 覆盖配置

        Returns:
            WebConfig 对象
        """
        # 从 YAML 加载
        if yaml_path:
            config = cls.from_yaml(yaml_path)
        else:
            config = WebConfig(**cls.DEFAULT_CONFIG)

        # 从环境变量加载
        if use_env:
            env_config = cls.from_env()
            for key, value in env_config.to_dict().items():
                if value != cls.DEFAULT_CONFIG.get(key):
                    setattr(config, key, value)

        # 应用覆盖配置
        if overrides:
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        return config


def get_default_config() -> WebConfig:
    """获取默认配置"""
    return WebConfig(**WebConfigLoader.DEFAULT_CONFIG)


def load_config(
    yaml_path: Optional[str] = None,
    use_env: bool = True,
) -> WebConfig:
    """加载配置的便捷函数"""
    return WebConfigLoader.load(yaml_path=yaml_path, use_env=use_env)
