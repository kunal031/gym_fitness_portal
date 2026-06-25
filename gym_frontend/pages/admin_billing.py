import streamlit as st
from components.sidebar import render_sidebar
from components.cards import stat_card
from components.tables import stylish_dataframe
from api import auth_client

# --- Setup & Security ---
# Secure the page for both Admins and Masters
if st.session_state.get("token") is None or st.session_state.get("role") not in ["admin", "master"]:
    st.error("SECURITY ALERT: Unauthorized access. Admin privileges required.")
    st.stop()

# Draw the standard sidebar
render_sidebar()

# --- Page Header ---
st.title("💳 Billing & Plans")
st.markdown("Manage gym membership tiers, track revenue, and view recent transactions.")
st.divider()

# --- 1. Financial Overview ---
st.subheader("📈 Revenue Snapshot")
col1, col2, col3 = st.columns(3)

# MOCK DATA: In a full deployment, these would be aggregated from your billing_manager service
with col1:
    stat_card("MRR (Monthly Recurring)", "$12,450", "+5.2% vs last month")
with col2:
    stat_card("Pending Invoices", "$840", "12 accounts overdue")
with col3:
    stat_card("YTD Revenue", "$74,200", "On track")

st.divider()

# --- 2. Active Fitness Plans ---
st.subheader("📋 Active Membership Plans")

# Fetch plans from the backend
token = st.session_state.get("token")
plans = auth_client.get_all_plans(token)

if plans:
    # Clean up the data for display
    display_plans = []
    for p in plans:
        # Securely convert the backend's cents back into a readable dollar format
        cents = p.get("price_cents", 0)
        formatted_price = f"${cents / 100:.2f}"
        
        display_plans.append({
            "Plan ID": p.get("plan_id"),
            # --- THE FIX: Tell the frontend to look for the correct backend keys ---
            "Name": p.get("name_of_plan", "Unknown"), 
            "Duration (Days)": p.get("duration_days"),
            "Price": formatted_price,
            "Description": p.get("description", "No description")
        })
        
    stylish_dataframe(display_plans)
else:
    st.info("No membership plans found. Create one below!")

# --- 3. Create New Plan Form ---
with st.expander("➕ Create New Membership Plan"):
    with st.form("create_plan_form", clear_on_submit=True):
        col_name, col_price = st.columns(2)
        with col_name:
            plan_name = st.text_input("Plan Name", placeholder="e.g., Annual VIP Pass")
            duration = st.number_input("Duration (in days)", min_value=1, value=30)
        with col_price:
            plan_price = st.number_input("Price ($)", min_value=0.0, value=50.0, step=5.0)
            description = st.text_input("Description", placeholder="e.g., Full access + Locker")
            
        submit_plan = st.form_submit_button("Launch Plan", type="primary")
        
        if submit_plan:
            if not plan_name:
                st.warning("Plan name is required.")
            else:
                with st.spinner("Saving to database..."):
                    # --- THE FIX: Match the backend schema exactly ---
                    payload = {
                        "name_of_plan": plan_name,              # Updated key
                        "description": description,
                        "price_cents": int(plan_price * 100),   # Convert $50.00 to 5000 cents
                        "duration_days": duration
                    }
                    # -----------------------------------------------
                    
                    success, msg = auth_client.create_fitness_plan(token, payload)
                    if success:
                        st.success(msg)
                        st.rerun() # Refresh the page to show the new table data
                    else:
                        st.error(msg)

st.divider()


# --- 4. Recent Transactions Log ---
st.subheader("🧾 Recent Transactions")

# Fetch live ledger from the backend
live_tx = auth_client.get_transactions(token)

if live_tx:
    display_tx = []
    for t in live_tx:
        display_tx.append({
            "Invoice ID": f"INV-{t.get('id')}",
            "Member ID": t.get("member_id"),
            "Plan": t.get("plan_name"),
            "Amount": f"${t.get('amount'):.2f}",
            "Status": t.get("status"),
            "Date": t.get("date")[:10] if t.get("date") else "Unknown" # Just grab the YYYY-MM-DD
        })
    stylish_dataframe(display_tx)
else:
    st.info("No transactions have been recorded yet.")