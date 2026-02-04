from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.security import get_current_user, require_roles
from app.db.session import get_db

router = APIRouter(prefix="/task-center", tags=["task-center"])


def _task_to_read(task: models.Task) -> schemas.TaskReadWithAssignee:
    return schemas.TaskReadWithAssignee.model_validate(task)


@router.get("/tasks", response_model=list[schemas.TaskReadWithAssignee])
def list_task_center_tasks(
    include_archived: bool = False,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = select(models.Task)
    if not include_archived:
        q = q.where(models.Task.is_archived == False)  # noqa: E712
    # doctors/techs see all tasks for now; could filter by assignee later
    tasks = list(db.scalars(q.order_by(models.Task.id.desc())).all())
    return [_task_to_read(t) for t in tasks]


@router.post("/tasks/{task_id}/assign", response_model=schemas.TaskAssignResult)
def assign_task_manual(
    task_id: int,
    payload: schemas.TaskAssignManual,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles("admin", "doctor")),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(404, "task not found")

    assignee = None
    if payload.assignee_id is not None:
        assignee = db.get(models.User, payload.assignee_id)
        if not assignee or not assignee.is_active:
            raise HTTPException(404, "assignee not found")

    task.assignee_id = payload.assignee_id
    task.assigned_at = datetime.utcnow() if payload.assignee_id is not None else None
    task.assign_strategy = models.TaskAssignStrategy.manual
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"task": _task_to_read(task), "assignee": assignee}


@router.post("/tasks/{task_id}/auto-assign", response_model=schemas.TaskAssignResult)
def assign_task_auto(
    task_id: int,
    payload: schemas.TaskAssignAuto,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_roles("admin", "doctor")),
):
    task = db.get(models.Task, task_id)
    if not task:
        raise HTTPException(404, "task not found")

    if payload.strategy not in ("by_count", "by_time"):
        raise HTTPException(400, "invalid strategy")
    if payload.eligible_role not in ("doctor", "tech"):
        raise HTTPException(400, "invalid eligible_role")

    eligible = list(
        db.scalars(
            select(models.User)
            .where(models.User.is_active == True)  # noqa: E712
            .where(models.User.role == payload.eligible_role)
            .order_by(models.User.id.asc())
        ).all()
    )
    if not eligible:
        raise HTTPException(409, "no eligible users")

    now = datetime.utcnow()
    if payload.strategy == "by_count":
        # pick user with fewest open (not done, not archived) tasks
        counts = dict(
            db.execute(
                select(models.Task.assignee_id, func.count(models.Task.id))
                .where(models.Task.assignee_id.is_not(None))
                .where(models.Task.is_archived == False)  # noqa: E712
                .where(models.Task.status != models.TaskStatus.done)
                .group_by(models.Task.assignee_id)
            ).all()
        )
        chosen = min(eligible, key=lambda u: (counts.get(u.id, 0), u.id))
        task.assign_strategy = models.TaskAssignStrategy.by_count
    else:
        lookback = max(1, int(payload.lookback_minutes))
        since = now - timedelta(minutes=lookback)
        # pick user with fewest assignments in lookback window
        counts = dict(
            db.execute(
                select(models.Task.assignee_id, func.count(models.Task.id))
                .where(models.Task.assignee_id.is_not(None))
                .where(models.Task.assigned_at.is_not(None))
                .where(models.Task.assigned_at >= since)
                .group_by(models.Task.assignee_id)
            ).all()
        )
        chosen = min(eligible, key=lambda u: (counts.get(u.id, 0), u.id))
        task.assign_strategy = models.TaskAssignStrategy.by_time

    task.assignee_id = chosen.id
    task.assigned_at = now
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"task": _task_to_read(task), "assignee": chosen}


@router.get("/users", response_model=list[schemas.UserRead])
def list_assignable_users(
    role: str | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    q = select(models.User).where(models.User.is_active == True)  # noqa: E712
    if role:
        q = q.where(models.User.role == role)
    return list(db.scalars(q.order_by(models.User.id.asc())).all())
