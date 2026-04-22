from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLMs
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # LangSmith
    langsmith_api_key: str = ""
    langsmith_project: str = "podforge-dev"
    langchain_tracing_v2: str = "true"

    # Infrastructure
    database_url: str = "postgresql+psycopg://podforge:podforge@localhost:5432/podforge"
    redis_url: str = "redis://localhost:6379"

    # Pipeline tuning
    planner_model: str = "claude-sonnet-4-6"
    debate_model: str = "claude-sonnet-4-6"
    outline_model: str = "claude-sonnet-4-6"
    fact_check_model: str = "claude-sonnet-4-6"
    quality_threshold: float = 7.0
    max_outline_retries: int = 3
    debate_max_turns: int = 12
    tts_default_provider: str = "elevenlabs"


@lru_cache
def get_settings() -> Settings:
    return Settings()
