"""
Тонкая обёртка над HTTP-запросами к backend.

Ничего не знает про SQLite и про Kivy — только формирует
запросы и разбирает ответы. Логика синхронизации (что с этим
дальше делать) живёт в sync.py.
"""

import os
from typing import List, Optional

import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


class ApiError(Exception):
    """Любая ошибка сети или ответа backend с кодом != 2xx."""


class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, email: str, password: str) -> str:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10,
        )
        if response.status_code != 200:
            raise ApiError(f"Login failed: {response.status_code} {response.text}")
        self.token = response.json()["access_token"]
        return self.token

    def register(self, email: str, password: str) -> None:
        response = requests.post(
            f"{self.base_url}/auth/register",
            json={"email": email, "password": password},
            timeout=10,
        )
        if response.status_code != 201:
            raise ApiError(f"Register failed: {response.status_code} {response.text}")

    def sync(self, local_changes: List[dict], last_synced_at: Optional[str]) -> dict:
        """
        Отправляет локальные изменения, получает изменения с сервера.
        Возвращает словарь вида {"server_changes": [...], "synced_at": "..."}
        """
        response = requests.post(
            f"{self.base_url}/sync",
            json={
                "changes": local_changes,
                "last_synced_at": last_synced_at,
            },
            headers=self._headers(),
            timeout=15,
        )
        if response.status_code != 200:
            raise ApiError(f"Sync failed: {response.status_code} {response.text}")
        return response.json()
