# Storage Management

Simple full-stack app to track warehouse stock for different items.

- **Frontend:** Next.js (App Router)
- **Backend:** FastAPI (OpenAPI / Swagger at `/docs`)
- **Storage:** in-memory only (no database). Inventory is reseeded on every start; changes are lost on restart.

## Features

- JWT login
- List / create / adjust / delete stock items
- Low-stock highlighting
- Inventory loaded on startup

## Administrator provisioning

Production startup does not create demo accounts. To provision an administrator, set both `INITIAL_ADMIN_USERNAME` and `INITIAL_ADMIN_PASSWORD` as protected deployment environment variables before starting the backend. Use a unique, strong password, keep these values out of source control and logs, and remove or rotate the provisioning values according to your deployment process. If neither variable is set, no user is created and login is unavailable; setting only one causes startup seeding to fail rather than silently using an incomplete configuration.

Test mode uses demo users only for automated tests; those credentials are not production credentials.

## Quick start (Docker)

```bash
docker compose up --build
```

- App: http://localhost:3000  
- API + Swagger: http://localhost:8000/docs

For a usable deployment, configure the administrator provisioning variables through the environment mechanism used by your deployment platform.

## Deploy on Vercel

`vercel.json` deploys both apps as one project: `/api/*` goes to the FastAPI backend and everything else to Next.js. Run both locally with `vercel dev`.
Note: Vercel runs the backend as serverless functions, so the in-memory data can reset at any time and may differ between instances. Configure the administrator variables as protected deployment environment variables.

## Local development

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Set `INITIAL_ADMIN_USERNAME` and `INITIAL_ADMIN_PASSWORD` in the backend environment to provision a local account. Optional configuration is in `backend/.env.example`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

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
backend/     FastAPI app, in-memory store + seed data, pytest
frontend/    Next.js UI + Jest tests
docker-compose.yml
```

## License

MIT — see [LICENSE](LICENSE).
