from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from utils.models import BaseModel


class ApplicationVersion(BaseModel):
    __tablename__ = "application_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    architecture: Mapped[str | None] = mapped_column(String(50), nullable=True)
    minimum_supported_version: Mapped[str] = mapped_column(String(50), nullable=False)
    release_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
