import streamlit as st
from ui.dashboard import render_app
from config.config import ensure_directories

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="AI Road Hazard Detection & Smart Speed Control",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

if __name__ == "__main__":
    ensure_directories()
    render_app()
