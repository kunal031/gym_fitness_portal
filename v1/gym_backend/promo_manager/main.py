from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database import Base, engine, get_db
from api.schemas import CouponCreate, CouponValidationResponse, RewardCheckoutPayload, WalletRead, ReferralInvite
from api.services import create_coupon, validate_coupon, process_checkout_reward, create_referral
from api.models import LoyaltyWallet, Referral
from api.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Microservice D: Handles Coupons, Referrals, and Loyalty Points."
)

# --- AUTHENTICATION MOCKS ---
def get_current_user_id() -> int:
    return 1  
def require_admin_role() -> bool:
    return True
def require_internal_service() -> bool:
    # Protects internal webhooks from the outside world
    return True
# ----------------------------

@app.on_event("startup")
def startup():
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)

# ==========================================
# INTERNAL SERVICE ENDPOINTS (Service B to D)
# ==========================================
@app.get("/internal/validate-coupon/{code}", response_model=CouponValidationResponse)
def internal_validate_coupon(code: str, db: Session = Depends(get_db)):
    """Service B calls this BEFORE charging the card."""
    return validate_coupon(db, code)

@app.post("/internal/reward-checkout", dependencies=[Depends(require_internal_service)])
def internal_reward_checkout(payload: RewardCheckoutPayload, db: Session = Depends(get_db)):
    """Service B calls this AFTER successfully charging the card."""
    return process_checkout_reward(db, payload)


# ==========================================
# ADMIN ENDPOINTS (Campaign Management)
# ==========================================
@app.post("/admin/coupons", dependencies=[Depends(require_admin_role)])
def create_new_coupon(payload: CouponCreate, db: Session = Depends(get_db)):
    """Admin creates a new flash sale or discount code."""
    return create_coupon(db, payload)


# ==========================================
# USER ENDPOINTS
# ==========================================
@app.get("/my-wallet", response_model=WalletRead)
def get_my_wallet(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """User checks their loyalty points balance."""
    wallet = db.get(LoyaltyWallet, current_user_id)
    if not wallet:
        # Return an empty wallet if they haven't earned points yet
        return {"member_id": current_user_id, "current_balance": 0}
    return wallet

@app.post("/referrals/invite")
def invite_friend(payload: ReferralInvite, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    """User submits a friend's email to get a referral link."""
    ref = create_referral(db, current_user_id, payload.referred_email)
    # In a real system, this would also trigger an email to be sent.
    return {"message": "Invite generated", "referral_id": ref.referral_id}