# Notes App — Backend (FastAPI)

## Запуск локально (без Docker)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

По умолчанию использует SQLite (`notes_dev.db`) — Postgres не нужен
для быстрой локальной проверки. Документация API появится на
http://localhost:8000/docs

## Запуск через Docker (см. корневой docker-compose.yml)

```bash
docker-compose up -d
```

## Переменные окружения

См. `.env.example` в корне проекта. Обязательные для прода:
`DATABASE_URL`, `SECRET_KEY`.

## Тесты

```bash
pip install pytest httpx
python -m pytest tests/ -v
```

14 тестов: регистрация/логин, CRUD заметок, изоляция заметок
между пользователями, синхронизация (включая разрешение конфликтов).

## Эндпоинты

| Метод | Путь | Auth | Описание |
|---|---|---|---|
| GET | `/health` | нет | проверка живости (для мониторинга) |
| POST | `/auth/register` | нет | регистрация |
| POST | `/auth/login` | нет | логин, возвращает JWT |
| GET | `/notes` | да | список своих заметок |
| POST | `/notes` | да | создать заметку |
| PUT | `/notes/{id}` | да | обновить заметку |
| DELETE | `/notes/{id}` | да | удалить (soft-delete) |
| POST | `/sync` | да | синхронизация с клиентом |

## Миграции (Alembic)

Пока схема БД создаётся автоматически при старте (`Base.metadata.create_all`
в `main.py`) — удобно для разработки. На проде вместо этого:

```bash
alembic revision --autogenerate -m "описание изменения"
alembic upgrade head
```

## Известные ограничения (MVP)

- Разрешение конфликтов синка — простое правило "кто новее, тот победил"
  по `updated_at`, без ручного мержа
- Нет rate-limiting на `/auth/login` (защита от подбора пароля) — стоит
  добавить перед реальным продакшеном
- Нет refresh-токенов — только access-токен с фиксированным сроком жизни
