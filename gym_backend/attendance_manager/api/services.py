# new services.py
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from api.models import MemberQuota, AttendanceLog, QuotaStatus
from api.schemas import InternalRenewalRequest

def process_renewal_webhook(db: Session, payload: InternalRenewalRequest) -> MemberQuota:
    """Triggered internally by Service B when a payment succeeds."""
    quota = db.get(MemberQuota, payload.member_id)
    
    # If this is their first ever purchase, create the row.
    if not quota:
        quota = MemberQuota(
            member_id=payload.member_id,
            total_allocated_days=payload.days_to_add,
            days_used=0,  # <-- ADD THIS LINE HERE
            status=QuotaStatus.active
        )
        db.add(quota)
    else:
        # If renewing, add days on top of existing total
        quota.total_allocated_days += payload.days_to_add
        
    # Recalculate status based on new totals
    remaining = quota.total_allocated_days - quota.days_used
    if remaining > 5:
        quota.status = QuotaStatus.active
    elif remaining > 0:
        quota.status = QuotaStatus.needs_renewal
        
    db.commit()
    db.refresh(quota)
    return quota

def mark_attendance(db: Session, member_id: int) -> dict:
    """Handles the daily check-in logic."""
    quota = db.get(MemberQuota, member_id)
    if not quota:
        raise HTTPException(status_code=404, detail="Member quota not found. Please purchase a plan.")

    today = datetime.now(timezone.utc).date()
    
    # 1. Reject if out of days
    if quota.status == QuotaStatus.exhausted or quota.days_used >= quota.total_allocated_days:
        raise HTTPException(status_code=403, detail="Quota exhausted. Please renew.")

    # 2. Logic: Only deduct a day if this is their first visit today
    if quota.last_check_in != today:
        quota.days_used += 1
        quota.last_check_in = today

        # Check if they just hit the renewal warning threshold or exhausted their plan
        remaining = quota.total_allocated_days - quota.days_used
        if remaining <= 0:
            quota.status = QuotaStatus.exhausted
        elif remaining <= 5:
            quota.status = QuotaStatus.needs_renewal

    # 3. Always log the physical entry
    log = AttendanceLog(member_id=member_id)
    db.add(log)
    
    db.commit()
    db.refresh(quota)
    
    return {"message": "Access Granted", "remaining_days": quota.total_allocated_days - quota.days_used}


def get_member_quota(db: Session, member_id: int) -> MemberQuota:
    quota = db.get(MemberQuota, member_id)
    if not quota:
        raise HTTPException(status_code=404, detail="Quota not found.")
    
    return quota