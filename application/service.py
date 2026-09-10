from sqlalchemy.orm import Session

from .repository import ApplicationVersionRepository
from .schema import VersionCheckResponse
from config import settings
from utils.exceptions import AppException


def _version_tuple(version: str) -> tuple[int, ...]:
    parts = []
    for segment in version.split("."):
        digits = "".join(ch for ch in segment if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


class ApplicationService:
    def __init__(self, db: Session):
        self.repo = ApplicationVersionRepository(db)

    def check_version(self, platform: str, current_version: str | None) -> VersionCheckResponse:
        latest = self.repo.get_latest_for_platform(platform)
        if latest is None:
            raise AppException(
                "No version configured for this platform", status_code=404, error_code="VERSION_NOT_CONFIGURED"
            )

        update_required = (
            current_version is not None
            and _version_tuple(current_version) < _version_tuple(latest.minimum_supported_version)
        )

        return VersionCheckResponse(
            latest_version=latest.version,
            minimum_supported_version=latest.minimum_supported_version,
            update_required=update_required,
            release_url=latest.release_url,
        )

    def get_config(self) -> dict:
        return {"app_env": settings.APP_ENV}
