import asyncio
import random
import uuid
import httpx
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks

from api.models import Payment, PaymentStatus
from api.schemas import CheckoutRequest
from api.config import get_settings

settings = get_settings()

async def verify_plan_with_service_a(plan_id: int, requested_amount: int) -> bool:
    """Makes an HTTP call to Service A to fetch ONE specific plan."""
    # Target a specific plan URL instead of the whole list
    url = f"{settings.service_a_url}/plans/{plan_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            
            # Catch the case where Service A says the plan doesn't exist
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Invalid plan ID.")
                
            response.raise_for_status()
            target_plan = response.json()
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service A is currently unreachable.")
        
    # Check the price against the single downloaded plan
    if target_plan["price_cents"] != requested_amount:
        raise HTTPException(status_code=400, detail="Price mismatch detected. Potential tampering.")
        
    return True

async def mock_payment_gateway() -> tuple[bool, str]:
    """Simulates a 1-second network call to a bank."""
    await asyncio.sleep(1.0) 
    is_success = random.random() > 0.2  # 80% success rate
    fake_receipt_id = f"mock_txn_{uuid.uuid4().hex[:10]}"
    return is_success, fake_receipt_id

async def notify_with_retry(client: httpx.AsyncClient, url: str, payload: dict, max_retries: int = 3):
    """Helper function that tries to send a webhook multiple times if it fails."""
    for attempt in range(max_retries):
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True  # Success!
        except Exception as e:
            print(f"Webhook to {url} failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff: waits 1s, then 2s, then 4s
                await asyncio.sleep(2 ** attempt) 
    
    # If we reach here, all retries failed. In a production app, 
    # you would log this to a database table for manual review.
    print(f"CRITICAL ERROR: Failed to notify {url} after {max_retries} attempts.")
    return False

async def notify_downstream_services(member_id: int, plan_id: int, amount_cents: int, payment_id: str, coupon_code: str | None = None):
    """The Webhook Handshake, now protected with automatic retries."""
    async with httpx.AsyncClient() as client:
        
        # 1. Notify Service C (Attendance)
        await notify_with_retry(
            client=client,
            url="http://localhost:8002/internal/renew",
            payload={"member_id": member_id, "days_to_add": 30}
        )

        # 2. Notify Service D (Promo)
        await notify_with_retry(
            client=client,
            url="http://localhost:8003/internal/reward-checkout",
            payload={
                "member_id": member_id, 
                "amount_spent_cents": amount_cents,
                "payment_id": payment_id,
                "coupon_code": coupon_code
            }
        )

async def process_checkout(db: Session, payload: CheckoutRequest, member_id: int, background_tasks: BackgroundTasks) -> Payment:
    # 1. Verify with Service A first
    await verify_plan_with_service_a(payload.plan_id, payload.amount_cents)

    # 2. Create the pending payment record using the secure member_id
    payment = Payment(
        member_id=member_id, # Replaced payload.member_id
        plan_id=payload.plan_id,
        amount_cents=payload.amount_cents
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # 3. Simulate the bank charge
    is_success, txn_id = await mock_payment_gateway()

    # 4. Update the database with the final result
    if is_success:
        payment.status = PaymentStatus.completed
        payment.gateway_transaction_id = txn_id
        db.commit()
        
        # Safely extract coupon_code if you've added it to your CheckoutRequest schema
        coupon_code = getattr(payload, 'coupon_code', None)
        
        # 5. THE HANDSHAKE: Tell downstream services to update their states
        background_tasks.add_task(
            notify_downstream_services, 
            member_id=payment.member_id, 
            plan_id=payment.plan_id, 
            amount_cents=payment.amount_cents,
            payment_id=str(payment.payment_id),
            coupon_code=coupon_code
        )
        
    else:
        payment.status = PaymentStatus.failed
        db.commit()

    db.refresh(payment)
    return payment

def get_member_payments(db: Session, member_id: int) -> list[Payment]:
    return list(db.query(Payment).filter(Payment.member_id == member_id).order_by(Payment.created_at.desc()).all())

def get_all_payments(db: Session) -> list[Payment]:
    return list(db.query(Payment).order_by(Payment.created_at.desc()).all())