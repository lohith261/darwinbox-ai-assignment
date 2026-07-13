FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.1 /uv /uvx /usr/local/bin/

COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY backend ./backend
COPY frontend ./frontend
COPY docs ./docs
COPY data ./data

EXPOSE 8000 8501

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
