"""
Модели таблиц БД (SQLAlchemy ORM).

User — пользователь, Note — заметка, привязанная к пользователю
через user_id (внешний ключ). Одна заметка принадлежит ровно
одному пользователю — заметки разных пользователей никогда
не пересекаются.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now)

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    # id генерируется на КЛИЕНТЕ (uuid) и приходит как есть —
    # это важно для оффлайн-синка: заметка, созданная без сети,
    # уже должна иметь окончательный id, чтобы потом не путаться
    # при мерже с сервером.
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(String, nullable=False, default="")
    updated_at = Column(String, nullable=False)  # ISO-строка, как присылает клиент
    is_deleted = Column(Boolean, nullable=False, default=False)

    owner = relationship("User", back_populates="notes")
