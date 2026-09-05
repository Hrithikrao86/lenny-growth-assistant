from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password123@db:5432/lenny_assistant"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_embedding_model: str = "nomic-embed-text"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    default_provider: str = "ollama"
    similarity_threshold: float = Field(default=0.55, ge=0, le=1)
    retrieval_top_k: int = Field(default=5, ge=1, le=10)
    max_history_messages: int = Field(default=12, ge=0, le=30)
    log_level: str = "INFO"
    transcript_glob: str = "data/transcripts/**/transcript.md"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
