"""
Тесты для core/api_client.py.

Реальную сеть не используем — подменяем requests.post через
unittest.mock, чтобы проверить, что ApiClient формирует правильные
запросы и правильно разбирает ответы/ошибки, без необходимости
поднимать настоящий backend.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.api_client import ApiClient, ApiError


def make_response(status_code, json_data):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.text = str(json_data)
    return response


@patch("core.api_client.requests.post")
def test_login_success_sets_token(mock_post):
    mock_post.return_value = make_response(200, {"access_token": "fake-jwt-token"})

    client = ApiClient(base_url="http://testserver")
    token = client.login("user@example.com", "password123")

    assert token == "fake-jwt-token"
    assert client.token == "fake-jwt-token"

    # проверяем, что запрос ушёл на правильный URL с правильным телом
    called_url = mock_post.call_args[0][0]
    called_json = mock_post.call_args[1]["json"]
    assert called_url == "http://testserver/auth/login"
    assert called_json == {"email": "user@example.com", "password": "password123"}


@patch("core.api_client.requests.post")
def test_login_failure_raises_api_error(mock_post):
    mock_post.return_value = make_response(401, {"detail": "Неверный пароль"})

    client = ApiClient(base_url="http://testserver")

    with pytest.raises(ApiError):
        client.login("user@example.com", "wrong-password")


@patch("core.api_client.requests.post")
def test_sync_sends_bearer_token_when_authenticated(mock_post):
    mock_post.return_value = make_response(
        200, {"server_changes": [], "synced_at": "2026-01-01T00:00:00+00:00"}
    )

    client = ApiClient(base_url="http://testserver")
    client.token = "some-token"

    client.sync(local_changes=[], last_synced_at=None)

    called_headers = mock_post.call_args[1]["headers"]
    assert called_headers["Authorization"] == "Bearer some-token"


@patch("core.api_client.requests.post")
def test_sync_returns_parsed_json_on_success(mock_post):
    expected = {"server_changes": [{"id": "1", "content": "x"}], "synced_at": "now"}
    mock_post.return_value = make_response(200, expected)

    client = ApiClient(base_url="http://testserver")
    result = client.sync(local_changes=[], last_synced_at=None)

    assert result == expected


@patch("core.api_client.requests.post")
def test_sync_raises_on_server_error(mock_post):
    mock_post.return_value = make_response(500, {"detail": "internal error"})

    client = ApiClient(base_url="http://testserver")

    with pytest.raises(ApiError):
        client.sync(local_changes=[], last_synced_at=None)
