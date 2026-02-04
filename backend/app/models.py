import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class UserRole(str, enum.Enum):
    admin = "admin"
    doctor = "doctor"
    tech = "tech"


class TaskAssignStrategy(str, enum.Enum):
    manual = "manual"
    by_count = "by_count"
    by_time = "by_time"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.tech)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    slides: Mapped[list["Slide"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class Slide(Base):
    __tablename__ = "slides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    # human/recognized label (from filename/OCR/barcode etc.)
    label: Mapped[str] = mapped_column(String(255))

    # file & ingest metadata
    filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ingested_ok: Mapped[bool] = mapped_column(Boolean, default=False)
    level_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mpp_x: Mapped[float | None] = mapped_column(nullable=True)
    mpp_y: Mapped[float | None] = mapped_column(nullable=True)
    thumb_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # legacy placeholder for future DZI support
    dzi_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="slides")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="slide", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slide_id: Mapped[int] = mapped_column(ForeignKey("slides.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(1024))
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    slide: Mapped[Slide] = relationship(back_populates="attachments")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.todo)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    assign_strategy: Mapped[TaskAssignStrategy] = mapped_column(Enum(TaskAssignStrategy), default=TaskAssignStrategy.manual)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="tasks")
    assignee: Mapped[User | None] = relationship(back_populates="assigned_tasks", foreign_keys=[assignee_id])
