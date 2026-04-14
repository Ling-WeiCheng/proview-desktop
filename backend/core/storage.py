"""
持久化存储模块
用于保存面试记录、对话历史、评分等数据
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class InterviewStorage:
    """面试数据持久化存储"""

    def __init__(self, db_path: str = "data/interviews.db"):
        """
        初始化存储

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()

    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 面试会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                session_id TEXT PRIMARY KEY,
                candidate_name TEXT,
                position TEXT,
                interview_style TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT,
                metadata TEXT
            )
        """)

        # 对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id)
            )
        """)

        # 评分记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                dimension TEXT,
                score INTEGER,
                comment TEXT,
                timestamp TEXT,
                FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id)
            )
        """)

        # 简历记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                file_name TEXT,
                file_path TEXT,
                ocr_result TEXT,
                upload_time TEXT,
                FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id)
            )
        """)

        conn.commit()
        conn.close()

    def create_session(
        self,
        session_id: str,
        candidate_name: str = "",
        position: str = "",
        interview_style: str = "default",
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        创建新的面试会话

        Args:
            session_id: 会话ID
            candidate_name: 候选人姓名
            position: 应聘岗位
            interview_style: 面试风格
            metadata: 额外元数据

        Returns:
            是否创建成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO interview_sessions
                (session_id, candidate_name, position, interview_style, start_time, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                candidate_name,
                position,
                interview_style,
                datetime.now().isoformat(),
                "active",
                json.dumps(metadata or {})
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"创建会话失败: {e}")
            return False

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        保存对话消息

        Args:
            session_id: 会话ID
            role: 角色（user/assistant）
            content: 消息内容

        Returns:
            是否保存成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO chat_history (session_id, role, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (session_id, role, content, datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False

    def get_session_history(self, session_id: str) -> List[Dict]:
        """
        获取会话的对话历史

        Args:
            session_id: 会话ID

        Returns:
            对话历史列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT role, content, timestamp
                FROM chat_history
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))

            rows = cursor.fetchall()
            conn.close()

            return [
                {"role": row[0], "content": row[1], "timestamp": row[2]}
                for row in rows
            ]
        except Exception as e:
            print(f"获取历史失败: {e}")
            return []

    def save_resume(
        self,
        session_id: str,
        file_name: str,
        file_path: str,
        ocr_result: str = ""
    ) -> bool:
        """
        保存简历信息

        Args:
            session_id: 会话ID
            file_name: 文件名
            file_path: 文件路径
            ocr_result: OCR解析结果

        Returns:
            是否保存成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO resumes (session_id, file_name, file_path, ocr_result, upload_time)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, file_name, file_path, ocr_result, datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存简历失败: {e}")
            return False

    def save_evaluation(
        self,
        session_id: str,
        dimension: str,
        score: int,
        comment: str = ""
    ) -> bool:
        """
        保存评分

        Args:
            session_id: 会话ID
            dimension: 评分维度（如：技术能力、沟通能力等）
            score: 分数（1-10）
            comment: 评语

        Returns:
            是否保存成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO evaluations (session_id, dimension, score, comment, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, dimension, score, comment, datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存评分失败: {e}")
            return False

    def end_session(self, session_id: str) -> bool:
        """
        结束面试会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE interview_sessions
                SET end_time = ?, status = 'completed'
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"结束会话失败: {e}")
            return False

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT session_id, candidate_name, position, interview_style,
                       start_time, end_time, status, metadata
                FROM interview_sessions
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "session_id": row[0],
                    "candidate_name": row[1],
                    "position": row[2],
                    "interview_style": row[3],
                    "start_time": row[4],
                    "end_time": row[5],
                    "status": row[6],
                    "metadata": json.loads(row[7]) if row[7] else {}
                }
            return None
        except Exception as e:
            print(f"获取会话信息失败: {e}")
            return None

    def list_sessions(self, limit: int = 50) -> List[Dict]:
        """
        列出所有面试会话

        Args:
            limit: 返回数量限制

        Returns:
            会话列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT session_id, candidate_name, position, interview_style,
                       start_time, end_time, status
                FROM interview_sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    "session_id": row[0],
                    "candidate_name": row[1],
                    "position": row[2],
                    "interview_style": row[3],
                    "start_time": row[4],
                    "end_time": row[5],
                    "status": row[6]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"列出会话失败: {e}")
            return []

    def get_session_statistics(self, session_id: str) -> Dict:
        """
        获取会话统计信息

        Args:
            session_id: 会话ID

        Returns:
            统计信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 对话轮数
            cursor.execute("""
                SELECT COUNT(*) FROM chat_history
                WHERE session_id = ? AND role = 'user'
            """, (session_id,))
            turn_count = cursor.fetchone()[0]

            # 评分信息
            cursor.execute("""
                SELECT dimension, score, comment
                FROM evaluations
                WHERE session_id = ?
            """, (session_id,))
            evaluations = [
                {"dimension": row[0], "score": row[1], "comment": row[2]}
                for row in cursor.fetchall()
            ]

            conn.close()

            return {
                "turn_count": turn_count,
                "evaluations": evaluations,
                "avg_score": sum(e["score"] for e in evaluations) / len(evaluations) if evaluations else 0
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {"turn_count": 0, "evaluations": [], "avg_score": 0}


if __name__ == "__main__":
    # 测试代码
    storage = InterviewStorage()

    # 创建测试会话
    session_id = "test_session_001"
    storage.create_session(
        session_id=session_id,
        candidate_name="张三",
        position="后端开发工程师",
        interview_style="default"
    )

    # 保存对话
    storage.save_message(session_id, "user", "你好，我想面试后端开发岗位")
    storage.save_message(session_id, "assistant", "欢迎参加面试，请先介绍一下你的背景")

    # 保存评分
    storage.save_evaluation(session_id, "技术能力", 8, "技术基础扎实")
    storage.save_evaluation(session_id, "沟通能力", 7, "表达清晰")

    # 获取历史
    history = storage.get_session_history(session_id)
    print("对话历史:", history)

    # 获取统计
    stats = storage.get_session_statistics(session_id)
    print("统计信息:", stats)

    # 结束会话
    storage.end_session(session_id)

    # 列出所有会话
    sessions = storage.list_sessions()
    print("所有会话:", sessions)
