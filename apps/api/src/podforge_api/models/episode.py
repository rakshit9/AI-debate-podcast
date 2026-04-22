import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from podforge_shared_types.enums import EpisodeFormatEnum, EpisodeStatusEnum
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from podforge_api.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from podforge_api.models.show import Show


class Episode(Base, TimestampMixin):
    __tablename__ = "episodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    show_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(1024), nullable=False)
    format: Mapped[str] = mapped_column(
        String(50), nullable=False, default=EpisodeFormatEnum.DEBATE
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=EpisodeStatusEnum.QUEUED, index=True
    )
    script: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # type: ignore[type-arg]
    audio_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=Decimal("0"))
    published_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    published_urls: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # type: ignore[type-arg]
    pipeline_progress: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)  # type: ignore[type-arg]

    show: Mapped["Show"] = relationship("Show", back_populates="episodes", lazy="selectin")
