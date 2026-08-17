"""
Тесты для core/storage.py.

Используем временный файл БД для каждого теста (tmp_path — это
встроенная pytest-фикстура), чтобы тесты не мешали друг другу
и не трогали настоящую базу пользователя.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.storage import Storage
from core.models import Note


def make_storage(tmp_path) -> Storage:
    return Storage(db_path=tmp_path / "test_notes.sqlite3")


def test_save_and_get_note(tmp_path):
    storage = make_storage(tmp_path)
    note = Note(content="Первая заметка")

    storage.save(note)
    fetched = storage.get_by_id(note.id)

    assert fetched is not None
    assert fetched.content == "Первая заметка"


def test_get_all_excludes_deleted_by_default(tmp_path):
    storage = make_storage(tmp_path)

    note1 = Note(content="Видимая")
    note2 = Note(content="Удалённая")
    storage.save(note1)
    storage.save(note2)
    storage.soft_delete(note2.id)

    all_notes = storage.get_all()

    assert len(all_notes) == 1
    assert all_notes[0].content == "Видимая"


def test_soft_delete_does_not_remove_row(tmp_path):
    storage = make_storage(tmp_path)
    note = Note(content="Заметка")
    storage.save(note)

    storage.soft_delete(note.id)

    # заметка всё ещё физически в базе, просто помечена
    all_including_deleted = storage.get_all(include_deleted=True)
    assert len(all_including_deleted) == 1
    assert all_including_deleted[0].is_deleted is True


def test_get_unsynced_returns_only_unsynced(tmp_path):
    storage = make_storage(tmp_path)

    note1 = Note(content="Не синхронизирована", is_synced=False)
    note2 = Note(content="Синхронизирована", is_synced=True)
    storage.save(note1)
    storage.save(note2)

    unsynced = storage.get_unsynced()

    assert len(unsynced) == 1
    assert unsynced[0].id == note1.id


def test_mark_synced_updates_flag(tmp_path):
    storage = make_storage(tmp_path)
    note = Note(content="Заметка", is_synced=False)
    storage.save(note)

    storage.mark_synced(note.id)
    fetched = storage.get_by_id(note.id)

    assert fetched.is_synced is True
