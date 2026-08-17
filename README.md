# Notes App

Заметки с офлайн-режимом и синхронизацией между устройствами.
Клиент на Kivy (desktop/Android), backend на FastAPI + PostgreSQL.

## Быстрый старт (локально)

```bash
cp .env.example .env
# впиши свои локальные значения в .env

docker-compose up -d
```

Backend поднимется на http://localhost:8000, документация API — на
http://localhost:8000/docs

Запуск клиента (отдельно, не в Docker):
```bash
cd client
pip install -r requirements.txt
python main.py
```

## Структура проекта

```
notes-app/
├── client/          # Kivy-приложение
├── backend/         # FastAPI API
├── nginx/           # reverse proxy конфиг (для прода)
├── scripts/         # бэкапы, ручной деплой
├── terraform/        # инфраструктура как код (опционально)
└── .github/workflows/ # CI/CD
```

## Разработка

- Ветки: `feature/<название>`, PR в `main` только через прохождение CI
- Тесты гоняются автоматически на каждый push/PR (см. `.github/workflows/test.yml`)

## Деплой на прод

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Автоматический деплой происходит через GitHub Actions при мерже в `main`,
после успешного прохождения тестов (см. `.github/workflows/deploy.yml`).

## Тесты

```bash
# backend
cd backend && python -m pytest -v

# client
cd client && python -m pytest -v
```
