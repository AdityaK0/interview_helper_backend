from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import ApplicationVersion


class ApplicationVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_for_platform(self, platform: str) -> ApplicationVersion | None:
        q = (
            select(ApplicationVersion)
            .where(ApplicationVersion.platform == platform, ApplicationVersion.is_active.is_(True))
            .order_by(ApplicationVersion.created_at.desc())
        )
        return self.db.scalar(q)
