import streamlit as st
from api import billing_client, promo_client

def checkout_form(plan_id: int, base_price_cents: int):
    """A clean checkout interface that handles promo codes and payment."""
    with st.container(border=True):
        st.subheader("🛒 Secure Checkout")
        
        # We use a form so the page doesn't reload on every keystroke
        with st.form(key=f"checkout_{plan_id}"):
            promo_code = st.text_input("Promo Code (Optional)")
            
            # The actual submit button
            submit = st.form_submit_button("Confirm Payment", type="primary", use_container_width=True)
            
            if submit:
                with st.spinner("Processing payment..."):
                    # Here we grab the token from the user's backpack
                    token = st.session_state.get("token")
                    
                    # Hit the API!
                    result = billing_client.checkout(token, plan_id, base_price_cents, promo_code)
                    
                    if result:
                        st.success("🎉 Payment successful! Your plan is active.")
                        st.balloons()
                        # Clear the selected plan so they don't buy it twice
                        st.session_state.selected_plan_id = None
                        
def create_coupon_form():
    """For the Gym Owner to generate new marketing campaigns."""
    with st.container(border=True):
        st.subheader("Create Flash Sale")
        
        with st.form("new_coupon"):
            code = st.text_input("Coupon Code", placeholder="e.g., SUMMER50")
            discount = st.slider("Discount Percentage", min_value=1, max_value=100, value=20)
            max_uses = st.number_input("Maximum Uses", min_value=1, value=100)
            expires_at = st.date_input("Expiration Date")
            
            if st.form_submit_button("Launch Campaign", type="primary"):
                # Hit the promo_client API here
                st.success(f"Campaign {code} is now live!")

from api import auth_client

def add_member_form():
    """A secure form for Admins/Masters to manually add users to the database."""
    with st.container(border=True):
        st.subheader("➕ Register New Member")
        
        with st.form("add_member_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name")
                phone = st.text_input("Phone Number")
                # If a Master is using this, let them create other admins!
                role_options = ["user", "admin"] if st.session_state.get("role") == "master" else ["user"]
                role = st.selectbox("Account Role", options=role_options)
                
            with col2:
                email = st.text_input("Email Address")
                address = st.text_input("Home Address")
                password = st.text_input("Temporary Password", type="password")
                
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            
            if submit:
                if not full_name or not email or not password:
                    st.warning("Name, Email, and Password are required.")
                else:
                    with st.spinner("Encrypting and saving to database..."):
                        token = st.session_state.get("token")
                        
                        payload = {
                            "full_name": full_name,
                            "email": email,
                            "phone_no": phone,
                            "address": address,
                            "password": password,
                            "role": role
                        }
                        
                        success, message = auth_client.create_new_user(token, payload)
                        
                        if success:
                            st.success(message)
                        else:
                            st.error(f"Error: {message}")