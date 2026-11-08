from fastapi import APIRouter

from app.schemas.common import RootResponse

router = APIRouter(tags=["root"])


@router.get("/", response_model=RootResponse)
def root() -> RootResponse:
    return RootResponse(message="Welcome to ResumeIQ API")
