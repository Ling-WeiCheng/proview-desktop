from __future__ import annotations

import os
from pathlib import Path

from runtime_paths import APP_DATA_ROOT, get_app_data_path

BACKEND_DIR = Path(__file__).resolve().parent


def resolve_sqlite_path(raw_path: str, default_name: str = "interviews.db") -> Path:
    candidate = (raw_path or "").strip()
    if not candidate:
        return get_app_data_path("data", default_name).resolve()

    path = Path(candidate)
    if not path.is_absolute():
        path = (APP_DATA_ROOT / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_primary_sqlite_path() -> Path:
    return resolve_sqlite_path(os.getenv("PROVIEW_SQLITE_DB_PATH", ""), "interviews.db")


def get_career_sqlite_path() -> Path:
    raw_path = os.getenv("PROVIEW_CAREER_DB_PATH", "").strip()
    if raw_path:
        return resolve_sqlite_path(raw_path, "career_planning.sqlite3")
    return get_primary_sqlite_path()


def get_session_token_sqlite_path() -> Path:
    raw_path = os.getenv("PROVIEW_SESSION_TOKEN_DB_PATH", "").strip()
    if raw_path:
        return resolve_sqlite_path(raw_path, "session_tokens.sqlite3")
    return get_primary_sqlite_path()
