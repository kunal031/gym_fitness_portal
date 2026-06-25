from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from api.models import Coupon, LoyaltyWallet, LoyaltyLedger, LedgerAction, Referral
from api.schemas import CouponCreate, RewardCheckoutPayload
from sqlalchemy import update

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def create_coupon(db: Session, payload: CouponCreate) -> Coupon:
    coupon = Coupon(**payload.model_dump())
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon

def validate_coupon(db: Session, code: str) -> dict:
    """Checks if a coupon is eligible for use right now."""
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    now = utcnow()

    if not coupon:
        return {"valid": False, "discount_percent": 0, "reason": "Coupon not found"}
    if not coupon.is_active:
        return {"valid": False, "discount_percent": 0, "reason": "Coupon is inactive"}
    if coupon.expires_at <= now:
        return {"valid": False, "discount_percent": 0, "reason": "Coupon expired"}
    if coupon.current_uses >= coupon.max_uses:
        return {"valid": False, "discount_percent": 0, "reason": "Usage limit reached"}

    return {"valid": True, "discount_percent": coupon.discount_percent, "reason": "Success"}


def process_checkout_reward(db: Session, payload: RewardCheckoutPayload) -> dict:
    """Webhook: Triggered by Service B after a successful payment."""
    
    # --- FIX 1: The "Overselling" Race Condition ---
    if payload.coupon_code:
        # We tell the database to increment usage ONLY if it hasn't hit the max.
        # This completely blocks the millisecond concurrency bug.
        rows_updated = db.query(Coupon).filter(
            Coupon.code == payload.coupon_code,
            Coupon.current_uses < Coupon.max_uses
        ).update(
            {"current_uses": Coupon.current_uses + 1}, 
            synchronize_session=False
        )
        
        if rows_updated == 0:
            # If 0 rows updated, the coupon maxed out literally during checkout.
            # In a real app, you'd log this for a customer support review.
            print(f"WARNING: Coupon {payload.coupon_code} usage blocked to prevent overselling.")

    # --- FIX 3: The "Missing Undo" Gap (Spending Points) ---
    if payload.points_redeemed > 0:
        # Atomically deduct points from the wallet
        deduction_success = db.query(LoyaltyWallet).filter(
            LoyaltyWallet.member_id == payload.member_id,
            LoyaltyWallet.current_balance >= payload.points_redeemed # Prevent going into negative
        ).update(
            {"current_balance": LoyaltyWallet.current_balance - payload.points_redeemed}, 
            synchronize_session=False
        )
        
        if deduction_success > 0:
            # Write the deduction to the Immutable Ledger
            spent_ledger = LoyaltyLedger(
                member_id=payload.member_id,
                amount=-payload.points_redeemed, # Negative amount for spending
                action_type=LedgerAction.spent_discount,
                reference_id=payload.payment_id
            )
            db.add(spent_ledger)


    # --- FIX 2: The "Lost Points" Glitch (Earning Points) ---
    points_earned = payload.amount_spent_cents // 100
    if points_earned > 0:
        # 1. Ensure the wallet exists first
        wallet = db.get(LoyaltyWallet, payload.member_id)
        if not wallet:
            wallet = LoyaltyWallet(member_id=payload.member_id, current_balance=0)
            db.add(wallet)
            db.flush() # Force the database to create the row immediately
            
        # 2. Atomically ADD points using the database, not Python memory
        db.query(LoyaltyWallet).filter(
            LoyaltyWallet.member_id == payload.member_id
        ).update(
            {"current_balance": LoyaltyWallet.current_balance + points_earned}, 
            synchronize_session=False
        )

        # 3. Write the earnings to the Immutable Ledger
        earned_ledger = LoyaltyLedger(
            member_id=payload.member_id,
            amount=points_earned,
            action_type=LedgerAction.earned_purchase,
            reference_id=payload.payment_id
        )
        db.add(earned_ledger)

    db.commit()
    return {
        "status": "success", 
        "points_awarded": points_earned, 
        "points_redeemed": payload.points_redeemed
    }

def create_referral(db: Session, referrer_id: int, email: str) -> Referral:
    ref = Referral(referrer_id=referrer_id, referred_email=email)
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref