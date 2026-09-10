from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from users.models import User
from .schema import SubscriptionResponse
from .service import SubscriptionService

subscriptions_router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@subscriptions_router.get("/me", response_model=SubscriptionResponse)
def get_my_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SubscriptionService(db).get_current_for_user(current_user.id)
