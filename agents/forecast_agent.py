# ============================================================================
# File: agents/forecast_agent.py
# ============================================================================
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from typing import Dict, List
from openai import OpenAI
from .base_agent import BaseAgent
import warnings
warnings.filterwarnings('ignore')


class ForecastAgent(BaseAgent):
    """Agent specialized in time series forecasting and predictions."""
    
    def __init__(self, client: OpenAI, db_config: Dict):
        super().__init__(
            name="Forecasting Agent",
            role="""You are an expert data scientist specializing in time series forecasting and predictions.
Your responsibilities:
- Analyze historical data patterns
- Create forecasts for future periods (months or years)
- Provide confidence intervals for predictions
- Explain forecasting methodology
- Use the forecast_data tool to generate predictions

When users ask about:
- Predictions, forecasts, or future values
- "What will X be in 2026/2027"
- "Predict my expenses next year"
- "Expected costs in the future"

You should ALWAYS use the forecast_data tool to generate data-driven predictions.""",
            client=client
        )
        self.db_config = db_config
    
    def get_db_connection(self):
        """Create database connection."""
        return psycopg2.connect(**self.db_config)
    
    def get_tools(self) -> List[Dict]:
        return [{
            "type": "function",
            "function": {
                "name": "forecast_data",
                "description": "Forecast future values based on historical data. Retrieves data from database and generates predictions with confidence intervals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric": {
                            "type": "string",
                            "description": "What to forecast (e.g., 'total cost', 'credit', 'mortgage', 'revenue')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional: specific category to forecast (e.g., 'Credit', 'Mortgage'). Leave empty for total."
                        },
                        "periods_ahead": {
                            "type": "integer",
                            "description": "Number of periods to forecast (e.g., 12 for 12 months, 3 for 3 years)"
                        },
                        "period_type": {
                            "type": "string",
                            "enum": ["month", "year"],
                            "description": "Type of period: 'month' or 'year'"
                        },
                        "target_year": {
                            "type": "integer",
                            "description": "Optional: specific year to predict for (e.g., 2025, 2026)"
                        }
                    },
                    "required": ["metric", "periods_ahead", "period_type"]
                }
            }
        }]
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        if tool_name == "forecast_data":
            try:
                category = tool_input.get('category')
                periods_ahead = tool_input['periods_ahead']
                period_type = tool_input['period_type']
                target_year = tool_input.get('target_year')
                
                print(f"📊 Forecasting: {tool_input['metric']}")
                print(f"   Category: {category or 'All'}")
                print(f"   Periods: {periods_ahead} {period_type}(s)")
                if target_year:
                    print(f"   Target Year: {target_year}")
                
                # Build query based on category and period type
                if period_type == "month":
                    if category:
                        query = f"""
                        SELECT 
                            DATE_TRUNC('month', date) as period,
                            AVG(amount) as value
                        FROM expenses
                        WHERE category = '{category}'
                        GROUP BY period
                        ORDER BY period;
                        """
                    else:
                        query = """
                        SELECT 
                            DATE_TRUNC('month', date) as period,
                            SUM(amount) as value
                        FROM expenses
                        GROUP BY period
                        ORDER BY period;
                        """
                else:  # year
                    if category:
                        query = f"""
                        SELECT 
                            EXTRACT(YEAR FROM date) as year,
                            SUM(amount) as value
                        FROM expenses
                        WHERE category = '{category}'
                        GROUP BY year
                        ORDER BY year;
                        """
                    else:
                        query = """
                        SELECT 
                            EXTRACT(YEAR FROM date) as year,
                            SUM(amount) as value
                        FROM expenses
                        GROUP BY year
                        ORDER BY year;
                        """
                
                # Execute query
                conn = self.get_db_connection()
                df = pd.read_sql(query, conn)
                conn.close()
                
                if len(df) < 3:
                    return {
                        "success": False,
                        "error": "Not enough historical data for forecasting (need at least 3 periods)"
                    }
                
                print(f"✅ Retrieved {len(df)} historical data points")
                
                # Prepare data for forecasting
                df['period_index'] = range(len(df))
                X = df['period_index'].values.reshape(-1, 1)
                y = df['value'].values
                
                # Use polynomial regression for better fit
                poly = PolynomialFeatures(degree=2)
                X_poly = poly.fit_transform(X)
                
                model = LinearRegression()
                model.fit(X_poly, y)
                
                # Calculate R² score
                r_squared = model.score(X_poly, y)
                print(f"📈 Model R² Score: {r_squared:.4f}")
                
                # Generate predictions
                future_indices = np.arange(len(df), len(df) + periods_ahead).reshape(-1, 1)
                X_future_poly = poly.transform(future_indices)
                predictions = model.predict(X_future_poly)
                
                # Calculate confidence intervals (95%)
                residuals = y - model.predict(X_poly)
                std_error = np.std(residuals)
                confidence_interval = 1.96 * std_error
                
                # Create forecast results
                forecast_results = []
                current_date = datetime.now()
                
                for i, pred in enumerate(predictions):
                    if period_type == "month":
                        # Calculate future month
                        future_month = current_date.month + i + 1
                        future_year = current_date.year
                        while future_month > 12:
                            future_month -= 12
                            future_year += 1
                        period_label = f"{future_year}-{future_month:02d}"
                    else:  # year
                        future_year = current_date.year + i + 1
                        period_label = str(future_year)
                    
                    forecast_results.append({
                        "period": period_label,
                        "predicted_value": float(pred),
                        "lower_bound": float(max(0, pred - confidence_interval)),
                        "upper_bound": float(pred + confidence_interval)
                    })
                
                # Historical data for context
                historical_data = []
                for _, row in df.iterrows():
                    if period_type == "month":
                        period_label = row['period'].strftime('%Y-%m')
                    else:
                        period_label = str(int(row['year']))
                    
                    historical_data.append({
                        "period": period_label,
                        "value": float(row['value'])
                    })
                
                print(f"✅ Forecast generated successfully!")
                
                return {
                    "success": True,
                    "forecast": forecast_results,
                    "historical": historical_data,
                    "model_metrics": {
                        "r_squared": float(r_squared),
                        "std_error": float(std_error),
                        "confidence_level": 0.95
                    },
                    "metadata": {
                        "metric": tool_input['metric'],
                        "category": category,
                        "period_type": period_type,
                        "periods_forecast": periods_ahead,
                        "historical_periods": len(df)
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Forecasting error: {str(e)}"
                }
        
        return {"error": "Unknown tool"}