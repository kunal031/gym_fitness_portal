import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Enum, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from api.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class ReferralStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"

class LedgerAction(str, enum.Enum):
    earned_purchase = "earned_purchase"
    earned_referral = "earned_referral"
    spent_discount = "spent_discount"

class Coupon(Base):
    __tablename__ = "coupons"
    coupon_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    current_uses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

class Referral(Base):
    __tablename__ = "referrals"
    referral_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    referred_email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ReferralStatus] = mapped_column(Enum(ReferralStatus, name="referral_status"), default=ReferralStatus.pending, nullable=False)
    reward_issued: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class LoyaltyWallet(Base):
    __tablename__ = "loyalty_wallets"
    member_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    current_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

class LoyaltyLedger(Base):
    __tablename__ = "loyalty_ledger"
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False) # Can be positive or negative
    action_type: Mapped[LedgerAction] = mapped_column(Enum(LedgerAction, name="ledger_action"), nullable=False)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True) # Links to payment or referral ID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)