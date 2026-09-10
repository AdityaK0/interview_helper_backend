from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Installation


class InstallationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, installation: Installation) -> Installation:
        self.db.add(installation)
        self.db.commit()
        self.db.refresh(installation)
        return installation

    def get_by_id(self, installation_pk: int) -> Installation | None:
        return self.db.scalar(select(Installation).where(Installation.id == installation_pk))

    def get_by_installation_id(self, installation_id: str) -> Installation | None:
        return self.db.scalar(select(Installation).where(Installation.installation_id == installation_id))

    def list_for_user(self, user_id: int) -> list[Installation]:
        q = select(Installation).where(Installation.user_id == user_id).order_by(Installation.created_at.desc())
        return list(self.db.scalars(q).all())

    def save(self, installation: Installation) -> Installation:
        self.db.commit()
        self.db.refresh(installation)
        return installation
