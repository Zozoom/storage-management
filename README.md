# Storage Management

Simple full-stack app to track warehouse stock for different items.

- **Frontend:** Next.js (App Router)
- **Backend:** FastAPI (OpenAPI / Swagger at `/docs`)
- **Storage:** in-memory only (no database). Dummy inventory is reseeded on every start in development/demo mode; changes are lost on restart.

## Features

- JWT login
- List / create / adjust / delete stock items
- Low-stock highlighting
- Optional demo users and inventory for development/demo mode

## Credentials and configuration

The backend requires `SECRET_KEY` to be set to a random, deployment-specific value supplied through your environment or secret manager. It fails to start if the key is missing, shorter than 32 characters, or a known development value. For local development, generate a key rather than using the placeholder in `backend/.env.example`:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
```

Demo accounts are not created in production mode (the default). To seed demo users and inventory, explicitly set `APP_MODE=demo` and configure unique account usernames and passwords outside source control. Both demo passwords must be different and at least 16 characters long:

```bash
export APP_MODE=demo
export DEMO_ADMIN_USERNAME="your-admin-username"
export DEMO_ADMIN_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(24))')"
export DEMO_CLERK_USERNAME="your-clerk-username"
export DEMO_CLERK_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(24))')"
```

Keep the generated values private and use different values for each deployment. Docker Compose passes these environment variables to the backend.

## Quick start (Docker)

```bash
# Set SECRET_KEY as described above, then:
docker compose up --build
```

- App: http://localhost:3000  
- API + Swagger: http://localhost:8000/docs  

For demo accounts and seeded inventory, also configure `APP_MODE=demo` and all four demo credential variables before starting Compose.

## Deploy on Vercel

`vercel.json` deploys both apps as one project: `/api/*` goes to the FastAPI backend and everything else goes to Next.js. Run both locally with `vercel dev`.
Configure a random, deployment-specific `SECRET_KEY` through Vercel's secret/environment-variable settings. Do not enable demo mode in production. Vercel runs the backend as serverless functions, so the in-memory data can reset at any time and may differ between instances.

## Local development

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Set SECRET_KEY as described above before starting the backend.
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

To load demo users and inventory locally, set `APP_MODE=demo` and configure the four demo credential environment variables before starting the backend.

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
