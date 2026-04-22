import uuid
import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from podforge_shared_types.enums import SubscriptionTier


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    subscription_tier: SubscriptionTier
    monthly_episodes_used: int
    monthly_episodes_limit: int
    is_active: bool
    created_at: datetime.datetime
