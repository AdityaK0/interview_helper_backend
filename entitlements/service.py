from sqlalchemy.orm import Session

from subscriptions.plans import PLAN_CATALOG, Plan, SubscriptionStatus
from subscriptions.service import SubscriptionService
from .schema import EntitlementResponse


class EntitlementService:
    """Computes the caller's entitlement from server-side subscription state.
    This is informational for the client — any protected operation elsewhere
    in the backend must call `has_feature`/`get_for_user` itself rather than
    trusting a client-supplied entitlement value."""

    def __init__(self, db: Session):
        self.subscriptions = SubscriptionService(db)

    def get_for_user(self, user_id: int) -> EntitlementResponse:
        subscription = self.subscriptions.get_current_for_user(user_id)
        plan = Plan(subscription["plan"] if isinstance(subscription, dict) else subscription.plan)
        status = subscription["status"] if isinstance(subscription, dict) else subscription.status
        expires_at = subscription["expires_at"] if isinstance(subscription, dict) else subscription.expires_at

        active = status == SubscriptionStatus.ACTIVE.value
        features = PLAN_CATALOG[plan]["features"]

        return EntitlementResponse(active=active, plan=plan.value, expires_at=expires_at, features=features)

    def has_feature(self, user_id: int, feature: str) -> bool:
        entitlement = self.get_for_user(user_id)
        return entitlement.active and bool(entitlement.features.get(feature))
