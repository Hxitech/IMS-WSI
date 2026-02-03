# Data Model

## Case
- `id` (PK)
- `title`
- `description` (optional)
- `created_at`

Relations:
- Case 1—N Slides
- Case 1—N Tasks

## Slide
- `id` (PK)
- `case_id` (FK → cases.id)
- `label`
- `dzi_path` (optional) — path or URL to DeepZoom (DZI) / IIIF source
- `created_at`

Relations:
- Slide 1—N Attachments

## Attachment
- `id` (PK)
- `slide_id` (FK → slides.id)
- `filename`
- `mime_type` (optional)
- `storage_path` (relative to STORAGE_ROOT)
- `size_bytes` (optional)
- `created_at`

## Task
- `id` (PK)
- `case_id` (FK → cases.id)
- `title`
- `notes` (optional)
- `status` enum: todo | in_progress | done
- `is_archived` boolean
- `created_at`
