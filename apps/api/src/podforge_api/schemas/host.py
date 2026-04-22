import uuid
import datetime

from pydantic import BaseModel, ConfigDict, Field

from podforge_shared_types.enums import VoiceProvider


class HostCreate(BaseModel):
    name: str
    personality_prompt: str
    voice_id: str
    voice_provider: VoiceProvider
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: str = "claude-sonnet-4-6"


class HostUpdate(BaseModel):
    name: str | None = None
    personality_prompt: str | None = None
    voice_id: str | None = None
    voice_provider: VoiceProvider | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    model: str | None = None


class HostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    personality_prompt: str
    voice_id: str
    voice_provider: str
    temperature: float
    model: str
    created_at: datetime.datetime
