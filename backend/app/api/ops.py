from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.security import require_roles
from app import models

router = APIRouter(prefix="/ops", tags=["ops"])


# ---- helpers ----

def _storage_root() -> Path:
    return Path(settings.storage_root).resolve()


def _trash_root() -> Path:
    return _storage_root() / ".trash"


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _fmt_bytes(n: int) -> str:
    unit = ["B", "KB", "MB", "GB", "TB", "PB"]
    f = float(n)
    i = 0
    while f >= 1024 and i < len(unit) - 1:
        f /= 1024
        i += 1
    if i == 0:
        return f"{int(f)} {unit[i]}"
    return f"{f:.2f} {unit[i]}"


def _safe_relpath(p: Path, base: Path) -> str:
    p = p.resolve()
    base = base.resolve()
    try:
        rel = p.relative_to(base)
    except Exception as e:
        raise HTTPException(400, "path outside storage") from e
    return str(rel)


@dataclass
class TrashEntry:
    relpath: str
    abs_path: Path
    size_bytes: int
    mtime: float


def _iter_trash_entries() -> list[TrashEntry]:
    troot = _trash_root()
    if not troot.exists():
        return []
    out: list[TrashEntry] = []
    for p in troot.rglob("*"):
        if p.is_file():
            st = p.stat()
            out.append(TrashEntry(relpath=_safe_relpath(p, troot), abs_path=p, size_bytes=st.st_size, mtime=st.st_mtime))
    out.sort(key=lambda e: e.mtime, reverse=True)
    return out


def _move_to_trash(target: Path, *, reason: str) -> dict:
    sroot = _storage_root()
    troot = _trash_root()
    if not target.exists():
        return {"moved": False, "reason": "missing"}

    rel = _safe_relpath(target, sroot)
    ts = int(time.time())
    dest = troot / f"{ts}_{reason}" / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest_root = dest.parent
    troot.mkdir(parents=True, exist_ok=True)

    # allow moving dirs/files
    shutil.move(str(target), str(dest))
    return {"moved": True, "from": rel, "to": _safe_relpath(dest, troot), "trash_batch": _safe_relpath(dest_root, troot)}


# ---- schemas ----


class StorageUsage(BaseModel):
    storage_root: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    used_percent: float
    warn_threshold_percent: int
    warn: bool

    total_h: str
    used_h: str
    free_h: str


class CleanupRequest(BaseModel):
    include_tiles: bool = True
    include_thumbs: bool = True
    include_raw: bool = False


class CleanupResult(BaseModel):
    moved_paths: list[dict] = Field(default_factory=list)


class TrashListEntry(BaseModel):
    path: str
    size_bytes: int
    mtime: float

    size_h: str
    mtime_iso: str


class TrashListResponse(BaseModel):
    entries: list[TrashListEntry]
    total_bytes: int
    total_h: str


class TrashRestoreRequest(BaseModel):
    path: str  # path relative to .trash


class TrashPurgeRequest(BaseModel):
    path: str | None = None  # if absent: purge expired only
    purge_all: bool = False


class ExportRequest(BaseModel):
    # absolute path on server filesystem
    dest_path: str
    include_raw: bool = True
    include_thumbs: bool = True
    include_tiles: bool = True


# ---- endpoints (admin only) ----


@router.get("/storage", response_model=StorageUsage)
def storage_usage(_: models.User = Depends(require_roles("admin"))):
    sroot = _storage_root()
    sroot.mkdir(parents=True, exist_ok=True)
    du = shutil.disk_usage(str(sroot))
    used = du.used
    total = du.total
    free = du.free
    used_percent = (used / total * 100.0) if total else 0.0
    warn_th = int(settings.ops_warn_threshold)
    warn = used_percent >= warn_th
    return {
        "storage_root": str(sroot),
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "used_percent": round(used_percent, 2),
        "warn_threshold_percent": warn_th,
        "warn": warn,
        "total_h": _fmt_bytes(total),
        "used_h": _fmt_bytes(used),
        "free_h": _fmt_bytes(free),
    }


@router.post("/cleanup", response_model=CleanupResult)
def cleanup(payload: CleanupRequest, _: models.User = Depends(require_roles("admin"))):
    sroot = _storage_root()
    moved: list[dict] = []

    # tiles cache
    if payload.include_tiles:
        p = sroot / "tiles"
        if p.exists():
            moved.append(_move_to_trash(p, reason="tiles"))

    # thumbs are stored inside slides/*/*/thumb.jpg, so we trash thumb files only.
    if payload.include_thumbs:
        thumbs = []
        slides_dir = sroot / "slides"
        if slides_dir.exists():
            thumbs = list(slides_dir.rglob("thumb.jpg"))
        for t in thumbs:
            moved.append(_move_to_trash(t, reason="thumb"))

    # raw slide files: slides/<case>/<slide>/raw/*
    if payload.include_raw:
        raw_dirs = []
        slides_dir = sroot / "slides"
        if slides_dir.exists():
            raw_dirs = [p for p in slides_dir.rglob("raw") if p.is_dir()]
        for rd in raw_dirs:
            moved.append(_move_to_trash(rd, reason="raw"))

    return {"moved_paths": [m for m in moved if m.get("moved")]}


