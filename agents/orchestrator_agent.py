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


class OrchestratorAgent(BaseAgent):
    """Orchestrator that coordinates between specialized agents."""
    
    def __init__(self, client: OpenAI, sql_agent: SQLAgent, viz_agent: VisualizationAgent, analyst_agent: AnalystAgent):
        super().__init__(
            name="Orchestrator Agent",
            role="""You are the orchestrator agent coordinating a team of specialists:
- SQL Agent: Writes and executes database queries (use this to GET data from database)
- Visualization Agent: Creates charts and graphs
- Data Analyst Agent: Provides insights and analysis

Your responsibilities:
- Understand user requests and break them down into tasks
- Delegate tasks to appropriate agents with clear instructions
- When user asks about database content, ALWAYS delegate to SQL Agent to execute queries
- Coordinate the workflow between agents
- Synthesize results into coherent responses

CRITICAL: For any question about database content (tables, data, records, etc.), you MUST delegate to SQL Agent who will execute the actual query.""",
            client=client
        )
        self.sql_agent = sql_agent
        self.viz_agent = viz_agent
        self.analyst_agent = analyst_agent
    
    def get_tools(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "delegate_to_sql_agent",
                    "description": "Ask SQL Agent to execute a database query and return actual results. Use this whenever you need to retrieve data from the database.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task": {
                                "type": "string",
                                "description": "Clear instruction for what data to retrieve (e.g., 'Get all table names', 'Find top 10 customers by revenue')"
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