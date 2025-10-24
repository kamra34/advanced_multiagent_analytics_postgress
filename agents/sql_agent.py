# ============================================================================
# File: agents/sql_agent.py
# ============================================================================
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List
from openai import OpenAI
from .base_agent import BaseAgent


class SQLAgent(BaseAgent):
    """Agent specialized in writing and executing SQL queries."""
    
    def __init__(self, client: OpenAI, db_config: Dict):
        super().__init__(
            name="SQL Agent",
            role="""You are an expert SQL developer specializing in PostgreSQL. 
Your responsibilities:
- ALWAYS use the execute_sql tool to run queries - never just explain them
- Write efficient, optimized SQL queries
- Handle complex joins, aggregations, and window functions
- Ensure query safety and performance
- After executing, explain what the results show

IMPORTANT: When asked to retrieve data, you MUST use the execute_sql tool to actually run the query and get results. Don't just describe the query.""",
            client=client
        )
        self.db_config = db_config
    
    def get_db_connection(self):
        """Create database connection."""
        return psycopg2.connect(**self.db_config)
    
    def get_database_schema(self) -> str:
        """Retrieve database schema."""
        query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """
        
        conn = self.get_db_connection()
        try:
            df = pd.read_sql(query, conn)
            schema_text = "Database Schema:\n\n"
            for table in df['table_name'].unique():
                schema_text += f"Table: {table}\n"
                table_cols = df[df['table_name'] == table]
                for _, row in table_cols.iterrows():
                    schema_text += f"  - {row['column_name']} ({row['data_type']}, {'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'})\n"
                schema_text += "\n"
            return schema_text
        finally:
            conn.close()
    
    def get_tools(self) -> List[Dict]:
        return [{
            "type": "function",
            "function": {
                "name": "execute_sql",
                "description": "Execute a SQL query on the PostgreSQL database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to execute"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Brief explanation of what the query does"
                        }
                    },
                    "required": ["query", "explanation"]
                }
            }
        }]
    
    def process_tool_call(self, tool_name: str, tool_input: Dict) -> Dict:
        if tool_name == "execute_sql":
            print(f"📝 Query: {tool_input['query']}")
            print(f"💡 Explanation: {tool_input['explanation']}")
            
            conn = self.get_db_connection()
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(tool_input['query'])
                
                if cursor.description:
                    results = cursor.fetchall()
                    results_list = [dict(row) for row in results]
                    return {
                        "success": True,
                        "data": results_list,
                        "row_count": len(results_list)
                    }
                else:
                    conn.commit()
                    return {
                        "success": True,
                        "message": "Query executed successfully",
                        "rows_affected": cursor.rowcount
                    }
            except Exception as e:
                return {"success": False, "error": str(e)}
            finally:
                conn.close()
        
        return {"error": "Unknown tool"}