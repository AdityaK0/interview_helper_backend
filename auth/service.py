import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session as DBSession

from .models import Session
from .repository import SessionRepository
from config import settings
from installations.models import Installation
from installations.service import InstallationService
from users.models import User
from users.service import UserService
from utils.exceptions import AppException
from utils.security import (
    create_access_token,
    generate_token_secret,
    hash_token_secret,
    verify_password,
)

logger = logging.getLogger("app.auth")


class AuthService:
    def __init__(self, db: DBSession):
        self.db = db
        self.users = UserService(db)
        self.installations = InstallationService(db)
        self.sessions = SessionRepository(db)

    def register(self, email: str, password: str) -> User:
        user = self.users.register(email, password)
        logger.info("user registered user_id=%s", user.id)
        return user

    def login(
        self,
        email: str,
        password: str,
        installation_id: str,
        device_name: str | None = None,
        platform: str | None = None,
    ) -> tuple[str, str, User]:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            logger.info("login failed email=%s", email)
            raise AppException("Invalid email or password", status_code=401, error_code="INVALID_CREDENTIALS")
        if not user.is_active:
            raise AppException("Account is disabled", status_code=403, error_code="ACCOUNT_DISABLED")

        installation = self.installations.get_active_or_create(
            user_id=user.id, installation_id=installation_id, device_name=device_name, platform=platform
        )

        access_token, refresh_token = self._issue_tokens(user, installation)
        logger.info("login succeeded user_id=%s installation_id=%s", user.id, installation.id)
        return access_token, refresh_token, user

    def refresh(self, refresh_token: str) -> tuple[str, str, User]:
        session = self._resolve_session(refresh_token)

        installation = self.installations.repo.get_by_id(session.installation_id)
        if installation is None or installation.revoked_at is not None:
            raise AppException("Installation has been revoked", status_code=403, error_code="INSTALLATION_REVOKED")

        user = self.users.repo.get_by_id(session.user_id)
        if user is None or not user.is_active:
            raise AppException("Account is disabled", status_code=403, error_code="ACCOUNT_DISABLED")

        self.installations.touch(installation)
        access_token, new_refresh_token = self._rotate_session(session, user)
        logger.info("token refreshed user_id=%s session_id=%s", user.id, session.id)
        return access_token, new_refresh_token, user

    def logout(self, refresh_token: str) -> None:
        session = self._resolve_session(refresh_token)
        session.revoked_at = datetime.utcnow()
        self.sessions.save(session)
        logger.info("logout user_id=%s session_id=%s", session.user_id, session.id)

    def _issue_tokens(self, user: User, installation: Installation) -> tuple[str, str]:
        secret = generate_token_secret()
        session = Session(
            user_id=user.id,
            installation_id=installation.id,
            token_hash=hash_token_secret(secret),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            last_used_at=datetime.utcnow(),
        )
        session = self.sessions.create(session)
        access_token = create_access_token(subject=str(user.id))
        return access_token, f"{session.id}.{secret}"

    def _rotate_session(self, session: Session, user: User) -> tuple[str, str]:
        secret = generate_token_secret()
        session.token_hash = hash_token_secret(secret)
        session.expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        session.last_used_at = datetime.utcnow()
        session = self.sessions.save(session)
        access_token = create_access_token(subject=str(user.id))
        return access_token, f"{session.id}.{secret}"

    def _resolve_session(self, refresh_token: str) -> Session:
        invalid = AppException("Invalid or expired refresh token", status_code=401, error_code="INVALID_REFRESH_TOKEN")

        session_id_raw, _, secret = refresh_token.partition(".")
        if not secret or not session_id_raw.isdigit():
            raise invalid

        session = self.sessions.get_by_id(int(session_id_raw))
        if session is None or session.token_hash != hash_token_secret(secret):
            raise invalid
        if session.revoked_at is not None:
            raise invalid
        if session.expires_at < datetime.utcnow():
            raise invalid
        return session
