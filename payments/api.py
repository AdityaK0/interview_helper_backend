import json

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from subscriptions.plans import Plan
from users.models import User
from utils.exceptions import AppException
from .schema import CreateOrderRequest, PaymentResponse
from .service import PaymentService

payments_router = APIRouter(prefix="/payments", tags=["Payments"])


@payments_router.post("/orders", response_model=PaymentResponse, status_code=201)
def create_order(data: CreateOrderRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        plan = Plan(data.plan)
    except ValueError:
        raise AppException("Unknown plan", status_code=400, error_code="UNKNOWN_PLAN")
    return PaymentService(db).create_order(current_user.id, plan)


@payments_router.get("/me", response_model=list[PaymentResponse])
def list_my_payments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PaymentService(db).list_for_user(current_user.id)


@payments_router.post("/webhook/{provider}", status_code=200)
async def payment_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    # Generic header name to keep this endpoint provider-agnostic. A real
    # Razorpay integration reads X-Razorpay-Signature specifically — adjust
    # per-provider when wiring a live account.
    x_webhook_signature: str | None = Header(None),
):
    raw_body = await request.body()
    try:
        payload = json.loads(raw_body or b"{}")
    except json.JSONDecodeError:
        raise AppException("Malformed webhook payload", status_code=400, error_code="INVALID_WEBHOOK_PAYLOAD")

    PaymentService(db).handle_webhook(provider, raw_body, payload, x_webhook_signature)
    return {"success": True}
