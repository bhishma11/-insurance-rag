# app/mcp/supabase_client.py
"""
Supabase Client for MCP Gateway - REST API Version (supports sb_ keys)
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any

class SupabaseClient:
    """MCP Client for Supabase Database using REST API"""

    def __init__(self):
        # Get from environment variables
        self.url = os.getenv("SUPABASE_URL", "https://YOUR_PROJECT.supabase.co")
        
        # ✅ Use new publishable key (or fallback to legacy)
        self.key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
        
        # Headers for REST API calls
        self.headers = {
            "apikey": self.key,
            "Content-Type": "application/json"
        }
        
        self.admin_headers = {
            "apikey": self.service_key,
            "Content-Type": "application/json"
        }
        
        key_type = "NEW (publishable)" if self.key and self.key.startswith("sb_") else "LEGACY (anon)"
        print(f"✅ Supabase client initialized with {key_type} key using REST API")

    def _request(self, method: str, path: str, data: dict = None, admin: bool = False) -> Any:
        """Make a REST API request to Supabase"""
        headers = self.admin_headers if admin else self.headers
        url = f"{self.url}/rest/v1/{path}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            
            if response.status_code >= 400:
                raise Exception(f"Supabase API error ({response.status_code}): {response.text}")
            
            return response.json() if response.text else {}
        except requests.exceptions.RequestException as e:
            print(f"❌ Supabase request failed: {e}")
            return {}

    # ============ USERS ============

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = self._request("GET", f"users?email=eq.{email}")
        return result[0] if result else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        result = self._request("GET", f"users?user_id=eq.{user_id}")
        return result[0] if result else None

    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        return self._request("POST", "users", data=user_data)

    def update_user_status(self, email: str, status: str, password: str = None) -> Dict:
        """Update user status"""
        data = {"status": status}
        if password:
            data["password"] = password
        result = self._request("PATCH", f"users?email=eq.{email}", data=data, admin=True)
        return result[0] if result else {}

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        result = self._request("GET", "users")
        return result if isinstance(result, list) else []

    # ============ USER REQUESTS ============

    def create_user_request(self, request_data: Dict) -> Dict:
        """Create a user access request"""
        return self._request("POST", "user_requests", data=request_data)

    def get_pending_request(self, email: str) -> Optional[Dict]:
        """Get pending request by email"""
        result = self._request("GET", f"user_requests?email=eq.{email}&status=eq.PENDING")
        return result[0] if result else None

    def get_request_by_ticket(self, ticket: str) -> Optional[Dict]:
        """Get request by ticket"""
        result = self._request("GET", f"user_requests?ticket=eq.{ticket}")
        return result[0] if result else None

    def update_request_status(self, ticket: str, status: str) -> Dict:
        """Update request status"""
        data = {"status": status}
        if status == "APPROVED":
            data["approved_at"] = "now()"
        result = self._request("PATCH", f"user_requests?ticket=eq.{ticket}", data=data, admin=True)
        return result[0] if result else {}

    # ============ APPROVALS ============

    def create_approval(self, ticket: str, approved_by: str) -> Dict:
        """Create approval record"""
        data = {"ticket": ticket, "approved_by": approved_by}
        return self._request("POST", "approvals", data=data, admin=True)

    # ============ CHAT HISTORY ============

    def save_chat(self, session_id: str, user_id: str, user_message: str, ai_response: str, sources: str = None) -> Dict:
        """Save chat history"""
        data = {
            "session_id": session_id,
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "sources": sources
        }
        return self._request("POST", "chat_history", data=data)

    def get_chat_history(self, session_id: str, limit: int = 100) -> List[Dict]:
        """Get chat history for a session"""
        result = self._request("GET", f"chat_history?session_id=eq.{session_id}&order=created_at.asc&limit={limit}")
        return result if isinstance(result, list) else []

    def get_all_sessions(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """Get all sessions"""
        query = "chat_history?select=session_id,created_at&order=created_at.desc&limit={limit}"
        if user_id:
            query = f"chat_history?select=session_id,created_at&user_id=eq.{user_id}&order=created_at.desc&limit={limit}"
        else:
            query = f"chat_history?select=session_id,created_at&order=created_at.desc&limit={limit}"
        result = self._request("GET", query)
        return result if isinstance(result, list) else []

    # ============ AUDIT LOGS ============

    def log_audit(self, user_id: str, action: str, details: Dict, ip_address: str = None, session_id: str = None) -> Dict:
        """Log an audit event"""
        data = {
            "user_id": user_id,
            "action": action,
            "details": json.dumps(details),
            "ip_address": ip_address,
            "session_id": session_id
        }
        return self._request("POST", "audit_logs", data=data, admin=True)

    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """Get audit logs"""
        result = self._request("GET", f"audit_logs?order=created_at.desc&limit={limit}", admin=True)
        return result if isinstance(result, list) else []

# Singleton instance
supabase_client = SupabaseClient()