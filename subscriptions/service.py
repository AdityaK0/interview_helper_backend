from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .models import Subscription
from .plans import PLAN_CATALOG, Plan, SubscriptionStatus
from .repository import SubscriptionRepository
from utils.exceptions import AppException

FREE_TIER = {"plan": Plan.FREE.value, "status": SubscriptionStatus.ACTIVE.value, "starts_at": None, "expires_at": None}


class SubscriptionService:
    def __init__(self, db: Session):
        self.repo = SubscriptionRepository(db)

    def get_current_for_user(self, user_id: int) -> Subscription | dict:
        """Every user has *some* entitlement — users with no paid subscription
        are implicitly on the FREE plan, so this never returns None."""
        subscription = self.repo.get_latest_active_for_user(user_id)
        if subscription is None:
            return FREE_TIER

        if subscription.expires_at is not None and subscription.expires_at < datetime.utcnow():
            subscription.status = SubscriptionStatus.EXPIRED.value
            self.repo.save(subscription)
            return FREE_TIER

        return subscription

    def list_for_user(self, user_id: int) -> list[Subscription]:
        return self.repo.list_for_user(user_id)

    def create_pending(self, user_id: int, plan: Plan) -> Subscription:
        if plan not in PLAN_CATALOG:
            raise AppException("Unknown plan", status_code=400, error_code="UNKNOWN_PLAN")
        subscription = Subscription(
            user_id=user_id,
            plan=plan.value,
            status=SubscriptionStatus.PENDING.value,
            starts_at=datetime.utcnow(),
            expires_at=None,
        )
        return self.repo.create(subscription)

    def activate(self, subscription_id: int) -> Subscription:
        """Called once a payment for this subscription is confirmed (see payments module)."""
        subscription = self.repo.get_by_id(subscription_id)
        if not subscription:
            raise AppException("Subscription not found", status_code=404, error_code="SUBSCRIPTION_NOT_FOUND")

        duration_days = PLAN_CATALOG[Plan(subscription.plan)]["duration_days"]
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.starts_at = datetime.utcnow()
        subscription.expires_at = (
            datetime.utcnow() + timedelta(days=duration_days) if duration_days is not None else None
        )
        return self.repo.save(subscription)

    def cancel(self, user_id: int, subscription_id: int) -> Subscription:
        subscription = self.repo.get_by_id(subscription_id)
        if not subscription or subscription.user_id != user_id:
            raise AppException("Subscription not found", status_code=404, error_code="SUBSCRIPTION_NOT_FOUND")
        subscription.status = SubscriptionStatus.CANCELLED.value
        return self.repo.save(subscription)
