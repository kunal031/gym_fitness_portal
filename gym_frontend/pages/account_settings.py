import streamlit as st
from components.sidebar import render_sidebar
from api import auth_client

# --- Setup & Security ---
# Ensure the user is logged in
if st.session_state.get("token") is None:
    st.error("Unauthorized access. Please log in.")
    st.stop()

# Draw the left-hand navigation menu
render_sidebar()

# --- Page Header ---
st.title("⚙️ Account Settings")
st.markdown("Manage your profile and security preferences.")
st.divider()

# --- Password Change Form ---
st.subheader("🔒 Security: Change Password")

with st.container(border=True):
    with st.form("change_password_form", clear_on_submit=True):
        # We use a 2-column layout to make the form look clean
        col1, col2 = st.columns(2)
        
        with col1:
            old_pw = st.text_input("Current Password", type="password")
            
        with col2:
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            
        submit_pw = st.form_submit_button("Update Password", type="primary", use_container_width=True)
        
        # The logic that runs when they click the button
        if submit_pw:
            if not old_pw or not new_pw:
                st.warning("Please fill out all fields.")
            elif new_pw != confirm_pw:
                st.error("Your new passwords do not match!")
            else:
                with st.spinner("Encrypting and updating securely..."):
                    token = st.session_state.get("token")
                    
                    # Call the function we added to auth_client earlier!
                    success, msg = auth_client.change_user_password(token, old_pw, new_pw)
                    
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)