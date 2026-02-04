# Auth + Task Center (Option B)

This project now includes:
- Basic username/password login
- Bearer token (JWT-like HS256) auth
- Minimal RBAC roles: `admin`, `doctor`, `tech`
- Task Center: manual assign, auto-assign by-count, auto-assign by-time

## Default seed users
On backend startup, if there are **no users**, the backend seeds these accounts:

| username | password | role |
|---|---|---|
| admin | admin | admin |
| doctor1 | doctor1 | doctor |
| tech1 | tech1 | tech |
| tech2 | tech2 | tech |

## Backend endpoints

### Auth
- `POST /auth/login` → `{access_token, user}`
- `GET /auth/me`
- Admin-only:
  - `GET /auth/users`
  - `POST /auth/users`
  - `PATCH /auth/users/{user_id}`

### Task Center
- `GET /task-center/tasks` (all non-archived tasks)
- `POST /task-center/tasks/{task_id}/assign` (admin/doctor)
- `POST /task-center/tasks/{task_id}/auto-assign` (admin/doctor)
- `GET /task-center/users` (active users)

Auto-assign payload:
```json
{
  "strategy": "by_count",
  "eligible_role": "tech",
  "lookback_minutes": 120
}
```

## Assignment strategies

### Manual
Sets `assignee_id` exactly (or `null` to unassign) and sets `assign_strategy=manual`.

### Auto by-count
Chooses the eligible user with the **fewest open tasks**:
- open = `status != done` AND `is_archived = false`

### Auto by-time
Chooses the eligible user with the **fewest assignments** in the last `lookback_minutes`.

## Run locally (docker-compose)

1. Start services:
   ```bash
   docker compose up --build
   ```
2. Run DB migrations inside backend container (first run):
   ```bash
   docker compose exec backend alembic upgrade head
   ```
3. Frontend: open `http://localhost:5173`

## Quick test flow
1. Login at `/login` using `admin/admin`.
2. Create a case + tasks (existing UI).
3. Go to `/task-center` and try:
   - Manual assign to `tech1` / `tech2`
   - Auto by-count (eligible role = tech)
   - Auto by-time (lookback = 30)
