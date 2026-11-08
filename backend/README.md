# ResumeIQ Backend

FastAPI backend for ResumeIQ, an AI-powered resume analysis platform.

**Current milestone:** Backend Foundation — app setup, modular routing,
configuration, centralized error handling, and tests.

## Requirements

- Python 3.9+

## Setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Create your local environment file (never commit `.env`):

```bash
cd backend
cp .env.example .env
```

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

Tests use FastAPI's `TestClient` and do not need a database or any external
service. They also ignore your local `.env` file.

## Configuration

Settings live in `app/core/config.py` and are loaded from environment
variables (or `.env`). Names are case-insensitive.

| Variable      | Default        | Description                                  |
|---------------|----------------|----------------------------------------------|
| `APP_NAME`    | `ResumeIQ API` | Title shown in the API docs                  |
| `APP_VERSION` | `0.1.0`        | Version reported by `/health/` and the docs  |
| `ENVIRONMENT` | `development`  | `development`, `testing`, or `production`    |
| `DEBUG`       | `false`        | FastAPI debug mode — keep off in production  |

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
│   ├── models/            # ORM models (later milestones)
│   └── db/                # database setup (later milestones)
├── tests/
├── pytest.ini
├── requirements.txt
└── .env.example
```

### Adding a new route module

1. Create `app/api/routes/<feature>.py` with `router = APIRouter(prefix="/<feature>", tags=["<feature>"])`.
2. Include it in `app/api/router.py`.
3. Add tests in `tests/test_<feature>.py`.
