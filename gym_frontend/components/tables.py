import streamlit as st
import pandas as pd

def stylish_dataframe(data_list: list[dict]):
    """Takes a list of dictionaries from your API and renders a clean table."""
    if not data_list:
        st.info("No records found.")
        return
        
    # Convert to a Pandas DataFrame for automatic column sorting and resizing
    df = pd.DataFrame(data_list)
    
    # Render it without the ugly index numbers on the left
    st.dataframe(df, hide_index=True, use_container_width=True)