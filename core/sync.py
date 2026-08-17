"""
Логика синхронизации.

Связывает storage.py (что лежит локально) и api_client.py (что
можно отправить/получить с сервера). Конфликты разрешаются
простым правилом "кто новее (updated_at), тот и побеждает".
"""

import json
from pathlib import Path
from typing import Optional

from core.api_client import ApiClient, ApiError
from core.models import Note
from core.storage import Storage

META_PATH = Path.home() / ".notes_app" / "sync_meta.json"


class SyncManager:
    def __init__(self, storage: Storage, api_client: ApiClient):
        self.storage = storage
        self.api = api_client

    def _get_last_synced_at(self) -> Optional[str]:
        if META_PATH.exists():
            return json.loads(META_PATH.read_text()).get("last_synced_at")
        return None

    def _set_last_synced_at(self, value: str) -> None:
        META_PATH.parent.mkdir(parents=True, exist_ok=True)
        META_PATH.write_text(json.dumps({"last_synced_at": value}))

    def sync(self) -> bool:
        """
        Возвращает True, если синхронизация прошла успешно.
        Если сети нет — молча возвращает False, изменения
        остаются в очереди на следующий раз (offline-first).
        """
        unsynced = self.storage.get_unsynced()
        local_changes = [note.to_dict() for note in unsynced]
        last_synced_at = self._get_last_synced_at()

        try:
            result = self.api.sync(local_changes, last_synced_at)
        except ApiError:
            return False

        # применяем изменения, пришедшие с сервера (от других устройств)
        for change in result.get("server_changes", []):
            incoming = Note.from_dict(change)
            existing = self.storage.get_by_id(incoming.id)

            if existing is None or incoming.updated_at > existing.updated_at:
                incoming.is_synced = True
                self.storage.save(incoming)

        # локальные изменения, которые сервер подтвердил — помечаем синхронизированными
        for note in unsynced:
            self.storage.mark_synced(note.id)

        self._set_last_synced_at(result["synced_at"])
        return True
