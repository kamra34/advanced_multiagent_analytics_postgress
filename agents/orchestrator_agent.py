# ============================================================================
# File: agents/orchestrator_agent.py
# ============================================================================
import json
from typing import Dict, List
from openai import OpenAI
from .base_agent import BaseAgent
from .sql_agent import SQLAgent
from .visualization_agent import VisualizationAgent
from .analyst_agent import AnalystAgent
from .forecast_agent import ForecastAgent


class OrchestratorAgent(BaseAgent):
    """Orchestrator that coordinates between specialized agents."""
    
    def __init__(self, client: OpenAI, sql_agent: SQLAgent, viz_agent: VisualizationAgent, 
                 analyst_agent: AnalystAgent, forecast_agent: ForecastAgent):
        super().__init__(
            name="Orchestrator Agent",
            role="""You are the orchestrator agent coordinating a team of specialists:
- SQL Agent: Writes and executes database queries for HISTORICAL data
- Visualization Agent: Creates charts and graphs
- Data Analyst Agent: Provides insights and analysis on existing data
- Forecasting Agent: Creates PREDICTIONS and FORECASTS for FUTURE periods

Your responsibilities:
- Understand user requests and identify if they need historical data OR forecasts
- For questions about PREDICTIONS, FORECASTS, FUTURE values, or "what will happen", use Forecasting Agent
- For questions about PAST data, CURRENT data, or analysis of EXISTING data, use SQL Agent
- Coordinate workflow between multiple agents when needed
- Synthesize results into coherent responses

CRITICAL KEYWORDS for Forecasting Agent:
- predict, forecast, future, projection, expected
- "what will", "next month", "next year", "in 2026", "in 2027"
- "prediction for", "expected cost", "future expenses"

CRITICAL: For historical data, use SQL Agent. For future predictions, use Forecasting Agent.""",
            client=client
        )
        self.sql_agent = sql_agent
        self.viz_agent = viz_agent
        self.analyst_agent = analyst_agent
        self.forecast_agent = forecast_agent
    
    def get_tools(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_sql_agent",
                    "description": "Ask SQL Agent to execute a database query and return HISTORICAL data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Clear instruction for what historical data to retrieve"
                            }
                        },
                        "required": ["task"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_forecast_agent",
                    "description": "Ask Forecasting Agent to predict FUTURE values. Use this for any questions about predictions, forecasts, or future periods.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Clear instruction for what to forecast (e.g., 'Predict total expenses for 2026')"
                            }
                        },
                        "required": ["task"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_viz_agent",
                    "description": "Ask Visualization Agent to create a chart",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "The visualization task"
                            },
                            "data": {
                                "type": "string",
                                "description": "JSON string of data to visualize"
                            }
                        },
                        "required": ["task", "data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_analyst_agent",
                    "description": "Ask Data Analyst Agent to analyze data and provide insights",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "The analysis task"
                            },
                            "data": {
                                "type": "string",
                                "description": "JSON string of data to analyze"
                            }
                        },
                        "required": ["task", "data"]
                    }
                }
            }
        ]
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        if tool_name == "delegate_to_sql_agent":
            schema = self.sql_agent.get_database_schema()
            response = self.sql_agent.chat(tool_input['task'], context=schema)
            return {"response": response, "agent": "SQL Agent"}
        
        elif tool_name == "delegate_to_forecast_agent":
            response = self.forecast_agent.chat(tool_input['task'])
            return {"response": response, "agent": "Forecasting Agent"}
        
        elif tool_name == "delegate_to_viz_agent":
            # Parse the data and create a clearer message
            try:
                data = json.loads(tool_input['data'])
                message = f"""{tool_input['task']}

You must use the create_chart tool with the following data:

Data to visualize: {json.dumps(data, indent=2)}

Remember to include this data in the 'data' parameter of the create_chart tool call."""
            except:
                message = f"{tool_input['task']}\n\nData: {tool_input['data']}"
            
            response = self.viz_agent.chat(message)
            return {"response": response, "agent": "Visualization Agent"}
        
        elif tool_name == "delegate_to_analyst_agent":
            message = f"{tool_input['task']}\n\nData: {tool_input['data']}"
            response = self.analyst_agent.chat(message)
            return {"response": response, "agent": "Data Analyst Agent"}
        
        return {"error": "Unknown tool"}