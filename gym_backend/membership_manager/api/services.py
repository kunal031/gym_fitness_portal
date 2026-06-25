from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import (
    MemberInfo,
    FitnessPlan,
    MembershipMapping,
    ContractStatus,
    utcnow,
)

from api.schemas import MemberCreate, MemberUpdate, FitnessPlanCreate


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)

def create_plan(db: Session, payload: FitnessPlanCreate) -> FitnessPlan:
    plan = FitnessPlan(**payload.model_dump())
    db.add(plan)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plan name already exists") from exc
    db.refresh(plan)
    return plan


def list_plans(db: Session) -> list[FitnessPlan]:
    return list(db.scalars(select(FitnessPlan).order_by(FitnessPlan.plan_id)))


def enroll_member(db: Session, payload: MemberCreate) -> tuple[MemberInfo, MembershipMapping]:
    # 1. Verify the plan exists
    plan = db.get(FitnessPlan, payload.plan_id)
    if plan is None or not plan.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active fitness plan not found")

    now = utcnow()
    
    # 2. Create the user profile
    member = MemberInfo(
        full_name=payload.full_name, 
        email=str(payload.email), 
        phone_no=payload.phone_no,
        address=payload.address
    )
    
    # 3. Create the active membership mapping
    membership = MembershipMapping(
        member=member, 
        plan=plan, 
        plan_starts_at=now, 
        plan_ends_at=now + timedelta(days=plan.duration_days)
    )

    db.add_all([member, membership])
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member email already exists") from exc

    db.refresh(member)
    db.refresh(membership)
    return member, membership


def list_members(db: Session) -> list[MemberInfo]:
    return list(db.scalars(select(MemberInfo).order_by(MemberInfo.member_id)))


def get_member_or_404(db: Session, member_id: int) -> MemberInfo:
    member = db.get(MemberInfo, member_id)
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return member


def update_member(db: Session, member_id: int, payload: MemberUpdate) -> MemberInfo:
    member = get_member_or_404(db, member_id)
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(member, field, value)
    db.commit()
    db.refresh(member)
    return member
