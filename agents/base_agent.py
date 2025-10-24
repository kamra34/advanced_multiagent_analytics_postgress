# ============================================================================
# File: agents/base_agent.py
# ============================================================================
import json
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict
from openai import OpenAI


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, role: str, client: OpenAI):
        self.name = name
        self.role = role
        self.client = client
        self.conversation_history = []
    
    def get_tools(self) -> List[Dict]:
        """Override this method in subclasses to define agent-specific tools."""
        return []
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        """Override this method in subclasses to handle tool calls."""
        return {"error": "Tool not implemented"}
    
    def json_serialize(self, obj):
        """Convert non-serializable objects to serializable types."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def safe_json_dumps(self, obj):
        """Safely serialize objects to JSON, handling special types."""
        return json.dumps(obj, default=self.json_serialize)
    
    def chat(self, message: str, context: str = "") -> str:
        """Send a message to the agent and get a response."""
        print(f"\n{'🤖 ' + self.name:━^60}")
        
        system_message = f"{self.role}\n\n{context}" if context else self.role
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ]
        
        tools = self.get_tools()
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
            temperature=0.7
        )
        
        # Process tool calls if any
        while response.choices[0].finish_reason == "tool_calls":
            messages.append(response.choices[0].message)
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                print(f"\n🔧 Tool: {tool_name}")
                print(f"📋 Input: {json.dumps(tool_input, indent=2)}")
                
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
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=0.7
            )
        
        final_response = response.choices[0].message.content
        print(f"\n💬 Response: {final_response}\n")
        return final_response