import datetime
import uuid
from decimal import Decimal

from podforge_shared_types.enums import EpisodeFormat, EpisodeStatus
from pydantic import BaseModel, ConfigDict


class EpisodeCreate(BaseModel):
    show_id: uuid.UUID
    topic: str
    format: EpisodeFormat = "debate"


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
    script: dict  # type: ignore[type-arg]
    audio_url: str | None
    transcript: str | None
    duration_seconds: int | None
    cost_usd: Decimal
    published_at: datetime.datetime | None
    created_at: datetime.datetime
