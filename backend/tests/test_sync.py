def test_sync_uploads_new_note(client, auth_headers):
    response = client.post(
        "/sync",
        json={
            "changes": [
                {
                    "id": "note-1",
                    "content": "Заметка с телефона",
                    "updated_at": "2026-01-01T10:00:00+00:00",
                    "is_deleted": False,
                }
            ],
            "last_synced_at": None,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    notes = client.get("/notes", headers=auth_headers).json()
    assert len(notes) == 1
    assert notes[0]["content"] == "Заметка с телефона"


def test_sync_returns_server_changes_after_checkpoint(client, auth_headers):
    # создаём заметку напрямую через обычный CRUD (как будто с другого устройства)
    client.post("/notes", json={"content": "С другого устройства"}, headers=auth_headers)

    response = client.post(
        "/sync",
        json={"changes": [], "last_synced_at": "2020-01-01T00:00:00+00:00"},
        headers=auth_headers,
    )

    data = response.json()
    assert len(data["server_changes"]) == 1
    assert data["server_changes"][0]["content"] == "С другого устройства"


def test_sync_conflict_newer_client_change_wins(client, auth_headers):
    # сервер уже что-то знает про заметку
    client.post(
        "/sync",
        json={
            "changes": [
                {
                    "id": "note-conflict",
                    "content": "Старая версия",
                    "updated_at": "2026-01-01T10:00:00+00:00",
                    "is_deleted": False,
                }
            ],
            "last_synced_at": None,
        },
        headers=auth_headers,
    )

    # клиент присылает более новую версию той же заметки
    response = client.post(
        "/sync",
        json={
            "changes": [
                {
                    "id": "note-conflict",
                    "content": "Новая версия",
                    "updated_at": "2026-01-01T12:00:00+00:00",
                    "is_deleted": False,
                }
            ],
            "last_synced_at": "2020-01-01T00:00:00+00:00",
        },
        headers=auth_headers,
    )

    server_changes = response.json()["server_changes"]
    matching = [n for n in server_changes if n["id"] == "note-conflict"]
    assert matching[0]["content"] == "Новая версия"


def test_sync_conflict_older_client_change_loses(client, auth_headers):
    client.post(
        "/sync",
        json={
            "changes": [
                {
                    "id": "note-conflict-2",
                    "content": "Актуальная версия на сервере",
                    "updated_at": "2026-01-01T12:00:00+00:00",
                    "is_deleted": False,
                }
            ],
            "last_synced_at": None,
        },
        headers=auth_headers,
    )

    # клиент присылает УСТАРЕВШУЮ версию (более раннее время)
    response = client.post(
        "/sync",
        json={
            "changes": [
                {
                    "id": "note-conflict-2",
                    "content": "Старая версия с оффлайн-устройства",
                    "updated_at": "2026-01-01T09:00:00+00:00",
                    "is_deleted": False,
                }
            ],
            "last_synced_at": "2020-01-01T00:00:00+00:00",
        },
        headers=auth_headers,
    )

    server_changes = response.json()["server_changes"]
    matching = [n for n in server_changes if n["id"] == "note-conflict-2"]
    assert matching[0]["content"] == "Актуальная версия на сервере"
