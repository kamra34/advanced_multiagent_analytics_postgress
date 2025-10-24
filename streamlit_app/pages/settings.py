# ============================================================================
# File: streamlit_app/pages/settings.py
# ============================================================================
import streamlit as st
import os


def render_settings_page():
    """Render the settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure your application settings")
    
    with st.expander("🔐 Database Configuration", expanded=True):
        st.code(f"""
DB_HOST=***********
DB_NAME=***********
DB_USER=***********
DB_PORT=***********
        """)
        db_password = os.getenv('DB_PASSWORD')
        if db_password:
            st.success("✅ DB PASSWORD configured")
        else:
            st.error("❌ DB PASSWORD not found")
    
    with st.expander("🤖 OpenAI Configuration"):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            st.success("✅ API Key configured")
        else:
            st.error("❌ API Key not found")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Dashboard", use_container_width=True):
            st.session_state.dashboard_widgets = []
            st.success("Dashboard reset!")
            st.rerun()