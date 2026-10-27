# Storage Management

Simple full-stack app to track warehouse stock for different items.

- **Frontend:** Next.js (App Router)
- **Backend:** FastAPI (OpenAPI / Swagger at `/docs`)
- **Database:** PostgreSQL

## Features

- JWT login
- List / create / adjust / delete stock items
- Low-stock highlighting
- Seeded demo users and inventory

## Demo credentials

| Username | Password  |
|----------|-----------|
| `admin`  | `admin123`|
| `clerk`  | `clerk123`|

## Quick start (Docker)

```bash
docker compose up --build
```

- App: http://localhost:3000  
- API + Swagger: http://localhost:8000/docs  

## Local development

### 1. PostgreSQL

```bash
docker compose up db -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Optional: copy `backend/.env.example` to `backend/.env`.

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | OAuth2 form login (Swagger) |
| POST | `/api/auth/login/json` | JSON login |
| GET | `/api/auth/me` | Current user |
| GET/POST | `/api/items` | List / create items |
| PATCH/DELETE | `/api/items/{id}` | Update / delete |
| POST | `/api/items/{id}/adjust` | Change quantity by delta |

## Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Project layout

```
backend/     FastAPI app, seed data, pytest
frontend/    Next.js UI + Jest tests
docker-compose.yml
```

## License

MIT — see [LICENSE](LICENSE).
