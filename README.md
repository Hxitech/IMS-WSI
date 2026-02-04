# 数字病理切片管理与AI辅助平台（拟）

本仓库已初始化为可运行的全栈脚手架：FastAPI 后端 + Vue 前端。

## 目录结构
- `backend/`：FastAPI + SQLAlchemy + Alembic（Postgres）
- `frontend/`：Vue 3 + Vite + OpenSeadragon（切片查看占位）
- `docs/`：架构/接口草案/数据模型/存储布局
- `diagrams/`：架构图/流程图
- `storage/`：本地文件存储（默认挂载，已加入 .gitignore）

## Quickstart

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 （Swagger: http://localhost:8000/docs）

## Docs
- `docs/api.md`
- `docs/data-model.md`
- `docs/storage-layout.md`
- `docs/ops.md` (admin-only storage monitoring/cleanup/trash/export)
