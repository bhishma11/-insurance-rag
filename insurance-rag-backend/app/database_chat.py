# app/database_chat.py
import sqlite3
import json
from datetime import datetime
import os
import time as time_module

class ChatDatabase:
    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # ✅ Set timezone to local time
        # SQLite doesn't have timezone support, so we use CURRENT_TIMESTAMP
        # and convert on read
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON chat_history(session_id)")
        self.conn.commit()
        print(f"✅ Chat history database: {self.db_path}")
    
    async def save_chat(self, session_id: str, user_message: str, ai_response: str):
        """Save a chat exchange with local time"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (session_id, user_message, ai_response, timestamp)
            VALUES (?, ?, ?, datetime('now', 'localtime'))
        """, (session_id, user_message, ai_response))
        self.conn.commit()
        cursor.close()
    
    async def get_chat_history(self, session_id: str, limit: int = 100):
        """Get chat history for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_message, ai_response, timestamp
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        """, (session_id, limit))
        results = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in results]
    
    async def get_all_sessions(self, limit: int = 50):
        """Get all sessions with last message"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                session_id,
                MAX(timestamp) as last_activity,
                (SELECT user_message FROM chat_history c2 
                 WHERE c2.session_id = c1.session_id 
                 ORDER BY timestamp DESC LIMIT 1) as last_message
            FROM chat_history c1
            GROUP BY session_id
            ORDER BY last_activity DESC
            LIMIT ?
        """, (limit,))
        results = cursor.fetchall()
        cursor.close()
        
        sessions = []
        for row in results:
            sessions.append({
                "session_id": row["session_id"],
                "title": row["last_message"][:50] if row["last_message"] else "New Chat",
                "timestamp": row["last_activity"]
            })
        return sessions
    
    async def delete_session(self, session_id: str):
        """Delete a session"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        self.conn.commit()
        cursor.close()
    
    def close(self):
        if self.conn:
            self.conn.close()

# Create one instance
chat_db = ChatDatabase()