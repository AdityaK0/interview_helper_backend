# FastAPI Template

A minimal, production-style FastAPI backend template built around one
CRUD module — Notes. This is the reference pattern to copy for any new
resource: model → schema → repository → service → router.

---

## Architecture

```
API Layer        (notes/api.py)         — endpoints, request validation
Service Layer    (notes/service.py)     — business logic
Repository Layer (notes/repository.py)  — all database queries
Database         (SQLAlchemy + Alembic)
```

The router never touches SQLAlchemy directly — it calls the service, the
service calls the repository.

## Project Structure

```
fastapi-template/
├── notes/                 # the module — copy this for any new resource
│   ├── api.py              # endpoints
│   ├── service.py          # business logic
│   ├── repository.py       # DB queries
│   ├── models.py           # SQLAlchemy model
│   └── schema.py           # Pydantic schemas
├── middleware/
│   ├── request_logging.py # request ID + access logging
│   └── security.py        # security headers
├── utils/
│   ├── exceptions.py      # AppException
│   └── models.py          # BaseModel (created_at, updated_at, is_active)
├── alembic/               # database migrations
├── tests/                 # pytest suite
├── main.py
├── config.py
├── database.py
├── seed.py                # sample notes
├── requirements.txt
└── .env.example
```

---

## Setup

**1. Clone and create a virtual environment**
```bash
python -m venv env
source env/bin/activate        # macOS / Linux
env\Scripts\activate           # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**
```bash
cp .env.example .env
# Edit .env and set DATABASE_URL
```

**4. Start PostgreSQL** (any local Postgres works)

**5. Run database migrations**
```bash
alembic upgrade head
```

**6. (Optional) Seed demo data**
```bash
python seed.py
```

**7. Start the server**
```bash
uvicorn main:app --reload
```

API docs: `http://localhost:8000/docs`

### Using SQLite instead of Postgres

Postgres is the default and the only target treated as
production-representative, but for quick local experimentation:
```env
DATABASE_URL=sqlite:///./app.db
```
`database.py` detects the `sqlite://` prefix and adds
`connect_args={"check_same_thread": False}` — SQLite otherwise restricts a
connection to the thread that opened it, which breaks under FastAPI's
threadpool. No other code changes needed.

---

## Notes API

```
notes/models.py       — Note (id, title, content, is_pinned, is_archived, created_at, updated_at)
notes/schema.py        — NoteCreate / NoteUpdate / NoteResponse
notes/repository.py     — all DB queries
notes/service.py        — business logic, calls the repository
notes/api.py             — HTTP only, calls the service
```

```http
GET    /notes                 ?search=&archived=false
POST   /notes
GET    /notes/{note_id}
PATCH  /notes/{note_id}
DELETE /notes/{note_id}
```

- `POST` → `201`, returns the created note.
- `GET /{id}` and mutations on a missing id → `404`.
- A body that fails schema validation (e.g. missing `title`) → `422`,
  handled automatically by FastAPI/Pydantic.
- `DELETE` → `204`, permanently removes the row.

---

## Adding a New Module

Copy `notes/` as the template:

1. Create `yourmodule/` with `api.py`, `service.py`, `repository.py`, `models.py`, `schema.py`.
2. Register your router in `main.py`:
   ```python
   from yourmodule.api import your_router
   app.include_router(your_router)
   ```
3. Import your models in `alembic/env.py` so Alembic detects them:
   ```python
   from yourmodule import models
   ```
4. Generate and run the migration:
   ```bash
   alembic revision --autogenerate -m "add yourmodule tables"
   alembic upgrade head
   ```

---

## Database

`database.py` sets up a single `engine` (created once per process — it
owns the connection pool, so creating one per request would open a fresh
Postgres connection on every call) and a `SessionLocal` factory. `get_db()`
is a generator dependency: FastAPI runs its setup before the route and its
teardown (`db.close()`) after, whether the route succeeds or raises —
which is why every route takes `db: Session = Depends(get_db)` instead of
managing a session itself.

`utils/models.py`'s `BaseModel` gives every table `created_at`,
`updated_at`, and `is_active` without repeating those three columns in
every model.

---

## Alembic

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

`alembic/env.py` sets `sqlalchemy.url` from `config.settings` (one source
of truth — never duplicated into `alembic.ini`) and imports every
module's `models` so Alembic sees the full picture when diffing.

**Why Alembic and not `Base.metadata.create_all()`**: `create_all()` can
only *create* tables/columns that don't exist yet — it can't express "this
column used to be nullable and now isn't," can't be rolled back, and
leaves no reviewable history of how the schema evolved. Alembic generates
an explicit, ordered, reversible (`upgrade`/`downgrade`) migration per
change. `create_all()` is fine for the test suite's disposable in-memory
database (see `tests/conftest.py`), never for a schema real data lives in.

Run `alembic revision --autogenerate -m "create notes table"` once
against your database to generate the first migration.

---

## Middleware

- `RequestLoggingMiddleware` — generates a request ID, logs method/path/status/duration, and echoes it back as `X-Request-ID`.
- `SecurityHeadersMiddleware` — sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, etc. on every response.
- `CORSMiddleware` — origins come from `CORS_ORIGINS` in `.env`. CORS is a **browser** security mechanism (it stops a webpage's JS from reading a cross-origin response unless the server opts in) — it does nothing to stop curl, Postman, or a server-to-server call, so it's not a substitute for authentication.

---

## Error Format

All errors return:
```json
{
  "success": false,
  "message": "Note not found",
  "error_code": "NOTE_NOT_FOUND"
}
```

Raise from anywhere:
```python
from utils.exceptions import AppException

raise AppException("Note not found", status_code=404, error_code="NOTE_NOT_FOUND")
```

| Code | Meaning |
|---|---|
| 404 | resource doesn't exist |
| 409 | conflicts with current state |
| 422 | request body/params failed validation |

---

## Testing

```bash
pytest
```

`tests/conftest.py` overrides `get_db` with a session backed by an
in-memory SQLite database, created fresh (`Base.metadata.create_all`)
before every test. `tests/test_notes.py` covers create, get, list,
update, delete, the 404 case, and the 422 validation case.

---

## Health Check

`GET /health` → `{"status": "ok"}` — a plain liveness check with no
database dependency, so an unrelated DB blip can't make an orchestrator
kill and restart an otherwise-healthy process.
