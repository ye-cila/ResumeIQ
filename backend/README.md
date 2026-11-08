# ResumeIQ Backend

FastAPI backend for ResumeIQ, an AI-powered resume analysis platform.

**Completed milestones:**
1. Backend Foundation — app setup, modular routing, configuration,
   centralized error handling, and tests.
2. Database Foundation — PostgreSQL, SQLAlchemy 2.0 models, Alembic migrations.

## Requirements

- Python 3.12
- PostgreSQL 16 (local install, e.g. via Homebrew)

## Setup

From the repository root:

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r backend/requirements.txt
```

Create your local environment file (never commit `.env`):

```bash
cd backend
cp .env.example .env
```

## Database setup

### PostgreSQL assumptions

The defaults assume a local Homebrew PostgreSQL where your macOS username is
a database superuser that can connect without a password:

```bash
brew services start postgresql@16
createdb resumeiq        # development database
createdb resumeiq_test   # disposable database used only by the tests
```

### Configure `DATABASE_URL`

Set the URLs in `backend/.env` (copied from `.env.example`). The `+psycopg`
part selects the psycopg 3 driver:

```bash
DATABASE_URL=postgresql+psycopg://<user>[:<password>]@localhost:5432/resumeiq
TEST_DATABASE_URL=postgresql+psycopg://<user>[:<password>]@localhost:5432/resumeiq_test
```

With Homebrew this is usually just `postgresql+psycopg://your_macos_username@localhost:5432/resumeiq`.
If `DATABASE_URL` is unset, the app falls back to a credential-free
`postgresql+psycopg://localhost:5432/resumeiq`.

### Run migrations

Alembic owns the database schema. Never use `Base.metadata.create_all()`.
From `backend/`:

```bash
alembic upgrade head          # apply all migrations
alembic current               # show the database's current revision
alembic downgrade -1          # undo the latest migration
```

After changing a model, generate a new migration, **review it**, then apply it:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
alembic check                 # confirms models and migrations are in sync
```

Migration files live in `alembic/versions/`. Alembic reads the database URL
from the app settings (`DATABASE_URL`), not from `alembic.ini`.

### Database structure

```text
users                                  resumes
─────────────────────────────          ─────────────────────────────────────
id            UUID  PK                 id          UUID  PK
email         varchar(320) UNIQUE      user_id     UUID  FK → users.id (ON DELETE CASCADE), indexed
password_hash varchar(255)             file_name   varchar(255)  original name, display only
created_at    timestamptz default now  file_path   varchar(1024) UNIQUE, location in storage
updated_at    timestamptz default now  file_type   varchar(100)  MIME type
                                       file_size   bigint, CHECK (file_size >= 0)
                                       created_at  timestamptz default now
```

- One user has many resumes (`User.resumes` ↔ `Resume.user`).
- PostgreSQL stores resume **metadata only**. The file bytes will live in
  file storage (a later milestone), and `file_path` points to them.
- Deleting a user deletes their resume rows.

### How sessions work

`app/db/session.py` creates **one** engine (with a connection pool) per
process. Each request gets its own session from the `get_db` dependency, and
the session is always closed afterwards, even if the request fails:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

@router.get("/example")
def example(db: Session = Depends(get_db)): ...
```

Code that changes data must call `db.commit()`. Anything not committed is
rolled back when the session closes.

## Run the API

From `backend/`:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

| Method | Path       | Description                 |
|--------|------------|-----------------------------|
| GET    | `/`        | Welcome message             |
| GET    | `/health/` | Liveness check with version |

## Run the tests

From `backend/`:

```bash
pytest
```

- API tests (`tests/test_*.py`) use FastAPI's `TestClient`. They need no
  database and ignore your local `.env`.
- Database tests (`tests/db/`) run against `TEST_DATABASE_URL`, never against
  `DATABASE_URL`. At the start of a run they rebuild the test schema with
  Alembic (`downgrade base` then `upgrade head`), and each test runs inside a
  transaction that is rolled back.
- If `TEST_DATABASE_URL` is unset, the database tests are **skipped** (shown
  in the pytest summary). The tests refuse to run if the test database's
  name doesn't end in `_test` or matches the dev database.

## Configuration

Settings live in `app/core/config.py` and are loaded from environment
variables (or `.env`). Names are case-insensitive.

| Variable      | Default        | Description                                  |
|---------------|----------------|----------------------------------------------|
| `APP_NAME`    | `ResumeIQ API` | Title shown in the API docs                  |
| `APP_VERSION` | `0.1.0`        | Version reported by `/health/` and the docs  |
| `ENVIRONMENT` | `development`  | `development`, `testing`, or `production`    |
| `DEBUG`       | `false`        | FastAPI debug mode — keep off in production  |
| `DATABASE_URL` | `postgresql+psycopg://localhost:5432/resumeiq` | App + Alembic database |
| `DB_ECHO`     | `false`        | Log all SQL statements                       |
| `TEST_DATABASE_URL` | unset    | Disposable test DB (name must end `_test`)   |

## Error format

Every error response has the same shape:

```json
{
  "error": {
    "code": "not_found",
    "message": "Not Found",
    "details": null
  }
}
```

To return a custom error from app code, raise `AppException`:

```python
from app.core.exceptions import AppException

raise AppException("Resume not found", code="resume_not_found", status_code=404)
```

## Project structure

```text
backend/
├── app/
│   ├── main.py            # create_app(): builds and configures the app
│   ├── api/
│   │   ├── router.py      # registers all routers in one place
│   │   └── routes/        # one module per feature area (root, health, ...)
│   ├── core/
│   │   ├── config.py      # Settings loaded from env vars
│   │   └── exceptions.py  # AppException + centralized handlers
│   ├── schemas/           # Pydantic request/response models
│   ├── services/          # business logic (later milestones)
│   ├── models/            # ORM models; __init__.py registers them all
│   │   ├── user.py
│   │   └── resume.py
│   └── db/
│       ├── base.py        # DeclarativeBase + constraint naming convention
│       └── session.py     # engine, SessionLocal, get_db dependency
├── alembic/
│   ├── env.py             # wires Alembic to app settings + Base.metadata
│   └── versions/          # migration scripts
├── tests/
│   └── db/                # PostgreSQL-backed tests
├── alembic.ini
├── pytest.ini
├── requirements.txt
└── .env.example
```

### Adding a new route module

1. Create `app/api/routes/<feature>.py` with `router = APIRouter(prefix="/<feature>", tags=["<feature>"])`.
2. Include it in `app/api/router.py`.
3. Add tests in `tests/test_<feature>.py`.
