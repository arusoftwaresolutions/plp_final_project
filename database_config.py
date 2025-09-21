"""
Database Configuration for Streamlit Cloud Deployment
Supports multiple database options without credit card requirements
"""

import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

# Database choice - set via environment variable
USE_DATABASE = os.getenv("USE_DATABASE", "json").lower()

# Database URL for PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "")

class DatabaseInterface:
    """Interface for different database backends"""

    def get_users(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        raise NotImplementedError

    def get_sdg_data(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def add_sdg_data(self, sdg_data: Dict[str, Any]) -> bool:
        raise NotImplementedError

class JSONDatabase(DatabaseInterface):
    """JSON file-based database for development/testing"""

    def __init__(self):
        self.data_file = "data.json"
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Ensure data file exists with proper structure"""
        if not os.path.exists(self.data_file):
            initial_data = {
                "users": [],
                "sdg_data": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            with open(self.data_file, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_data_file()
            return self._load_data()

    def _save_data(self, data: Dict[str, Any]):
        """Save data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        data = self._load_data()
        return data.get("users", [])

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Add a new user"""
        data = self._load_data()
        users = data.get("users", [])

        # Add timestamp if not provided
        if "created_at" not in user_data:
            user_data["created_at"] = datetime.now().isoformat()

        users.append(user_data)
        data["users"] = users
        self._save_data(data)
        return True

    def get_sdg_data(self) -> List[Dict[str, Any]]:
        """Get all SDG data"""
        data = self._load_data()
        return data.get("sdg_data", [])

    def add_sdg_data(self, sdg_data: Dict[str, Any]) -> bool:
        """Add SDG data"""
        data = self._load_data()
        sdg_list = data.get("sdg_data", [])

        # Add timestamp if not provided
        if "created_at" not in sdg_data:
            sdg_data["created_at"] = datetime.now().isoformat()

        sdg_list.append(sdg_data)
        data["sdg_data"] = sdg_list
        self._save_data(data)
        return True

class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database for production"""

    def __init__(self):
        self.db_url = DATABASE_URL
        self._ensure_tables()

    def _get_connection(self):
        """Get database connection"""
        try:
            import psycopg2
            return psycopg2.connect(self.db_url)
        except ImportError:
            raise Exception("psycopg2 not installed. Install with: pip install psycopg2-binary")
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")

    def _ensure_tables(self):
        """Create tables if they don't exist"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Create users table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(255) UNIQUE NOT NULL,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    # Create SDG data table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS sdg_data (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            description TEXT,
                            category VARCHAR(100),
                            data JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)

                    conn.commit()
        except Exception as e:
            print(f"Table creation warning: {str(e)}")

    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users from PostgreSQL"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
                    rows = cur.fetchall()

                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error getting users: {str(e)}")
            return []

    def add_user(self, user_data: Dict[str, Any]) -> bool:
        """Add user to PostgreSQL"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (username, email, password_hash, created_at)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        user_data.get("username"),
                        user_data.get("email"),
                        user_data.get("password_hash"),
                        user_data.get("created_at", datetime.now())
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error adding user: {str(e)}")
            return False

    def get_sdg_data(self) -> List[Dict[str, Any]]:
        """Get SDG data from PostgreSQL"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM sdg_data ORDER BY created_at DESC")
                    rows = cur.fetchall()

                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error getting SDG data: {str(e)}")
            return []

    def add_sdg_data(self, sdg_data: Dict[str, Any]) -> bool:
        """Add SDG data to PostgreSQL"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO sdg_data (title, description, category, data, created_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        sdg_data.get("title"),
                        sdg_data.get("description"),
                        sdg_data.get("category"),
                        json.dumps(sdg_data.get("data", {})),
                        sdg_data.get("created_at", datetime.now())
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error adding SDG data: {str(e)}")
            return False

def get_db_connection() -> DatabaseInterface:
    """Get database connection based on configuration"""
    if USE_DATABASE == "json" or not DATABASE_URL:
        return JSONDatabase()
    else:
        return PostgreSQLDatabase()

# Create global database instance
db = get_db_connection()
