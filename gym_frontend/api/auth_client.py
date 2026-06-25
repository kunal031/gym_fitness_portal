import requests
import streamlit as st

# Point this to wherever your membership_manager is running
BASE_URL = "http://localhost:8000" 

def login(email: str, password: str) -> dict | None:
    """Hits the real FastAPI login endpoint and retrieves the JWT."""
    url = f"{BASE_URL}/login"
    
    # OAuth2 expects 'username' and 'password' as form data
    payload = {
        "username": email, 
        "password": password
    }
    
    try:
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "token": data.get("access_token"),
                "role": data.get("role", "user"), # Default to user if not provided
                "user_id": data.get("user_id")
            }
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException:
        st.error("Cannot connect to the Authentication Server. Is it running?")
        return None

def create_new_user(token: str, user_data: dict) -> tuple[bool, str]:
    """Hits the membership_manager to securely register a new user."""
    url = f"{BASE_URL}/admin/register"
    
    # Inject the Master/Admin JWT token to pass the backend security lock
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=user_data, headers=headers)
        
        # FastAPI returns 201 Created for successful POST requests
        if response.status_code in [200, 201]:
            return True, response.json().get("message")
        else:
            return False, response.json().get("detail", "Failed to create user.")
            
    except requests.exceptions.RequestException:
        return False, "Cannot connect to the Authentication Server."
    
def get_all_members(token: str) -> list:
    """Fetches the full list of registered members for Admin/Master view."""
    url = f"{BASE_URL}/admin/users"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.exceptions.RequestException:
        st.error("Cannot connect to the backend server.")
        return []
    

def change_user_password(token: str, old_pw: str, new_pw: str) -> tuple[bool, str]:
    """Hits the backend to update the current user's password."""
    url = f"{BASE_URL}/users/me/password"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "old_password": old_pw,
        "new_password": new_pw
    }
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True, response.json().get("message")
        else:
            return False, response.json().get("detail", "Failed to update password.")
            
    except requests.exceptions.RequestException:
        return False, "Cannot connect to the Authentication Server."
    
def get_all_plans(token: str) -> list:
    """Fetches the list of active fitness plans from the backend."""
    url = f"{BASE_URL}/plans"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []

def create_fitness_plan(token: str, plan_data: dict) -> tuple[bool, str]:
    """Hits the membership_manager to create a new gym plan."""
    url = f"{BASE_URL}/plans"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=plan_data, headers=headers)
        if response.status_code == 201:
            return True, "Successfully created new fitness plan!"
        else:
            return False, response.json().get("detail", "Failed to create plan.")
    except requests.exceptions.RequestException:
        return False, "Cannot connect to the server."
    

def process_mock_checkout(token: str, plan_id: int, plan_name: str, amount: float) -> tuple[bool, str]:
    """Sends the purchase request to the backend."""
    url = f"{BASE_URL}/checkout"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"plan_id": plan_id, "plan_name": plan_name, "amount": amount}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return True, response.json().get("message")
        return False, "Payment failed."
    except requests.exceptions.RequestException:
        return False, "Server connection error."

def get_transactions(token: str) -> list:
    """Fetches the financial ledger for Admins."""
    url = f"{BASE_URL}/admin/transactions"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []
    
def get_dashboard_stats(token: str) -> dict:
    """Fetches high-level aggregated stats for the Admin Dashboard."""
    url = f"{BASE_URL}/admin/stats"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return {}
    except requests.exceptions.RequestException:
        return {}
    
def process_kiosk_checkin(token: str, member_id: int) -> tuple[bool, str]:
    """Sends a check-in request from the Admin Kiosk to the backend."""
    # We pass the member_id as a query parameter
    url = f"{BASE_URL}/kiosk/checkin?member_id={member_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return True, response.json().get("message")
        return False, response.json().get("detail", "Check-in failed.")
    except requests.exceptions.RequestException:
        return False, "Server connection error."