# new schemas.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from api.models import QuotaStatus

# --- Incoming Requests ---
class MarkAttendanceRequest(BaseModel):
    member_id: int = Field(gt=0)

class InternalRenewalRequest(BaseModel):
    member_id: int = Field(gt=0)
    days_to_add: int = Field(gt=0)

# --- Outgoing Responses ---
class QuotaRead(BaseModel):
    member_id: int
    total_allocated_days: int
    days_used: int
    remaining_days: int  # We will calculate this dynamically!
    status: QuotaStatus
    
    model_config = ConfigDict(from_attributes=True)

class AttendanceLogRead(BaseModel):
    log_id: UUID
    member_id: int
    check_in_time: datetime
    
    model_config = ConfigDict(from_attributes=True)