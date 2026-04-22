from enum import StrEnum
from typing import Literal

EpisodeFormat = Literal["debate", "interview", "panel"]
EpisodeStatus = Literal[
    "queued",
    "researching",
    "scripting",
    "debating",
    "fact_checking",
    "synthesizing",
    "mixing",
    "publishing",
    "completed",
    "failed",
]
VoiceProvider = Literal["elevenlabs", "openai", "coqui"]
SubscriptionTier = Literal["free", "pro", "enterprise"]


class EpisodeFormatEnum(StrEnum):
    DEBATE = "debate"
    INTERVIEW = "interview"
    PANEL = "panel"


class EpisodeStatusEnum(StrEnum):
    QUEUED = "queued"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    DEBATING = "debating"
    FACT_CHECKING = "fact_checking"
    SYNTHESIZING = "synthesizing"
    MIXING = "mixing"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceProviderEnum(StrEnum):
    ELEVENLABS = "elevenlabs"
    OPENAI = "openai"
    COQUI = "coqui"


class SubscriptionTierEnum(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
