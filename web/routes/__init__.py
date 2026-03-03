"""
Web Routes - Web 路由模块

提供 API 路由定义。
"""

from .scenes import router as scenes_router
from .dialogue import router as dialogue_router
from .feedback import router as feedback_router

__all__ = [
    "scenes_router",
    "dialogue_router",
    "feedback_router",
]
