"""
Web Dashboard Router

Web 仪表盘路由：
- FastAPI 路由定义
- 仪表盘页面
- API 接口

Design Principles:
- RESTful API 设计
- 前后端分离
- 异步处理
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from users.service import UserService
from users.database import Database
from users.models import SessionCreate
from progress.tracker import ProgressTracker
from progress.history import SessionHistoryManager
from visualization.radar import DimensionRadarChart
from visualization.trends import ProgressTrendChart


# =============================================================================
# Request/Response Models
# =============================================================================

class DashboardSummary(BaseModel):
    """仪表盘摘要"""
    user_id: int
    username: str
    total_sessions: int
    completed_sessions: int
    avg_score: float
    streak_days: int
    last_session_at: Optional[datetime]


class SessionListItem(BaseModel):
    """会话列表项"""
    id: int
    scene_type: str
    title: Optional[str]
    status: str
    started_at: datetime
    duration_seconds: Optional[int]
    score: Optional[float]


class ProgressData(BaseModel):
    """进度数据"""
    total_sessions: int
    completed_sessions: int
    total_duration_seconds: int
    avg_score: float
    dimension_scores: Dict[str, float]
    improvement_rate: float
    streak_days: int


# =============================================================================
# Router
# =============================================================================

def create_dashboard_router(db: Database) -> APIRouter:
    """
    创建仪表盘路由
    
    Args:
        db: 数据库实例
        
    Returns:
        FastAPI Router
    """
    router = APIRouter(prefix="/dashboard", tags=["dashboard"])
    
    user_service = UserService(db)
    
    # =========================================================================
    # Helper Functions
    # =========================================================================
    
    def get_current_user_id(session_id: str = Query(...)) -> int:
        """获取当前用户 ID（从 session）"""
        session_info = user_service.verify_session(session_id)
        if not session_info:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return session_info["user_id"]
    
    # =========================================================================
    # Dashboard Pages
    # =========================================================================
    
    @router.get("/", response_class=HTMLResponse)
    async def dashboard_index(
        session_id: str = Query(...),
        user_id: int = Depends(get_current_user_id)
    ):
        """仪表盘主页"""
        # 获取用户数据
        user = user_service.get_user(user_id)
        progress_tracker = ProgressTracker(user_id, db)
        progress = progress_tracker.get_progress()
        
        # 生成雷达图 SVG
        radar_chart = DimensionRadarChart()
        dimension_scores = progress.get("dimension_scores", {}) if progress else {}
        radar_svg = radar_chart.generate(dimension_scores) if dimension_scores else ""
        
        # 生成趋势图 SVG
        trend_chart = ProgressTrendChart()
        history = progress_tracker.get_session_history(limit=50)
        trend_svg = trend_chart.generate(history) if history else ""
        
        # HTML 模板
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>用户仪表盘 - AgentScope AI Interview</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f6fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
                .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat-card .value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
                .stat-card .label {{ color: #666; margin-top: 5px; }}
                .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 20px; }}
                .chart-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .chart-card h3 {{ margin-bottom: 15px; color: #333; }}
                .actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
                .btn {{ padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
                .btn-primary {{ background: #667eea; color: white; }}
                .btn-secondary {{ background: #e0e0e0; color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>👋 欢迎回来，{user.get('display_name') or user.get('username')}</h1>
                    <p>继续你的练习之旅，不断提升自己的能力！</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="value">{progress.get('total_sessions', 0) if progress else 0}</div>
                        <div class="label">总会话数</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{progress.get('avg_score', 0):.1f}分</div>
                        <div class="label">平均分数</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">🔥 {progress.get('streak_days', 0) if progress else 0}天</div>
                        <div class="label">连续练习</div>
                    </div>
                    <div class="stat-card">
                        <div class="value">{progress.get('improvement_rate', 0):+.1f}%</div>
                        <div class="label">改进率</div>
                    </div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-card">
                        <h3>📊 七维度评估</h3>
                        <div style="text-align: center;">{radar_svg}</div>
                    </div>
                    <div class="chart-card">
                        <h3>📈 学习趋势</h3>
                        <div style="text-align: center;">{trend_svg}</div>
                    </div>
                </div>
                
                <div class="actions">
                    <a href="/scenes" class="btn btn-primary">开始新练习</a>
                    <a href="/history" class="btn btn-secondary">查看历史</a>
                    <a href="/report" class="btn btn-secondary">导出报告</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # =========================================================================
    # API Endpoints
    # =========================================================================
    
    @router.get("/api/summary", response_model=DashboardSummary)
    async def get_dashboard_summary(
        session_id: str = Query(...),
        user_id: int = Depends(get_current_user_id)
    ):
        """获取仪表盘摘要"""
        user = user_service.get_user(user_id)
        progress_tracker = ProgressTracker(user_id, db)
        progress = progress_tracker.get_progress()
        
        return DashboardSummary(
            user_id=user_id,
            username=user.get("username", "") if user else "",
            total_sessions=progress.get("total_sessions", 0) if progress else 0,
            completed_sessions=progress.get("completed_sessions", 0) if progress else 0,
            avg_score=progress.get("avg_score", 0.0) if progress else 0.0,
            streak_days=progress.get("streak_days", 0) if progress else 0,
            last_session_at=progress.get("last_session_at") if progress else None,
        )
    
    @router.get("/api/progress", response_model=ProgressData)
    async def get_progress_data(
        session_id: str = Query(...),
        user_id: int = Depends(get_current_user_id)
    ):
        """获取进度数据"""
        progress_tracker = ProgressTracker(user_id, db)
        progress = progress_tracker.get_progress()
        
        if not progress:
            return ProgressData(
                total_sessions=0,
                completed_sessions=0,
                total_duration_seconds=0,
                avg_score=0.0,
                dimension_scores={},
                improvement_rate=0.0,
                streak_days=0,
            )
        
        return ProgressData(**progress)
    
    @router.get("/api/sessions", response_model=List[SessionListItem])
    async def get_sessions(
        session_id: str = Query(...),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        user_id: int = Depends(get_current_user_id)
    ):
        """获取会话列表"""
        sessions = user_service.get_user_sessions(user_id, limit, offset)
        
        return [
            SessionListItem(
                id=s.id,
                scene_type=s.scene_type,
                title=s.title,
                status=s.status,
                started_at=s.started_at,
                duration_seconds=s.duration_seconds,
                score=0.0,  # 需要从 evaluation_result 解析
            )
            for s in sessions
        ]
    
    @router.get("/api/radar-chart")
    async def get_radar_chart(
        session_id: str = Query(...),
        user_id: int = Depends(get_current_user_id)
    ):
        """获取雷达图 SVG"""
        progress_tracker = ProgressTracker(user_id, db)
        progress = progress_tracker.get_progress()
        
        radar_chart = DimensionRadarChart()
        dimension_scores = progress.get("dimension_scores", {}) if progress else {}
        svg = radar_chart.generate(dimension_scores)
        
        return HTMLResponse(content=svg, media_type="image/svg+xml")
    
    @router.get("/api/trend-chart")
    async def get_trend_chart(
        session_id: str = Query(...),
        days: int = Query(30, ge=1, le=365),
        user_id: int = Depends(get_current_user_id)
    ):
        """获取趋势图 SVG"""
        progress_tracker = ProgressTracker(user_id, db)
        history = progress_tracker.get_session_history(limit=200)
        
        trend_chart = ProgressTrendChart()
        svg = trend_chart.generate(history, days=days)
        
        return HTMLResponse(content=svg, media_type="image/svg+xml")
    
    return router


# =============================================================================
# Standalone Dashboard App (for testing)
# =============================================================================

def create_dashboard_app(db: Database):
    """
    创建独立的 Dashboard FastAPI 应用
    
    Args:
        db: 数据库实例
        
    Returns:
        FastAPI 应用
    """
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(title="AgentScope Dashboard")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 路由
    router = create_dashboard_router(db)
    app.include_router(router)
    
    return app
