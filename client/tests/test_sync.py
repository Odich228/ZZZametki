"""
Тесты для core/sync.py.

Реальный backend здесь не поднимаем — вместо ApiClient подставляем
"поддельный" объект (fake), который ведёт себя как API, но ничего
никуда не отправляет по сети. Это классический приём: тестируем
ЛОГИКУ синка (что делает SyncManager с данными), а не саму сеть.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.storage import Storage
from core.models import Note
from core.sync import SyncManager
from core.api_client import ApiError


class FakeApiClient:
    """Подделка ApiClient — не ходит в сеть, просто возвращает то, что скажем."""

    def __init__(self, sync_response=None, raise_error=False):
        self.sync_response = sync_response or {"server_changes": [], "synced_at": "2026-01-01T00:00:00+00:00"}
        self.raise_error = raise_error
        self.last_call_args = None

    def sync(self, local_changes, last_synced_at):
        self.last_call_args = (local_changes, last_synced_at)
        if self.raise_error:
            raise ApiError("network is down")
        return self.sync_response


def make_sync_manager(tmp_path, fake_api):
    storage = Storage(db_path=tmp_path / "notes.sqlite3")
    return SyncManager(storage, fake_api), storage


def test_sync_sends_unsynced_notes(tmp_path):
    fake_api = FakeApiClient()
    manager, storage = make_sync_manager(tmp_path, fake_api)

    note = Note(content="Локальная заметка", is_synced=False)
    storage.save(note)

    manager.sync()

    sent_changes, _ = fake_api.last_call_args
    assert len(sent_changes) == 1
    assert sent_changes[0]["content"] == "Локальная заметка"


def test_sync_marks_notes_as_synced_after_success(tmp_path):
    fake_api = FakeApiClient()
    manager, storage = make_sync_manager(tmp_path, fake_api)

    note = Note(content="Заметка", is_synced=False)
    storage.save(note)

    manager.sync()

    fetched = storage.get_by_id(note.id)
    assert fetched.is_synced is True


def test_sync_applies_incoming_server_changes(tmp_path):
    server_note = {
        "id": "note-from-server",
        "content": "Пришло с другого устройства",
        "updated_at": "2026-01-01T10:00:00+00:00",
        "is_deleted": False,
    }
    fake_api = FakeApiClient(
        sync_response={"server_changes": [server_note], "synced_at": "2026-01-01T10:00:01+00:00"}
    )
    manager, storage = make_sync_manager(tmp_path, fake_api)

    manager.sync()

    fetched = storage.get_by_id("note-from-server")
    assert fetched is not None
    assert fetched.content == "Пришло с другого устройства"
    assert fetched.is_synced is True


def test_sync_returns_false_on_network_error(tmp_path):
    fake_api = FakeApiClient(raise_error=True)
    manager, storage = make_sync_manager(tmp_path, fake_api)

    note = Note(content="Офлайн заметка", is_synced=False)
    storage.save(note)

    result = manager.sync()

    assert result is False
    # заметка остаётся несинхронизированной — попробуем снова в следующий раз
    fetched = storage.get_by_id(note.id)
    assert fetched.is_synced is False


def test_sync_conflict_local_newer_wins_over_local_copy(tmp_path):
    """
    Если с сервера пришла заметка, которая старше локальной версии —
    локальная версия НЕ должна перезаписаться устаревшими данными.
    """
    fake_api = FakeApiClient()
    manager, storage = make_sync_manager(tmp_path, fake_api)

    local_note = Note(
        id="shared-note",
        content="Новая локальная версия",
        updated_at="2026-01-01T12:00:00+00:00",
        is_synced=True,
    )
    storage.save(local_note)

    fake_api.sync_response = {
        "server_changes": [
            {
                "id": "shared-note",
                "content": "Устаревшая версия с сервера",
                "updated_at": "2026-01-01T09:00:00+00:00",
                "is_deleted": False,
            }
        ],
        "synced_at": "2026-01-01T12:00:01+00:00",
    }

    manager.sync()

    fetched = storage.get_by_id("shared-note")
    assert fetched.content == "Новая локальная версия"
