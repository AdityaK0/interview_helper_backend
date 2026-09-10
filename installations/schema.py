from datetime import datetime
from pydantic import BaseModel


class InstallationResponse(BaseModel):
    id: int
    installation_id: str
    device_name: str | None
    platform: str | None
    last_seen_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
