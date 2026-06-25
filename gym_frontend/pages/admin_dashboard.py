import streamlit as st
import time

# Import our custom UI bricks
from api import auth_client
from components.sidebar import render_sidebar
from components.cards import stat_card
from components.tables import stylish_dataframe
from components.forms import add_member_form # <--- IMPORTING THE NEW FORM HERE

# --- Setup & Security ---
# Ensure the user is logged in. If they somehow bypass the gateway, stop them.
if st.session_state.get("token") is None:
    st.error("Unauthorized access. Please log in.")
    st.stop()

# Draw the left-hand navigation menu
render_sidebar()

# --- Page Header ---
st.title("🏢 Front Desk & Dashboard")
st.markdown("Welcome to the gym command center.")

# --- 1. Top Level Business Metrics ---
st.subheader("📊 Today's Overview")

# Fetch live stats from the backend!
stats = auth_client.get_dashboard_stats(st.session_state.get("token"))

# Extract the numbers securely, providing fallbacks if the API fails
active_members = stats.get("active_members", 0)
total_rev = stats.get("total_revenue", 0.0)
checkins = stats.get("todays_checkins", 0)

col1, col2, col3 = st.columns(3)

with col1:
    stat_card("Active Members", active_members, "Live from Database")
with col2:
    stat_card("Today's Check-ins", checkins, "Pending Attendance Module")
with col3:
    # Format the float back into a beautiful comma-separated dollar string!
    stat_card("Total Revenue", f"${total_rev:,.2f}", "Live from Transactions")

st.divider()

# --- 2. The Interactive Kiosk ---
st.subheader("🛎️ Express Check-In Kiosk")
st.markdown("Scan a membership barcode or enter the Member ID manually.")

with st.container(border=True):
    # Create an inline input and button
    col_input, col_btn = st.columns([3, 1])
    
    with col_input:
        member_id = st.text_input("Member ID", label_visibility="collapsed", placeholder="e.g., 1042")
        
    with col_btn:
        check_in_clicked = st.button("Check In", type="primary", use_container_width=True)

    if check_in_clicked:
        if not member_id:
            st.warning("Please enter a Member ID.")
        else:
            try:
                # Ensure the admin typed a number
                m_id_int = int(member_id)
                
                with st.spinner("Verifying with Attendance Manager..."):
                    token = st.session_state.get("token")
                    success, msg = auth_client.process_kiosk_checkin(token, m_id_int)
                    
                    if success:
                        st.success(f"✅ Access Granted! {msg}")
                        # Immediately rerun the app to refresh the top-level stats!
                        st.rerun() 
                    else:
                        st.error(f"❌ Access Denied: {msg}")
                        
            except ValueError:
                st.error("Invalid ID format. Please enter numbers only.")

st.divider()

# --- 3. Action Items (Data Table) ---
st.subheader("⚠️ Action Required: Renewals Due")
st.markdown("These members have 5 or fewer days remaining. Reach out to them today.")

# Mock data
mock_renewals = [
    {"Member ID": 2, "Name": "Jane Doe", "Status": "Exhausted", "Last Check-in": "2026-06-20"},
    {"Member ID": 5, "Name": "John Smith", "Status": "Needs Renewal", "Last Check-in": "2026-06-23"},
    {"Member ID": 8, "Name": "Alice Johnson", "Status": "Needs Renewal", "Last Check-in": "2026-06-24"}
]

stylish_dataframe(mock_renewals)

st.divider()

# --- 4. Member Management (THE NEW FORM) ---
# We literally just drop the function here, and Streamlit draws the entire form!
add_member_form()