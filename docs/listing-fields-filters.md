# Configurable list fields & filters (Cases / Slides)

This project now supports:
- **Per-user column visibility** for the Cases list and Case→Slides list.
- **Search / filter / sort** on list endpoints.

## Backend

### Slide model fields
Additional `slides` fields:
- `folder` (string)
- `filename` (string, existed)
- `ai_module` (string)
- `scan_magnification` (int)
- `ai_suggestion` (text)
- `processing_status` (string)
- `label_png_path` (string)
- `slide_number` (int)
- `quality` (string)
- `clarity` (string)
- `review_result` (string)
- `updated_at` (datetime)

### Case derived fields
- `slide_count` is returned by the list endpoint as an aggregated count of **non-archived slides**.

### Migrations
- `0005_slide_extra_fields_and_user_list_prefs` adds slide fields and `user_list_prefs` table.

### API

#### GET `/cases`
Returns paginated list with derived `slide_count`.

Query params:
- `q` search (title/description)
- `is_archived` (bool)
- `sort`: `id | title | created_at | slide_count`
- `order`: `asc | desc`
- `limit`, `offset`

Response shape:
```json
{ "items": [/* CaseRead + slide_count */], "total": 0, "limit": 200, "offset": 0 }
```

#### GET `/cases/{case_id}/slides`
Query params:
- `q` search (label, filename, folder, ai_module, processing_status)
- `is_archived` (bool)
- `processing_status`, `review_result`, `quality`, `clarity`, `ai_module`
- `scan_magnification` (int)
- `sort`: `id | label | filename | folder | processing_status | scan_magnification | updated_at | created_at | slide_number`
- `order`: `asc | desc`
- `limit`, `offset`

Response shape:
```json
{ "items": [/* SlideRead */], "total": 0, "limit": 200, "offset": 0 }
```

#### Per-user list preferences
- `GET /list-prefs/{key}` → `{ key, value }`
- `PUT /list-prefs/{key}` with `{ value }` → persists preference for current user.

Used keys in frontend:
- `cases_columns`
- `slides_columns`

## Frontend

### Cases page
- Table view with sortable columns.
- Search box.
- Column picker modal (persisted per user).

### Case page (Slides)
- Table view with sortable columns.
- Search, filters (status, review, archived).
- Column picker modal (persisted per user).

## Screenshot checklist
- Open **Cases** page → click **Columns** → toggle columns.
- In a Case → filter slides by **Status** or **Review**.
- Click a table header to change sort (shows ▲/▼).
