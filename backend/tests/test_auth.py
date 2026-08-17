def test_register_new_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"


def test_register_duplicate_email_fails(client):
    payload = {"email": "bob@example.com", "password": "secret123"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_login_with_correct_credentials(client):
    client.post(
        "/auth/register",
        json={"email": "carol@example.com", "password": "secret123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "carol@example.com", "password": "secret123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client):
    client.post(
        "/auth/register",
        json={"email": "dave@example.com", "password": "secret123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "dave@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_notes_endpoint_requires_auth(client):
    response = client.get("/notes")
    assert response.status_code == 401
