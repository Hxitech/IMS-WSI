from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models, schemas
from app.core.security import (
    create_access_token,
    get_current_user,
    get_user_by_username,
    hash_password,
    verify_password,
    require_roles,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, payload.username)
    if not user or not user.is_active:
        raise HTTPException(401, "invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "invalid credentials")
    token = create_access_token(user_id=user.id, role=user.role)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=schemas.UserRead)
def me(user: models.User = Depends(get_current_user)):
    return user


# --- Users admin ---

@router.get("/users", response_model=list[schemas.UserRead])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))):
    return db.query(models.User).order_by(models.User.id.asc()).all()


@router.post("/users", response_model=schemas.UserRead)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))):
    if get_user_by_username(db, payload.username):
        raise HTTPException(409, "username already exists")
    role = payload.role
    if role not in ("admin", "doctor", "tech"):
        raise HTTPException(400, "invalid role")
    obj = models.User(
        username=payload.username,
        full_name=payload.full_name,
        role=role,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/users/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_roles("admin"))):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "user not found")
    data = payload.model_dump(exclude_unset=True)
    if "role" in data and data["role"] is not None:
        if data["role"] not in ("admin", "doctor", "tech"):
            raise HTTPException(400, "invalid role")
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data.pop("password"))
    for k, v in data.items():
        setattr(user, k, v)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
