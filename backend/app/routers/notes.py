import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Note, User
from app.schemas import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("", response_model=List[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notes = (
        db.query(Note)
        .filter(Note.user_id == current_user.id, Note.is_deleted == False)  # noqa: E712
        .order_by(Note.updated_at.desc())
        .all()
    )
    return notes


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = Note(
        id=payload.id or str(uuid.uuid4()),
        user_id=current_user.id,
        content=payload.content,
        updated_at=_now_iso(),
        is_deleted=False,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def _get_owned_note(note_id: str, db: Session, current_user: User) -> Note:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == current_user.id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note


@router.put("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: str,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_owned_note(note_id, db, current_user)
    note.content = payload.content
    note.updated_at = _now_iso()
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    note = _get_owned_note(note_id, db, current_user)
    note.is_deleted = True
    note.updated_at = _now_iso()
    db.commit()
    return None
