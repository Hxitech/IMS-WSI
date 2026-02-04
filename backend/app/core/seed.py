from sqlalchemy.orm import Session

from app import models
from app.core.security import hash_password


def ensure_seed_users(db: Session) -> None:
    # create default admin if none exists
    existing = db.query(models.User).count() if hasattr(models, 'User') else 0
    if existing:
        return

    users = [
        models.User(username="admin", full_name="Admin", role=models.UserRole.admin, is_active=True, password_hash=hash_password("admin")),
        models.User(username="doctor1", full_name="Doctor One", role=models.UserRole.doctor, is_active=True, password_hash=hash_password("doctor1")),
        models.User(username="tech1", full_name="Tech One", role=models.UserRole.tech, is_active=True, password_hash=hash_password("tech1")),
        models.User(username="tech2", full_name="Tech Two", role=models.UserRole.tech, is_active=True, password_hash=hash_password("tech2")),
    ]
    db.add_all(users)
    db.commit()
