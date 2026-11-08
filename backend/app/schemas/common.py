from typing import Literal

from pydantic import BaseModel


class RootResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    environment: str
