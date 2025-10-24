# 🤖 AI-Powered Multi-Agent Analytics Platform

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple.svg)

**Enterprise-Grade Data Analytics Platform with Autonomous AI Agents**

[Features](#-key-features) • [Architecture](#-solution-architecture) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Demo](#-demo)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Solution Architecture](#-solution-architecture)
- [Key Features](#-key-features)
- [Agent Ecosystem](#-agent-ecosystem)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Advanced Features](#-advanced-features)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The **AI-Powered Multi-Agent Analytics Platform** is an enterprise-grade solution that revolutionizes data analytics through autonomous AI agents. Built on a sophisticated **Multi-Agent Collaboration Protocol (MCP)**, the platform intelligently orchestrates specialized agents to deliver comprehensive data insights, predictive analytics, and interactive visualizations.

### What Makes This Platform Unique?

- **🧠 Autonomous Intelligence**: Five specialized AI agents work collaboratively to understand, query, analyze, and predict data patterns
- **🔮 Predictive Analytics**: Advanced time-series forecasting with confidence intervals using polynomial regression models
- **🎯 Zero SQL Knowledge Required**: Natural language queries automatically translated to optimized SQL
- **📊 Real-Time Visualization**: Interactive dashboards with Plotly charts and customizable widgets
- **🔍 Complete Transparency**: Full execution logging shows every decision, tool call, and data transformation
- **🗄️ Intelligent Schema Discovery**: **Automatic database schema detection and context-aware query generation**
- **⚡ Production-Ready**: Modular architecture, error handling, and enterprise scalability

---

## 🏗️ Solution Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                                │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐   │
│  │  Streamlit UI   │  │   CLI Interface  │  │   REST API (Future)     │   │
│  │  - Chat         │  │   - Interactive  │  │   - Programmatic Access │   │
│  │  - Dashboard    │  │   - Batch Queries│  │   - Integration Ready   │   │
│  │  - Settings     │  │   - Scripting    │  │                         │   │
│  └────────┬────────┘  └────────┬─────────┘  └────────┬────────────────┘   │
└───────────┼─────────────────────┼─────────────────────┼──────────────────────┘
            │                     │                     │
            └─────────────────────┴─────────────────────┘
                                  │
            ┌─────────────────────▼─────────────────────┐
            │    MULTI-AGENT ORCHESTRATION LAYER        │
            │                                            │
            │  ┌──────────────────────────────────────┐ │
            │  │     🎯 ORCHESTRATOR AGENT            │ │
            │  │  - Intent Recognition                │ │
            │  │  - Agent Selection & Routing         │ │
            │  │  - Workflow Coordination             │ │
            │  │  - Response Synthesis                │ │
            │  └──────────────┬───────────────────────┘ │
            └─────────────────┼──────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
    ┌───────────▼───┐  ┌─────▼──────┐  ┌──▼──────────┐
    │  SPECIALIZED  │  │ SPECIALIZED │  │ SPECIALIZED │
    │    AGENTS     │  │   AGENTS    │  │   AGENTS    │
    └───────────────┘  └─────────────┘  └─────────────┘
                              │
    ┌────────────────────────┴────────────────────────┐
    │                                                  │
┌───▼────────────┐ ┌──────────────┐ ┌───────────────▼┐ ┌─────────────────┐
│  💾 SQL AGENT  │ │ 🔮 FORECAST  │ │ 📊 VISUALIZATION│ │ 📈 ANALYST      │
│                │ │    AGENT      │ │     AGENT       │ │    AGENT        │
│ • Schema Auto- │ │               │ │                 │ │                 │
│   Discovery    │ │ • Polynomial  │ │ • Chart         │ │ • Statistical   │
│ • Query        │ │   Regression  │ │   Generation    │ │   Analysis      │
│   Optimization │ │ • Confidence  │ │ • Plotly/       │ │ • Correlation   │
│ • PostgreSQL   │ │   Intervals   │ │   Matplotlib    │ │   Analysis      │
│   Connector    │ │ • Time Series │ │ • Dark Theme    │ │ • Descriptive   │
│ • RealDictCur- │ │   Analysis    │ │   Styling       │ │   Statistics    │
│   sor Support  │ │ • Trend       │ │ • Interactive   │ │ • Trend         │
│ • Error        │ │   Detection   │ │   Widgets       │ │   Identification│
│   Handling     │ │               │ │                 │ │                 │
└────────┬───────┘ └───────┬───────┘ └────────┬────────┘ └────────┬────────┘
         │                 │                  │                   │
         └─────────────────┴──────────────────┴───────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │      TOOL EXECUTION LAYER      │
                    │                                 │
                    │  ┌──────────────────────────┐  │
                    │  │  • execute_sql()         │  │
                    │  │  • forecast_data()       │  │
                    │  │  • create_chart()        │  │
                    │  │  • analyze_data()        │  │
                    │  └──────────────────────────┘  │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────▼────────────────┐
                    │       DATA ACCESS LAYER         │
                    │                                 │
                    │  ┌──────────────────────────┐  │
                    │  │   PostgreSQL Database    │  │
                    │  │   • Tables               │  │
                    │  │   • Views                │  │
                    │  │   • Schemas              │  │
                    │  │   • Relationships        │  │
                    │  └──────────────────────────┘  │
                    └─────────────────────────────────┘
```

### Multi-Agent Collaboration Protocol (MCP)

The platform implements a sophisticated **Multi-Agent Collaboration Protocol** that enables seamless communication and coordination between specialized agents:

#### 🎯 **Orchestration Flow**

1. **User Query Reception**: Natural language input received through UI or CLI
2. **Intent Analysis**: Orchestrator analyzes query semantics and keywords
3. **Agent Selection**: Intelligent routing based on query type:
   - Historical data queries → SQL Agent
   - Future predictions → Forecasting Agent
   - Visual requirements → Visualization Agent
   - Statistical analysis → Analyst Agent
4. **Execution Coordination**: Sequential or parallel agent execution with context sharing
5. **Result Synthesis**: Orchestrator combines outputs into coherent response
6. **Response Delivery**: Formatted output with visualizations and insights

#### 🔄 **Inter-Agent Communication**

```python
# Example: Complex Query Requiring Multiple Agents
User Query: "Predict expenses for Q1 2026 and create a visual comparison with 2025"

Orchestrator Decision Tree:
├─► SQL Agent: Fetch historical expenses data (2023-2025)
│   └─► Returns: DataFrame with monthly expenses
├─► Forecasting Agent: Generate Q1 2026 predictions
│   └─► Returns: Forecast with confidence intervals
├─► Visualization Agent: Create comparison chart
│   └─► Returns: Interactive Plotly chart with historical + forecast
└─► Analyst Agent: Provide statistical insights
    └─► Returns: Trend analysis and recommendations
```

---

## 🚀 Key Features

### 🧠 **Intelligent Natural Language Processing**

- **Context-Aware Query Understanding**: Advanced NLP to interpret user intent
- **Multi-Turn Conversations**: Maintains context across conversation history
- **Ambiguity Resolution**: Clarifying questions when queries are unclear
- **Domain-Specific Vocabulary**: Financial, sales, and business terminology recognition

### 🗄️ **Automatic Schema Intelligence**

The platform's **crown jewel** is its ability to automatically understand your database structure:

- **✨ Zero-Configuration Schema Discovery**: Automatically queries `information_schema` to discover:
  - All tables in the public schema
  - Column names, data types, and nullability constraints
  - Table relationships and foreign keys
  - Index information for optimization hints

- **🎯 Context-Aware Query Generation**: 
  - Agents receive complete schema context before query generation
  - Intelligent column selection based on data types
  - Automatic JOIN detection for related tables
  - Query optimization based on table size and indexes

- **📚 Schema-Driven Intelligence**:
  ```sql
  -- Automatic Schema Query (Behind the Scenes)
  SELECT 
      table_name,
      column_name,
      data_type,
      is_nullable
  FROM information_schema.columns
  WHERE table_schema = 'public'
  ORDER BY table_name, ordinal_position;
  ```

- **🔍 Smart Table Discovery**: Dashboard builder automatically populates available tables
- **⚡ Real-Time Column Detection**: Dynamic column lists based on selected table
- **🛡️ Type-Safe Operations**: Validates operations based on column data types

### 🔮 **Advanced Predictive Analytics**

- **Time Series Forecasting**: Polynomial regression (degree 2) for non-linear trends
- **Confidence Intervals**: 95% prediction bounds using residual analysis
- **Seasonal Detection**: Identifies and accounts for seasonal patterns
- **Model Quality Metrics**: R² scores, standard error, and validation statistics
- **Flexible Forecasting Periods**: Monthly or yearly predictions
- **Category-Specific Predictions**: Forecast by product, region, or custom dimensions

### 📊 **Dynamic Dashboard System**

- **Direct Database Integration**: Query any table without pre-processing
- **5 Chart Types**: Bar, Line, Scatter, Pie, Area with Plotly interactivity
- **Real-Time Data Refresh**: On-demand widget data updates
- **Custom SQL Support**: Advanced users can write custom queries
- **Export Capabilities**: Download charts as PNG or dashboard configs as JSON
- **Responsive Grid Layout**: Automatic adaptation to screen size

### 🔍 **Complete Execution Transparency**

The platform provides unprecedented visibility into AI decision-making:

- **Real-Time Execution Logs**: Watch agents work in real-time
- **Tool Call Inspection**: See exact SQL queries, function calls, and parameters
- **Decision Tracking**: Understand why each agent was selected
- **Performance Metrics**: Execution time for each operation
- **Error Diagnostics**: Detailed error messages with resolution suggestions

**Execution Log Example:**
```
🎯 Orchestrator Started
  ⏰ 2025-10-24T14:32:01

🎯 Delegated to SQL Agent
  Task: Retrieve monthly sales for 2025
  ⏰ 2025-10-24T14:32:02

🚀 SQL Agent Started
  ⏰ 2025-10-24T14:32:02

🔧 Tool Called: execute_sql
  📝 Query: SELECT DATE_TRUNC('month', date) AS month, 
              SUM(amount) AS total_sales
           FROM sales 
           WHERE EXTRACT(YEAR FROM date) = 2025
           GROUP BY month ORDER BY month;
  💡 Explanation: Aggregates sales by month for 2025
  ⏰ 2025-10-24T14:32:03

✅ Tool Result: Success ✓
  Rows: 10
  ⏰ 2025-10-24T14:32:04

🏁 SQL Agent Completed
  Response Length: 487 characters
  ⏰ 2025-10-24T14:32:05
```

### 🎨 **Modern User Interface**

- **Beautiful Dark Theme**: Eye-friendly design with purple/blue gradients
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Polished transitions and hover effects
- **Accessibility**: WCAG 2.1 compliant with keyboard navigation
- **Progressive Disclosure**: Complex features revealed as needed

---

## 🤖 Agent Ecosystem

### 1️⃣ **SQL Agent** - Database Query Specialist

**Responsibilities:**
- **Automatic Schema Discovery**: Queries database metadata on initialization
- **Intelligent Query Generation**: Creates optimized SQL based on schema context
- **Query Execution**: Uses psycopg2 with RealDictCursor for JSON-compatible results
- **Error Handling**: Graceful failure recovery with user-friendly messages
- **Result Formatting**: Converts PostgreSQL types (Decimal, Date) to JSON-compatible formats

**Key Features:**
- ✅ **Zero SQL knowledge required** - translates natural language to SQL
- ✅ **Schema-aware** - understands your table structure automatically
- ✅ **Type-safe** - handles Decimal, Date, DateTime, and custom types
- ✅ **Optimized** - generates efficient queries with proper indexing hints

**Example Tool Call:**
```json
{
  "tool": "execute_sql",
  "parameters": {
    "query": "SELECT category, SUM(amount) FROM expenses GROUP BY category",
    "explanation": "Aggregates total expenses by category"
  }
}
```

### 2️⃣ **Forecasting Agent** - Predictive Analytics Specialist

**Responsibilities:**
- **Historical Data Analysis**: Retrieves and analyzes time-series data
- **Trend Detection**: Identifies linear and non-linear patterns
- **Prediction Generation**: Creates forecasts using polynomial regression
- **Confidence Calculation**: Computes 95% confidence intervals
- **Model Validation**: Reports R² scores and error metrics

**Forecasting Methodology:**
```python
# Polynomial Regression (Degree 2)
X = historical_periods
y = historical_values

poly = PolynomialFeatures(degree=2)
model = LinearRegression()
model.fit(poly.transform(X), y)

predictions = model.predict(poly.transform(future_periods))
confidence_interval = 1.96 * std_error  # 95% CI
```

**Capabilities:**
- 📈 Monthly or yearly forecasts
- 🎯 Category-specific predictions
- 📊 Historical context visualization
- 🔢 Statistical quality metrics
- ⚠️ Uncertainty quantification

### 3️⃣ **Visualization Agent** - Data Visualization Specialist

**Responsibilities:**
- **Chart Type Selection**: Recommends optimal visualization for data type
- **Interactive Chart Creation**: Generates Plotly or Matplotlib visualizations
- **Styling & Theming**: Applies consistent dark theme styling
- **Export Management**: Saves charts as high-resolution images

**Supported Visualizations:**
- 📊 **Bar Charts**: Categorical comparisons
- 📈 **Line Charts**: Time series and trends
- 🎯 **Scatter Plots**: Correlation analysis
- 🥧 **Pie Charts**: Proportional data
- 📉 **Area Charts**: Cumulative trends
- 📦 **Box Plots**: Distribution analysis
- 🔥 **Heatmaps**: Multi-dimensional data

### 4️⃣ **Analyst Agent** - Statistical Analysis Specialist

**Responsibilities:**
- **Descriptive Statistics**: Mean, median, mode, std dev, quartiles
- **Correlation Analysis**: Pearson correlation matrices
- **Trend Identification**: Moving averages and pattern detection
- **Anomaly Detection**: Identifies outliers and unusual patterns
- **Business Insights**: Translates statistics into actionable recommendations

**Analysis Types:**
```python
- Descriptive: df.describe() with enhanced metrics
- Summary: Row counts, data types, missing values
- Correlation: Pearson coefficients for numeric columns
- Trend: Moving averages and growth rates
```

### 5️⃣ **Orchestrator Agent** - Master Coordinator

**Responsibilities:**
- **Intent Recognition**: NLP-based query classification
- **Agent Selection**: Intelligent routing based on keywords and context
- **Workflow Management**: Sequential or parallel agent execution
- **Context Sharing**: Passes results between agents
- **Response Synthesis**: Combines multi-agent outputs coherently

**Keyword-Based Routing:**
```python
# Forecasting Keywords
Keywords: ["predict", "forecast", "future", "next year", "2026", 
           "expected", "projection", "will be"]
→ Routes to: Forecasting Agent

# Historical Keywords  
Keywords: ["show", "get", "list", "current", "last month", "2024"]
→ Routes to: SQL Agent

# Visual Keywords
Keywords: ["chart", "graph", "plot", "visualize", "dashboard"]
→ Routes to: Visualization Agent
```

---

## 🛠️ Technology Stack

### **Core Technologies**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Core development language |
| **AI Model** | OpenAI GPT-4o | Latest | Natural language processing & reasoning |
| **Database** | PostgreSQL | 12+ | Data storage and querying |
| **Web Framework** | Streamlit | 1.31+ | Interactive web interface |
| **CLI Framework** | Python argparse | Built-in | Command-line interface |

### **Key Dependencies**

```python
# AI & Machine Learning
openai>=1.12.0              # OpenAI API client
scikit-learn>=1.3.0         # ML algorithms for forecasting
numpy>=1.24.0               # Numerical computations

# Database
psycopg2-binary>=2.9.9      # PostgreSQL adapter
pandas>=2.1.4               # Data manipulation

# Visualization
plotly>=5.18.0              # Interactive charts (Streamlit)
matplotlib>=3.8.0           # Static charts (CLI)
seaborn>=0.13.0             # Statistical visualizations

# Configuration
python-dotenv>=1.0.0        # Environment variable management
```

### **Architecture Patterns**

- **Multi-Agent System (MAS)**: Distributed AI architecture
- **Tool-Use Pattern**: OpenAI function calling for agent actions
- **Observer Pattern**: Real-time execution logging
- **Factory Pattern**: Agent instantiation and configuration
- **Strategy Pattern**: Dynamic algorithm selection for forecasting

---

## 📦 Installation

### **Prerequisites**

- Python 3.9 or higher
- PostgreSQL 12 or higher
- OpenAI API key
- 4GB RAM minimum (8GB recommended)
- Modern web browser (for Streamlit UI)

### **Step 1: Clone Repository**

```bash
git clone https://github.com/kamra34/advanced_multiagent_analytics_postgress.git
cd advanced_multiagent_analytics_postgress
```

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 4: Configure Environment**

Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# PostgreSQL Configuration
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

### **Step 5: Verify Installation**

```bash
# Test CLI
python main.py

# Test Streamlit UI
streamlit run app.py
```

---

## ⚙️ Configuration

### **Database Setup**

The platform **automatically discovers** your database schema. Simply ensure your PostgreSQL database is accessible:

```sql
-- Example: Create sample database
CREATE DATABASE analytics_db;

-- Connect to database
\c analytics_db

-- Platform will automatically discover all tables and columns
-- No manual configuration required!
```

### **Agent Configuration**

Customize agent behavior in `agents/` directory:

```python
# Example: Customize SQL Agent query timeout
class SQLAgent(BaseAgent):
    def __init__(self, client, db_config):
        super().__init__(
            name="SQL Agent",
            role="Expert SQL developer...",
            client=client
        )
        self.query_timeout = 30  # seconds
```

### **UI Customization**

Modify styling in `streamlit_app/config.py`:

```python
# Change primary color
--primary-color: #your-hex-color;

# Modify theme
template="plotly_dark"  # or "plotly_white", "ggplot2"
```

---

## 🎮 Usage

### **Streamlit Web Interface** (Recommended)

```bash
streamlit run app.py
```

**Features:**
- 💬 **Chat Interface**: Natural language queries with real-time responses
- 📊 **Dashboard Builder**: Direct database table selection and visualization
- 🔍 **Execution Logs**: Toggle to see agent decision-making process
- ⚙️ **Settings**: Configuration management and system status

**Example Queries:**

```
Historical Analysis:
"Show me total expenses by category for 2024"
"What are the top 10 customers by revenue?"
"Analyze spending trends over the last 6 months"

Predictive Analytics:
"What is your prediction for total revenue in 2026?"
"Predict credit card expenses for next year"
"Forecast mortgage costs for the next 12 months"

Visualization:
"Create a bar chart of monthly expenses"
"Show me a trend line for sales growth"
"Visualize product performance by region"
```

### **Command Line Interface**

```bash
python main.py
```

**Interactive Mode:**
```
🚀 Initializing Multi-Agent PostgreSQL Analyst System...
   Now with Forecasting Capabilities! 🔮

✅ System ready! Available agents:
  - SQL Agent: Database queries and historical data retrieval
  - Visualization Agent: Chart creation and visual analytics
  - Data Analyst Agent: Statistical analysis and insights
  - Forecasting Agent: Time series predictions and future forecasts 🔮
  - Orchestrator Agent: Coordinates all agents intelligently

👤 You: Show me all tables
```

### **Programmatic Usage** (Future API)

```python
from agents import MultiAgentSystem
from utils import get_database_config

# Initialize system
db_config = get_database_config()
system = MultiAgentSystem(db_config, api_key="your-key")

# Query
response, logs = system.query("Predict sales for Q1 2026")
print(response)
```

---

## 📚 API Reference

### **MultiAgentSystem**

Main entry point for the platform.

```python
class MultiAgentSystem:
    def __init__(self, db_config: Dict, api_key: str):
        """
        Initialize the multi-agent system.
        
        Args:
            db_config: Database configuration dictionary
            api_key: OpenAI API key
        """
        
    def query(self, user_message: str) -> Tuple[str, List[Dict]]:
        """
        Process user query through agent ecosystem.
        
        Args:
            user_message: Natural language query
            
        Returns:
            Tuple of (response_text, execution_logs)
        """
```

### **Agent Base Class**

All agents inherit from `BaseAgent`:

```python
class BaseAgent:
    def chat(self, message: str, context: str = "", 
             execution_logs: List = None) -> Tuple[str, List]:
        """
        Send message to agent and get response with logs.
        
        Args:
            message: Query for the agent
            context: Optional context (e.g., database schema)
            execution_logs: Shared execution log list
            
        Returns:
            Tuple of (response, updated_logs)
        """
```

---

## 🔬 Advanced Features

### **Custom Agent Development**

Create new specialized agents:

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, client, config):
        super().__init__(
            name="Custom Agent",
            role="Your specialized agent role description",
            client=client
        )
    
    def get_tools(self):
        return [{
            "type": "function",
            "function": {
                "name": "custom_tool",
                "description": "Tool description",
                "parameters": { /* JSON schema */ }
            }
        }]
    
    def process_tool_call(self, tool_name, tool_input):
        # Implement tool logic
        return {"success": True, "data": result}
```

### **Forecast Model Customization**

Adjust forecasting algorithms:

```python
# In agents/forecast_agent.py

# Change polynomial degree (1=linear, 2=quadratic, 3=cubic)
poly = PolynomialFeatures(degree=3)

# Adjust confidence level (0.95 = 95%)
confidence_interval = 2.576 * std_error  # 99% CI

# Add seasonal decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
```

### **Database Connection Pooling**

For production deployments:

```python
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **db_config
)
```

---

## 📊 Performance Benchmarks

| Operation | Average Time | Notes |
|-----------|-------------|-------|
| Schema Discovery | 50-100ms | Cached after first load |
| Simple SQL Query | 100-300ms | Depends on table size |
| Complex Aggregation | 500ms-2s | With JOINs and GROUP BY |
| Forecast Generation | 1-3s | Includes data fetch + model training |
| Chart Rendering | 200-500ms | Plotly interactive charts |
| Agent Delegation | 50-100ms | Orchestrator decision time |

**Optimization Tips:**
- Enable PostgreSQL query result caching
- Use database indexes on frequently queried columns
- Limit forecast training data to relevant time periods
- Cache dashboard widgets for frequently accessed views

---

## 🔐 Security Considerations

### **Environment Variables**
- ✅ Never commit `.env` files to version control
- ✅ Use secret management services in production (AWS Secrets Manager, Azure Key Vault)
- ✅ Rotate API keys regularly

### **Database Security**
- ✅ Use read-only database users for analytics workloads
- ✅ Implement row-level security (RLS) for multi-tenant deployments
- ✅ Enable SSL/TLS for database connections
- ✅ Sanitize all SQL inputs (psycopg2 handles this automatically with parameterized queries)

### **API Security**
- ✅ Implement rate limiting for API endpoints
- ✅ Use JWT tokens for authentication
- ✅ Enable CORS policies for web deployments
- ✅ Monitor OpenAI API usage and set budget limits


## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### **Contribution Areas**

- 🐛 Bug fixes and issue resolution
- ✨ New agent implementations
- 📝 Documentation improvements
- 🧪 Test coverage expansion
- 🎨 UI/UX enhancements
- 🌍 Internationalization

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.


<div align="center">

[⬆ Back to Top](#-ai-powered-multi-agent-analytics-platform)

</div>