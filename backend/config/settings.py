"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = Field(default="Agentic HR Workflow Engine")
    app_env: str = Field(default="local")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)
    log_level: str = Field(default="INFO")
    api_v1_prefix: str = Field(default="/api/v1")

    openai_api_key: str = Field(default="")
    openai_base_url: str | None = Field(default=None)
    openai_model: str = Field(default="gpt-4.1-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    sqlite_path: Path = Field(default=Path("data/sqlite/app.db"))
    chroma_persist_directory: Path = Field(default=Path("data/chroma"))
    chroma_collection_name: str = Field(default="hr_policy_documents")
    backend_base_url: str = Field(default="http://localhost:8000")
    streamlit_server_port: int = Field(default=8501)
    policy_document_path: Path = Field(default=Path("docs/hr_policy.md"))
    policy_chunk_size: int = Field(default=900)
    policy_chunk_overlap: int = Field(default=150)


@lru_cache
def get_settings() -> Settings:
    """Cache settings for application lifetime."""
    return Settings()
