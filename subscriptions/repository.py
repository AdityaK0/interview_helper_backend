from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Subscription
from .plans import SubscriptionStatus


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, subscription: Subscription) -> Subscription:
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_by_id(self, subscription_id: int) -> Subscription | None:
        return self.db.scalar(select(Subscription).where(Subscription.id == subscription_id))

    def get_latest_active_for_user(self, user_id: int) -> Subscription | None:
        q = (
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.status == SubscriptionStatus.ACTIVE.value)
            .order_by(Subscription.expires_at.desc().nullsfirst())
        )
        return self.db.scalar(q)

    def list_for_user(self, user_id: int) -> list[Subscription]:
        q = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.created_at.desc())
        return list(self.db.scalars(q).all())

    def save(self, subscription: Subscription) -> Subscription:
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
