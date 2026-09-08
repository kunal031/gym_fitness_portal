# new main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from api.database import Base, engine, get_db
from api.schemas import CheckoutRequest, PaymentReceipt
from api.services import process_checkout, get_member_payments, get_all_payments
from api.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Microservice B: Handles financial transactions and receipts."
)

# --- MOCKED AUTHENTICATION DEPENDENCIES ---
def get_current_user_id() -> int:
    return 1  # Pretend Member ID #1 is currently logged in via JWT

def require_admin_role() -> bool:
    is_admin = True  # Toggle to False to test 403 Forbidden
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return True
# -----------------------------------------

@app.on_event("startup")
def startup():
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)


@app.post("/checkout", response_model=PaymentReceipt)
async def checkout(
    payload: CheckoutRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_member_id: int = Depends(get_current_user_id)
):
    """Creates a payment and simulates the bank transaction."""
    return await process_checkout(db, payload, current_member_id, background_tasks)

# --- USER ENDPOINTS ---
@app.get("/my-payments", response_model=list[PaymentReceipt])
def read_my_payments(
    db: Session = Depends(get_db), 
    current_member_id: int = Depends(get_current_user_id)
):
    """Users can ONLY see their own payments based on their auth token."""
    return get_member_payments(db, current_member_id)

# --- ADMIN ENDPOINTS ---
@app.get("/admin/payments", response_model=list[PaymentReceipt], dependencies=[Depends(require_admin_role)])
def read_all_payments(db: Session = Depends(get_db)):
    """Admins can see the entire ledger."""
    return get_all_payments(db)

@app.get("/admin/payments/{member_id}", response_model=list[PaymentReceipt], dependencies=[Depends(require_admin_role)])
def read_specific_member_payments(member_id: int, db: Session = Depends(get_db)):
    """Admins can query a specific user's history."""
    return get_member_payments(db, member_id)