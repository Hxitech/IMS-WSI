from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass
class SlideMeta:
    level_count: int
    width: int
    height: int
    mpp_x: Optional[float]
    mpp_y: Optional[float]


def read_meta_and_thumbnail(input_path: str, thumb_path: str, size: tuple[int, int] = (1024, 1024)) -> SlideMeta:
    """Open a WSI with OpenSlide, read basic metadata, and write a JPEG thumbnail."""
    try:
        import openslide  # type: ignore
    except Exception as e:
        raise RuntimeError("openslide-python not installed or openslide library missing") from e

    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    slide = openslide.OpenSlide(input_path)
    level_count = slide.level_count
    w, h = slide.dimensions

    # MPP is optional and vendor-dependent
    mpp_x = None
    mpp_y = None
    try:
        mpp_x = float(slide.properties.get(openslide.PROPERTY_NAME_MPP_X)) if slide.properties.get(openslide.PROPERTY_NAME_MPP_X) else None
        mpp_y = float(slide.properties.get(openslide.PROPERTY_NAME_MPP_Y)) if slide.properties.get(openslide.PROPERTY_NAME_MPP_Y) else None
    except Exception:
        mpp_x = None
        mpp_y = None

    thumb = slide.get_thumbnail(size)
    if isinstance(thumb, Image.Image):
        if thumb.mode not in ("RGB", "L"):
            thumb = thumb.convert("RGB")
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        thumb.save(thumb_path, format="JPEG", quality=90)

    slide.close()

    return SlideMeta(level_count=level_count, width=w, height=h, mpp_x=mpp_x, mpp_y=mpp_y)
