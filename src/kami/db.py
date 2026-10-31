from __future__ import annotations
import sqlite3
from importlib.resources import files
from pathlib import Path
from kami.config import ensure_parent_dir

class KamiError(Exception):
    """Base class for errors"""

class DatabaseNotInitialized(KamiError):
    """DB file missing"""

def connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise DatabaseNotInitialized(f"db not found at {db_path}. Run 'kami init'")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn
