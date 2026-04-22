import datetime
import uuid
from decimal import Decimal
from typing import Any

from podforge_shared_types.enums import EpisodeFormat, EpisodeStatus
from pydantic import BaseModel, ConfigDict


class EpisodeCreate(BaseModel):
    show_id: uuid.UUID
    topic: str
    format: EpisodeFormat = "debate"
    requires_human_approval: bool = False


class EpisodeUpdate(BaseModel):
    topic: str | None = None
    status: EpisodeStatus | None = None
    audio_url: str | None = None
    transcript: str | None = None
    duration_seconds: int | None = None


class EpisodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    show_id: uuid.UUID
    topic: str
    format: str
    status: str
    script: dict[str, Any]
    audio_url: str | None
    transcript: str | None
    duration_seconds: int | None
    cost_usd: Decimal
    published_at: datetime.datetime | None
    celery_task_id: str | None
    published_urls: dict[str, Any]
    pipeline_progress: dict[str, Any]
    created_at: datetime.datetime


class EpisodeStatusResponse(BaseModel):
    episode_id: uuid.UUID
    status: str
    celery_state: str
    pipeline_progress: dict[str, Any]
    error: str | None = None


class EpisodeApproveRequest(BaseModel):
    decision: str = "approve"


class ShowStatsResponse(BaseModel):
    show_id: uuid.UUID
    total_episodes: int
    published_episodes: int
    processing_episodes: int
    queued_episodes: int
    total_duration_seconds: int
    total_cost_usd: Decimal
