import uuid

from podforge_shared_types.enums import SubscriptionTierEnum
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from podforge_api.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_key_hash: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    subscription_tier: Mapped[str] = mapped_column(
        String(50), default=SubscriptionTierEnum.FREE, nullable=False
    )
    monthly_episodes_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_episodes_limit: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
