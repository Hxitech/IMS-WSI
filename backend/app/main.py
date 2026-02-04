from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router
from app.api.static import router as static_router
from app.db.session import SessionLocal
from app.core.seed import ensure_seed_users

app = FastAPI(title="App API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"] ,
)

app.include_router(router)
app.include_router(static_router)


@app.on_event("startup")
def _seed_users():
    try:
        db = SessionLocal()
        ensure_seed_users(db)
    finally:
        try:
            db.close()
        except Exception:
            pass
