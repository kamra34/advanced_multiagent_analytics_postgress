# ============================================================================
# File: agents/multi_agent_system.py
# ============================================================================
import os
from openai import OpenAI
from typing import Dict
from .sql_agent import SQLAgent
from .visualization_agent import VisualizationAgent
from .analyst_agent import AnalystAgent
from .orchestrator_agent import OrchestratorAgent


class MultiAgentSystem:
    """Main system coordinating all agents."""
    
    def __init__(self, db_config: Dict, api_key: str = None):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        
        # Initialize specialized agents
        self.sql_agent = SQLAgent(self.client, db_config)
        self.viz_agent = VisualizationAgent(self.client)
        self.analyst_agent = AnalystAgent(self.client)
        
        # Initialize orchestrator
        self.orchestrator = OrchestratorAgent(
            self.client,
            self.sql_agent,
            self.viz_agent,
            self.analyst_agent
        )
    
    def query(self, user_message: str) -> str:
        """Process user query through the multi-agent system."""
        print(f"\n{'='*60}")
        print(f"👤 User: {user_message}")
        print(f"{'='*60}")
        
        response = self.orchestrator.chat(user_message)
        return response