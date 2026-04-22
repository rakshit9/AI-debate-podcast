import uuid
import datetime

from pydantic import BaseModel, ConfigDict

from podforge_shared_types.enums import EpisodeFormat


class ShowCreate(BaseModel):
    name: str
    description: str = ""
    style_guide: str = ""
    default_format: EpisodeFormat = "debate"
    host_ids: list[uuid.UUID] = []
    rss_feed_url: str | None = None
    artwork_url: str | None = None


class ShowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    style_guide: str | None = None
    default_format: EpisodeFormat | None = None
    host_ids: list[uuid.UUID] | None = None
    rss_feed_url: str | None = None
    artwork_url: str | None = None


class ShowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    description: str
    style_guide: str
    default_format: str
    host_ids: list[uuid.UUID]
    rss_feed_url: str | None
    artwork_url: str | None
    created_at: datetime.datetime
