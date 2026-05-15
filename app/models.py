import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


# Association table for note sharing (many-to-many)
note_shares = Table(
    "note_shares",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("note_id", String, ForeignKey("notes.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")
    shared_notes = relationship("Note", secondary=note_shares, back_populates="shared_with")


class Label(Base):
    __tablename__ = "labels"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="labels")


# Association table for note-label (many-to-many)
note_labels = Table(
    "note_labels",
    Base.metadata,
    Column("note_id", String, ForeignKey("notes.id"), primary_key=True),
    Column("label_id", String, ForeignKey("labels.id"), primary_key=True),
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="notes")
    shared_with = relationship("User", secondary=note_shares, back_populates="shared_notes")
    labels = relationship("Label", secondary=note_labels, backref="notes")
