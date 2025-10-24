# ============================================================================
# File: utils/database.py
# ============================================================================
import os


def get_database_config() -> dict:
    """Get database configuration from environment variables."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': int(os.getenv('DB_PORT', 5432))
    }
    
    # Validate required fields
    if not all([db_config['database'], db_config['user'], db_config['password']]):
        raise ValueError("DB_NAME, DB_USER, and DB_PASSWORD environment variables must be set")
    
    return db_config