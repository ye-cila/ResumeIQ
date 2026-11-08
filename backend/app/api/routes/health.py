from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Liveness check: confirms the API process is up and responding.

    Dependency checks (database, Redis, ...) will be added when those
    services are introduced in later milestones.
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )
