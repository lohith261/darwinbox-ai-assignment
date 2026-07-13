"""Error response schemas."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Stable error response payload."""

    detail: str
    error_code: str
    request_id: str
