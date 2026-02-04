# Ops Module

Admin-only endpoints and UI for storage monitoring, cleanup-to-trash, trash management, and exporting storage.

## Configuration

Backend env vars (see `backend/app/core/config.py`):

- `OPS_WARN_THRESHOLD` (default: `80`) — warn when disk usage is >= this percent
- `OPS_TRASH_RETENTION_DAYS` (default: `30`) — purge expired trash entries older than this many days

> Note: pydantic-settings reads lowercase field names from uppercase env vars automatically.

## Storage Layout

Under `STORAGE_ROOT` (default `./storage`):

- `slides/<case_id>/<slide_id>/raw/<filename>` — uploaded original slide file
- `slides/<case_id>/<slide_id>/thumb.jpg` — generated thumbnail
- `tiles/<slide_id>/<level>/<x>_<y>.jpg` — tile cache
- `attachments/<case_id>/<slide_id>/<filename>` — uploaded attachments
- `.trash/` — ops trash (recoverable)

## API (admin-only)

All endpoints require an `admin` JWT.

- `GET /api/ops/storage` — disk usage + warning threshold
- `POST /api/ops/cleanup` — moves selected items into `.trash/`
  - body: `{ include_tiles, include_thumbs, include_raw }`
- `GET /api/ops/trash` — list trash files
- `POST /api/ops/trash/restore` — restore a trash entry back to original location
  - body: `{ path }` where `path` is relative to `.trash/`
- `POST /api/ops/trash/purge`
  - `{ purge_all: true }` to purge everything
  - `{ path: "..." }` to delete one entry
  - `{}` to purge expired by retention
- `POST /api/ops/export` — copy storage out to an absolute path on the server
  - body: `{ dest_path, include_raw, include_thumbs, include_tiles }`

## UI

Frontend page: `/ops`

- Shows storage usage bar (warns at threshold)
- Cleanup controls (move tiles/thumbs/raw to trash)
- Trash browser (restore / delete / purge expired / purge all)
- Export form

## Safety Notes

- Cleanup **moves** files/dirs into `.trash/` (recoverable)
- Purge is permanent
- Export destination must be an **absolute** path and must be outside `storage_root`
