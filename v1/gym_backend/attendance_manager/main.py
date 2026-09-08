# new main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import Base, engine, get_db
from api.schemas import MarkAttendanceRequest, InternalRenewalRequest, QuotaRead, AttendanceLogRead
from api.services import process_renewal_webhook, mark_attendance, get_member_quota
from api.models import MemberQuota, AttendanceLog, QuotaStatus
from api.config import get_settings
from fastapi.security import APIKeyHeader

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Microservice C: Tracks daily check-ins and plan quotas."
)

# --- MOCKED AUTHENTICATION DEPENDENCIES ---
def get_current_user_id() -> int:
    return 1  

def require_admin_role() -> bool:
    return True
    
api_key_header = APIKeyHeader(name="X-Internal-API-Key")    
def require_internal_service(api_key: str = Depends(api_key_header)) -> bool:
    """Blocks anyone who doesn't have the secret server-to-server password."""
    if api_key != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal API key."
        )
    return True
# -----------------------------------------

@app.on_event("startup")
def startup():
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)


# ==========================================
# INTERNAL SERVICE ENDPOINTS (Service B to C)
# ==========================================
@app.post("/internal/renew", response_model=QuotaRead, dependencies=[Depends(require_internal_service)])
def handle_renewal(payload: InternalRenewalRequest, db: Session = Depends(get_db)):
    """Webhook: Service B calls this when a user successfully pays."""
    return process_renewal_webhook(db, payload)


# ==========================================
# ADMIN ENDPOINTS
# ==========================================
@app.post("/admin/attendance/mark", dependencies=[Depends(require_admin_role)])
def admin_mark_attendance(payload: MarkAttendanceRequest, db: Session = Depends(get_db)):
    """Admin scans a user's ID/Phone to check them into the gym."""
    return mark_attendance(db, payload.member_id)

@app.get("/admin/renewals-due", response_model=list[QuotaRead], dependencies=[Depends(require_admin_role)])
def get_renewals_due(db: Session = Depends(get_db)):
    """Dashboard: Lists all members with 5 or fewer days remaining."""
    return db.query(MemberQuota).filter(MemberQuota.status == QuotaStatus.needs_renewal).all()


# ==========================================
# USER ENDPOINTS (Read Only)
# ==========================================
@app.get("/my-status", response_model=QuotaRead)
def read_my_status(db: Session = Depends(get_db), current_member_id: int = Depends(get_current_user_id)):
    """User checks their own dashboard to see days remaining."""
    return get_member_quota(db, current_member_id)

@app.get("/my-attendance", response_model=list[AttendanceLogRead])
def read_my_attendance_logs(
    db: Session = Depends(get_db), 
    current_member_id: int = Depends(get_current_user_id),
    skip: int = 0,    # How many records to skip
    limit: int = 10   # Maximum records to return per request
):
    """User looks at their check-in history, paginated to prevent memory crashes."""
    return (
        db.query(AttendanceLog)
        .filter(AttendanceLog.member_id == current_member_id)
        .order_by(AttendanceLog.check_in_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )