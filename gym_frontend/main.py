import streamlit as st
import time
from api import auth_client  # Importing your real backend communicator

# --- Page Configuration ---
st.set_page_config(
    page_title="Gym Management System",
    page_icon="🏋️",
    layout="centered"
)

# --- 1. State Management (The Backpack) ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

def logout():
    """Clears the session state to log the user out."""
    st.session_state.token = None
    st.session_state.role = None
    st.session_state.user_id = None
    st.rerun()

# --- 2. The Login Gateway ---
if st.session_state.token is None:
    st.title("🏋️ Gym Portal Login")
    st.markdown("Please log in to access your dashboard.")
    
    # Notice this is the ONLY form called "login_form" now
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Log In")
        
        if submit_button:
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                with st.spinner("Contacting Authentication Server..."):
                    
                    # Using the REAL client to hit your FastAPI backend
                    auth_data = auth_client.login(email, password) 
                    
                    if auth_data:
                        # Store credentials in session state
                        st.session_state.token = auth_data["token"]
                        st.session_state.role = auth_data["role"]
                        st.session_state.user_id = auth_data["user_id"]
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun() # Refresh the app to load the secure pages

# --- 3. Role-Based Navigation (Secure Area) ---
else:
    # Define the pages based on the user's role
    if st.session_state.role in ["admin", "master"]:
        
        # Gym Owner Pages
        pages = {
            "Management": [
                st.Page("pages/admin_dashboard.py", title="Front Desk Kiosk", icon="🏢"),
                st.Page("pages/admin_directory.py", title="Member Directory", icon="👥"),
                st.Page("pages/admin_billing.py", title="Billing & Plans", icon="💳"),
                st.Page("pages/admin_marketing.py", title="Marketing Hub", icon="🏷️"),
            ],
            "Settings": [
                st.Page("pages/account_settings.py", title="Account Settings", icon="⚙️") # <--- ADDED HERE
            ]
        }
        
        if st.session_state.role == "master":
             pages["System Control"] = [
                 st.Page("pages/master_settings.py", title="Master Settings", icon="🔐") 
             ]
             
    else:
        # Gym Member Pages
        pages = {
            "My Portal": [
                st.Page("pages/member_pass.py", title="My Gym Pass", icon="📱"),
                st.Page("pages/member_store.py", title="Store & Checkout", icon="🛒"),
                st.Page("pages/member_wallet.py", title="Loyalty Wallet", icon="🎁"),
            ],
            "Settings": [
                st.Page("pages/account_settings.py", title="Account Settings", icon="⚙️") # <--- ADDED HERE
            ]
        }

    # Initialize and run the Streamlit navigation
    pg = st.navigation(pages)
    pg.run()