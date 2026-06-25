import streamlit as st
from components.sidebar import render_sidebar
from components.tables import stylish_dataframe
from api import auth_client

# --- Setup & Security ---
if st.session_state.get("token") is None or st.session_state.get("role") not in ["admin", "master"]:
    st.error("Unauthorized access. Admin privileges required.")
    st.stop()

render_sidebar()

# --- Page Header ---
st.title("👥 Member Directory")
st.markdown("View and manage all registered users in the system.")
st.divider()

# --- Fetch & Display Data ---
with st.spinner("Securely fetching member database..."):
    token = st.session_state.get("token")
    
    # Hit the API client we just built
    raw_members = auth_client.get_all_members(token)
    
    if raw_members:
        # Clean up the data for the UI table
        display_data = []
        for m in raw_members:
            display_data.append({
                # --- THE FIX: Check for both common ID keys ---
                "ID": m.get("id") or m.get("member_id", "Unknown"), 
                "Name": m.get("full_name", "Unknown"),
                "Email": m.get("email", "Unknown"),
                "Phone": m.get("phone_no", "N/A"),
                "Role": str(m.get("role", "User")).upper()
            })
            
        # Draw the table using our Lego brick
        stylish_dataframe(display_data)
    else:
        st.info("No members found or unable to connect to database.")