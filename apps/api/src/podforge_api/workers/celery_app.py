from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict


class _WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    redis_url: str = "redis://localhost:6379"


_s = _WorkerSettings()

celery_app = Celery(
    "podforge",
    broker=_s.redis_url,
    backend=_s.redis_url,
    include=["podforge_api.workers.episode"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
