# src/postgres_memory.py - Using pg8000 (pure Python, no DLLs)
import pg8000
import os
from datetime import datetime
import json
import hashlib

class PostgresMemory:
    def __init__(self):
        """Initialize PostgreSQL connection using pg8000"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5433'))
        self.database = os.getenv('DB_NAME', 'conversations')
        self.user = os.getenv('DB_USER', 'admin')
        self.password = os.getenv('DB_PASS', 'admin')
        
        try:
            self.conn = pg8000.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self._init_tables()
            self._init_pgvector()
            print("✅ PostgreSQL connected successfully (pg8000)")
            self.available = True
        except Exception as e:
            print(f"⚠️ PostgreSQL connection failed: {e}")
            self.available = False
    
    def _init_tables(self):
        """Create conversations table if it doesn't exist"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_query TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                sources TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        cursor.close()
        print("✅ Conversations table ready")
    
    def _init_pgvector(self):
        """Enable pgvector extension (if available)"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS vector')
            self.conn.commit()
            print("✅ pgvector extension enabled")
        except Exception as e:
            print(f"⚠️ pgvector not available: {e}")
        cursor.close()
    
    def save_conversation(self, session_id, user_query, ai_response, sources=None, embedding=None):
        """Save a conversation turn to database"""
        if not self.available:
            return None
        
        cursor = self.conn.cursor()
        try:
            sources_json = json.dumps(sources) if sources else None
            
            cursor.execute('''
                INSERT INTO conversations (session_id, user_query, ai_response, sources)
                VALUES (%s, %s, %s, %s)
            ''', (session_id, user_query, ai_response, sources_json))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Failed to save conversation: {e}")
            return False
        finally:
            cursor.close()
    
    def get_conversation_history(self, session_id, limit=10):
        """Get recent conversation history for a session"""
        if not self.available:
            return []
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT user_query, ai_response, sources, timestamp 
                FROM conversations 
                WHERE session_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            ''', (session_id, limit))
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                history.append({
                    "user_query": row[0],
                    "ai_response": row[1],
                    "sources": json.loads(row[2]) if row[2] else None,
                    "timestamp": row[3].isoformat() if row[3] else None
                })
            return history[::-1]  # Return chronological order
        except Exception as e:
            print(f"Failed to get history: {e}")
            return []
        finally:
            cursor.close()
    
    def clear_session_history(self, session_id):
        """Clear all conversations for a session"""
        if not self.available:
            return
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM conversations WHERE session_id = %s', (session_id,))
            self.conn.commit()
            print(f"Cleared history for session {session_id}")
        except Exception as e:
            print(f"Failed to clear history: {e}")
        finally:
            cursor.close()
    
    def search_similar_conversations(self, query_embedding, session_id=None, limit=5):
        """Search for semantically similar past conversations"""
        if not self.available:
            return []
        
        # pg8000 doesn't support vector type directly, return empty for now
        return []
