# Backend

## Run (docker compose)

```bash
docker compose up --build
```

API: http://localhost:8000
Docs (Swagger): http://localhost:8000/docs

## Migrations

Inside the backend container:

```bash
docker compose exec backend alembic upgrade head
```

Create new migration:

```bash
docker compose exec backend alembic revision --autogenerate -m "..."
```
