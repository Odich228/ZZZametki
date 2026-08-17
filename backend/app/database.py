"""
Подключение к базе данных.

engine — единая точка подключения к БД (Postgres на проде,
SQLite по умолчанию для локальной разработки без Docker).

get_db() — dependency для FastAPI: открывает сессию на время
одного запроса и обязательно закрывает её после, даже если
запрос упал с ошибкой (через try/finally).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
