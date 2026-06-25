from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from api.models import ContractStatus
from typing import Optional

class FitnessPlanCreate(BaseModel):
    name_of_plan: str = Field(min_length=2, max_length=120)
    duration_days: int = Field(gt=0, le=365)
    price_cents: int = Field(ge=0)


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class FitnessPlanRead(FitnessPlanCreate):
    plan_id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)



class MemberCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone_no: str
    address: str
    password: str               # Required for the hash!
    role: Optional[str] = "user" # Defaults to "user" if not provided

class MemberUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    phone_no: str | None = Field(default=None, max_length=40)
    address: str | None = Field(default=None, max_length=255)

class MembershipMappingRead(BaseModel):
    membership_id: int
    plan_id: int
    status: ContractStatus
    plan_starts_at: datetime
    plan_ends_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MemberRead(BaseModel):
    member_id: int
    full_name: str
    email: EmailStr
    phone_no: str | None
    address: str | None
    created_at: datetime
    memberships: list[MembershipMappingRead] = []
    
    model_config = ConfigDict(from_attributes=True)

class EnrollmentRead(BaseModel):
    member: MemberRead
    membership: MembershipMappingRead

# --- Schemas for Billing ---
class CheckoutPayload(BaseModel):
    plan_id: int
    plan_name: str
    amount: float