@router.get("/trash", response_model=TrashListResponse)
def list_trash(_: models.User = Depends(require_roles("admin"))):
    entries = _iter_trash_entries()
    total = sum(e.size_bytes for e in entries)
    return {
        "entries": [
            {
                "path": e.relpath,
                "size_bytes": e.size_bytes,
                "mtime": e.mtime,
                "size_h": _fmt_bytes(e.size_bytes),
                "mtime_iso": datetime.fromtimestamp(e.mtime, tz=timezone.utc).isoformat(),
            }
            for e in entries
        ],
        "total_bytes": total,
        "total_h": _fmt_bytes(total),
    }


@router.post("/trash/restore")
def restore_from_trash(payload: TrashRestoreRequest, _: models.User = Depends(require_roles("admin"))):
    troot = _trash_root().resolve()
    sroot = _storage_root().resolve()
    src = (troot / payload.path).resolve()
    if not src.exists():
        raise HTTPException(404, "trash entry not found")
    if troot not in src.parents and src != troot:
        raise HTTPException(400, "invalid path")

    # expected layout: <batch>/<original relpath>
    rel_under_trash = src.relative_to(troot)
    parts = rel_under_trash.parts
    if len(parts) < 2:
        raise HTTPException(400, "cannot restore batch root")
    orig_rel = Path(*parts[1:])
    dest = (sroot / orig_rel).resolve()
    if sroot not in dest.parents and dest != sroot:
        raise HTTPException(400, "invalid dest")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))

    # cleanup empty batch dirs
    try:
        cur = src.parent
        while cur != troot and cur.exists() and not any(cur.iterdir()):
            cur.rmdir()
            cur = cur.parent
    except Exception:
        pass

    return {"restored": True, "to": str(dest.relative_to(sroot))}


@router.post("/trash/purge")
def purge_trash(payload: TrashPurgeRequest, _: models.User = Depends(require_roles("admin"))):
    troot = _trash_root()
    troot.mkdir(parents=True, exist_ok=True)

    if payload.purge_all:
        shutil.rmtree(troot)
        troot.mkdir(parents=True, exist_ok=True)
        return {"purged": True, "mode": "all"}

    if payload.path:
        target = (troot / payload.path).resolve()
        if not target.exists():
            raise HTTPException(404, "trash entry not found")
        if troot.resolve() not in target.parents and target != troot.resolve():
            raise HTTPException(400, "invalid path")
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        return {"purged": True, "mode": "path", "path": payload.path}

    # default: purge expired by mtime
    days = int(settings.ops_trash_retention_days)
    cutoff = _now_utc() - timedelta(days=days)
    removed = 0
    for e in _iter_trash_entries():
        if datetime.fromtimestamp(e.mtime, tz=timezone.utc) < cutoff:
            try:
                e.abs_path.unlink()
                removed += 1
            except Exception:
                pass

    # remove empty directories
    for p in sorted(troot.rglob("*"), reverse=True):
        if p.is_dir():
            try:
                if not any(p.iterdir()):
                    p.rmdir()
            except Exception:
                pass

    return {"purged": True, "mode": "expired", "removed_files": removed, "retention_days": days}


@router.post("/export")
def export_storage(payload: ExportRequest, _: models.User = Depends(require_roles("admin"))):
    sroot = _storage_root()
    dest = Path(payload.dest_path).expanduser().resolve()

    # safety: require absolute path
    if not dest.is_absolute():
        raise HTTPException(400, "dest_path must be absolute")

    # prevent exporting into storage itself
    if dest == sroot or sroot in dest.parents:
        raise HTTPException(400, "dest_path must be outside storage_root")

    dest.mkdir(parents=True, exist_ok=True)

    items: list[tuple[Path, Path]] = []
    if payload.include_tiles:
        items.append((sroot / "tiles", dest / "tiles"))
    if payload.include_thumbs or payload.include_raw:
        items.append((sroot / "slides", dest / "slides"))
    if payload.include_thumbs or payload.include_raw:
        items.append((sroot / "attachments", dest / "attachments"))

    copied = []

    def _copytree(src: Path, dst: Path):
        if not src.exists():
            return
        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        else:
            if dst.exists():
                # merge
                for root, dirs, files in os.walk(src):
                    r = Path(root)
                    rel = r.relative_to(src)
                    (dst / rel).mkdir(parents=True, exist_ok=True)
                    for fn in files:
                        shutil.copy2(r / fn, dst / rel / fn)
            else:
                shutil.copytree(src, dst)

    for src, dst in items:
        if src.name == "slides" and (payload.include_raw != True or payload.include_thumbs != True):
            # selective copy for slides
            if not src.exists():
                continue
            for p in src.rglob("*"):
                if p.is_dir():
                    continue
                # include thumb.jpg
                if payload.include_thumbs and p.name == "thumb.jpg":
                    rel = p.relative_to(src)
                    _copytree(p, dst / rel)
                # include raw files under raw/
                if payload.include_raw and "raw" in p.parts:
                    rel = p.relative_to(src)
                    _copytree(p, dst / rel)
            copied.append({"src": str(src), "dst": str(dst), "mode": "selective"})
            continue

        _copytree(src, dst)
        copied.append({"src": str(src), "dst": str(dst), "mode": "full"})

    return {"exported": True, "to": str(dest), "items": copied}
