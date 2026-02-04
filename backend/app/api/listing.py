from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, asc, desc

from app.db.session import get_db
from app.core.security import get_current_user
from app import models

router = APIRouter(tags=["listing"])


CASE_SORT_FIELDS = {
    "id": models.Case.id,
    "title": models.Case.title,
    "created_at": models.Case.created_at,
    "slide_count": None,  # special
}

SLIDE_SORT_FIELDS = {
    "id": models.Slide.id,
    "label": models.Slide.label,
    "filename": models.Slide.filename,
    "folder": models.Slide.folder,
    "processing_status": models.Slide.processing_status,
    "scan_magnification": models.Slide.scan_magnification,
    "updated_at": models.Slide.updated_at,
    "created_at": models.Slide.created_at,
    "slide_number": models.Slide.slide_number,
}


@router.get("/cases")
def list_cases(
    q: str | None = None,
    is_archived: bool | None = None,
    sort: str = "id",
    order: str = "desc",
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    slide_count = func.count(models.Slide.id).label("slide_count")
    stmt = (
        db.query(models.Case, slide_count)
        .outerjoin(models.Slide, (models.Slide.case_id == models.Case.id) & (models.Slide.is_archived == func.false()))
        .group_by(models.Case.id)
    )

    if is_archived is not None:
        stmt = stmt.filter(models.Case.is_archived == is_archived)

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.filter(or_(models.Case.title.ilike(like), models.Case.description.ilike(like)))

    sort_col = CASE_SORT_FIELDS.get(sort, models.Case.id)
    if sort == "slide_count":
        sort_expr = slide_count
    else:
        sort_expr = sort_col

    sort_expr = asc(sort_expr) if order.lower() == "asc" else desc(sort_expr)
    stmt = stmt.order_by(sort_expr)

    total = stmt.count()
    rows = stmt.offset(offset).limit(limit).all()
    items = []
    for case, sc in rows:
        items.append(
            {
                "id": case.id,
                "title": case.title,
                "description": case.description,
                "is_archived": case.is_archived,
                "created_at": case.created_at,
                "slide_count": int(sc or 0),
            }
        )

    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/cases/{case_id}/slides")
def list_slides(
    case_id: int,
    q: str | None = None,
    is_archived: bool | None = None,
    processing_status: str | None = None,
    review_result: str | None = None,
    quality: str | None = None,
    clarity: str | None = None,
    ai_module: str | None = None,
    scan_magnification: int | None = None,
    sort: str = "id",
    order: str = "desc",
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    stmt = db.query(models.Slide).filter(models.Slide.case_id == case_id)

    if is_archived is not None:
        stmt = stmt.filter(models.Slide.is_archived == is_archived)

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.filter(
            or_(
                models.Slide.label.ilike(like),
                models.Slide.filename.ilike(like),
                models.Slide.folder.ilike(like),
                models.Slide.ai_module.ilike(like),
                models.Slide.processing_status.ilike(like),
            )
        )

    if processing_status:
        stmt = stmt.filter(models.Slide.processing_status == processing_status)
    if review_result:
        stmt = stmt.filter(models.Slide.review_result == review_result)
    if quality:
        stmt = stmt.filter(models.Slide.quality == quality)
    if clarity:
        stmt = stmt.filter(models.Slide.clarity == clarity)
    if ai_module:
        stmt = stmt.filter(models.Slide.ai_module == ai_module)
    if scan_magnification is not None:
        stmt = stmt.filter(models.Slide.scan_magnification == scan_magnification)

    sort_col = SLIDE_SORT_FIELDS.get(sort, models.Slide.id)
    sort_expr = asc(sort_col) if order.lower() == "asc" else desc(sort_col)
    stmt = stmt.order_by(sort_expr)

    total = stmt.count()
    items = stmt.offset(offset).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
