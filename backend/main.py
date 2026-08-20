"""
Точка входа backend-приложения.

Создаёт FastAPI-приложение, подключает роутеры, создаёт таблицы
в БД при старте (для локальной разработки — на проде схему
БД лучше вести через Alembic-миграции, см. alembic/).
"""

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, notes, sync

# создаёт таблицы, если их ещё нет — удобно для локальной разработки,
# на проде вместо этого используются миграции (alembic upgrade head)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes App API")

app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(sync.router)


@app.get("/health")
def health():
    """Используется docker-compose healthcheck и мониторингом (Uptime Kuma и т.д.)."""
    return {"status": "ok"}
