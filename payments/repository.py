from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.db.scalar(select(Payment).where(Payment.id == payment_id))

    def get_by_provider_order_id(self, provider: str, provider_order_id: str) -> Payment | None:
        q = select(Payment).where(Payment.provider == provider, Payment.provider_order_id == provider_order_id)
        return self.db.scalar(q)

    def list_for_user(self, user_id: int) -> list[Payment]:
        q = select(Payment).where(Payment.user_id == user_id).order_by(Payment.created_at.desc())
        return list(self.db.scalars(q).all())

    def save(self, payment: Payment) -> Payment:
        self.db.commit()
        self.db.refresh(payment)
        return payment
