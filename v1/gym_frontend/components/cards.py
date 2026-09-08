import streamlit as st

def plan_card(plan_id: int, name: str, price_cents: int, features: list[str], is_admin: bool = False):
    """
    Draws a bordered card for a fitness plan. 
    Changes slightly depending on if an Admin or a User is viewing it.
    """
    price_dollars = price_cents / 100
    
    with st.container(border=True):
        st.subheader(name)
        st.markdown(f"### **${price_dollars:.2f}**")
        
        # Display features nicely
        for feature in features:
            st.markdown(f"✅ {feature}")
            
        st.divider()
        
        if is_admin:
            # Admins might just want to edit or delete plans
            cols = st.columns(2)
            cols[0].button("Edit", key=f"edit_plan_{plan_id}", use_container_width=True)
            cols[1].button("Disable", key=f"disable_plan_{plan_id}", type="primary", use_container_width=True)
        else:
            # Users want to buy the plan
            if st.button("Select Plan", key=f"buy_plan_{plan_id}", type="primary", use_container_width=True):
                # When clicked, save the selected plan to the backpack so the checkout page knows what to charge
                st.session_state.selected_plan_id = plan_id
                st.session_state.selected_plan_price = price_cents
                st.success("Plan selected! Scroll down to checkout.")

def stat_card(title: str, value: str | int, delta: str = None):
    """
    A simple wrapper around st.metric to display key business metrics 
    for the Gym Owner (e.g., Revenue, Active Members).
    """
    with st.container(border=True):
        st.metric(label=title, value=value, delta=delta)

def coupon_card(code: str, discount: int, current_uses: int, max_uses: int, is_active: bool):
    """
    Displays a marketing campaign's status for the Admin Marketing Hub.
    """
    with st.container(border=True):
        cols = st.columns([2, 1])
        
        with cols[0]:
            st.subheader(f"🎟️ {code}")
            st.write(f"**{discount}% OFF**")
            
        with cols[1]:
            # Show a colored badge based on status
            if is_active and current_uses < max_uses:
                st.success("Active")
            else:
                st.error("Exhausted")
                
        # Draw a visual progress bar for usage
        usage_percent = min(current_uses / max_uses, 1.0)
        st.progress(usage_percent, text=f"{current_uses} / {max_uses} Uses")