from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from api.models import MemberInfo
from api.dependencies import get_current_user, require_admin_role
from api.security import verify_password, create_access_token, get_password_hash
from api.models import Transaction
from sqlalchemy.sql import func

from api.models import Attendance
from datetime import datetime, timedelta, timezone

from api.config import get_settings
from api.database import Base, engine, get_db
from api.schemas import (
    MemberCreate,
    MemberRead,
    MemberUpdate,
    FitnessPlanCreate,
    FitnessPlanRead,
    MembershipMappingRead,
    EnrollmentRead,
    PasswordChangeRequest,
    CheckoutPayload
)
from api.services import (
    create_plan,
    list_plans,
    enroll_member,
    list_members,
    get_member_or_404,
    update_member,
)

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Membership Manager service for profile-info, fitnness_plan-info and contracts.",
)


@app.on_event("startup")
def startup() -> None:
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Standard OAuth2 endpoint that returns the token AND user identity."""
    
    # 1. Find the user
    user = db.query(MemberInfo).filter(MemberInfo.email == form_data.username).first()
    
    # 2. Verify password
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create the token
    access_token = create_access_token(data={"sub": str(user.member_id), "role": user.role})
    
    # --- THE FIX: Include role and user_id in the response ---
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,              # Frontend auth_client will grab this!
        "user_id": user.member_id       # Frontend auth_client will grab this!
    }

# --- Example of a Protected Route ---
@app.get("/users/me")
def read_my_profile(current_user: MemberInfo = Depends(get_current_user)):
    """Any logged-in user can access this."""
    return current_user

@app.get("/admin/users")
def get_all_users(db: Session = Depends(get_db), admin_user: MemberInfo = Depends(require_admin_role)):
    """Only admins can access this."""
    return db.query(MemberInfo).all()

# --- Admin User Management ---
@app.post("/admin/register", status_code=status.HTTP_201_CREATED)
def admin_create_user(
    payload: MemberCreate, 
    db: Session = Depends(get_db), 
    admin_user: MemberInfo = Depends(require_admin_role)
):
    """Allows Admins and Masters to manually create new accounts with passwords."""
    
    # 1. Check if email is already taken
    existing_user = db.query(MemberInfo).filter(MemberInfo.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="A user with this email already exists."
        )

    # 2. Hash the password (Assuming payload has a .password attribute)
    new_user = MemberInfo(
        full_name=payload.full_name,
        email=payload.email,
        phone_no=payload.phone_no,
        address=payload.address,
        role=payload.role if hasattr(payload, 'role') else "user",
        hashed_password=get_password_hash(payload.password) 
    )
    
    db.add(new_user)
    db.commit()
    
    return {"message": f"Success! {new_user.full_name} added as a {new_user.role}."}


@app.post("/plans", response_model=FitnessPlanRead, status_code=status.HTTP_201_CREATED)
def create_membership_plan(
    payload: FitnessPlanCreate, 
    db: Session = Depends(get_db),
    admin_user: MemberInfo = Depends(require_admin_role) 
) -> FitnessPlanRead:
    return create_plan(db, payload)


@app.get("/plans", response_model=list[FitnessPlanRead])
def read_plans(db: Session = Depends(get_db)) -> list[FitnessPlanRead]:
    return list_plans(db)


@app.post("/members/enroll", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
def enroll(
    payload: MemberCreate, 
    db: Session = Depends(get_db),
    admin_user: MemberInfo = Depends(require_admin_role)
) -> EnrollmentRead:
    member, membership = enroll_member(db, payload)
    return EnrollmentRead(member=member, membership=membership)


@app.get("/members", response_model=list[MemberRead])
def read_members(db: Session = Depends(get_db)) -> list[MemberRead]:
    return list_members(db)


@app.get("/members/{member_id}", response_model=MemberRead)
def read_member(member_id: int, db: Session = Depends(get_db)) -> MemberRead:
    return get_member_or_404(db, member_id)


@app.patch("/members/{member_id}", response_model=MemberRead)
def patch_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)) -> MemberRead:
    return update_member(db, member_id, payload)

@app.patch("/users/me/password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: MemberInfo = Depends(get_current_user)
):
    """Allows any logged-in user to securely update their own password."""
    
    # 1. Verify the old password matches what is in the database
    if not verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect current password."
        )
    
    # 2. Hash the new password and update the user record
    current_user.hashed_password = get_password_hash(payload.new_password)
    
    # 3. Save changes
    db.commit()
    
    return {"message": "Password updated successfully!"}


# --- The User Checkout Endpoint ---
@app.post("/checkout", status_code=status.HTTP_200_OK)
def process_checkout(
    payload: CheckoutPayload, 
    db: Session = Depends(get_db), 
    current_user: MemberInfo = Depends(get_current_user)
):
    """Processes a mock payment and logs the transaction."""
    new_tx = Transaction(
        member_id=current_user.member_id,
        plan_name=payload.plan_name,
        amount=payload.amount,
        status="Paid"
    )
    db.add(new_tx)
    db.commit()
    
    return {"message": f"Successfully enrolled in {payload.plan_name}!"}

# ---  The Admin Financial Log ---
@app.get("/admin/transactions")
def get_all_transactions(db: Session = Depends(get_db), admin_user: MemberInfo = Depends(require_admin_role)):
    """Fetches all financial logs for the Admin dashboard."""
    # Order by newest first
    return db.query(Transaction).order_by(Transaction.date.desc()).all()

# ---  Dashboard Analytics ---
@app.get("/admin/stats")
def get_dashboard_stats(db: Session = Depends(get_db), admin_user: MemberInfo = Depends(require_admin_role)):
    """Aggregates live database metrics for the Admin dashboard."""
    
    # 1. Count active members (Users only, exclude Admins/Masters)
    active_members = db.query(MemberInfo).filter(MemberInfo.role == "user").count()
    
    # 2. Sum total revenue from the Transactions table
    # We use .scalar() to pull the single number out of the query result, defaulting to 0.0 if None
    total_revenue = db.query(func.sum(Transaction.amount)).filter(Transaction.status == "Paid").scalar() or 0.0
    
    # 3. Check-ins (Count attendance records from the last 24 hours)
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    todays_checkins = db.query(Attendance).filter(Attendance.check_in_time >= yesterday).count()
    
    return {
        "active_members": active_members,
        "total_revenue": total_revenue,
        "todays_checkins": todays_checkins
    }

@app.post("/kiosk/checkin")
def process_kiosk_checkin(
    member_id: int, 
    db: Session = Depends(get_db), 
    admin_user: MemberInfo = Depends(require_admin_role)
):
    """Verifies a member exists and logs their attendance."""
    # 1. Verify the member exists
    member = db.query(MemberInfo).filter(MemberInfo.member_id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member ID not found.")

    # 2. Log the check-in
    new_checkin = Attendance(member_id=member.member_id)
    db.add(new_checkin)
    db.commit()
    
    return {"message": f"Welcome, {member.full_name}!"}