import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from podforge_api.models.base import Base, TimestampMixin
from podforge_shared_types.enums import EpisodeFormatEnum

if TYPE_CHECKING:
    from podforge_api.models.episode import Episode
    from podforge_api.models.user import User


class Show(Base, TimestampMixin):
    __tablename__ = "shows"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    style_guide: Mapped[str] = mapped_column(Text, nullable=False, default="")
    default_format: Mapped[str] = mapped_column(
        String(50), nullable=False, default=EpisodeFormatEnum.DEBATE
    )
    host_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False, default=list
    )
    rss_feed_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    artwork_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    owner: Mapped["User"] = relationship("User", backref="shows", lazy="selectin")
    episodes: Mapped[list["Episode"]] = relationship(
        "Episode", back_populates="show", lazy="selectin"
    )
