# ============================================================================
# PROJECT STRUCTURE
# ============================================================================
"""
ai-analytics-platform/
├── main.py                     # Main CLI application
├── requirements.txt            # Dependencies
├── .env                        # Environment variables
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # BaseAgent class
│   ├── sql_agent.py           # SQL query agent
│   ├── visualization_agent.py # Visualization agent
│   ├── analyst_agent.py       # Data analyst agent
│   └── orchestrator_agent.py  # Orchestrator
│
└── utils/
    ├── __init__.py
    └── database.py            # Database utilities
"""