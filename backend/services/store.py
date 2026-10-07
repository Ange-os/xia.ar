"""Persistencia local (SQLite): usuarios, cuotas, conversaciones y mensajes humanos."""

from __future__ import annotations

import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timezone
from typing import Any, Generator, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self._init_schema()

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    google_sub TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL,
                    name TEXT,
                    picture TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS usage_daily (
                    user_id TEXT NOT NULL,
                    day TEXT NOT NULL,
                    message_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (user_id, day),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL UNIQUE,
                    conversa_conversation_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                );

                CREATE TABLE IF NOT EXISTS pending_agent_messages (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    delivered INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
                """
            )

    def upsert_google_user(
        self,
        *,
        google_sub: str,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> dict[str, Any]:
        now = _utc_now()
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE google_sub = ?", (google_sub,)
            ).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE users
                    SET email = ?, name = ?, picture = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (email, name, picture, now, row["id"]),
                )
                user_id = row["id"]
            else:
                user_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO users (id, google_sub, email, name, picture, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, google_sub, email, name, picture, now, now),
                )
            updated = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(updated)

    def get_user(self, user_id: str) -> Optional[dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def get_user_by_google_sub(self, google_sub: str) -> Optional[dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE google_sub = ?", (google_sub,)
            ).fetchone()
            return dict(row) if row else None

    def get_daily_usage(self, user_id: str, day: Optional[str] = None) -> int:
        day = day or date.today().isoformat()
        with self._conn() as conn:
            row = conn.execute(
                "SELECT message_count FROM usage_daily WHERE user_id = ? AND day = ?",
                (user_id, day),
            ).fetchone()
            return int(row["message_count"]) if row else 0

    def increment_daily_usage(self, user_id: str, amount: int = 1) -> int:
        day = date.today().isoformat()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO usage_daily (user_id, day, message_count)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, day)
                DO UPDATE SET message_count = message_count + excluded.message_count
                """,
                (user_id, day, amount),
            )
            row = conn.execute(
                "SELECT message_count FROM usage_daily WHERE user_id = ? AND day = ?",
                (user_id, day),
            ).fetchone()
            return int(row["message_count"])

    def get_or_create_conversation(self, user_id: str) -> dict[str, Any]:
        now = _utc_now()
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM conversations WHERE user_id = ?", (user_id,)
            ).fetchone()
            if row:
                return dict(row)
            conv_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO conversations (id, user_id, conversa_conversation_id, created_at, updated_at)
                VALUES (?, ?, NULL, ?, ?)
                """,
                (conv_id, user_id, now, now),
            )
            return dict(
                conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
            )

    def set_conversa_conversation_id(self, conversation_id: str, conversa_id: str) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                UPDATE conversations
                SET conversa_conversation_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (conversa_id, _utc_now(), conversation_id),
            )

    def add_message(self, conversation_id: str, role: str, content: str) -> dict[str, Any]:
        msg_id = str(uuid.uuid4())
        now = _utc_now()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (msg_id, conversation_id, role, content, now),
            )
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )
            return {
                "id": msg_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "created_at": now,
            }

    def recent_messages(self, conversation_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (conversation_id, limit),
            ).fetchall()
            return [dict(r) for r in reversed(rows)]

    def clear_conversation_messages(self, conversation_id: str) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (_utc_now(), conversation_id),
            )

    def enqueue_agent_message(self, user_id: str, content: str) -> dict[str, Any]:
        msg_id = str(uuid.uuid4())
        now = _utc_now()
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO pending_agent_messages (id, user_id, content, created_at, delivered)
                VALUES (?, ?, ?, ?, 0)
                """,
                (msg_id, user_id, content, now),
            )
            return {"id": msg_id, "user_id": user_id, "content": content, "created_at": now}

    def pull_pending_agent_messages(self, user_id: str) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM pending_agent_messages
                WHERE user_id = ? AND delivered = 0
                ORDER BY created_at ASC
                """,
                (user_id,),
            ).fetchall()
            ids = [r["id"] for r in rows]
            if ids:
                placeholders = ",".join("?" for _ in ids)
                conn.execute(
                    f"UPDATE pending_agent_messages SET delivered = 1 WHERE id IN ({placeholders})",
                    ids,
                )
            return [dict(r) for r in rows]

    def dump_debug(self) -> dict[str, Any]:
        with self._conn() as conn:
            return {
                "users": conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"],
                "messages": conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone()["c"],
            }
