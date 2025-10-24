# ============================================================================
# File: streamlit_app/pages/chat.py
# ============================================================================
import streamlit as st
from datetime import datetime
import pandas as pd
import json
from streamlit_app.utils import create_forecast_chart


def render_chat_page(multi_agent_system):
    """Render the chat page with AI assistant."""
    st.title("💬 AI Data Analyst Chat")
    st.markdown("Ask questions about your data and get instant insights powered by AI")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                    <div class="user-message">
                        <strong>You:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                    <div class="assistant-message">
                        <strong>🤖 AI Analyst:</strong> {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show execution logs if enabled
                if st.session_state.show_agent_reasoning and message.get("execution_logs"):
                    _render_execution_logs(message["execution_logs"])
                
                # Show data preview if available
                if message.get("data"):
                    _render_data_preview(message)
    
    # Chat input
    st.divider()
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask a question about your data...",
            placeholder="e.g., Show me monthly amount for category Credit.",
            label_visibility="collapsed",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("Send 🚀", use_container_width=True)
    
    if send_button and user_input:
        _process_user_message(user_input, multi_agent_system)


def _process_user_message(user_input, multi_agent_system):
    """Process user message through the multi-agent system."""
    if not multi_agent_system:
        st.error("⚠️ Agent system not initialized. Check your environment variables.")
        return
    
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Create placeholder for real-time logs
    status_placeholder = st.empty()
    logs_placeholder = st.empty()
    
    # Get AI response with execution tracking
    try:
        with status_placeholder:
            st.info("🤔 AI is thinking...")
        
        # Show execution logs in real-time if enabled
        if st.session_state.show_agent_reasoning:
            with logs_placeholder:
                with st.expander("🔍 Execution Details", expanded=True):
                    log_container = st.container()
        
        # Query the system
        response, execution_logs = multi_agent_system.query(user_input)
        
        # Display logs in real-time
        if st.session_state.show_agent_reasoning:
            with logs_placeholder:
                with st.expander("🔍 Execution Details", expanded=True):
                    with log_container:
                        for log in execution_logs:
                            _render_single_log(log)
        
        # Extract data from logs (look for SQL results or forecast data)
        data = None
        for log in execution_logs:
            if log.get("type") == "tool_result" and log.get("success"):
                # Check if this is from orchestrator's result
                pass
        
        # Clear status
        status_placeholder.empty()
        
        # Add assistant message
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "data": data,
            "execution_logs": execution_logs,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update current data
        if data:
            st.session_state.current_data = data
        
        st.rerun()
    except Exception as e:
        status_placeholder.empty()
        st.error(f"❌ Error: {str(e)}")


def _render_single_log(log):
    """Render a single log entry."""
    if log["type"] == "orchestrator_start":
        st.markdown(f"""
        <div style="background-color: #6366f1; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🎯 Orchestrator Started</strong><br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif log["type"] == "agent_delegation":
        st.markdown(f"""
        <div style="background-color: #8b5cf6; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🎯 Delegated to {log['agent']} Agent</strong><br>
            <strong>Task:</strong> {log['task']}<br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif log["type"] == "agent_start":
        st.markdown(f"""
        <div style="background-color: #1e40af; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🚀 {log['agent']} Started</strong><br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif log["type"] == "decision":
        st.markdown(f"""
        <div style="background-color: #7c3aed; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🧠 Decision (Iteration {log['iteration']}):</strong> {log['decision']}<br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif log["type"] == "tool_call":
        st.markdown(f"""
        <div style="background-color: #059669; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🔧 Tool Called:</strong> {log['tool_name']}<br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        if log.get("tool_input"):
            if "query" in log["tool_input"]:
                st.code(log["tool_input"]["query"], language="sql")
            if "explanation" in log["tool_input"]:
                st.caption(f"💡 {log['tool_input']['explanation']}")
            
            # Show forecast parameters
            if log["tool_name"] == "forecast_data":
                params = log["tool_input"]
                st.info(f"""
                📊 **Forecast Parameters:**
                - Metric: {params.get('metric')}
                - Category: {params.get('category', 'All')}
                - Periods: {params.get('periods_ahead')} {params.get('period_type')}(s)
                """)
    
    elif log["type"] == "tool_result":
        success_color = "#059669" if log.get("success") else "#dc2626"
        st.markdown(f"""
        <div style="background-color: {success_color}; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>✅ Tool Result:</strong> {log['tool_name']}<br>
            <strong>Status:</strong> {'Success ✓' if log.get('success') else 'Failed ✗'}<br>
            {f"<strong>Rows:</strong> {log.get('row_count')}<br>" if log.get('row_count') else ''}
            {f"<strong>Error:</strong> {log.get('error')}<br>" if log.get('error') else ''}
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif log["type"] == "agent_complete":
        st.markdown(f"""
        <div style="background-color: #047857; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🏁 {log['agent']} Completed</strong><br>
            <strong>Response Length:</strong> {log['response_length']} characters<br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    elif log["type"] == "orchestrator_complete":
        st.markdown(f"""
        <div style="background-color: #10b981; padding: 10px; border-radius: 8px; margin: 5px 0;">
            <strong>🎉 Orchestrator Completed</strong><br>
            <small>⏰ {log['timestamp']}</small>
        </div>
        """, unsafe_allow_html=True)


def _render_execution_logs(logs):
    """Render execution logs in an expander."""
    with st.expander("🔍 View Execution Details", expanded=False):
        for log in logs:
            if log["type"] == "orchestrator_start":
                st.markdown(f"""
                <div style="background-color: #6366f1; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong>🎯 Orchestrator Started</strong><br>
                    <small>⏰ {log['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            elif log["type"] == "agent_delegation":
                st.markdown(f"""
                <div style="background-color: #8b5cf6; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong>🎯 Delegated to {log['agent']} Agent</strong><br>
                    <strong>Task:</strong> {log['task']}<br>
                    <small>⏰ {log['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
            
            elif log["type"] == "tool_call":
                st.markdown(f"""
                <div style="background-color: #059669; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong>🔧 Tool Called:</strong> {log['tool_name']}<br>
                    <small>⏰ {log['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if log.get("tool_input"):
                    if "query" in log["tool_input"]:
                        st.code(log["tool_input"]["query"], language="sql")
                    if "explanation" in log["tool_input"]:
                        st.caption(f"💡 {log['tool_input']['explanation']}")
            
            elif log["type"] == "tool_result":
                success_color = "#059669" if log.get("success") else "#dc2626"
                st.markdown(f"""
                <div style="background-color: {success_color}; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong>✅ Tool Result:</strong> {log['tool_name']}<br>
                    <strong>Status:</strong> {'Success ✓' if log.get('success') else 'Failed ✗'}<br>
                    {f"<strong>Rows:</strong> {log.get('row_count')}<br>" if log.get('row_count') else ''}
                    <small>⏰ {log['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)


def _render_data_preview(message):
    """Render data preview with download options."""
    with st.expander("📊 View Query Results"):
        data = message["data"]
        
        # Check if this is forecast data
        if isinstance(data, dict) and "forecast" in data:
            _render_forecast_data(data, message["timestamp"])
        else:
            _render_regular_data(data, message["timestamp"])


def _render_forecast_data(forecast_data, timestamp):
    """Render forecast results with visualization."""
    st.subheader("🔮 Forecast Results")
    
    # Display forecast table
    forecast_df = pd.DataFrame(forecast_data["forecast"])
    st.dataframe(forecast_df, use_container_width=True)
    
    # Create and display forecast chart
    fig = create_forecast_chart(forecast_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # Model metrics
    if forecast_data.get("model_metrics"):
        metrics = forecast_data["model_metrics"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R² Score", f"{metrics['r_squared']:.4f}")
        with col2:
            st.metric("Std Error", f"{metrics['std_error']:.2f}")
        with col3:
            st.metric("Confidence", f"{metrics.get('confidence_level', 0.95)*100:.0f}%")
    
    # Download forecast
    csv = forecast_df.to_csv(index=False)
    st.download_button(
        "💾 Download Forecast CSV",
        csv,
        f"forecast_{timestamp}.csv",
        "text/csv",
        key=f"download_forecast_{timestamp}"
    )


def _render_regular_data(data, timestamp):
    """Render regular query results."""
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"📌 Pin to Dashboard", key=f"pin_{timestamp}"):
            st.session_state.current_data = data
            st.success("✅ Data pinned! Go to Dashboard Builder to visualize.")
            st.info("💡 Or use the new Dashboard Builder to select tables directly!")
    with col2:
        csv = df.to_csv(index=False)
        st.download_button(
            "💾 Download CSV",
            csv,
            f"data_{timestamp}.csv",
            "text/csv",
            key=f"download_{timestamp}"
        )