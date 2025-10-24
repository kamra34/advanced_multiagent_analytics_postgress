# ============================================================================
# File: app.py
# ============================================================================
"""
AI Data Analytics Platform - Streamlit Web Application

Beautiful web interface for the multi-agent analytics system with:
- AI Chat interface
- Interactive dashboard builder
- Forecasting capabilities
- Detailed execution logging

Run with: streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import modules
from streamlit_app.config import get_custom_css
from streamlit_app.pages import render_chat_page, render_dashboard_page, render_settings_page
from utils import get_database_config
from agents import MultiAgentSystem

# Page configuration
st.set_page_config(
    page_title="AI Data Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'dashboard_widgets' not in st.session_state:
    st.session_state.dashboard_widgets = []
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'multi_agent_system' not in st.session_state:
    st.session_state.multi_agent_system = None
if 'show_agent_reasoning' not in st.session_state:
    st.session_state.show_agent_reasoning = True

# Initialize agent system
@st.cache_resource
def init_agent_system(_db_config):
    """Initialize the multi-agent system."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found in environment variables")
        return None
    return MultiAgentSystem(_db_config, api_key)


# Initialize on first run
if st.session_state.multi_agent_system is None:
    try:
        db_config = get_database_config()
        st.session_state.multi_agent_system = init_agent_system(db_config)
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/analytics.png", width=80)
    st.title("🎯 Navigation")
    
    page = st.radio(
        "Select Page",
        ["💬 AI Chat", "📊 Dashboard Builder", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Developer options
    st.subheader("🔍 Developer Options")
    st.session_state.show_agent_reasoning = st.toggle(
        "Show Agent Reasoning",
        value=st.session_state.show_agent_reasoning,
        help="Display detailed execution logs showing tool calls and decision-making process"
    )
    
    st.divider()
    
    # Quick Stats
    st.subheader("📈 Quick Stats")
    if st.session_state.current_data:
        st.metric("Data Points", len(st.session_state.current_data))
    st.metric("Dashboard Widgets", len(st.session_state.dashboard_widgets))
    st.metric("Chat Messages", len(st.session_state.chat_history))
    
    st.divider()
    
    # Agent Status
    st.subheader("🤖 Agents")
    if st.session_state.multi_agent_system:
        st.success("✅ SQL Agent")
        st.success("✅ Visualization Agent")
        st.success("✅ Analyst Agent")
        st.success("✅ Forecasting Agent 🔮")
        st.success("✅ Orchestrator")
    else:
        st.error("❌ Agents not initialized")
    
    st.divider()
    st.caption("AI Data Analytics Platform v2.0")

# Main content - route to appropriate page
if page == "💬 AI Chat":
    render_chat_page(st.session_state.multi_agent_system)
elif page == "📊 Dashboard Builder":
    render_dashboard_page()
else:  # Settings
    render_settings_page()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Built using Streamlit, OpenAI, and PostgreSQL | 5 Specialized Agents
    </div>
    """,
    unsafe_allow_html=True
)