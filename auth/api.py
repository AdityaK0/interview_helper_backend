from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from users.schema import UserResponse
from .dependencies import get_current_user
from .schema import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse
from .service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService(db).register(data.email, data.password)


@auth_router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    access_token, refresh_token, user = AuthService(db).login(
        email=data.email,
        password=data.password,
        installation_id=data.installation_id,
        device_name=data.device_name,
        platform=data.platform,
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user)


@auth_router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    access_token, refresh_token, user = AuthService(db).refresh(data.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, user=user)


@auth_router.post("/logout", status_code=204)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    AuthService(db).logout(data.refresh_token)


@auth_router.get("/me", response_model=UserResponse)
def me(current_user=Depends(get_current_user)):
    return current_user
