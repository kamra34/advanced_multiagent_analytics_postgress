import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from openai import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Data Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --background-color: #0f172a;
        --card-background: #1e293b;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #6366f1;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        color: white;
    }
    
    .assistant-message {
        background-color: #334155;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        color: white;
    }
    
    /* Dashboard card */
    .dashboard-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin: 10px 0;
        border: 1px solid #334155;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e293b;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'dashboard_widgets' not in st.session_state:
    st.session_state.dashboard_widgets = []
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'multi_agent_system' not in st.session_state:
    st.session_state.multi_agent_system = None
if 'show_agent_reasoning' not in st.session_state:
    st.session_state.show_agent_reasoning = True
if 'execution_logs' not in st.session_state:
    st.session_state.execution_logs = []

# Import the multi-agent system classes
class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, role: str, client: OpenAI):
        self.name = name
        self.role = role
        self.client = client
    
    def json_serialize(self, obj):
        """Convert non-serializable objects to serializable types."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime.date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def safe_json_dumps(self, obj):
        """Safely serialize objects to JSON, handling special types."""
        return json.dumps(obj, default=self.json_serialize)
    
    def chat(self, message: str, context: str = "") -> tuple:
        """Send a message to the agent and get a response with data."""
        system_message = f"{self.role}\n\n{context}" if context else self.role
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ]
        
        tools = self.get_tools()
        query_data = None
        execution_log = []
        
        # Log initial state
        execution_log.append({
            "type": "agent_start",
            "agent": self.name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
            temperature=0.7
        )
        
        iteration = 0
        while response.choices[0].finish_reason == "tool_calls":
            iteration += 1
            messages.append(response.choices[0].message)
            
            execution_log.append({
                "type": "decision",
                "iteration": iteration,
                "decision": f"Agent decided to use {len(response.choices[0].message.tool_calls)} tool(s)",
                "timestamp": datetime.now().isoformat()
            })
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                # Log tool call
                execution_log.append({
                    "type": "tool_call",
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                result = self.process_tool_call(tool_name, tool_input)
                
                # Log tool result
                execution_log.append({
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "success": result.get("success", False),
                    "row_count": result.get("row_count"),
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Capture query data for dashboard
                if tool_name == "execute_sql" and result.get("success"):
                    query_data = result.get("data")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": self.safe_json_dumps(result)
                })
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=0.7
            )
        
        final_response = response.choices[0].message.content
        
        # Log completion
        execution_log.append({
            "type": "agent_complete",
            "agent": self.name,
            "response_length": len(final_response),
            "timestamp": datetime.now().isoformat()
        })
        
        return final_response, query_data, execution_log
    
    def get_tools(self) -> List[Dict]:
        return []
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        return {"error": "Tool not implemented"}


class SQLAgent(BaseAgent):
    """Agent specialized in writing and executing SQL queries."""
    
    def __init__(self, client: OpenAI, db_config: Dict):
        super().__init__(
            name="SQL Agent",
            role="""You are an expert SQL developer specializing in PostgreSQL. 
Always use the execute_sql tool to run queries and get actual results.""",
            client=client
        )
        self.db_config = db_config
    
    def get_db_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def get_database_schema(self) -> str:
        query = """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """
        conn = self.get_db_connection()
        try:
            df = pd.read_sql(query, conn)
            schema_text = "Database Schema:\n\n"
            for table in df['table_name'].unique():
                schema_text += f"Table: {table}\n"
                table_cols = df[df['table_name'] == table]
                for _, row in table_cols.iterrows():
                    schema_text += f"  - {row['column_name']} ({row['data_type']})\n"
                schema_text += "\n"
            return schema_text
        finally:
            conn.close()
    
    def get_tools(self) -> List[Dict]:
        return [{
            "type": "function",
            "function": {
                "name": "execute_sql",
                "description": "Execute a SQL query on the PostgreSQL database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The SQL query to execute"},
                        "explanation": {"type": "string", "description": "Brief explanation"}
                    },
                    "required": ["query", "explanation"]
                }
            }
        }]
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        if tool_name == "execute_sql":
            conn = self.get_db_connection()
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(tool_input['query'])
                
                if cursor.description:
                    results = cursor.fetchall()
                    results_list = [dict(row) for row in results]
                    return {"success": True, "data": results_list, "row_count": len(results_list)}
                else:
                    conn.commit()
                    return {"success": True, "message": "Query executed successfully"}
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                conn.close()
        return {"error": "Unknown tool"}


class MultiAgentSystem:
    """Simplified multi-agent system for Streamlit."""
    
    def __init__(self, db_config: Dict, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.sql_agent = SQLAgent(self.client, db_config)
    
    def query(self, user_message: str) -> tuple:
        """Process user query and return response with data and logs."""
        schema = self.sql_agent.get_database_schema()
        response, data, logs = self.sql_agent.chat(user_message, context=schema)
        return response, data, logs


# Database connection function
@st.cache_resource
def init_database():
    """Initialize database connection."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': int(os.getenv('DB_PORT', 5432))
    }
    return db_config


