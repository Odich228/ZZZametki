"""
Модель заметки на клиенте.

Это простая структура данных (dataclass), которая описывает,
как заметка выглядит внутри приложения — до того как она
превращается в строку SQLite или JSON для отправки на сервер.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Note:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    is_synced: bool = False
    is_deleted: bool = False

    def touch(self) -> None:
        """Обновить метку времени и пометить как несинхронизированное."""
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.is_synced = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            id=data["id"],
            content=data.get("content", ""),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            is_synced=data.get("is_synced", False),
            is_deleted=data.get("is_deleted", False),
        )
