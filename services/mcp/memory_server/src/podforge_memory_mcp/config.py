from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    qdrant_url: str = "http://localhost:6333"
    database_url: str = "postgresql+asyncpg://podforge:podforge@localhost:5432/podforge"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    host_memory_collection: str = "host_memory"
    episodes_collection: str = "episodes"


@lru_cache
def get_settings() -> Settings:
    return Settings()
