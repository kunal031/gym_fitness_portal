import streamlit as st

# Import our custom UI bricks
from components.sidebar import render_sidebar
from components.cards import coupon_card
from components.forms import create_coupon_form

# --- Setup & Security ---
# Ensure the user is logged in AND has the correct role
if st.session_state.get("token") is None or st.session_state.get("role") not in ["admin", "master"]:
    st.error("Unauthorized access. Admin privileges required.")
    st.stop()

# Draw the left-hand navigation menu
render_sidebar()

# --- Page Header ---
st.title("🏷️ Marketing Hub")
st.markdown("Manage flash sales, discount codes, and track campaign performance.")
st.divider()

# --- 1. Campaign Launcher ---
# Snap in the form Lego brick we built earlier
create_coupon_form()

st.divider()

# --- 2. Live Campaigns Tracker ---
st.subheader("📊 Active Campaigns")
st.markdown("Monitor how your promo codes are performing in real-time.")

# MOCK DATA: In a fully wired app, you would fetch this using your promo_client
mock_coupons = [
    {"code": "SUMMER50", "discount": 50, "current_uses": 85, "max_uses": 100, "is_active": True},
    {"code": "WELCOME10", "discount": 10, "current_uses": 42, "max_uses": 500, "is_active": True},
    {"code": "FLASH99", "discount": 99, "current_uses": 10, "max_uses": 10, "is_active": False}
]

# Render the coupons in a responsive 2-column grid
col1, col2 = st.columns(2)

for i, coupon in enumerate(mock_coupons):
    # This automatically alternates placing cards in the left and right columns
    with col1 if i % 2 == 0 else col2:
        coupon_card(
            code=coupon["code"],
            discount=coupon["discount"],
            current_uses=coupon["current_uses"],
            max_uses=coupon["max_uses"],
            is_active=coupon["is_active"]
        )