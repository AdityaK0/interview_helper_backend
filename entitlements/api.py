from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from users.models import User
from .schema import EntitlementResponse
from .service import EntitlementService

entitlements_router = APIRouter(prefix="/entitlements", tags=["Entitlements"])


@entitlements_router.get("/me", response_model=EntitlementResponse)
def get_my_entitlement(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EntitlementService(db).get_for_user(current_user.id)
