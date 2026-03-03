"""
Evaluation Storage - 评估存储模块 (v0.3)

基于 SQLite 的评估数据持久化系统，支持：
- 评估结果存储和检索
- 历史记录查询
- 统计分析和趋势追踪
- 数据导出功能

设计原则:
- 单一职责：专注于数据持久化
- 开闭原则：支持扩展新的存储后端
- 依赖倒置：通过抽象接口访问存储
- 接口隔离：提供细粒度的查询接口

Database Schema:
- evaluations: 评估主表
- dimension_scores: 维度评分表
- dialogue_history: 对话历史表
- analytics: 分析统计表
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from core.config import Config

logger = logging.getLogger(__name__)


@dataclass
class EvaluationRecord:
    """
    评估记录数据类

    用于数据库存储的评估记录格式

    Attributes:
        id: 记录 ID
        session_id: 会话 ID
        candidate_name: 候选人姓名
        position: 面试岗位
        domain: 面试领域
        style: 面试风格
        overall_score: 总体评分
        level: 评级
        dimension_scores: 维度评分 JSON
        summary: 评估摘要
        strengths: 优势列表 JSON
        weaknesses: 待改进列表 JSON
        suggestions: 建议列表 JSON
        dialogue_length: 对话长度
        created_at: 创建时间
        metadata: 元数据 JSON
    """
    id: Optional[int] = None
    session_id: str = ""
    candidate_name: str = ""
    position: str = ""
    domain: str = ""
    style: str = ""
    overall_score: float = 0.0
    level: str = "C"
    dimension_scores: str = "{}"
    summary: str = ""
    strengths: str = "[]"
    weaknesses: str = "[]"
    suggestions: str = "[]"
    dialogue_length: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: str = "{}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "position": self.position,
            "domain": self.domain,
            "style": self.style,
            "overall_score": self.overall_score,
            "level": self.level,
            "dimension_scores": json.loads(self.dimension_scores),
            "summary": self.summary,
            "strengths": json.loads(self.strengths),
            "weaknesses": json.loads(self.weaknesses),
            "suggestions": json.loads(self.suggestions),
            "dialogue_length": self.dialogue_length,
            "created_at": self.created_at,
            "metadata": json.loads(self.metadata),
        }

    @classmethod
    def from_result(
        cls,
        result: Any,
        session_id: str,
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> "EvaluationRecord":
        """
        从评估结果创建记录

        Args:
            result: AdvancedEvaluationResult 实例
            session_id: 会话 ID
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            EvaluationRecord 实例
        """
        candidate_info = candidate_info or {}
        interview_info = interview_info or {}

        return cls(
            session_id=session_id,
            candidate_name=candidate_info.get("name", ""),
            position=candidate_info.get("position", ""),
            domain=interview_info.get("domain", ""),
            style=interview_info.get("style", ""),
            overall_score=result.overall_score,
            level=result.level,
            dimension_scores=json.dumps({
                k.value: v.to_dict() for k, v in result.dimension_scores.items()
            }),
            summary=result.summary,
            strengths=json.dumps(result.strengths),
            weaknesses=json.dumps(result.weaknesses),
            suggestions=json.dumps(result.suggestions),
            dialogue_length=result.metadata.get("answer_count", 0),
            metadata=json.dumps(result.metadata),
        )


@dataclass
class EvaluationStatistics:
    """
    评估统计数据类

    Attributes:
        total_evaluations: 总评估数
        avg_score: 平均分
        score_distribution: 分数分布
        level_distribution: 等级分布
        dimension_averages: 维度平均分
        trend_data: 趋势数据
        time_range: 时间范围
    """
    total_evaluations: int = 0
    avg_score: float = 0.0
    score_distribution: Dict[str, int] = field(default_factory=dict)
    level_distribution: Dict[str, int] = field(default_factory=dict)
    dimension_averages: Dict[str, float] = field(default_factory=dict)
    trend_data: List[Dict[str, Any]] = field(default_factory=list)
    time_range: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_evaluations": self.total_evaluations,
            "avg_score": round(self.avg_score, 2),
            "score_distribution": self.score_distribution,
            "level_distribution": self.level_distribution,
            "dimension_averages": {k: round(v, 2) for k, v in self.dimension_averages.items()},
            "trend_data": self.trend_data,
            "time_range": self.time_range,
        }


class EvaluationStorage:
    """
    评估存储类

    基于 SQLite 的评估数据持久化系统

    Attributes:
        db_path: 数据库文件路径
        connection: 数据库连接
    """

    # 数据库版本
    DB_VERSION = 1

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        config: Optional[Config] = None,
    ):
        """
        初始化存储

        Args:
            db_path: 数据库文件路径
            config: 配置对象
        """
        # 确定数据库路径
        if db_path:
            self.db_path = Path(db_path)
        elif config and config.has("storage.db_path"):
            self.db_path = Path(config.get("storage.db_path"))
        else:
            # 默认路径
            self.db_path = Path(__file__).parent.parent / "data" / "evaluations.db"

        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection: Optional[sqlite3.Connection] = None
        self._connect()
        self._init_schema()

        logger.info(f"EvaluationStorage 初始化完成，数据库：{self.db_path}")

    def _connect(self) -> None:
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
            )
            self.connection.row_factory = sqlite3.Row
            logger.debug(f"数据库连接成功：{self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败：{e}")
            raise

    def _init_schema(self) -> None:
        """初始化数据库 schema"""
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        try:
            # 创建评估主表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    candidate_name TEXT,
                    position TEXT,
                    domain TEXT,
                    style TEXT,
                    overall_score REAL NOT NULL,
                    level TEXT NOT NULL,
                    dimension_scores TEXT NOT NULL,
                    summary TEXT,
                    strengths TEXT,
                    weaknesses TEXT,
                    suggestions TEXT,
                    dialogue_length INTEGER,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id ON evaluations(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_candidate_name ON evaluations(candidate_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_overall_score ON evaluations(overall_score)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_level ON evaluations(level)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON evaluations(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_domain ON evaluations(domain)
            """)

            # 创建版本表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
            """)

            # 插入版本记录
            cursor.execute("""
                INSERT OR IGNORE INTO schema_version (version) VALUES (?)
            """, (self.DB_VERSION,))

            self.connection.commit()
            logger.debug("数据库 schema 初始化完成")

        except sqlite3.Error as e:
            logger.error(f"Schema 初始化失败：{e}")
            raise

    def save_evaluation(
        self,
        result: Any,
        session_id: str,
        candidate_info: Optional[Dict[str, Any]] = None,
        interview_info: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        保存评估结果

        Args:
            result: AdvancedEvaluationResult 实例
            session_id: 会话 ID
            candidate_info: 候选人信息
            interview_info: 面试信息

        Returns:
            插入的记录 ID
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        record = EvaluationRecord.from_result(
            result, session_id, candidate_info, interview_info
        )

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO evaluations (
                    session_id, candidate_name, position, domain, style,
                    overall_score, level, dimension_scores, summary,
                    strengths, weaknesses, suggestions, dialogue_length,
                    created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.session_id,
                record.candidate_name,
                record.position,
                record.domain,
                record.style,
                record.overall_score,
                record.level,
                record.dimension_scores,
                record.summary,
                record.strengths,
                record.weaknesses,
                record.suggestions,
                record.dialogue_length,
                record.created_at,
                record.metadata,
            ))

            self.connection.commit()
            record_id = cursor.lastrowid

            logger.info(f"评估结果已保存，ID: {record_id}, session: {session_id}")
            return record_id

        except sqlite3.Error as e:
            logger.error(f"保存评估结果失败：{e}")
            self.connection.rollback()
            raise

    def get_evaluation_by_id(self, evaluation_id: int) -> Optional[EvaluationRecord]:
        """
        根据 ID 获取评估记录

        Args:
            evaluation_id: 记录 ID

        Returns:
            EvaluationRecord 或 None
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT * FROM evaluations WHERE id = ?
            """, (evaluation_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
            return None

        except sqlite3.Error as e:
            logger.error(f"查询评估记录失败：{e}")
            return None

    def get_evaluation_by_session(self, session_id: str) -> Optional[EvaluationRecord]:
        """
        根据会话 ID 获取评估记录

        Args:
            session_id: 会话 ID

        Returns:
            EvaluationRecord 或 None
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                SELECT * FROM evaluations WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
            return None

        except sqlite3.Error as e:
            logger.error(f"查询评估记录失败：{e}")
            return None

    def list_evaluations(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        descending: bool = True,
    ) -> List[EvaluationRecord]:
        """
        获取评估记录列表

        Args:
            limit: 限制数量
            offset: 偏移量
            order_by: 排序字段
            descending: 是否降序

        Returns:
            EvaluationRecord 列表
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()
        order_dir = "DESC" if descending else "ASC"

        try:
            cursor.execute(f"""
                SELECT * FROM evaluations
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """, (limit, offset))

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"查询评估列表失败：{e}")
            return []

    def search_evaluations(
        self,
        candidate_name: Optional[str] = None,
        position: Optional[str] = None,
        domain: Optional[str] = None,
        level: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[EvaluationRecord]:
        """
        搜索评估记录

        Args:
            candidate_name: 候选人姓名（模糊匹配）
            position: 面试岗位
            domain: 面试领域
            level: 评级
            min_score: 最低分数
            max_score: 最高分数
            start_date: 开始日期 (ISO 格式)
            end_date: 结束日期 (ISO 格式)
            limit: 限制数量

        Returns:
            EvaluationRecord 列表
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if candidate_name:
            conditions.append("candidate_name LIKE ?")
            params.append(f"%{candidate_name}%")

        if position:
            conditions.append("position = ?")
            params.append(position)

        if domain:
            conditions.append("domain = ?")
            params.append(domain)

        if level:
            conditions.append("level = ?")
            params.append(level)

        if min_score is not None:
            conditions.append("overall_score >= ?")
            params.append(min_score)

        if max_score is not None:
            conditions.append("overall_score <= ?")
            params.append(max_score)

        if start_date:
            conditions.append("created_at >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("created_at <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        try:
            cursor.execute(f"""
                SELECT * FROM evaluations
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            """, params + [limit])

            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"搜索评估记录失败：{e}")
            return []

    def get_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> EvaluationStatistics:
        """
        获取评估统计数据

        Args:
            start_date: 开始日期
            end_date: 结束日期
            domain: 面试领域

        Returns:
            EvaluationStatistics 实例
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if start_date:
            conditions.append("created_at >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("created_at <= ?")
            params.append(end_date)

        if domain:
            conditions.append("domain = ?")
            params.append(domain)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        stats = EvaluationStatistics()

        try:
            # 总数和平均分
            cursor.execute(f"""
                SELECT COUNT(*) as total, AVG(overall_score) as avg_score,
                       MIN(created_at) as min_date, MAX(created_at) as max_date
                FROM evaluations
                WHERE {where_clause}
            """, params)

            row = cursor.fetchone()
            if row:
                stats.total_evaluations = row["total"] or 0
                stats.avg_score = row["avg_score"] or 0.0
                stats.time_range = {
                    "start": row["min_date"] or "",
                    "end": row["max_date"] or "",
                }

            # 等级分布
            cursor.execute(f"""
                SELECT level, COUNT(*) as count
                FROM evaluations
                WHERE {where_clause}
                GROUP BY level
            """, params)

            stats.level_distribution = {
                row["level"]: row["count"] for row in cursor.fetchall()
            }

            # 分数分布
            cursor.execute(f"""
                SELECT 
                    CASE 
                        WHEN overall_score >= 4.5 THEN 'S'
                        WHEN overall_score >= 4.0 THEN 'A'
                        WHEN overall_score >= 3.0 THEN 'B'
                        WHEN overall_score >= 2.0 THEN 'C'
                        ELSE 'D'
                    END as score_level,
                    COUNT(*) as count
                FROM evaluations
                WHERE {where_clause}
                GROUP BY score_level
            """, params)

            stats.score_distribution = {
                row["score_level"]: row["count"] for row in cursor.fetchall()
            }

            # 维度平均分（需要解析 JSON）
            cursor.execute(f"""
                SELECT dimension_scores FROM evaluations WHERE {where_clause}
            """, params)

            dimension_totals = {}
            dimension_counts = {}

            for row in cursor.fetchall():
                try:
                    scores = json.loads(row["dimension_scores"])
                    for dim_name, dim_data in scores.items():
                        score = dim_data.get("score", 0)
                        if dim_name not in dimension_totals:
                            dimension_totals[dim_name] = 0
                            dimension_counts[dim_name] = 0
                        dimension_totals[dim_name] += score
                        dimension_counts[dim_name] += 1
                except (json.JSONDecodeError, KeyError):
                    continue

            stats.dimension_averages = {
                dim: dimension_totals[dim] / dimension_counts[dim]
                for dim in dimension_totals
                if dimension_counts[dim] > 0
            }

            # 趋势数据（按天统计）
            cursor.execute(f"""
                SELECT DATE(created_at) as date, 
                       AVG(overall_score) as avg_score,
                       COUNT(*) as count
                FROM evaluations
                WHERE {where_clause}
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """, params)

            stats.trend_data = [
                {"date": row["date"], "avg_score": row["avg_score"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

            return stats

        except sqlite3.Error as e:
            logger.error(f"获取统计数据失败：{e}")
            return stats

    def get_trend_analysis(
        self,
        days: int = 30,
        group_by: str = "day",
    ) -> List[Dict[str, Any]]:
        """
        获取趋势分析数据

        Args:
            days: 分析天数
            group_by: 分组方式 (day/week/month)

        Returns:
            趋势数据列表
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        # 计算起始日期
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # 根据分组方式确定格式
        if group_by == "week":
            date_format = "%Y-%W"
        elif group_by == "month":
            date_format = "%Y-%m"
        else:
            date_format = "%Y-%m-%d"

        try:
            cursor.execute("""
                SELECT strftime(?, created_at) as period,
                       AVG(overall_score) as avg_score,
                       COUNT(*) as count,
                       MIN(overall_score) as min_score,
                       MAX(overall_score) as max_score
                FROM evaluations
                WHERE created_at >= ?
                GROUP BY period
                ORDER BY period
            """, (date_format, start_date))

            return [
                {
                    "period": row["period"],
                    "avg_score": round(row["avg_score"], 2),
                    "count": row["count"],
                    "min_score": row["min_score"],
                    "max_score": row["max_score"],
                }
                for row in cursor.fetchall()
            ]

        except sqlite3.Error as e:
            logger.error(f"获取趋势分析失败：{e}")
            return []

    def delete_evaluation(self, evaluation_id: int) -> bool:
        """
        删除评估记录

        Args:
            evaluation_id: 记录 ID

        Returns:
            是否删除成功
        """
        if not self.connection:
            raise RuntimeError("数据库未连接")

        cursor = self.connection.cursor()

        try:
            cursor.execute("""
                DELETE FROM evaluations WHERE id = ?
            """, (evaluation_id,))

            self.connection.commit()
            deleted = cursor.rowcount > 0

            if deleted:
                logger.info(f"评估记录已删除，ID: {evaluation_id}")

            return deleted

        except sqlite3.Error as e:
            logger.error(f"删除评估记录失败：{e}")
            self.connection.rollback()
            return False

    def export_to_json(
        self,
        output_path: Union[str, Path],
        evaluations: Optional[List[EvaluationRecord]] = None,
    ) -> int:
        """
        导出评估数据为 JSON

        Args:
            output_path: 输出文件路径
            evaluations: 要导出的记录列表，None 表示导出全部

        Returns:
            导出的记录数
        """
        if evaluations is None:
            evaluations = self.list_evaluations(limit=10000)

        data = {
            "exported_at": datetime.now().isoformat(),
            "total_count": len(evaluations),
            "evaluations": [record.to_dict() for record in evaluations],
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"评估数据已导出到：{output_path}, 记录数：{len(evaluations)}")
            return len(evaluations)

        except IOError as e:
            logger.error(f"导出 JSON 失败：{e}")
            return 0

    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.debug("数据库连接已关闭")

    def _row_to_record(self, row: sqlite3.Row) -> EvaluationRecord:
        """将数据库行转换为 EvaluationRecord"""
        return EvaluationRecord(
            id=row["id"],
            session_id=row["session_id"],
            candidate_name=row["candidate_name"],
            position=row["position"],
            domain=row["domain"],
            style=row["style"],
            overall_score=row["overall_score"],
            level=row["level"],
            dimension_scores=row["dimension_scores"],
            summary=row["summary"],
            strengths=row["strengths"],
            weaknesses=row["weaknesses"],
            suggestions=row["suggestions"],
            dialogue_length=row["dialogue_length"],
            created_at=row["created_at"],
            metadata=row["metadata"],
        )

    def __enter__(self) -> "EvaluationStorage":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self):
        self.close()
