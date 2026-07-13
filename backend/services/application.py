"""Application-facing service placeholders."""

from dataclasses import dataclass

from backend.config.settings import Settings
from backend.schemas.health import HealthResponse


@dataclass(slots=True)
class ApplicationService:
    """Service facade for system-level application concerns."""

    settings: Settings

    def health(self) -> HealthResponse:
        """Return application health data."""
        return HealthResponse(
            status="ok",
            service=self.settings.app_name,
            environment=self.settings.app_env,
        )
