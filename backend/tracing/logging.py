"""structlog configuration helpers."""

import logging
from typing import cast

import structlog


def configure_logging(log_level: str) -> None:
    """Configure application logging once during startup."""
    resolved_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(level=resolved_level, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(resolved_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a configured structured logger."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
