"""SQLite connection provider for VAULTX with thread safety, foreign keys, and resilient fallback."""

import os
import sqlite3
import tempfile
from pathlib import Path

DEFAULT_DB_PATH = Path("data/vaultx.db")
_OVERRIDE_DB_PATH = None


def set_db_path(path: Path):
    """Override database path for tests or alternate profiles."""
    global _OVERRIDE_DB_PATH
    _OVERRIDE_DB_PATH = path


def get_db_path() -> Path:
    """Return the currently configured SQLite database path."""
    if _OVERRIDE_DB_PATH is not None:
        return _OVERRIDE_DB_PATH
    env_path = os.environ.get("VAULTX_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def _try_connect(target_path: Path) -> sqlite3.Connection:
    if str(target_path) != ":memory:":
        target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    # Probe database write/read ability to ensure filesystem supports SQLite locking
    conn.execute("CREATE TABLE IF NOT EXISTS _sqlite_probe_ (id INTEGER PRIMARY KEY);")
    return conn


def get_connection() -> sqlite3.Connection:
    """Create and return an active SQLite connection configured with Row factory and foreign keys."""
    db_path = get_db_path()
    try:
        return _try_connect(db_path)
    except sqlite3.OperationalError as e:
        err_msg = str(e).lower()
        if "disk i/o error" in err_msg or "unable to open" in err_msg or "locking" in err_msg:
            fallback_path = Path(tempfile.gettempdir()) / "vaultx.db"
            set_db_path(fallback_path)
            return _try_connect(fallback_path)
        raise
