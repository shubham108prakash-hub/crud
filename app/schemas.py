from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# --- User Schemas ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str


# --- Note Schemas ---

class NoteCreate(BaseModel):
    title: str
    content: str = ""


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Share Schema ---

class ShareRequest(BaseModel):
    share_with_email: EmailStr


# --- Label Schemas ---

class LabelCreate(BaseModel):
    name: str


class LabelResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class NoteWithLabelsResponse(NoteResponse):
    labels: list[LabelResponse] = []

    class Config:
        from_attributes = True


# --- Generic ---

class MessageResponse(BaseModel):
    message: str
