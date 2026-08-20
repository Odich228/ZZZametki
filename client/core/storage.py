"""
Локальное хранилище заметок (SQLite).

Отвечает ТОЛЬКО за чтение/запись на диск. Ничего не знает
про сеть, про backend, про Kivy-виджеты — это чистая логика
данных, поэтому её легко тестировать в изоляции (см. tests/test_storage.py).
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from core.models import Note

DB_PATH = Path.home() / ".notes_app" / "notes.sqlite3"


class Storage:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_synced INTEGER NOT NULL DEFAULT 0,
                    is_deleted INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def get_all(self, include_deleted: bool = False) -> List[Note]:
        query = "SELECT * FROM notes"
        if not include_deleted:
            query += " WHERE is_deleted = 0"
        query += " ORDER BY updated_at DESC"

        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [self._row_to_note(row) for row in rows]

    def get_by_id(self, note_id: str) -> Optional[Note]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM notes WHERE id = ?", (note_id,)
            ).fetchone()
        return self._row_to_note(row) if row else None

    def save(self, note: Note) -> None:
        """Создать заметку или обновить существующую (upsert)."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO notes (id, content, updated_at, is_synced, is_deleted)
                VALUES (:id, :content, :updated_at, :is_synced, :is_deleted)
                ON CONFLICT(id) DO UPDATE SET
                    content = excluded.content,
                    updated_at = excluded.updated_at,
                    is_synced = excluded.is_synced,
                    is_deleted = excluded.is_deleted
                """,
                {
                    "id": note.id,
                    "content": note.content,
                    "updated_at": note.updated_at,
                    "is_synced": int(note.is_synced),
                    "is_deleted": int(note.is_deleted),
                },
            )

    def soft_delete(self, note_id: str) -> None:
        """
        Не удаляем строку физически — помечаем is_deleted=1.
        Это нужно, чтобы факт удаления тоже можно было
        синхронизировать на другие устройства.
        """
        note = self.get_by_id(note_id)
        if note:
            note.is_deleted = True
            note.touch()
            self.save(note)

    def get_unsynced(self) -> List[Note]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM notes WHERE is_synced = 0"
            ).fetchall()
        return [self._row_to_note(row) for row in rows]

    def mark_synced(self, note_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE notes SET is_synced = 1 WHERE id = ?", (note_id,)
            )

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            content=row["content"],
            updated_at=row["updated_at"],
            is_synced=bool(row["is_synced"]),
            is_deleted=bool(row["is_deleted"]),
        )
