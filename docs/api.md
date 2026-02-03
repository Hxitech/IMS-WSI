# API Draft

Base URL: `/`

## Health
- `GET /health`

## Cases
- `POST /cases` {title, description?}
- `GET /cases`
- `GET /cases/{case_id}`

## Slides
- `POST /slides` {case_id, label, dzi_path?}
- `GET /cases/{case_id}/slides`

## Attachments
- `POST /slides/{slide_id}/attachments` multipart form-data: `file`

## Tasks
- `POST /tasks` {case_id, title, notes?}
- `PATCH /tasks/{task_id}` {title?, notes?, status?, is_archived?}
- `GET /cases/{case_id}/tasks`
