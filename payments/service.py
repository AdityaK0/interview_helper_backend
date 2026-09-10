import logging

from sqlalchemy.orm import Session

from .models import Payment
from .providers import get_provider
from .repository import PaymentRepository
from subscriptions.plans import PLAN_CATALOG, Plan
from subscriptions.service import SubscriptionService
from utils.exceptions import AppException
from utils.security import generate_token_secret

logger = logging.getLogger("app.payments")

DEFAULT_PROVIDER = "razorpay"


class PaymentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PaymentRepository(db)
        self.subscriptions = SubscriptionService(db)

    def create_order(self, user_id: int, plan: Plan) -> Payment:
        if plan not in PLAN_CATALOG:
            raise AppException("Unknown plan", status_code=400, error_code="UNKNOWN_PLAN")

        catalog_entry = PLAN_CATALOG[plan]
        subscription = self.subscriptions.create_pending(user_id, plan)

        # No live provider call is made here (foundation only) — a real
        # integration would call the provider's "create order" API and use
        # its returned order id instead of this local placeholder.
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription.id,
            provider=DEFAULT_PROVIDER,
            provider_order_id=f"local_{generate_token_secret()[:16]}",
            provider_payment_id=None,
            amount=catalog_entry["amount_minor_units"],
            currency=catalog_entry["currency"],
            status="created",
        )
        payment = self.repo.create(payment)
        logger.info("payment order created user_id=%s payment_id=%s plan=%s", user_id, payment.id, plan.value)
        return payment

    def list_for_user(self, user_id: int) -> list[Payment]:
        return self.repo.list_for_user(user_id)

    def handle_webhook(self, provider_name: str, raw_body: bytes, payload: dict, signature_header: str | None) -> None:
        provider = get_provider(provider_name)

        if not provider.verify_webhook_signature(raw_body, signature_header):
            logger.warning("invalid webhook signature provider=%s", provider_name)
            raise AppException("Invalid webhook signature", status_code=400, error_code="INVALID_WEBHOOK_SIGNATURE")

        event = provider.parse_webhook_event(payload)
        if not event.provider_order_id:
            logger.warning("webhook event missing order id provider=%s", provider_name)
            raise AppException("Malformed webhook payload", status_code=400, error_code="INVALID_WEBHOOK_PAYLOAD")

        payment = self.repo.get_by_provider_order_id(provider_name, event.provider_order_id)
        if payment is None:
            logger.warning("webhook for unknown order provider=%s order_id=%s", provider_name, event.provider_order_id)
            raise AppException("Unknown payment order", status_code=404, error_code="PAYMENT_NOT_FOUND")

        payment.status = event.status
        payment.provider_payment_id = event.provider_payment_id or payment.provider_payment_id
        self.repo.save(payment)
        logger.info("payment webhook processed payment_id=%s status=%s", payment.id, payment.status)

        if event.status == "paid" and payment.subscription_id is not None:
            self.subscriptions.activate(payment.subscription_id)
