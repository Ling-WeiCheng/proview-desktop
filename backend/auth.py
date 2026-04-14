"""Token-based session management, replacing Flask cookie sessions."""
from contextlib import contextmanager
import sqlite3
import uuid
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import jsonify, request
from dotenv import load_dotenv
from runtime_paths import get_env_file_path
from sqlite_paths import get_session_token_sqlite_path

load_dotenv(get_env_file_path())


_TOKEN_DB_PATH = get_session_token_sqlite_path()


def _open_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_TOKEN_DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


@contextmanager
def _managed_connection() -> sqlite3.Connection:
    _ensure_store()
    conn = _open_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _ensure_store() -> None:
    _TOKEN_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _open_connection()
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_tokens (
                token TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _connect() -> sqlite3.Connection:
    _ensure_store()
    return _open_connection()


def create_token(session_id: str) -> str:
    """Create a token mapped to a session_id."""
    token = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with _managed_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO interview_tokens (token, session_id, created_at) VALUES (?, ?, ?)",
            (token, session_id, created_at),
        )
    return token


def get_session_id(token: str) -> str | None:
    """Resolve a token to its session_id."""
    with _managed_connection() as conn:
        row = conn.execute(
            "SELECT session_id FROM interview_tokens WHERE token = ?",
            (token,),
        ).fetchone()
    return row[0] if row else None


def revoke_token(token: str) -> None:
    """Remove a single token from the persistent token store."""
    with _managed_connection() as conn:
        conn.execute("DELETE FROM interview_tokens WHERE token = ?", (token,))


def revoke_session(session_id: str) -> None:
    """Remove all tokens bound to a session_id."""
    with _managed_connection() as conn:
        conn.execute("DELETE FROM interview_tokens WHERE session_id = ?", (session_id,))


def require_session(f):
    """Decorator: extract session_id from Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': '缺少认证 token'}), 401
        token = auth_header[7:]
        session_id = get_session_id(token)
        if not session_id:
            return jsonify({'error': '无效或过期的 token'}), 401
        kwargs['session_id'] = session_id
        return f(*args, **kwargs)
    return decorated
