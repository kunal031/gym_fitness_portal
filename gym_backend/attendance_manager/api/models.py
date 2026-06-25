# new models.py
import enum
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Integer, String, Enum, DateTime, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from api.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class QuotaStatus(str, enum.Enum):
    active = "active"
    needs_renewal = "needs_renewal"
    exhausted = "exhausted"

class MemberQuota(Base):
    __tablename__ = "member_quotas"

    member_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    total_allocated_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    days_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[QuotaStatus] = mapped_column(Enum(QuotaStatus, name="quota_status"), default=QuotaStatus.exhausted, nullable=False)
    last_check_in: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    @property
    def remaining_days(self) -> int:
        return self.total_allocated_days - self.days_used


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    log_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    member_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    check_in_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)