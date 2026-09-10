import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from users.models import User
from users.service import UserService
from utils.exceptions import AppException
from utils.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = AppException("Not authenticated", status_code=401, error_code="NOT_AUTHENTICATED")
    if credentials is None:
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise unauthorized

    if payload.get("type") != "access":
        raise unauthorized

    user = UserService(db).repo.get_by_id(int(payload["sub"]))
    if user is None or not user.is_active:
        raise unauthorized
    return user
