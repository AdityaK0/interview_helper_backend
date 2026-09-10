from sqlalchemy.orm import Session as DBSession
from sqlalchemy import select

from .models import Session


class SessionRepository:
    def __init__(self, db: DBSession):
        self.db = db

    def create(self, session: Session) -> Session:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_id(self, session_id: int) -> Session | None:
        return self.db.scalar(select(Session).where(Session.id == session_id))

    def save(self, session: Session) -> Session:
        self.db.commit()
        self.db.refresh(session)
        return session
