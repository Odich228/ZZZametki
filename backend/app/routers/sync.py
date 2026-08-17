"""
Эндпоинт синхронизации.

Клиент присылает:
- список своих локальных изменений (changes)
- время последней успешной синхронизации (last_synced_at)

Сервер:
1. применяет входящие изменения (если они новее того, что уже есть в БД —
   разрешение конфликтов по правилу "кто новее, тот и победил")
2. возвращает клиенту все заметки пользователя, изменившиеся
   после last_synced_at (в т.ч. с других устройств)
3. возвращает текущее серверное время как новый "чекпоинт" синхронизации
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Note, User
from app.schemas import SyncRequest, SyncResponse

router = APIRouter(tags=["sync"])


@router.post("/sync", response_model=SyncResponse)
def sync(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. применяем входящие изменения от клиента
    for change in payload.changes:
        existing = (
            db.query(Note)
            .filter(Note.id == change.id, Note.user_id == current_user.id)
            .first()
        )

        if existing is None:
            # новая заметка, которой ещё нет на сервере
            note = Note(
                id=change.id,
                user_id=current_user.id,
                content=change.content,
                updated_at=change.updated_at,
                is_deleted=change.is_deleted,
            )
            db.add(note)
        elif change.updated_at > existing.updated_at:
            # клиентская версия новее — она побеждает
            existing.content = change.content
            existing.updated_at = change.updated_at
            existing.is_deleted = change.is_deleted
        # если существующая версия новее или равна — клиентское
        # изменение игнорируем, серверная версия и так победит
        # ниже, когда мы вернём её обратно клиенту

    db.commit()

    # 2. собираем изменения, которые нужно отдать клиенту
    query = db.query(Note).filter(Note.user_id == current_user.id)
    if payload.last_synced_at:
        query = query.filter(Note.updated_at > payload.last_synced_at)

    server_changes = query.all()

    return SyncResponse(
        server_changes=server_changes,
        synced_at=datetime.now(timezone.utc).isoformat(),
    )
