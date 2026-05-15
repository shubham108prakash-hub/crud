from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, Note, Label, note_shares
from app.schemas import NoteCreate, NoteUpdate, NoteResponse, ShareRequest, MessageResponse, LabelCreate, LabelResponse
from app.auth import get_current_user

router = APIRouter()


# ---------- helpers ----------

def _get_own_or_shared_note(note_id: str, user: User, db: Session) -> Note:
    """Return a note if the user owns it or it was shared with them."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id == user.id:
        return note
    if user in note.shared_with:
        return note
    raise HTTPException(status_code=403, detail="Not authorized to access this note")


def _get_own_note(note_id: str, user: User, db: Session) -> Note:
    """Return a note only if the user owns it."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this note")
    return note


# ---------- CRUD ----------

@router.get("/notes", response_model=list[NoteResponse])
def list_notes(
    page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    label: Optional[str] = Query(None, description="Filter by label name"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all notes owned by or shared with the authenticated user. Supports optional pagination and label filtering."""
    query = (
        db.query(Note)
        .filter(
            or_(
                Note.owner_id == user.id,
                Note.shared_with.any(User.id == user.id),
            )
        )
        .order_by(Note.updated_at.desc())
    )
    if label is not None:
        query = query.filter(Note.labels.any(Label.name == label))
    if page is not None:
        query = query.offset((page - 1) * per_page).limit(per_page)
    return query.all()


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(note_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_own_or_shared_note(note_id, user, db)


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    note = Note(title=payload.title, content=payload.content, owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: str, payload: NoteUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = _get_own_note(note_id, user, db)
    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = _get_own_note(note_id, user, db)
    db.delete(note)
    db.commit()
    return None


# ---------- Share ----------

@router.post("/notes/{note_id}/share", response_model=MessageResponse)
def share_note(
    note_id: str,
    payload: ShareRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = _get_own_note(note_id, user, db)

    target_user = db.query(User).filter(User.email == payload.share_with_email).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if target_user.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot share a note with yourself")
    if target_user in note.shared_with:
        raise HTTPException(status_code=400, detail="Note already shared with this user")

    note.shared_with.append(target_user)
    db.commit()
    return {"message": "Note shared successfully"}


# ---------- Search (stretch goal) ----------

@router.get("/search", response_model=list[NoteResponse])
def search_notes(
    q: str = Query(..., min_length=1, description="Search keyword"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full-text search across titles and content of notes the user can access."""
    pattern = f"%{q}%"
    results = (
        db.query(Note)
        .filter(
            or_(
                Note.owner_id == user.id,
                Note.shared_with.any(User.id == user.id),
            )
        )
        .filter(
            or_(
                Note.title.ilike(pattern),
                Note.content.ilike(pattern),
            )
        )
        .order_by(Note.updated_at.desc())
        .all()
    )
    return results


# ---------- Labels (custom feature) ----------

@router.post("/notes/{note_id}/labels", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
def add_label(
    note_id: str,
    payload: LabelCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a label to a note. Creates the label if it doesn't exist for this user."""
    note = _get_own_note(note_id, user, db)
    if not payload.name or not payload.name.strip():
        raise HTTPException(status_code=400, detail="Label name cannot be empty")

    label_name = payload.name.strip().lower()
    # Reuse existing label for this user or create new
    label = db.query(Label).filter(Label.name == label_name, Label.user_id == user.id).first()
    if not label:
        label = Label(name=label_name, user_id=user.id)
        db.add(label)
        db.flush()

    if label in note.labels:
        raise HTTPException(status_code=400, detail="Label already attached to this note")
    note.labels.append(label)
    db.commit()
    db.refresh(label)
    return label


@router.delete("/notes/{note_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_label(
    note_id: str,
    label_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a label from a note."""
    note = _get_own_note(note_id, user, db)
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label or label not in note.labels:
        raise HTTPException(status_code=404, detail="Label not found on this note")
    note.labels.remove(label)
    db.commit()
    return None
