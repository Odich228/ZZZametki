def test_create_note(client, auth_headers):
    response = client.post(
        "/notes", json={"content": "Моя первая заметка"}, headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["content"] == "Моя первая заметка"


def test_list_notes_returns_only_own_notes(client, auth_headers):
    client.post("/notes", json={"content": "Заметка 1"}, headers=auth_headers)
    client.post("/notes", json={"content": "Заметка 2"}, headers=auth_headers)

    response = client.get("/notes", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_note(client, auth_headers):
    create_resp = client.post(
        "/notes", json={"content": "Старый текст"}, headers=auth_headers
    )
    note_id = create_resp.json()["id"]

    response = client.put(
        f"/notes/{note_id}", json={"content": "Новый текст"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Новый текст"


def test_delete_note_is_soft_delete(client, auth_headers):
    create_resp = client.post(
        "/notes", json={"content": "Удаляемая заметка"}, headers=auth_headers
    )
    note_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    list_resp = client.get("/notes", headers=auth_headers)
    ids = [note["id"] for note in list_resp.json()]
    assert note_id not in ids


def test_cannot_access_note_of_another_user(client):
    # первый пользователь создаёт заметку
    client.post("/auth/register", json={"email": "u1@example.com", "password": "pass1234"})
    login1 = client.post("/auth/login", json={"email": "u1@example.com", "password": "pass1234"})
    headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

    create_resp = client.post("/notes", json={"content": "Секрет"}, headers=headers1)
    note_id = create_resp.json()["id"]

    # второй пользователь пытается получить доступ
    client.post("/auth/register", json={"email": "u2@example.com", "password": "pass1234"})
    login2 = client.post("/auth/login", json={"email": "u2@example.com", "password": "pass1234"})
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    response = client.put(
        f"/notes/{note_id}", json={"content": "Взлом"}, headers=headers2
    )

    assert response.status_code == 404
