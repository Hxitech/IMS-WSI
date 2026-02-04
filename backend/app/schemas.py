from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models import TaskStatus


class CaseCreate(BaseModel):
    title: str
    description: str | None = None


class CaseRead(BaseModel):
    id: int
    title: str
    description: str | None
    is_archived: bool
    slide_count: int = 0
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
    is_archived: bool
    label: str

    folder: str | None = None
    filename: str | None = None
    ai_module: str | None = None
    scan_magnification: int | None = None
    ai_suggestion: str | None = None
    processing_status: str | None = None
    label_png_path: str | None = None
    slide_number: int | None = None
    quality: str | None = None
    clarity: str | None = None
    review_result: str | None = None
    updated_at: datetime | None = None

    storage_path: str | None = None
    ingested_ok: bool | None = None
    level_count: int | None = None
    width: int | None = None
    height: int | None = None
    mpp_x: float | None = None
    mpp_y: float | None = None
    thumb_path: str | None = None
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


# --- Auth / Users ---

class UserRead(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    full_name: str | None = None
    role: str = "tech"
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


# --- Task Center ---

class TaskReadWithAssignee(TaskRead):
    assignee_id: int | None = None
    assigned_at: datetime | None = None
    assign_strategy: str | None = None


class TaskAssignManual(BaseModel):
    assignee_id: int | None = None


class TaskAssignAuto(BaseModel):
    strategy: str  # by_count | by_time
    eligible_role: str = "tech"  # doctor | tech
    lookback_minutes: int = 120


class TaskAssignResult(BaseModel):
    task: TaskReadWithAssignee
    assignee: UserRead | None = None
