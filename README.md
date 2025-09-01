# Me-API Playground

A tiny backend + minimal UI that stores and exposes your candidate profile.

## Tech
- **Backend:** FastAPI, SQLAlchemy, SQLite (default)
- **Frontend:** Static HTML/CSS/JS (served by FastAPI)
- **Auth:** Basic Auth (env-configured) for write ops
- **Extras:** `/health`, CORS, simple rate limit, pagination, Postman collection

## Live URLs
> Replace these after deploying.
- API base: `https://your-api.example.com`
- Frontend: `https://your-api.example.com/` (served from the same container)

## Quickstart (Local)

### 1) Python
```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
export ADMIN_USER=admin ADMIN_PASS=change-me
export DATABASE_URL=sqlite:///./meapi.db
uvicorn backend.main:app --reload
```
- Visit: `http://localhost:8000` (frontend) and `http://localhost:8000/docs` (API docs)

### 2) Seed the DB
```bash
python -c "from backend.seed import main; main()"
```

### 3) Docker
```bash
docker compose up --build
```

## API

- `GET /health` → 200 OK
- `GET /profile` → Returns your full profile
- `POST /profile` (Basic Auth) → Create profile (only once)
- `PUT /profile` (Basic Auth) → Replace profile
- `GET /projects?skill=Python&q=api&limit=10&offset=0`
- `GET /skills/top?limit=5`
- `GET /search?q=python`

> Set Basic Auth credentials via `ADMIN_USER` / `ADMIN_PASS` envs.

## Database Schema
- `profiles(id, name, email, education, github, linkedin, portfolio)`
- `skills(id, name, level)`
- `profile_skills(profile_id, skill_id)`
- `projects(id, profile_id, title, description)`
- `project_links(id, project_id, label, url)`
- `project_skills(project_id, skill_id)`
- `work(id, profile_id, company, title, start_date, end_date, description)`

## Frontend
A small page under `/` that can:
- View profile
- Search by text
- List projects (optionally filter by skill)
- Show top skills

## Deployment
- **Render / Railway / Fly.io / Azure App Service / GCP Cloud Run**: Build the Docker image with the `Dockerfile`. Expose port `8000`. Add environment variables: `ADMIN_USER`, `ADMIN_PASS`, `ALLOWED_ORIGINS`, `RATE_LIMIT_PER_MINUTE`.
- CORS: Default allows all (`*`). Lock it down in production.

## Postman / curl
Import `postman_collection.json` or try:
```bash
curl http://localhost:8000/health

# Create profile (replace JSON with your real data)
curl -u admin:change-me -X POST http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d @sample_profile.json
```

Create `sample_profile.json` using your info following `schemas.ProfileIn`.

## Resume
Add your resume link here: **https://...**

## Known limitations
- Single-user (one profile) by design.
- In-memory rate limit resets every minute and not distributed.
- SQLite by default; switch `DATABASE_URL` for Postgres/MySQL. SQLAlchemy models are portable.

## License
MIT
# me-api-playground
