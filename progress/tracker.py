"""
Progress Tracker

进度追踪器核心类：
- 跟踪用户学习进度
- 记录和更新指标
- 生成进度报告

Design Principles:
- 单一职责
- 依赖注入
- 事件驱动更新
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from .metrics import ProgressMetricsCalculator, SessionMetrics, AggregatedMetrics, EvaluationDimension
from users.repository import ProgressRepository, SessionRepository
from users.database import Database


class ProgressTracker:
    """
    进度追踪器
    
    负责跟踪和记录用户的学习进度
    
    Usage:
        tracker = ProgressTracker(user_id=1)
        tracker.record_session(session_data)
        progress = tracker.get_progress()
        report = tracker.generate_report()
    """
    
    def __init__(self, user_id: int, db: Optional[Database] = None):
        """
        初始化进度追踪器
        
        Args:
            user_id: 用户 ID
            db: 数据库实例（可选）
        """
        self.user_id = user_id
        self.db = db or Database.get_instance()
        self.metrics_calculator = ProgressMetricsCalculator()
    
    def record_session(self, session_id: int, scene_type: str,
                      evaluation_result: Optional[Dict[str, Any]] = None,
                      duration_seconds: int = 0) -> bool:
        """
        记录会话完成
        
        Args:
            session_id: 会话 ID
            scene_type: 场景类型
            evaluation_result: 评估结果（可选）
            duration_seconds: 会话时长（秒）
            
        Returns:
            是否成功记录
        """
        with self.db.get_session() as session:
            progress_repo = ProgressRepository(session)
            session_repo = SessionRepository(session)
            
            # 获取或创建进度记录
            progress = progress_repo.create_or_get(self.user_id)
            
            # 更新会话计数
            progress.total_sessions += 1
            progress.completed_sessions += 1
            progress.total_duration_seconds += duration_seconds
            
            # 更新平均分
            if evaluation_result:
                score = evaluation_result.get("overall_score", 0.0)
                total_score = progress.avg_score * (progress.total_sessions - 1) + score
                progress.avg_score = total_score / progress.total_sessions
                
                # 更新维度分数
                self._update_dimension_scores(session, progress, evaluation_result)
            
            # 更新最后会话时间
            progress.last_session_at = datetime.utcnow()
            progress.updated_at = datetime.utcnow()
            
            # 更新会话记录
            session_record = session_repo.get_by_id(session_id)
            if session_record:
                session_repo.complete_session(
                    session_id,
                    evaluation_result=str(evaluation_result) if evaluation_result else None
                )
            
            session.commit()
            return True
    
    def _update_dimension_scores(self, session: Session, progress,
                                evaluation_result: Dict[str, Any]) -> None:
        """
        更新维度分数
        
        Args:
            session: SQLAlchemy Session
            progress: ProgressTable 对象
            evaluation_result: 评估结果
        """
        existing_scores = progress.dimension_scores or {}
        
        # 更新各维度分数（移动平均）
        for dim in EvaluationDimension:
            dim_key = dim.value
            new_score = evaluation_result.get(dim_key, 0.0)
            
            if new_score > 0:
                if dim_key in existing_scores:
                    # 移动平均
                    existing_scores[dim_key] = (existing_scores[dim_key] + new_score) / 2
                else:
                    existing_scores[dim_key] = new_score
        
        progress.dimension_scores = existing_scores
    
    def get_progress(self) -> Optional[Dict[str, Any]]:
        """
        获取当前进度
        
        Returns:
            进度数据字典，不存在则返回 None
        """
        with self.db.get_session() as session:
            progress_repo = ProgressRepository(session)
            progress = progress_repo.get_by_user_id(self.user_id)
            
            if progress is None:
                return None
            
            return {
                "user_id": self.user_id,
                "total_sessions": progress.total_sessions,
                "completed_sessions": progress.completed_sessions,
                "total_duration_seconds": progress.total_duration_seconds,
                "avg_score": progress.avg_score,
                "dimension_scores": progress.dimension_scores or {},
                "improvement_rate": progress.improvement_rate,
                "streak_days": progress.streak_days,
                "last_session_at": progress.last_session_at,
                "updated_at": progress.updated_at,
            }
    
    def get_session_history(self, limit: int = 50,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取会话历史
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            会话历史列表
        """
        with self.db.get_session() as session:
            session_repo = SessionRepository(session)
            sessions = session_repo.get_by_user(self.user_id, limit, offset)
            
            return [
                {
                    "id": s.id,
                    "scene_type": s.scene_type,
                    "title": s.title,
                    "status": s.status,
                    "started_at": s.started_at,
                    "ended_at": s.ended_at,
                    "duration_seconds": s.duration_seconds,
                    "evaluation_result": s.evaluation_result,
                }
                for s in sessions
            ]
    
    def calculate_improvement_rate(self) -> float:
        """
        计算改进率
        
        Returns:
            改进率 (%)
        """
        sessions = self.get_session_history(limit=100)
        
        if not sessions:
            return 0.0
        
        # 转换为 SessionMetrics
        session_metrics = []
        for s in sessions:
            if s.get("evaluation_result"):
                import json
                try:
                    eval_result = json.loads(s["evaluation_result"])
                    session_metrics.append(SessionMetrics(
                        session_id=s["id"],
                        scene_type=s["scene_type"],
                        completed_at=s["ended_at"] or s["started_at"],
                        duration_seconds=s["duration_seconds"] or 0,
                        overall_score=eval_result.get("overall_score", 0.0),
                        dimension_scores={},
                    ))
                except:
                    pass
        
        return self.metrics_calculator.calculate_improvement_rate(session_metrics)
    
    def update_streak(self) -> int:
        """
        更新连续练习天数
        
        Returns:
            连续天数
        """
        sessions = self.get_session_history(limit=100)
        
        with self.db.get_session() as session:
            progress_repo = ProgressRepository(session)
            progress = progress_repo.create_or_get(self.user_id)
            
            streak_days = self.metrics_calculator.calculate_streak_days(sessions)
            progress.streak_days = streak_days
            progress.updated_at = datetime.utcnow()
            
            session.commit()
            
            return streak_days
    
    def generate_report(self, period_days: int = 30) -> Dict[str, Any]:
        """
        生成进度报告
        
        Args:
            period_days: 统计周期（天）
            
        Returns:
            进度报告字典
        """
        sessions = self.get_session_history(limit=200)
        
        # 使用计算器生成报告
        report = self.metrics_calculator.generate_progress_report(sessions, period_days)
        
        # 添加用户信息
        report["user_id"] = self.user_id
        
        return report
    
    def get_dimension_trends(self) -> Dict[str, Dict[str, Any]]:
        """
        获取各维度趋势
        
        Returns:
            维度趋势字典
        """
        sessions = self.get_session_history(limit=100)
        
        if not sessions:
            return {}
        
        # 转换为 SessionMetrics
        session_metrics = []
        for s in sessions:
            if s.get("evaluation_result"):
                import json
                try:
                    eval_result = json.loads(s["evaluation_result"])
                    dimension_scores = {
                        EvaluationDimension(dim): eval_result.get(dim, 0.0)
                        for dim in EvaluationDimension
                    }
                    session_metrics.append(SessionMetrics(
                        session_id=s["id"],
                        scene_type=s["scene_type"],
                        completed_at=s["ended_at"] or s["started_at"],
                        duration_seconds=s["duration_seconds"] or 0,
                        overall_score=eval_result.get("overall_score", 0.0),
                        dimension_scores=dimension_scores,
                    ))
                except:
                    pass
        
        # 计算各维度趋势
        trends = {}
        for dim in EvaluationDimension:
            trend = self.metrics_calculator.calculate_trend(session_metrics, dim)
            trends[dim.value] = {
                "trend": trend,
                "name": dim.value.replace("_", " ").title(),
            }
        
        return trends
    
    def get_milestones(self) -> List[Dict[str, Any]]:
        """
        获取里程碑
        
        Returns:
            里程碑列表
        """
        progress = self.get_progress()
        
        if not progress:
            return []
        
        milestones = []
        
        # 会话数里程碑
        session_milestones = [1, 5, 10, 20, 50, 100]
        for milestone in session_milestones:
            if progress["total_sessions"] >= milestone:
                milestones.append({
                    "type": "sessions",
                    "name": f"完成{milestone}次练习",
                    "achieved_at": progress.get("last_session_at"),
                    "icon": "🎯",
                })
        
        # 分数里程碑
        score_milestones = [60, 70, 80, 90]
        for milestone in score_milestones:
            if progress["avg_score"] >= milestone:
                milestones.append({
                    "type": "score",
                    "name": f"平均分达到{milestone}",
                    "achieved_at": progress.get("last_session_at"),
                    "icon": "🏆",
                })
        
        # 连续练习里程碑
        streak_milestones = [3, 7, 14, 30]
        for milestone in streak_milestones:
            if progress["streak_days"] >= milestone:
                milestones.append({
                    "type": "streak",
                    "name": f"连续练习{milestone}天",
                    "achieved_at": progress.get("last_session_at"),
                    "icon": "🔥",
                })
        
        return milestones
