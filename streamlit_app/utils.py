# ============================================================================
# File: streamlit_app/utils.py
# ============================================================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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


def create_forecast_chart(forecast_data):
    """Create a forecast visualization with confidence intervals."""
    historical_df = pd.DataFrame(forecast_data["historical"])
    forecast_df = pd.DataFrame(forecast_data["forecast"])
    
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=historical_df['period'],
        y=historical_df['value'],
        mode='lines+markers',
        name='Historical',
        line=dict(color='#667eea', width=2)
    ))
    
    # Forecast data
    fig.add_trace(go.Scatter(
        x=forecast_df['period'],
        y=forecast_df['predicted_value'],
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#10b981', width=2, dash='dash')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_df['period'],
        y=forecast_df['upper_bound'],
        mode='lines',
        name='Upper Bound',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df['period'],
        y=forecast_df['lower_bound'],
        mode='lines',
        name='95% Confidence',
        fill='tonexty',
        fillcolor='rgba(16, 185, 129, 0.2)',
        line=dict(width=0)
    ))
    
    fig.update_layout(
        template="plotly_dark",
        title="Forecast with Confidence Interval",
        xaxis_title="Period",
        yaxis_title="Value",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified'
    )
    
    return fig