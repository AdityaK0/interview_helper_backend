import hashlib
import hmac
from abc import ABC, abstractmethod
from dataclasses import dataclass

from config import settings
from utils.exceptions import AppException


@dataclass
class PaymentEvent:
    provider_payment_id: str | None
    provider_order_id: str | None
    status: str  # "paid" | "failed" | "refunded"
    raw: dict


class PaymentProvider(ABC):
    name: str

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature_header: str | None) -> bool: ...

    @abstractmethod
    def parse_webhook_event(self, payload: dict) -> PaymentEvent: ...


class RazorpayProvider(PaymentProvider):
    """Foundation only — matches Razorpay's documented webhook signature
    scheme (HMAC-SHA256 of the raw body, hex-encoded, compared to the
    X-Razorpay-Signature header). Event payload parsing is intentionally
    conservative; adjust to the exact fields needed once wired to a live
    account."""

    name = "razorpay"

    def verify_webhook_signature(self, payload: bytes, signature_header: str | None) -> bool:
        if not signature_header or not settings.PAYMENT_PROVIDER_SECRET:
            return False
        expected = hmac.new(
            settings.PAYMENT_PROVIDER_SECRET.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature_header)

    def parse_webhook_event(self, payload: dict) -> PaymentEvent:
        entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_status = entity.get("status")
        status_map = {"captured": "paid", "failed": "failed", "refunded": "refunded"}
        return PaymentEvent(
            provider_payment_id=entity.get("id"),
            provider_order_id=entity.get("order_id"),
            status=status_map.get(razorpay_status, "failed"),
            raw=payload,
        )


_PROVIDERS: dict[str, PaymentProvider] = {"razorpay": RazorpayProvider()}


def get_provider(name: str) -> PaymentProvider:
    provider = _PROVIDERS.get(name)
    if provider is None:
        raise AppException("Unknown payment provider", status_code=400, error_code="UNKNOWN_PROVIDER")
    return provider
