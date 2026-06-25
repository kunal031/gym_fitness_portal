import streamlit as st
from components.sidebar import render_sidebar

# --- Setup & Security ---
# Ensure only the Master user can access this page
if st.session_state.get("token") is None or st.session_state.get("role") != "master":
    st.error("SECURITY ALERT: Unauthorized access. Master privileges required.")
    st.stop()

# Draw the left-hand navigation menu
render_sidebar()

# --- Page Content ---
st.title("⚙️ Master System Settings")
st.markdown("Welcome, System Overlord. This is your restricted command center.")

st.warning("⚠️ **DANGER ZONE** ⚠️")

with st.container(border=True):
    st.subheader("Database Management")
    st.markdown("These actions will permanently alter the production database.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("Wipe All Member Data", type="primary", use_container_width=True, disabled=True)
    with col2:
        st.button("Force Sync Microservices", use_container_width=True, disabled=True)

st.divider()
st.info("Additional master configurations and logs will be built out here.")