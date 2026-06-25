import requests
import streamlit as st

# Point this to wherever your promo_manager is running
BASE_URL = "http://localhost:8003"

def get_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def get_my_wallet(token: str) -> int:
    """Fetches the user's current loyalty points balance."""
    url = f"{BASE_URL}/my-wallet"
    
    try:
        response = requests.get(url, headers=get_headers(token))
        if response.status_code == 200:
            data = response.json()
            return data.get("current_balance", 0)
        return 0
    except requests.exceptions.RequestException:
        st.error("Could not fetch wallet balance.")
        return 0

def create_admin_coupon(token: str, code: str, discount: int, max_uses: int, expires_at: str) -> bool:
    """Admin only: Creates a new marketing coupon."""
    url = f"{BASE_URL}/admin/coupons"
    payload = {
        "code": code,
        "discount_percent": discount,
        "max_uses": max_uses,
        "expires_at": expires_at
    }
    
    try:
        response = requests.post(url, json=payload, headers=get_headers(token))
        if response.status_code == 200:
            return True
        st.error(f"Failed to create coupon: {response.json().get('detail')}")
        return False
    except requests.exceptions.RequestException:
        st.error("Promo Service unreachable.")
        return False