from datetime import datetime
from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    id: int | None = None
    plan: str
    status: str
    starts_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = {"from_attributes": True}
