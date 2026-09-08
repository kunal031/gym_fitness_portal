from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr

class CouponCreate(BaseModel):
    code: str = Field(min_length=3, max_length=50)
    discount_percent: int = Field(gt=0, le=100)
    max_uses: int = Field(gt=0)
    expires_at: datetime

class CouponValidationResponse(BaseModel):
    valid: bool
    discount_percent: int
    reason: str | None = None

class RewardCheckoutPayload(BaseModel):
    member_id: int
    amount_spent_cents: int
    coupon_code: str | None = None
    payment_id: str
    points_redeemed: int = Field(default=0, ge=0)

class WalletRead(BaseModel):
    member_id: int
    current_balance: int
    model_config = ConfigDict(from_attributes=True)

class ReferralInvite(BaseModel):
    referred_email: EmailStr