@st.cache_resource
def init_agent_system(_db_config):
    """Initialize the multi-agent system."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("⚠️ OPENAI_API_KEY not found in environment variables")
        return None
    return MultiAgentSystem(_db_config, api_key)


def create_plotly_chart(data, chart_type, x_col, y_col, title):
    """Create a Plotly chart based on the specified type."""
    df = pd.DataFrame(data)
    
    if chart_type == "Bar Chart":
        fig = px.bar(df, x=x_col, y=y_col, title=title, 
                     color_discrete_sequence=['#667eea'])
    elif chart_type == "Line Chart":
        fig = px.line(df, x=x_col, y=y_col, title=title, 
                      markers=True, color_discrete_sequence=['#667eea'])
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=x_col, y=y_col, title=title,
                        color_discrete_sequence=['#667eea'])
    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=x_col, values=y_col, title=title)
    elif chart_type == "Area Chart":
        fig = px.area(df, x=x_col, y=y_col, title=title,
                     color_discrete_sequence=['#667eea'])
    else:
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    
    # Update layout for dark theme
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font_size=20,
        title_font_color='#667eea'
    )
    
    return fig


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/analytics.png", width=80)
    st.title("🎯 Navigation")
    
    page = st.radio(
        "Select Page",
        ["💬 AI Chat", "📊 Dashboard Builder", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Agent reasoning toggle
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
    st.caption("AI Data Analytics Platform v1.0")


# Main content area
if page == "💬 AI Chat":
    st.title("💬 AI Data Analyst Chat")
    st.markdown("Ask questions about your data and get instant insights powered by AI")
    
    # Initialize agent system
    if st.session_state.multi_agent_system is None:
        db_config = init_database()
        st.session_state.multi_agent_system = init_agent_system(db_config)
    
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
                    with st.expander("🔍 View Execution Details", expanded=False):
                        logs = message["execution_logs"]
                        
                        for log in logs:
                            if log["type"] == "agent_start":
                                st.markdown(f"""
                                <div style="background-color: #1e40af; padding: 10px; border-radius: 8px; margin: 5px 0;">
                                    <strong>🚀 Agent Started:</strong> {log['agent']}<br>
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
                                
                                # Show tool input in code block
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
                                    {f"<strong>Error:</strong> {log.get('error')}<br>" if log.get('error') else ''}
                                    <small>⏰ {log['timestamp']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            elif log["type"] == "agent_complete":
                                st.markdown(f"""
                                <div style="background-color: #047857; padding: 10px; border-radius: 8px; margin: 5px 0;">
                                    <strong>🏁 Agent Completed:</strong> {log['agent']}<br>
                                    <strong>Response Length:</strong> {log['response_length']} characters<br>
                                    <small>⏰ {log['timestamp']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                
                # Show data preview if available
                if message.get("data"):
                    with st.expander("📊 View Query Results"):
                        df = pd.DataFrame(message["data"])
                        st.dataframe(df, use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"📌 Pin to Dashboard", key=f"pin_{message['timestamp']}"):
                                st.session_state.current_data = message["data"]
                                st.success("✅ Data pinned! Go to Dashboard Builder to visualize.")
                        with col2:
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "💾 Download CSV",
                                csv,
                                f"data_{message['timestamp']}.csv",
                                "text/csv",
                                key=f"download_{message['timestamp']}"
                            )
    
    # Chat input
    st.divider()
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask a question about your data...",
            placeholder="e.g., Show me monthly revenue trends",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 🚀", use_container_width=True)
    
    if send_button and user_input:
        if st.session_state.multi_agent_system:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().isoformat()
            })
            
            # Get AI response
            with st.spinner("🤔 AI is thinking..."):
                response, data, execution_logs = st.session_state.multi_agent_system.query(user_input)
                
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
        else:
            st.error("⚠️ Agent system not initialized. Check your environment variables.")

elif page == "📊 Dashboard Builder":
    st.title("📊 Interactive Dashboard Builder")
    st.markdown("Create custom visualizations from your data")
    
    # Dashboard creation section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎨 Create New Widget")
        
        if st.session_state.current_data:
            df = pd.DataFrame(st.session_state.current_data)
            
            # Chart configuration
            with st.form("chart_form"):
                widget_title = st.text_input("Widget Title", "My Chart")
                
                chart_type = st.selectbox(
                    "Chart Type",
                    ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Area Chart"]
                )
                
                columns = list(df.columns)
                x_column = st.selectbox("X-Axis", columns)
                y_column = st.selectbox("Y-Axis", [col for col in columns if col != x_column])
                
                submitted = st.form_submit_button("➕ Add to Dashboard", use_container_width=True)
                
                if submitted:
                    widget = {
                        "id": len(st.session_state.dashboard_widgets),
                        "title": widget_title,
                        "type": chart_type,
                        "x_col": x_column,
                        "y_col": y_column,
                        "data": st.session_state.current_data
                    }
                    st.session_state.dashboard_widgets.append(widget)
                    st.success(f"✅ Widget '{widget_title}' added!")
                    st.rerun()
            
            # Data preview
            st.divider()
            st.subheader("📋 Current Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Total rows: {len(df)}")
            
        else:
            st.info("💡 No data available. Go to AI Chat and ask a question to get data!")
    
    with col2:
        st.subheader("📈 Your Dashboard")
        
        if st.session_state.dashboard_widgets:
            # Display widgets in a grid
            for i in range(0, len(st.session_state.dashboard_widgets), 2):
                cols = st.columns(2)
                
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx < len(st.session_state.dashboard_widgets):
                        widget = st.session_state.dashboard_widgets[idx]
                        
                        with col:
                            with st.container():
                                # Widget header
                                widget_col1, widget_col2 = st.columns([4, 1])
                                with widget_col1:
                                    st.markdown(f"**{widget['title']}**")
                                with widget_col2:
                                    if st.button("🗑️", key=f"delete_{widget['id']}"):
                                        st.session_state.dashboard_widgets.pop(idx)
                                        st.rerun()
                                
                                # Chart
                                fig = create_plotly_chart(
                                    widget['data'],
                                    widget['type'],
                                    widget['x_col'],
                                    widget['y_col'],
                                    widget['title']
                                )
                                st.plotly_chart(fig, use_container_width=True)
            
            # Export dashboard
            st.divider()
            if st.button("💾 Export Dashboard Configuration", use_container_width=True):
                config = json.dumps(st.session_state.dashboard_widgets, indent=2)
                st.download_button(
                    "Download JSON",
                    config,
                    "dashboard_config.json",
                    "application/json"
                )
        else:
            st.info("🎨 Your dashboard is empty. Create your first widget to get started!")

else:  # Settings page
    st.title("⚙️ Settings")
    st.markdown("Configure your application settings")
    
    with st.expander("🔐 Database Configuration", expanded=True):
        st.code(f"""
DB_HOST={os.getenv('DB_HOST', 'Not set')}
DB_NAME="***********"
DB_USER="***********"
DB_PORT="***********"
        """)
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'Not set')
        if DB_PASSWORD != 'Not set':
            st.success("✅ DB PASSWORD configured")
        else:
            st.error("❌ DB PASSWORD not found")
    
    with st.expander("🤖 OpenAI Configuration"):
        api_key = os.getenv('OPENAI_API_KEY', 'Not set')
        if api_key != 'Not set':
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