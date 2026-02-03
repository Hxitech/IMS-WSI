from datetime import datetime
from pydantic import BaseModel

from app.models import TaskStatus


class CaseCreate(BaseModel):
    title: str
    description: str | None = None


class CaseRead(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class SlideCreate(BaseModel):
    case_id: int
    label: str
    dzi_path: str | None = None


class SlideRead(BaseModel):
    id: int
    case_id: int
    label: str
    dzi_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentRead(BaseModel):
    id: int
    slide_id: int
    filename: str
    mime_type: str | None
    storage_path: str
    size_bytes: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    case_id: int
    title: str
    notes: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None
    status: TaskStatus | None = None
    is_archived: bool | None = None


class TaskRead(BaseModel):
    id: int
    case_id: int
    title: str
    notes: str | None
    status: TaskStatus
    is_archived: bool
    created_at: datetime

    class Config:
        from_attributes = True
