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
    
    def chat(self, message: str, context: str = "", execution_logs: list = None) -> tuple:
        """Send a message to the agent and get a response with execution logs."""
        print(f"\n{'🤖 ' + self.name:━^60}")
        
        # Initialize execution logs if not provided
        if execution_logs is None:
            execution_logs = []
        
        # Log agent start
        execution_logs.append({
            "type": "agent_start",
            "agent": self.name,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        system_message = f"{self.role}\n\n{context}" if context else self.role
        
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
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
            temperature=0.7
        )
        
        iteration = 0
        # Process tool calls if any
        while response.choices[0].finish_reason == "tool_calls":
            iteration += 1
            messages.append(response.choices[0].message)
            
            execution_logs.append({
                "type": "decision",
                "iteration": iteration,
                "decision": f"Agent decided to use {len(response.choices[0].message.tool_calls)} tool(s)",
                "timestamp": datetime.now().isoformat()
            })
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)
                
                print(f"\n🔧 Tool: {tool_name}")
                print(f"📋 Input: {json.dumps(tool_input, indent=2)}")
                
                # Log tool call
                execution_logs.append({
                    "type": "tool_call",
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                result = self.process_tool_call(tool_name, tool_input)
                
                # Log tool result
                execution_logs.append({
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "success": result.get("success", False),
                    "row_count": result.get("row_count"),
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat()
                })
                
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
        
        # Store conversation in history
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": final_response})
        
        # Keep only last 10 exchanges (20 messages) to avoid token limits
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        # Log agent completion
        execution_logs.append({
            "type": "agent_complete",
            "agent": self.name,
            "response_length": len(final_response),
            "timestamp": datetime.now().isoformat()
        })
        
        return final_response, execution_logs