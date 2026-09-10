from sqlalchemy.orm import Session

from .models import User
from .repository import UserRepository
from utils.exceptions import AppException
from utils.security import hash_password


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, email: str, password: str) -> User:
        if self.repo.get_by_email(email):
            raise AppException("Email is already registered", status_code=409, error_code="EMAIL_TAKEN")
        user = User(email=email, password_hash=hash_password(password))
        return self.repo.create(user)

    def get_or_404(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise AppException("User not found", status_code=404, error_code="USER_NOT_FOUND")
        return user

    def get_by_email(self, email: str) -> User | None:
        return self.repo.get_by_email(email)
