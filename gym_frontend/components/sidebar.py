import streamlit as st

def render_sidebar():
    """Draws the consistent sidebar profile and logout button."""
    with st.sidebar:
        # Gym branding
        st.image("https://cdn-icons-png.flaticon.com/512/2964/2964514.png", width=80) 
        st.title("FitCore Gym")
        
        # Safely fetch session state variables (fallback to 'Guest' if None)
        role = st.session_state.get("role") or "Guest"
        user_id = st.session_state.get("user_id") or "Unknown"
        
        # Display user identity
        st.markdown(f"**Logged in as:** {role.title()}")
        st.caption(f"User ID: {user_id}")
        
        st.divider()
        
        # The logout logic
        if st.button("Log Out", use_container_width=True, type="secondary"):
            # Completely wipe the session state backpack to ensure security
            st.session_state.clear() 
            # Rerun the app so main.py kicks them back to the login screen
            st.rerun()