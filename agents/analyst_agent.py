# ============================================================================
# File: agents/analyst_agent.py
# ============================================================================
import pandas as pd
from typing import Dict, List
from openai import OpenAI
from .base_agent import BaseAgent


class AnalystAgent(BaseAgent):
    """Agent specialized in data analysis and insights."""
    
    def __init__(self, client: OpenAI):
        super().__init__(
            name="Data Analyst Agent",
            role="""You are a senior data analyst with expertise in statistical analysis and business intelligence.
Your responsibilities:
- Analyze data patterns and trends
- Provide actionable business insights
- Identify anomalies and opportunities
- Suggest further analyses
- Communicate findings clearly to non-technical stakeholders""",
            client=client
        )
    
    def get_tools(self) -> List[Dict]:
        return [{
            "type": "function",
            "function": {
                "name": "analyze_data",
                "description": "Perform statistical analysis on data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "Data to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["descriptive", "trend", "correlation", "summary"],
                            "description": "Type of analysis to perform"
                        }
                    },
                    "required": ["data", "analysis_type"]
                }
            }
        }]
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        if tool_name == "analyze_data":
            try:
                df = pd.DataFrame(tool_input['data'])
                analysis_type = tool_input['analysis_type']
                
                if analysis_type == "descriptive":
                    stats = df.describe().to_dict()
                    return {"success": True, "statistics": stats}
                
                elif analysis_type == "summary":
                    summary = {
                        "row_count": len(df),
                        "column_count": len(df.columns),
                        "columns": list(df.columns),
                        "data_types": df.dtypes.astype(str).to_dict(),
                        "missing_values": df.isnull().sum().to_dict()
                    }
                    return {"success": True, "summary": summary}
                
                elif analysis_type == "correlation":
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 1:
                        corr = df[numeric_cols].corr().to_dict()
                        return {"success": True, "correlations": corr}
                    return {"success": False, "error": "Not enough numeric columns"}
                
                return {"success": True, "message": "Analysis complete"}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"error": "Unknown tool"}
