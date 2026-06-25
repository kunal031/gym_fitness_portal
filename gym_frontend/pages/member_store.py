import streamlit as st
from components.sidebar import render_sidebar
from api import auth_client

# --- Setup & Security ---
if st.session_state.get("token") is None:
    st.error("Unauthorized access. Please log in.")
    st.stop()

# Draw the left-hand navigation menu
render_sidebar()

# --- Page Header ---
st.title("🛒 Gym Store & Plans")
st.markdown("Upgrade your fitness journey by subscribing to one of our active plans.")
st.divider()

# --- Fetch Live Data ---
with st.spinner("Loading live membership plans..."):
    token = st.session_state.get("token")
    live_plans = auth_client.get_all_plans(token)

# --- Display the Storefront ---
if not live_plans:
    st.info("No membership plans are currently available. Please check back later!")
else:
    # Create a nice responsive grid layout (3 columns)
    cols = st.columns(3)
    
    for idx, plan in enumerate(live_plans):
        # This math cycles through the columns (0, 1, 2, 0, 1, 2...)
        col = cols[idx % 3] 
        
        with col:
            # Create a clean "Product Card" for each plan
            with st.container(border=True):
                # Safely extract data using the correct backend keys
                name = plan.get("name_of_plan", "Unknown Plan")
                cents = plan.get("price_cents", 0)
                price = f"${cents / 100:.2f}"
                duration = plan.get("duration_days", 30)
                desc = plan.get("description", "No description available.")
                plan_id = plan.get("plan_id")
                
                # Draw the card contents
                st.subheader(name)
                st.markdown(f"### {price}")
                st.caption(f"Valid for **{duration} days**")
                st.markdown(f"*{desc}*")
                
                st.divider()
                
                # Expandable Checkout Drawer
                with st.expander("Select & Checkout"):
                    st.markdown("💳 **Secure Mock Checkout**")
                    st.caption("No real credit card required for this MVP.")
                    
                    if st.button("Confirm Payment", key=f"pay_{plan_id}", use_container_width=True, type="primary"):
                        with st.spinner("Processing..."):
                            # Call our new checkout function
                            success, msg = auth_client.process_mock_checkout(
                                token=token, 
                                plan_id=plan_id, 
                                plan_name=name, 
                                amount=(cents / 100)
                            )
                            
                            if success:
                                st.success(msg)
                                st.balloons()
                            else:
                                st.error(msg)