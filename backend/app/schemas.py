"""
Pydantic-схемы: описывают, что API принимает на вход и что отдаёт
наружу. Отдельно от SQLAlchemy-моделей (models.py) намеренно —
модели описывают таблицу в БД, схемы описывают контракт API,
это разные вещи, даже если поля местами совпадают.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Notes ----------

class NoteCreate(BaseModel):
    id: Optional[str] = None
    content: str = ""


class NoteUpdate(BaseModel):
    content: str


class NoteRead(BaseModel):
    id: str
    content: str
    updated_at: str
    is_deleted: bool

    model_config = {"from_attributes": True}


# ---------- Sync ----------

class SyncChange(BaseModel):
    id: str
    content: str
    updated_at: str
    is_deleted: bool = False


class SyncRequest(BaseModel):
    changes: List[SyncChange] = []
    last_synced_at: Optional[str] = None


class SyncResponse(BaseModel):
    server_changes: List[NoteRead]
    synced_at: str
