# ============================================================================
# File: streamlit_app/pages/dashboard.py
# ============================================================================
import streamlit as st
import pandas as pd
from streamlit_app.utils import create_plotly_chart
import json


def render_dashboard_page():
    """Render the dashboard builder page."""
    st.title("📊 Interactive Dashboard Builder")
    st.markdown("Create custom visualizations directly from your database")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        _render_widget_creator()
    
    with col2:
        _render_dashboard()


def _get_available_tables():
    """Get list of tables from database."""
    if not st.session_state.multi_agent_system:
        return []
    
    try:
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
        """
        conn = st.session_state.multi_agent_system.sql_agent.get_db_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df['table_name'].tolist()
    except Exception as e:
        st.error(f"Error fetching tables: {e}")
        return []


def _get_table_columns(table_name):
    """Get columns for a specific table."""
    if not st.session_state.multi_agent_system:
        return []
    
    try:
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = '{table_name}'
        ORDER BY ordinal_position;
        """
        conn = st.session_state.multi_agent_system.sql_agent.get_db_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df['column_name'].tolist()
    except Exception as e:
        st.error(f"Error fetching columns: {e}")
        return []


def _fetch_table_data(table_name, x_column, y_column, limit=1000):
    """Fetch data from selected table."""
    if not st.session_state.multi_agent_system:
        return None
    
    try:
        query = f"""
        SELECT "{x_column}", "{y_column}"
        FROM {table_name}
        WHERE "{x_column}" IS NOT NULL AND "{y_column}" IS NOT NULL
        LIMIT {limit};
        """
        conn = st.session_state.multi_agent_system.sql_agent.get_db_connection()
        df = pd.read_sql(query, conn)
        conn.close()
        return df.to_dict('records')
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def _render_widget_creator():
    """Render the widget creation form with dynamic table/column selection."""
    st.subheader("🎨 Create New Widget")
    
    # Get available tables
    tables = _get_available_tables()
    
    if not tables:
        st.warning("⚠️ No tables found in database. Check your connection.")
        return
    
    # Table selection
    selected_table = st.selectbox(
        "📋 Select Table",
        tables,
        key="table_selector"
    )
    
    if selected_table:
        # Get columns for selected table
        columns = _get_table_columns(selected_table)
        
        if not columns:
            st.warning(f"No columns found in table '{selected_table}'")
            return
        
        # Chart configuration form
        with st.form("chart_form", clear_on_submit=False):
            widget_title = st.text_input(
                "Widget Title", 
                f"{selected_table} Visualization"
            )
            
            chart_type = st.selectbox(
                "📊 Chart Type",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Area Chart"]
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                x_column = st.selectbox("X-Axis Column", columns)
            with col_b:
                y_columns_available = [col for col in columns if col != x_column]
                y_column = st.selectbox("Y-Axis Column", y_columns_available)
            
            data_limit = st.slider("Data Limit (rows)", 100, 10000, 1000, 100)
            
            submitted = st.form_submit_button("➕ Add to Dashboard", use_container_width=True)
            
            if submitted:
                with st.spinner("Fetching data..."):
                    # Fetch data from database
                    data = _fetch_table_data(selected_table, x_column, y_column, data_limit)
                    
                    if data:
                        widget = {
                            "id": len(st.session_state.dashboard_widgets),
                            "title": widget_title,
                            "type": chart_type,
                            "table": selected_table,
                            "x_col": x_column,
                            "y_col": y_column,
                            "data": data,
                            "data_limit": data_limit
                        }
                        st.session_state.dashboard_widgets.append(widget)
                        st.success(f"✅ Widget '{widget_title}' added!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to fetch data from table")
        
        # Preview data
        st.divider()
        st.subheader("📋 Table Preview")
        
        if st.button("👁️ Preview Table Data", use_container_width=True):
            with st.spinner("Loading preview..."):
                try:
                    query = f"SELECT * FROM {selected_table} LIMIT 10;"
                    conn = st.session_state.multi_agent_system.sql_agent.get_db_connection()
                    preview_df = pd.read_sql(query, conn)
                    conn.close()
                    
                    st.dataframe(preview_df, use_container_width=True)
                    st.caption(f"Showing first 10 rows from {selected_table}")
                except Exception as e:
                    st.error(f"Error loading preview: {e}")


def _render_dashboard():
    """Render the dashboard with widgets."""
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
                            widget_col1, widget_col2, widget_col3 = st.columns([3, 1, 1])
                            with widget_col1:
                                st.markdown(f"**{widget['title']}**")
                            with widget_col2:
                                if st.button("🔄", key=f"refresh_{widget['id']}", help="Refresh data"):
                                    # Refresh widget data
                                    new_data = _fetch_table_data(
                                        widget['table'], 
                                        widget['x_col'], 
                                        widget['y_col'],
                                        widget.get('data_limit', 1000)
                                    )
                                    if new_data:
                                        st.session_state.dashboard_widgets[idx]['data'] = new_data
                                        st.success("✅ Refreshed!")
                                        st.rerun()
                            with widget_col3:
                                if st.button("🗑️", key=f"delete_{widget['id']}", help="Delete widget"):
                                    st.session_state.dashboard_widgets.pop(idx)
                                    st.rerun()
                            
                            # Show table and columns info
                            st.caption(f"📋 {widget['table']} | X: {widget['x_col']} | Y: {widget['y_col']}")
                            
                            # Chart
                            try:
                                fig = create_plotly_chart(
                                    widget['data'],
                                    widget['type'],
                                    widget['x_col'],
                                    widget['y_col'],
                                    widget['title']
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Error rendering chart: {e}")
        
        # Export dashboard
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Export Dashboard Configuration", use_container_width=True):
                # Remove data from config for smaller file
                export_config = []
                for widget in st.session_state.dashboard_widgets:
                    export_widget = widget.copy()
                    export_widget.pop('data', None)  # Remove data, keep structure
                    export_config.append(export_widget)
                
                config = json.dumps(export_config, indent=2)
                st.download_button(
                    "Download JSON",
                    config,
                    "dashboard_config.json",
                    "application/json",
                    key="download_config"
                )
        with col2:
            if st.button("🗑️ Clear All Widgets", use_container_width=True):
                st.session_state.dashboard_widgets = []
                st.success("✅ Dashboard cleared!")
                st.rerun()
    else:
        st.info("🎨 Your dashboard is empty. Create your first widget to get started!")
        st.markdown("""
        **How to create a widget:**
        1. Select a table from your database
        2. Choose columns for X and Y axes
        3. Pick a chart type
        4. Click "Add to Dashboard"
        """)