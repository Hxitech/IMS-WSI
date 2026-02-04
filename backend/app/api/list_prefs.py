import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app import models

router = APIRouter(prefix="/list-prefs", tags=["list-prefs"])


@router.get("/{key}")
def get_pref(key: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    row = (
        db.query(models.UserListPref)
        .filter(models.UserListPref.user_id == user.id, models.UserListPref.key == key)
        .one_or_none()
    )
    if not row:
        return {"key": key, "value": None}
    try:
        val = json.loads(row.value_json)
    except Exception:
        val = None
    return {"key": key, "value": val}


@router.put("/{key}")
def set_pref(key: str, payload: dict, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    value = payload.get("value")
    row = (
        db.query(models.UserListPref)
        .filter(models.UserListPref.user_id == user.id, models.UserListPref.key == key)
        .one_or_none()
    )
    if not row:
        row = models.UserListPref(user_id=user.id, key=key, value_json=json.dumps(value))
    else:
        row.value_json = json.dumps(value)
    db.add(row)
    db.commit()
    return {"key": key, "value": value}
