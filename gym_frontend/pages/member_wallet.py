import streamlit as st

# Import our custom UI bricks
from components.sidebar import render_sidebar
from components.cards import stat_card
from components.tables import stylish_dataframe

# --- Setup & Security ---
if st.session_state.get("token") is None:
    st.error("Unauthorized access. Please log in.")
    st.stop()

# Draw the left-hand navigation menu
render_sidebar()

# --- Page Header ---
st.title("🎁 Loyalty Wallet")
st.markdown("Earn points on purchases and referrals. Use them for discounts on your next plan!")
st.divider()

# --- 1. Current Balance ---
# MOCK DATA: In a real app, use: promo_client.get_my_wallet(st.session_state.token)
current_points = 1250 

# We use our stat_card Lego brick to make this look bold and impressive
st.subheader("Your Balance")
stat_card(
    title="Available Loyalty Points", 
    value=f"⭐ {current_points}", 
    delta="+150 this month"
)

st.divider()

# --- 2. Invite & Earn (Referral System) ---
st.subheader("🤝 Invite a Friend")
st.markdown("Give a friend 20% off their first month, and get **500 points** when they join!")

with st.container(border=True):
    with st.form("referral_form"):
        friend_email = st.text_input("Friend's Email Address", placeholder="friend@example.com")
        
        # We align the button nicely
        submitted = st.form_submit_button("Send Invite Link", type="primary", use_container_width=True)
        
        if submitted:
            if friend_email:
                # MOCK API: Here you would trigger promo_client.create_referral(...)
                st.success(f"Invite successfully sent to {friend_email}! We'll credit your account when they sign up.")
                st.balloons() # Give it that rewarding pop
            else:
                st.warning("Please enter a valid email address.")

st.divider()

# --- 3. Points History (The Ledger) ---
st.subheader("📜 Recent Activity")

# MOCK DATA: Representing the LoyaltyLedger from your promo_manager backend
mock_ledger = [
    {"Date": "2026-06-20", "Action": "Earned (Purchase)", "Points": "+500", "Reference": "INV-1042"},
    {"Date": "2026-06-15", "Action": "Spent (Discount)", "Points": "-200", "Reference": "INV-0988"},
    {"Date": "2026-06-01", "Action": "Earned (Referral)", "Points": "+950", "Reference": "REF-Alice"}
]

# Render the ledger beautifully using our table component
stylish_dataframe(mock_ledger)