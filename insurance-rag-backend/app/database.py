# app/database.py
import pg8000  # ← Change from asyncpg to pg8000
from typing import Optional, List, Dict, Any
from app.config import settings
import json

class Database:
    def __init__(self):
        self.conn: Optional[pg8000.Connection] = None
        self.available = False
    
    async def connect(self):
        """Create connection to PostgreSQL using pg8000"""
        try:
            self.conn = pg8000.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASS
            )
            self.available = True
            await self._init_tables()
            print("✅ Database connected")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            self.available = False
            self.conn = None
    
    async def _init_tables(self):
        """Create tables if they don't exist"""
        if not self.available:
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    user_id TEXT DEFAULT 'anonymous',
                    user_query TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    sources TEXT,
                    title TEXT DEFAULT 'New Conversation',
                    model_used TEXT DEFAULT 'unknown',
                    tokens_used INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
                ON conversations(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp DESC)
            """)
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    name TEXT,
                    role TEXT DEFAULT 'user',
                    status TEXT DEFAULT 'active',
                    total_requests INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost DECIMAL(10, 4) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            print("✅ Tables ready")
        except Exception as e:
            print(f"⚠️ Table creation failed: {e}")
        finally:
            cursor.close()
    
    async def save_conversation(self, session_id: str, user_id: str, user_query: str, 
                                ai_response: str, sources: str = None, 
                                model_used: str = "unknown", tokens_used: int = 0):
        """Save a conversation to database"""
        if not self.available:
            return None
        cursor = self.conn.cursor()
        try:
            # Check if first message in session
            cursor.execute(
                "SELECT COUNT(*) = 0 FROM conversations WHERE session_id = %s",
                (session_id,)
            )
            is_first = cursor.fetchone()[0]
            
            title = user_query[:50] + ("..." if len(user_query) > 50 else "") if is_first else None
            
            cursor.execute("""
                INSERT INTO conversations (session_id, user_id, user_query, ai_response, sources, title, model_used, tokens_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session_id, user_id, user_query, ai_response, sources, title, model_used, tokens_used))
            
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ Failed to save conversation: {e}")
        finally:
            cursor.close()
    
    async def get_chat_history(self, session_id: str, limit: int = 50):
        """Get chat history for a session"""
        if not self.available:
            return []
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT user_query, ai_response, sources, timestamp
                FROM conversations
                WHERE session_id = %s
                ORDER BY timestamp ASC
                LIMIT %s
            """, (session_id, limit))
            rows = cursor.fetchall()
            return [dict(zip(['user_query', 'ai_response', 'sources', 'timestamp'], row)) for row in rows]
        finally:
            cursor.close()
    
    async def get_all_sessions(self):
        """Get all unique sessions with their titles"""
        if not self.available:
            return []
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT DISTINCT ON (session_id) 
                    session_id, 
                    title,
                    timestamp,
                    user_query as first_query
                FROM conversations
                ORDER BY session_id, timestamp ASC
            """)
            rows = cursor.fetchall()
            return [dict(zip(['session_id', 'title', 'timestamp', 'first_query'], row)) for row in rows]
        finally:
            cursor.close()
    
    async def delete_session(self, session_id: str):
        """Delete a session and all its messages"""
        if not self.available:
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM conversations WHERE session_id = %s",
                (session_id,)
            )
            self.conn.commit()
        finally:
            cursor.close()
    
    async def update_user_stats(self, user_id: str, tokens_used: int):
        """Update user statistics"""
        if not self.available or user_id == "anonymous":
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (user_id, total_requests, total_tokens, last_active)
                VALUES (%s, 1, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    total_requests = users.total_requests + 1,
                    total_tokens = users.total_tokens + %s,
                    total_cost = users.total_cost + (%s * 0.000001),
                    last_active = CURRENT_TIMESTAMP
            """, (user_id, tokens_used, tokens_used, tokens_used))
            self.conn.commit()
        finally:
            cursor.close()
    
    async def get_user_stats(self) -> List[Dict]:
        """Get all users with their stats"""
        if not self.available:
            return []
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    user_id,
                    COALESCE(email, '') as email,
                    COALESCE(name, user_id) as name,
                    total_requests,
                    total_tokens,
                    total_cost,
                    last_active,
                    created_at
                FROM users
                ORDER BY total_requests DESC
                LIMIT 100
            """)
            rows = cursor.fetchall()
            columns = ['user_id', 'email', 'name', 'total_requests', 'total_tokens', 'total_cost', 'last_active', 'created_at']
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()

# Create global instance
db = Database()