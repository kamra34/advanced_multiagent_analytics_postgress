# ============================================================================
# File: agents/visualization_agent.py
# ============================================================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List
from openai import OpenAI
from .base_agent import BaseAgent


class VisualizationAgent(BaseAgent):
    """Agent specialized in creating data visualizations."""
    
    def __init__(self, client: OpenAI):
        super().__init__(
            name="Visualization Agent",
            role="""You are a data visualization expert. 
Your responsibilities:
- Choose the most appropriate chart type for the data
- Create clear, insightful visualizations
- Apply best practices in data visualization
- Use appropriate colors, labels, and formatting
- Suggest multiple visualization options when relevant

IMPORTANT: When given data in the message, you MUST extract it and pass it to the create_chart tool in the 'data' parameter. The data will be provided as a JSON string that you need to include in your tool call.""",
            client=client
        )
        self.chart_counter = 0
        sns.set_style("whitegrid")
    
    def get_tools(self) -> List[Dict]:
        return [{
            "type": "function",
            "function": {
                "name": "create_chart",
                "description": "Create a data visualization chart. You MUST provide the data array in the 'data' parameter.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object"
                            },
                            "description": "REQUIRED: Array of data objects to visualize. This must be provided from the data given in the message."
                        },
                        "chart_type": {
                            "type": "string",
                            "enum": ["bar", "line", "scatter", "pie", "histogram", "box", "heatmap"],
                            "description": "Type of chart to create"
                        },
                        "x_column": {
                            "type": "string",
                            "description": "Column name for x-axis"
                        },
                        "y_column": {
                            "type": "string",
                            "description": "Column name for y-axis"
                        },
                        "title": {
                            "type": "string",
                            "description": "Chart title"
                        },
                        "x_label": {
                            "type": "string",
                            "description": "X-axis label"
                        },
                        "y_label": {
                            "type": "string",
                            "description": "Y-axis label"
                        }
                    },
                    "required": ["data", "chart_type", "title"]
                }
            }
        }]
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        if tool_name == "create_chart":
            try:
                df = pd.DataFrame(tool_input['data'])
                chart_type = tool_input['chart_type']
                
                plt.figure(figsize=(12, 7))
                
                if chart_type == "bar":
                    plt.bar(df[tool_input['x_column']], df[tool_input['y_column']])
                    plt.xlabel(tool_input.get('x_label', tool_input['x_column']))
                    plt.ylabel(tool_input.get('y_label', tool_input['y_column']))
                    plt.xticks(rotation=45, ha='right')
                
                elif chart_type == "line":
                    plt.plot(df[tool_input['x_column']], df[tool_input['y_column']], marker='o', linewidth=2)
                    plt.xlabel(tool_input.get('x_label', tool_input['x_column']))
                    plt.ylabel(tool_input.get('y_label', tool_input['y_column']))
                    plt.grid(True, alpha=0.3)
                
                elif chart_type == "scatter":
                    plt.scatter(df[tool_input['x_column']], df[tool_input['y_column']], alpha=0.6, s=100)
                    plt.xlabel(tool_input.get('x_label', tool_input['x_column']))
                    plt.ylabel(tool_input.get('y_label', tool_input['y_column']))
                
                elif chart_type == "pie":
                    plt.pie(df[tool_input['y_column']], labels=df[tool_input['x_column']], 
                           autopct='%1.1f%%', startangle=90)
                    plt.axis('equal')
                
                elif chart_type == "histogram":
                    plt.hist(df[tool_input['x_column']], bins=30, edgecolor='black', alpha=0.7)
                    plt.xlabel(tool_input.get('x_label', tool_input['x_column']))
                    plt.ylabel('Frequency')
                
                elif chart_type == "box":
                    df.boxplot(column=tool_input['y_column'], by=tool_input['x_column'])
                    plt.xlabel(tool_input.get('x_label', tool_input['x_column']))
                    plt.ylabel(tool_input.get('y_label', tool_input['y_column']))
                
                plt.title(tool_input['title'], fontsize=14, fontweight='bold')
                plt.tight_layout()
                
                self.chart_counter += 1
                filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.chart_counter}.png"
                plt.savefig(filename, dpi=300, bbox_inches='tight')
                plt.close()
                
                return {
                    "success": True,
                    "filename": filename,
                    "message": f"Chart saved as {filename}"
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"error": "Unknown tool"}