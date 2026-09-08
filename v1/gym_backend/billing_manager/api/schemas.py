# new schemas.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from api.models import PaymentStatus

class CheckoutRequest(BaseModel):
    plan_id: int
    amount_cents: int = Field(gt=0) 

class PaymentReceipt(BaseModel):
    payment_id: UUID
    member_id: int
    plan_id: int
    amount_cents: int
    currency: str
    status: PaymentStatus
    gateway_transaction_id: str | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)