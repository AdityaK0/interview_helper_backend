from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from utils.models import BaseModel


class Session(BaseModel):
    """A login session for one user on one installation. The refresh token
    handed to the client is `{id}.{secret}` — only a SHA-256 hash of the
    secret is stored, and each refresh rotates it."""

    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    installation_id: Mapped[int] = mapped_column(Integer, ForeignKey("installations.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
