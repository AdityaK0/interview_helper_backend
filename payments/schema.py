from datetime import datetime
from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    plan: str = Field(..., description="One of the Plan enum values, e.g. 'monthly'")


class PaymentResponse(BaseModel):
    id: int
    provider: str
    provider_order_id: str | None
    provider_payment_id: str | None
    amount: int
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
