# ============================================================================
# File: agents/orchestrator_agent.py
# ============================================================================
import json
from datetime import datetime
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
            response, logs = self.sql_agent.chat(tool_input['task'], context=schema, execution_logs=self.execution_logs)
            return {"response": response, "agent": "SQL Agent"}
        
        elif tool_name == "delegate_to_forecast_agent":
            response, logs = self.forecast_agent.chat(tool_input['task'], execution_logs=self.execution_logs)
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
            
            response, logs = self.viz_agent.chat(message, execution_logs=self.execution_logs)
            return {"response": response, "agent": "Visualization Agent"}
        
        elif tool_name == "delegate_to_analyst_agent":
            message = f"{tool_input['task']}\n\nData: {tool_input['data']}"
            response, logs = self.analyst_agent.chat(message, execution_logs=self.execution_logs)
            return {"response": response, "agent": "Data Analyst Agent"}
        
        return {"error": "Unknown tool"}
    
    def chat(self, message: str, context: str = "", execution_logs: list = None) -> tuple:
        """Send a message and get response with execution logs."""
        # Initialize execution logs
        if execution_logs is None:
            execution_logs = []
        
        self.execution_logs = execution_logs
        
        # Log orchestrator start
        execution_logs.append({
            "type": "orchestrator_start",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        system_message = self.role
        
        # Build messages with conversation history
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history for context
        messages.extend(self.conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        tools = self.get_tools()
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )
        
        iteration = 0
        # Process tool calls if any
        while response.choices[0].finish_reason == "tool_calls":
            iteration += 1
            messages.append(response.choices[0].message)
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                # Log delegation
                agent_name = tool_name.replace("delegate_to_", "").replace("_agent", "").upper()
                execution_logs.append({
                    "type": "agent_delegation",
                    "agent": agent_name,
                    "task": tool_input.get('task', ''),
                    "timestamp": datetime.now().isoformat()
                })
                
                result = self.process_tool_call(tool_name, tool_input)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": self.safe_json_dumps(result)
                })
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )
        
        final_response = response.choices[0].message.content
        
        # Store conversation in history
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": final_response})
        
        # Keep only last 10 exchanges (20 messages) to avoid token limits
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        # Log completion
        execution_logs.append({
            "type": "orchestrator_complete",
            "timestamp": datetime.now().isoformat()
        })
        
        return final_response, execution_logs