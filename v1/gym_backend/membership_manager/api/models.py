import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Float
from datetime import datetime, timezone

from api.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ContractStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    cancelled = "cancelled"
    expired = "expired"


class MemberInfo(Base):
    __tablename__ = "member_info"

    member_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_no: Mapped[str | None] = mapped_column(String(40))
    address: Mapped[str | None] = mapped_column(String(255))

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    
    # Standardizing time storage to UTC
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    # Establishing the link to the mapping table
    memberships: Mapped[list["MembershipMapping"]] = relationship(back_populates="member", cascade="all, delete-orphan")


class FitnessPlan(Base):
    __tablename__ = "fitness_plans"

    plan_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name_of_plan: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    
    # Store money in cents to avoid floating point math errors
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    # Soft-delete flag so we can retire old plans without breaking historical records
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    memberships: Mapped[list["MembershipMapping"]] = relationship(back_populates="plan")


class MembershipMapping(Base):
    __tablename__ = "membership_mapping"

    membership_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Foreign Keys link back to the exact ID of the member and plan
    member_id: Mapped[int] = mapped_column(ForeignKey("member_info.member_id"), nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("fitness_plans.plan_id"), nullable=False)
    
    # Using Enum instead of boolean for better lifecycle management
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, name="contract_status"), default=ContractStatus.active, nullable=False
    )
    
    plan_starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    plan_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Bidirectional relationships so SQLAlchemy can navigate between tables
    member: Mapped["MemberInfo"] = relationship(back_populates="memberships")
    plan: Mapped["FitnessPlan"] = relationship(back_populates="memberships")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("member_info.member_id"))
    plan_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="Paid")

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("member_info.member_id"))
    check_in_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))