from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    pixabay_api_key: str = ""
    pixabay_base_url: str = "https://pixabay.com/api/"


@lru_cache
def get_settings() -> Settings:
    return Settings()
