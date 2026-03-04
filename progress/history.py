"""
Session History Management

会话历史管理：
- 会话记录存储和检索
- 历史记录查询
- 数据导出

Design Principles:
- 高效查询
- 支持分页
- 数据序列化
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from users.tables import SessionTable
from users.database import Database
from users.models import SessionStatus


class SessionHistoryManager:
    """
    会话历史管理器
    
    管理用户会话历史的存储和检索
    
    Usage:
        history = SessionHistoryManager(user_id=1)
        sessions = history.get_recent_sessions(days=30)
        session = history.get_session(session_id)
    """
    
    def __init__(self, user_id: int, db: Optional[Database] = None):
        """
        初始化历史管理器
        
        Args:
            user_id: 用户 ID
            db: 数据库实例（可选）
        """
        self.user_id = user_id
        self.db = db or Database.get_instance()
    
    def add_session(self, scene_type: str, scene_id: Optional[str] = None,
                   title: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        添加会话记录
        
        Args:
            scene_type: 场景类型
            scene_id: 场景 ID（可选）
            title: 会话标题（可选）
            metadata: 元数据（可选）
            
        Returns:
            新建会话的 ID
        """
        with self.db.get_session() as session:
            session_record = SessionTable(
                user_id=self.user_id,
                scene_type=scene_type,
                scene_id=scene_id,
                title=title,
                status="active",
                metadata=metadata
            )
            session.add(session_record)
            session.commit()
            
            return session_record.id
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        获取会话详情
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话数据字典，不存在则返回 None
        """
        with self.db.get_session() as session:
            session_record = session.get(SessionTable, session_id)
            
            if session_record is None or session_record.user_id != self.user_id:
                return None
            
            return self._session_to_dict(session_record)
    
    def get_recent_sessions(self, days: int = 30, limit: int = 50,
                           status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取最近的会话
        
        Args:
            days: 天数限制
            limit: 返回数量限制
            status: 状态过滤（可选）
            
        Returns:
            会话列表
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.db.get_session() as session:
            stmt = select(SessionTable).where(
                SessionTable.user_id == self.user_id,
                SessionTable.started_at >= cutoff_date
            )
            
            if status:
                stmt = stmt.where(SessionTable.status == status)
            
            stmt = stmt.order_by(SessionTable.started_at.desc()).limit(limit)
            
            sessions = session.execute(stmt).scalars().all()
            
            return [self._session_to_dict(s) for s in sessions]
    
    def get_all_sessions(self, limit: int = 200, offset: int = 0,
                        status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有会话（分页）
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            status: 状态过滤（可选）
            
        Returns:
            会话列表
        """
        with self.db.get_session() as session:
            stmt = select(SessionTable).where(SessionTable.user_id == self.user_id)
            
            if status:
                stmt = stmt.where(SessionTable.status == status)
            
            stmt = stmt.order_by(SessionTable.started_at.desc())
            stmt = stmt.offset(offset).limit(limit)
            
            sessions = session.execute(stmt).scalars().all()
            
            return [self._session_to_dict(s) for s in sessions]
    
    def update_session(self, session_id: int, **kwargs) -> bool:
        """
        更新会话信息
        
        Args:
            session_id: 会话 ID
            **kwargs: 要更新的字段
            
        Returns:
            是否成功更新
        """
        with self.db.get_session() as session:
            session_record = session.get(SessionTable, session_id)
            
            if session_record is None or session_record.user_id != self.user_id:
                return False
            
            # 更新允许的字段
            allowed_fields = {
                "status", "title", "metadata", "dialogue_history",
                "evaluation_result", "ended_at", "duration_seconds"
            }
            
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(session_record, field):
                    setattr(session_record, field, value)
            
            session_record.updated_at = datetime.utcnow()
            session.commit()
            
            return True
    
    def complete_session(self, session_id: int,
                        evaluation_result: Optional[Dict[str, Any]] = None,
                        dialogue_history: Optional[Dict[str, Any]] = None) -> bool:
        """
        完成会话
        
        Args:
            session_id: 会话 ID
            evaluation_result: 评估结果（可选）
            dialogue_history: 对话历史（可选）
            
        Returns:
            是否成功完成
        """
        with self.db.get_session() as session:
            session_record = session.get(SessionTable, session_id)
            
            if session_record is None or session_record.user_id != self.user_id:
                return False
            
            # 计算持续时间
            if session_record.started_at:
                duration = datetime.utcnow() - session_record.started_at
                session_record.duration_seconds = int(duration.total_seconds())
            
            # 更新状态
            session_record.status = "completed"
            session_record.ended_at = datetime.utcnow()
            
            # 保存评估结果和对话历史
            if evaluation_result:
                session_record.evaluation_result = json.dumps(evaluation_result)
            if dialogue_history:
                session_record.dialogue_history = json.dumps(dialogue_history)
            
            session_record.updated_at = datetime.utcnow()
            session.commit()
            
            return True
    
    def delete_session(self, session_id: int) -> bool:
        """
        删除会话记录
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否成功删除
        """
        with self.db.get_session() as session:
            session_record = session.get(SessionTable, session_id)
            
            if session_record is None or session_record.user_id != self.user_id:
                return False
            
            session.delete(session_record)
            session.commit()
            
            return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取会话统计
        
        Returns:
            统计数据字典
        """
        with self.db.get_session() as session:
            # 总会话数
            total_stmt = select(func.count(SessionTable.id)).where(
                SessionTable.user_id == self.user_id
            )
            total = session.execute(total_stmt).scalar() or 0
            
            # 已完成会话数
            completed_stmt = select(func.count(SessionTable.id)).where(
                SessionTable.user_id == self.user_id,
                SessionTable.status == "completed"
            )
            completed = session.execute(completed_stmt).scalar() or 0
            
            # 总时长
            duration_stmt = select(func.sum(SessionTable.duration_seconds)).where(
                SessionTable.user_id == self.user_id
            )
            total_duration = session.execute(duration_stmt).scalar() or 0
            
            # 按场景类型统计
            scene_type_stmt = select(
                SessionTable.scene_type,
                func.count(SessionTable.id)
            ).where(
                SessionTable.user_id == self.user_id
            ).group_by(SessionTable.scene_type)
            
            scene_types = dict(session.execute(scene_type_stmt).all())
            
            return {
                "total_sessions": total,
                "completed_sessions": completed,
                "total_duration_seconds": total_duration,
                "total_duration_hours": round(total_duration / 3600, 2),
                "scene_types": scene_types,
            }
    
    def search_sessions(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        搜索会话
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            匹配的会话列表
        """
        with self.db.get_session() as session:
            stmt = select(SessionTable).where(
                SessionTable.user_id == self.user_id
            )
            
            # 搜索标题和场景类型
            stmt = stmt.where(
                (SessionTable.title.like(f"%{keyword}%")) |
                (SessionTable.scene_type.like(f"%{keyword}%"))
            )
            
            stmt = stmt.order_by(SessionTable.started_at.desc()).limit(limit)
            
            sessions = session.execute(stmt).scalars().all()
            
            return [self._session_to_dict(s) for s in sessions]
    
    def export_sessions(self, format: str = "json") -> str:
        """
        导出会话数据
        
        Args:
            format: 导出格式（json, csv）
            
        Returns:
            导出的数据字符串
        """
        sessions = self.get_all_sessions(limit=1000)
        
        if format == "json":
            return json.dumps(sessions, indent=2, default=str)
        
        elif format == "csv":
            if not sessions:
                return ""
            
            # CSV 头
            headers = ["id", "scene_type", "title", "status", "started_at", "ended_at", "duration_seconds"]
            lines = [",".join(headers)]
            
            for s in sessions:
                row = [
                    str(s.get("id", "")),
                    str(s.get("scene_type", "")),
                    str(s.get("title", "")),
                    str(s.get("status", "")),
                    str(s.get("started_at", "")),
                    str(s.get("ended_at", "")),
                    str(s.get("duration_seconds", "")),
                ]
                lines.append(",".join(row))
            
            return "\n".join(lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _session_to_dict(self, session_record: SessionTable) -> Dict[str, Any]:
        """
        将会话记录转换为字典
        
        Args:
            session_record: SessionTable 对象
            
        Returns:
            会话数据字典
        """
        return {
            "id": session_record.id,
            "user_id": session_record.user_id,
            "scene_type": session_record.scene_type,
            "scene_id": session_record.scene_id,
            "title": session_record.title,
            "status": session_record.status,
            "metadata": session_record.metadata,
            "dialogue_history": session_record.dialogue_history,
            "evaluation_result": session_record.evaluation_result,
            "started_at": session_record.started_at,
            "ended_at": session_record.ended_at,
            "duration_seconds": session_record.duration_seconds,
            "created_at": session_record.created_at,
            "updated_at": session_record.updated_at,
        }
