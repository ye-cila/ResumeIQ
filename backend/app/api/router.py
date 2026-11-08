"""Central place where all route modules are registered.

To add a new feature area, create `app/api/routes/<feature>.py` with its own
APIRouter and include it here.
"""

from fastapi import APIRouter

from app.api.routes import health, root

api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(health.router)
