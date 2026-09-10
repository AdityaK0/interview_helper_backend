from datetime import datetime

from sqlalchemy.orm import Session

from .models import Installation
from .repository import InstallationRepository
from utils.exceptions import AppException


class InstallationService:
    def __init__(self, db: Session):
        self.repo = InstallationRepository(db)

    def get_active_or_create(
        self,
        user_id: int,
        installation_id: str,
        device_name: str | None = None,
        platform: str | None = None,
    ) -> Installation:
        """Resolves the installation for a login/refresh. The client only supplies an
        opaque identifier it generated locally — ownership and revocation state are
        decided here, never trusted from the client."""
        installation = self.repo.get_by_installation_id(installation_id)
        now = datetime.utcnow()

        if installation is None:
            installation = Installation(
                user_id=user_id,
                installation_id=installation_id,
                device_name=device_name,
                platform=platform,
                last_seen_at=now,
            )
            return self.repo.create(installation)

        if installation.user_id != user_id:
            raise AppException(
                "Installation is already bound to a different account",
                status_code=403,
                error_code="INSTALLATION_OWNER_MISMATCH",
            )
        if installation.revoked_at is not None:
            raise AppException("Installation has been revoked", status_code=403, error_code="INSTALLATION_REVOKED")

        installation.last_seen_at = now
        if device_name is not None:
            installation.device_name = device_name
        if platform is not None:
            installation.platform = platform
        return self.repo.save(installation)

    def touch(self, installation: Installation) -> Installation:
        installation.last_seen_at = datetime.utcnow()
        return self.repo.save(installation)

    def list_for_user(self, user_id: int) -> list[Installation]:
        return self.repo.list_for_user(user_id)

    def revoke(self, user_id: int, installation_pk: int) -> Installation:
        installation = self.repo.get_by_id(installation_pk)
        if not installation or installation.user_id != user_id:
            raise AppException("Installation not found", status_code=404, error_code="INSTALLATION_NOT_FOUND")
        installation.revoked_at = datetime.utcnow()
        return self.repo.save(installation)
