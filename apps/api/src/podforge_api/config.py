import os
from functools import lru_cache

from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# Walk up from this file to find .env at the repo root, regardless of cwd
_here = os.path.dirname(__file__)
_env_file = next(
    (
        os.path.join(d, ".env")
        for d in [
            os.path.join(_here, "../../../.."),  # repo root from src/podforge_api/
            os.path.join(_here, "../../.."),
            os.path.join(_here, "../.."),
            ".",
        ]
        if os.path.exists(os.path.join(d, ".env"))
    ),
    ".env",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str
    database_sync_url: str

    # Redis
    redis_url: RedisDsn

    # Qdrant
    qdrant_url: str = "http://localhost:6333"

    # MinIO / S3
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "podforge"

    # Auth
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # App
    app_env: str = "development"
    app_debug: bool = False
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
