# Tile-based WSI viewer (OpenSeadragon + FastAPI + OpenSlide)

This project supports a simple JPEG tile viewer for Whole Slide Images (WSI).

## Backend

### Slide info

`GET /api/slides/{slide_id}/info`

Returns metadata needed to configure an OpenSeadragon custom tile source:

- `width`, `height` (level 0 full resolution)
- `level_count`
- `levels[]` with `{ level, width, height }`
- `tileSize` (query param, default `256`)

### Tile endpoint

`GET /api/slides/{slide_id}/tile/{level}/{x}/{y}.jpg?tileSize=256`

- `level` is the **OpenSlide level index** (0 = highest resolution)
- `x`,`y` are tile coordinates at that level
- tiles are generated with `OpenSlide.read_region` and encoded as JPEG

### Disk cache

Tiles are cached on disk:

`storage/tiles/{slide_id}/{level}/{x}_{y}.jpg`

Delete `storage/tiles/` to clear the cache.

## Frontend

Open a slide viewer at:

`/slides/:slideId/view`

The viewer uses OpenSeadragon with a custom tile source. OpenSeadragon's level numbering is the opposite of OpenSlide (OSD maxLevel is the highest resolution), so the frontend maps:

`apiLevel = maxLevel - osdLevel`

## Notes / limitations

- Tile boundaries outside the image are currently returned as black/empty regions (OpenSlide behavior).
- The backend uses a naive assumption that each level is downsampled by `2**level` for the `levels[]` list. Tile reads use `OpenSlide.level_downsamples[level]` for correct placement.
- No auth is implemented (MVP).
