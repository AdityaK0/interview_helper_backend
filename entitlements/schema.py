from datetime import datetime
from pydantic import BaseModel


class EntitlementResponse(BaseModel):
    active: bool
    plan: str
    expires_at: datetime | None
    features: dict
