from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from users.models import User
from .schema import InstallationResponse
from .service import InstallationService

installations_router = APIRouter(prefix="/installations", tags=["Installations"])


@installations_router.get("/me", response_model=list[InstallationResponse])
def list_my_installations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return InstallationService(db).list_for_user(current_user.id)


@installations_router.post("/{installation_pk}/revoke", response_model=InstallationResponse)
def revoke_installation(
    installation_pk: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return InstallationService(db).revoke(current_user.id, installation_pk)
