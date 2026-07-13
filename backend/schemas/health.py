"""System schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health endpoint response model."""

    status: str
    service: str
    environment: str
