# ============================================================================
# File: main.py
# ============================================================================
import os
from dotenv import load_dotenv
from agents import MultiAgentSystem
from utils import get_database_config

# Load environment variables
load_dotenv()


def main():
    """Main CLI application."""
    print("🚀 Initializing Multi-Agent PostgreSQL Analyst System...")
    
    # Get configuration
    try:
        db_config = get_database_config()
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        return
    
    # Initialize system
    system = MultiAgentSystem(db_config, api_key)
    
    print("\n✅ System ready! Available agents:")
    print("  - SQL Agent: Database queries and data retrieval")
    print("  - Visualization Agent: Chart creation and visual analytics")
    print("  - Data Analyst Agent: Statistical analysis and insights")
    print("  - Orchestrator Agent: Coordinates all agents")
    
    # Example queries
    examples = [
        "Show me the top 10 expense Categroies",
        "Analyze Credit trends over the last 6 months with visualizations",
        "What are the key metrics from the expenses table."
    ]
    
    print("\n📋 Example queries:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")
    
    # Interactive mode
    print("\n" + "="*60)
    print("🎯 Interactive Mode - Type your queries or 'exit' to quit")
    print("="*60)
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if user_input:
            try:
                system.query(user_input)
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print("Please enter a query.")


if __name__ == "__main__":
    main()