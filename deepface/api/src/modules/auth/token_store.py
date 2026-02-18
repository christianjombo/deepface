# built-in dependencies
import sqlite3
import time
import threading
from dataclasses import dataclass
from typing import Optional, Dict, Tuple

# project dependencies
from deepface.commons.logger import Logger

logger = Logger()


@dataclass
class TokenRecord:
    name: str
    status: str


class TokenStore:
    def __init__(self, db_path: str, ttl_seconds: int = 1800) -> None:
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[float, TokenRecord]] = {}
        self._lock = threading.Lock()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL CHECK (status IN ('active','revoked')) DEFAULT 'active',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    revoked_at TEXT NULL,
                    last_seen_at TEXT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_api_tokens_token ON api_tokens(token)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_api_tokens_status ON api_tokens(status)"
            )
            conn.commit()

    def lookup(self, token: str) -> Optional[TokenRecord]:
        with self._lock:
            cached = self._cache.get(token)
            if cached:
                expires_at, record = cached
                if time.time() < expires_at:
                    if record.status == "active":
                        return record
                    return None
                del self._cache[token]

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT name, status FROM api_tokens WHERE token = ?",
                (token,),
            )
            row = cur.fetchone()
        if row is None:
            return None

        record = TokenRecord(name=row["name"], status=row["status"])
        if record.status != "active":
            with self._lock:
                self._cache[token] = (
                    time.time() + self.ttl_seconds,
                    record,
                )
            return None

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE api_tokens SET last_seen_at = datetime('now') WHERE token = ?",
                (token,),
            )
            conn.commit()

        with self._lock:
            self._cache[token] = (time.time() + self.ttl_seconds, record)

        return record
