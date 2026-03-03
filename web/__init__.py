"""
Web Module - Web 应用程序模块 (v0.4)

提供基于 FastAPI 的 Web 界面，包括：
- RESTful API 接口
- Jinja2 模板渲染
- 静态资源服务
- WebSocket 实时通信

版本：v0.4.0
"""

from .app import create_app, WebApplication
from .config import WebConfig, WebConfigLoader

__version__ = "0.4.0"

__all__ = [
    # Version
    "__version__",
    # Application
    "create_app",
    "WebApplication",
    # Config
    "WebConfig",
    "WebConfigLoader",
]
