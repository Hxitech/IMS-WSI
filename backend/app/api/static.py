from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import settings

router = APIRouter()


@router.get("/files/{rel_path:path}")
def get_file(rel_path: str):
    """Serve a file from STORAGE_ROOT. For MVP only (no auth)."""
    root = Path(settings.storage_root).resolve()
    target = (root / rel_path).resolve()
    if not str(target).startswith(str(root)):
        # path traversal
        raise FileNotFoundError()
    if not target.exists() or not target.is_file():
        raise FileNotFoundError()
    return FileResponse(str(target))
