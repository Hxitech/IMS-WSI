from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
import shutil

from app.db.session import get_db
from app.core.config import settings
from app import models, schemas
from app.services.openslide_service import read_meta_and_thumbnail
from app.api.auth import router as auth_router
from app.api.task_center import router as task_center_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(task_center_router)


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


@router.post("/cases/{case_id}/slides/upload", response_model=schemas.SlideRead)
def upload_slide(case_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(404, "case not found")

    # create slide record first
    label = Path(file.filename).stem
    slide = models.Slide(case_id=case_id, label=label, filename=file.filename)
    db.add(slide)
    db.commit()
    db.refresh(slide)

    storage_root = Path(settings.storage_root)
    dest_dir = storage_root / "slides" / str(case_id) / str(slide.id) / "raw"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename

    with dest_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # openslide ingest + thumbnail
    thumb_path = storage_root / "slides" / str(case_id) / str(slide.id) / "thumb.jpg"
    try:
        meta = read_meta_and_thumbnail(str(dest_path), str(thumb_path))
        slide.ingested_ok = True
        slide.level_count = meta.level_count
        slide.width = meta.width
        slide.height = meta.height
        slide.mpp_x = meta.mpp_x
        slide.mpp_y = meta.mpp_y
        slide.thumb_path = str(thumb_path.relative_to(storage_root))
    except Exception:
        slide.ingested_ok = False

    slide.storage_path = str(dest_path.relative_to(storage_root))

    db.add(slide)
    db.commit()
    db.refresh(slide)
    return slide


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


@router.get("/slides/{slide_id}", response_model=schemas.SlideRead)
def get_slide(slide_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Slide, slide_id)
    if not obj:
        raise HTTPException(404, "slide not found")
    return obj


@router.get("/slides/{slide_id}/info")
def slide_info(slide_id: int, tileSize: int = 256, db: Session = Depends(get_db)):
    slide = db.get(models.Slide, slide_id)
    if not slide:
        raise HTTPException(404, "slide not found")
    if not slide.ingested_ok or not slide.storage_path or not slide.width or not slide.height or not slide.level_count:
        raise HTTPException(409, "slide not ingested")

    # Provide all level dimensions for OpenSeadragon custom tile source.
    # Level index 0 is highest resolution.
    dims = []
    for level in range(int(slide.level_count)):
        ds = 2**level
        dims.append({"level": level, "width": (slide.width + ds - 1)//ds, "height": (slide.height + ds - 1)//ds})

    return {
        "id": slide.id,
        "case_id": slide.case_id,
        "label": slide.label,
        "tileSize": tileSize,
        "level_count": int(slide.level_count),
        "width": int(slide.width),
        "height": int(slide.height),
        "levels": dims,
        "mpp_x": slide.mpp_x,
        "mpp_y": slide.mpp_y,
        "thumb_url": f"/files/{slide.thumb_path}" if slide.thumb_path else None,
    }


@router.get("/slides/{slide_id}/tile/{level}/{x}/{y}.jpg")
def slide_tile(slide_id: int, level: int, x: int, y: int, tileSize: int = 256, db: Session = Depends(get_db)):
    slide = db.get(models.Slide, slide_id)
    if not slide:
        raise HTTPException(404, "slide not found")
    if not slide.ingested_ok or not slide.storage_path:
        raise HTTPException(409, "slide not ingested")

    if level < 0 or x < 0 or y < 0:
        raise HTTPException(400, "invalid tile coordinate")

    from pathlib import Path
    storage_root = Path(settings.storage_root)
    cache_path = storage_root / "tiles" / str(slide_id) / str(level) / f"{x}_{y}.jpg"
    if cache_path.exists():
        return FileResponse(str(cache_path), media_type="image/jpeg")

    slide_path = storage_root / slide.storage_path

    try:
        import openslide  # type: ignore
    except Exception as e:
        raise HTTPException(500, "openslide not available") from e

    if not slide_path.exists():
        raise HTTPException(404, "slide file not found")

    osr = openslide.OpenSlide(str(slide_path))
    try:
        if level >= osr.level_count:
            raise HTTPException(404, "level out of range")

        downsample = float(osr.level_downsamples[level])
        base_x = int(x * tileSize * downsample)
        base_y = int(y * tileSize * downsample)

        region = osr.read_region((base_x, base_y), level, (tileSize, tileSize))
        img = region.convert("RGB")

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(cache_path), format="JPEG", quality=85, optimize=True)
        return FileResponse(str(cache_path), media_type="image/jpeg")
    finally:
        try:
            osr.close()
        except Exception:
            pass
