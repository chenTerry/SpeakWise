"""
Web Application - Web 主应用程序模块

提供基于 FastAPI 的完整 Web 应用程序。
"""

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .config import WebConfig, WebConfigLoader
from .routes import scenes_router, dialogue_router, feedback_router


def create_app(config: Optional[WebConfig] = None) -> FastAPI:
    """
    创建 FastAPI 应用程序

    Args:
        config: Web 配置对象

    Returns:
        FastAPI 应用程序
    """
    # 加载配置
    if config is None:
        config = WebConfigLoader.load()

    # 创建应用
    app = FastAPI(
        title="AgentScope AI Interview",
        description="AI 模拟面试平台 - Web 界面",
        version="0.4.0",
        debug=config.debug,
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 设置模板
    template_dir = Path(config.template_path)
    if not template_dir.exists():
        template_dir.mkdir(parents=True, exist_ok=True)

    templates = Jinja2Templates(directory=str(template_dir))

    # 挂载静态文件
    static_dir = Path(config.static_path)
    if not static_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # 注册路由
    app.include_router(scenes_router)
    app.include_router(dialogue_router)
    app.include_router(feedback_router)

    # 存储配置和模板
    app.state.config = config
    app.state.templates = templates

    # 注册页面路由
    register_page_routes(app, templates)

    return app


def register_page_routes(app: FastAPI, templates: Jinja2Templates) -> None:
    """注册页面路由"""

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """首页"""
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "title": "AgentScope AI Interview",
                "version": "0.4.0",
            },
        )

    @app.get("/scenes", response_class=HTMLResponse)
    async def scenes_page(request: Request):
        """场景选择页"""
        return templates.TemplateResponse(
            "scene_selection.html",
            {
                "request": request,
                "title": "选择场景",
            },
        )

    @app.get("/dialogue/{session_id}", response_class=HTMLResponse)
    async def dialogue_page(request: Request, session_id: str):
        """对话页"""
        return templates.TemplateResponse(
            "dialogue.html",
            {
                "request": request,
                "title": "对话中",
                "session_id": session_id,
            },
        )

    @app.get("/feedback/{evaluation_id}", response_class=HTMLResponse)
    async def feedback_page(request: Request, evaluation_id: str):
        """反馈页"""
        return templates.TemplateResponse(
            "feedback.html",
            {
                "request": request,
                "title": "评估报告",
                "evaluation_id": evaluation_id,
            },
        )

    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy", "version": "0.4.0"}


class WebApplication:
    """
    Web 应用程序包装类

    提供更高级的应用程序管理功能。

    Example:
        >>> app = WebApplication()
        >>> app.run()
    """

    def __init__(self, config: Optional[WebConfig] = None):
        """
        初始化 Web 应用程序

        Args:
            config: Web 配置对象
        """
        self.config = config or WebConfigLoader.load()
        self.app = create_app(self.config)

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        reload: Optional[bool] = None,
    ) -> None:
        """
        运行 Web 服务器

        Args:
            host: 主机地址
            port: 端口
            reload: 自动重载
        """
        import uvicorn

        uvicorn.run(
            self.app,
            host=host or self.config.host,
            port=port or self.config.port,
            reload=reload if reload is not None else self.config.reload,
        )


# 创建全局应用实例
app = create_app()


if __name__ == "__main__":
    # 直接运行时启动服务器
    web_app = WebApplication()
    web_app.run()
