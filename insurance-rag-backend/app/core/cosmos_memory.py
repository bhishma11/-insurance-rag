# src/cosmos_memory.py
from azure.cosmos import CosmosClient
import os
from datetime import datetime
import uuid

class CosmosMemory:
    def __init__(self):
        """Initialize Cosmos DB connection"""
        endpoint = os.getenv('COSMOS_ENDPOINT')
        key = os.getenv('COSMOS_KEY')
        
        if not endpoint or not key:
            print("⚠️ Cosmos DB not configured - using local memory only")
            self.available = False
            return
        
        try:
            self.client = CosmosClient(endpoint, key)
            database_name = os.getenv('COSMOS_DATABASE', 'insurance-db')
            self.database = self.client.get_database_client(database_name)
            container_name = os.getenv('COSMOS_CONTAINER', 'conversations')
            self.container = self.database.get_container_client(container_name)
            self.available = True
            print("✅ Cosmos DB connected")
        except Exception as e:
            print(f"⚠️ Cosmos DB connection failed: {e}")
            self.available = False
    
    def save_conversation(self, session_id, user_query, ai_response, sources=None, metadata=None):
        """Save a conversation turn to Cosmos DB"""
        if not self.available:
            return None
        
        try:
            doc = {
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'user_query': user_query,
                'ai_response': ai_response,
                'sources': sources or [],
                'metadata': metadata or {},
                'timestamp': datetime.now().isoformat(),
                'type': 'message'
            }
            self.container.upsert_item(doc)
            return doc['id']
        except Exception as e:
            print(f"Failed to save conversation: {e}")
            return None
    
    def get_conversation_history(self, session_id, limit=10):
        """Get recent conversation history"""
        if not self.available:
            return []
        
        try:
            query = f"""
            SELECT * FROM c 
            WHERE c.session_id = '{session_id}' 
            AND c.type = 'message'
            ORDER BY c.timestamp DESC 
            OFFSET 0 LIMIT {limit}
            """
            items = list(self.container.query_items(query, enable_cross_partition_query=True))
            return items[::-1]  # Return in chronological order
        except Exception as e:
            print(f"Failed to get history: {e}")
            return []
    
    def clear_history(self, session_id):
        """Clear conversation history for a session"""
        if not self.available:
            return
        
        try:
            query = f"SELECT * FROM c WHERE c.session_id = '{session_id}'"
            items = list(self.container.query_items(query, enable_cross_partition_query=True))
            for item in items:
                self.container.delete_item(item, partition_key=item['session_id'])
            print(f"Cleared {len(items)} messages for session {session_id}")
        except Exception as e:
            print(f"Failed to clear history: {e}")
