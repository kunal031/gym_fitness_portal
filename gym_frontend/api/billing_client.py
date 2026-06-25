import requests
import streamlit as st

# Point this to wherever your billing_manager is running
BASE_URL = "http://localhost:8001" 

def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def get_fitness_plans(token: str) -> list:
    """Fetches available plans for the user to buy."""
    url = f"{BASE_URL}/plans"
    
    try:
        response = requests.get(url, headers=get_headers(token))
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        st.error("Failed to connect to Billing Service.")
        return []

def checkout(token: str, plan_id: int, amount_cents: int, promo_code: str = None) -> dict | None:
    """Processes a payment."""
    url = f"{BASE_URL}/checkout"
    payload = {
        "plan_id": plan_id,
        "amount_cents": amount_cents,
        "coupon_code": promo_code
    }
    
    try:
        response = requests.post(url, json=payload, headers=get_headers(token))
        if response.status_code == 200:
            return response.json()
        
        st.error(f"Checkout failed: {response.json().get('detail')}")
        return None
    except requests.exceptions.RequestException:
        st.error("Payment Gateway unreachable.")
        return None