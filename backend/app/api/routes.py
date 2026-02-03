from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
import shutil

from app.db.session import get_db
from app.core.config import settings
from app import models, schemas

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/cases", response_model=schemas.CaseRead)
def create_case(payload: schemas.CaseCreate, db: Session = Depends(get_db)):
    obj = models.Case(title=payload.title, description=payload.description)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/cases", response_model=list[schemas.CaseRead])
def list_cases(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Case).order_by(models.Case.id.desc())).all())


@router.get("/cases/{case_id}", response_model=schemas.CaseRead)
def get_case(case_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Case, case_id)
    if not obj:
        raise HTTPException(404, "case not found")
    return obj


@router.post("/slides", response_model=schemas.SlideRead)
def create_slide(payload: schemas.SlideCreate, db: Session = Depends(get_db)):
    case = db.get(models.Case, payload.case_id)
    if not case:
        raise HTTPException(404, "case not found")
    obj = models.Slide(case_id=payload.case_id, label=payload.label, dzi_path=payload.dzi_path)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/cases/{case_id}/slides", response_model=list[schemas.SlideRead])
def list_slides(case_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Slide).where(models.Slide.case_id == case_id).order_by(models.Slide.id.desc())).all())


@router.post("/slides/{slide_id}/attachments", response_model=schemas.AttachmentRead)
def upload_attachment(slide_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    slide = db.get(models.Slide, slide_id)
    if not slide:
        raise HTTPException(404, "slide not found")

    storage_root = Path(settings.storage_root)
    dest_dir = storage_root / "attachments" / str(slide.case_id) / str(slide.id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    obj = models.Attachment(
        slide_id=slide.id,
        filename=file.filename,
        mime_type=file.content_type,
        storage_path=str(dest_path.relative_to(storage_root)),
        size_bytes=dest_path.stat().st_size,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/tasks", response_model=schemas.TaskRead)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    case = db.get(models.Case, payload.case_id)
    if not case:
        raise HTTPException(404, "case not found")
    obj = models.Task(case_id=payload.case_id, title=payload.title, notes=payload.notes)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/tasks/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    obj = db.get(models.Task, task_id)
    if not obj:
        raise HTTPException(404, "task not found")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/cases/{case_id}/tasks", response_model=list[schemas.TaskRead])
def list_tasks(case_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Task).where(models.Task.case_id == case_id).order_by(models.Task.id.desc())).all())
