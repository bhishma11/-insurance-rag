# app/mcp/gateway.py
import json
import uuid
import requests
import random
import string
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from app.mcp.supabase_client import supabase_client
from app.mcp.handlers import MCPHandlers
from openai import OpenAI


class MCPGateway:
    """MCP Gateway - Single entry point for all business logic with Supabase"""

    def __init__(self):
        # ✅ Initialize handlers
        self.handlers = MCPHandlers()
        # ✅ Pass gateway reference to handlers so they can call Kaggle methods
        self.handlers.gateway = self
        
        self.tools = {
            # Auth Tools
            "signup_user": self.signup_user,
            "approve_user": self.approve_user,
            "login_user": self.login_user,
            "get_user_status": self.get_user_status,
            "get_all_users": self.get_all_users,
            
            # RAG Tools
            "query_insurance": self.query_insurance,
            
            # ✅ MCP Handlers (async)
            "calculate_insurance_premium": self.handlers.handle_calculate_premium,
            "check_claim_status": self.handlers.handle_check_claim,
            "compare_insurance_policies": self.handlers.handle_compare_policies,
            "get_policy_coverage": self.handlers.handle_get_coverage,
            "file_claim_instructions": self.handlers.handle_file_claim,
            "get_insurance_definition": self.handlers.handle_get_definition,
            "search_policies": self.handlers.handle_search_policies,
            "schedule_callback": self.handlers.handle_schedule_callback,
            "analyze_claim_outcome": self.handlers.handle_analyze_claim,
        }
        
        self.n8n_url = os.getenv("N8N_URL", "https://n8n-ceaooreqza-uc.a.run.app")
        self.ollama_url = "http://localhost:11434"
        self.secret_key = "your-secret-key"

        # ✅ Initialize DeepSeek client
        api_key = os.getenv('DEEPSEEK_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE', 'https://api.deepseek.com')
        
        if api_key:
            try:
                self.deepseek = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                print(f"✅ DeepSeek client initialized successfully")
            except Exception as e:
                self.deepseek = None
                print(f"⚠️ Failed to initialize DeepSeek: {e}")
        else:
            self.deepseek = None
            print("⚠️ DEEPSEEK_API_KEY not found in environment variables!")

    # ============ KAGGLE API INTEGRATION ============
    
    def _get_kaggle_url(self) -> Optional[str]:
        """Get Kaggle API URL from environment"""
        return os.getenv('KAGGLE_API_URL')
    
    def _call_kaggle_qlora(self, query: str) -> Optional[str]:
        """Call Kaggle API for QLoRA inference"""
        kaggle_url = self._get_kaggle_url()
        if not kaggle_url:
            return None
        
        try:
            response = requests.post(
                f"{kaggle_url}/api/qlora/query",
                json={"query": query},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("response")
            return None
        except Exception as e:
            print(f"⚠️ Kaggle QLoRA API call failed: {e}")
            return None
    
    def _call_kaggle_rag(self, query: str, top_k: int = 3) -> Optional[dict]:
        """Call Kaggle API for RAG search"""
        kaggle_url = self._get_kaggle_url()
        if not kaggle_url:
            return None
        
        try:
            response = requests.post(
                f"{kaggle_url}/api/rag/query",
                json={"query": query, "top_k": top_k},
                timeout=60
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"⚠️ Kaggle RAG API call failed: {e}")
            return None
    
    def _call_kaggle_vision(self, image_data: bytes, analyze: bool = True) -> dict:
        """Call Kaggle API for vision analysis"""
        kaggle_url = self._get_kaggle_url()
        if not kaggle_url:
            return {"success": False, "error": "KAGGLE_API_URL not set"}
        
        try:
            endpoint = "/api/vision/analyze" if analyze else "/api/vision/classify"
            files = {'file': ('image.jpg', image_data, 'image/jpeg')}
            response = requests.post(
                f"{kaggle_url}{endpoint}",
                files=files,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _call_kaggle_vision_status(self) -> dict:
        """Call Kaggle API for vision status"""
        kaggle_url = self._get_kaggle_url()
        if not kaggle_url:
            return {"loaded": False, "error": "KAGGLE_API_URL not set"}
        
        try:
            response = requests.get(
                f"{kaggle_url}/api/vision/status",
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return {"loaded": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"loaded": False, "error": str(e)}

    # ============ AUTH TOOLS (Using Supabase) ============

    def signup_user(self, params):
        """Sign up a new user - status PENDING"""
        email = params.get("email")
        name = params.get("name")
        company = params.get("company", "N/A")

        if not email or not name:
            return {"success": False, "error": "Email and name required"}

        existing_user = supabase_client.get_user_by_email(email)
        if existing_user:
            return {"success": False, "error": "User already exists"}

        user_id = 'USER-' + str(uuid.uuid4())[:8]
        ticket = 'TICKET-' + str(int(datetime.now().timestamp())) + '-' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        request_date = datetime.now().isoformat()

        user_data = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "company": company,
            "status": "PENDING"
        }
        supabase_client.create_user(user_data)

        request_data = {
            "ticket": ticket,
            "email": email,
            "name": name,
            "company": company,
            "status": "PENDING",
            "request_date": request_date
        }
        supabase_client.create_user_request(request_data)

        supabase_client.log_audit(
            user_id=user_id,
            action="signup",
            details={"email": email, "name": name, "company": company},
            ip_address=params.get("ip", "unknown")
        )

        self._send_approval_email(email, name, user_id, company, request_date, ticket)

        return {
            "success": True,
            "user_id": user_id,
            "status": "PENDING",
            "ticket": ticket,
            "message": "Signup successful! Waiting for admin approval."
        }

    def approve_user(self, params):
        """Approve a user - status ACTIVE, generate password"""
        email = params.get("email")
        admin_key = params.get("admin_key")

        if admin_key != "tool12sober34":
            return {"success": False, "error": "Unauthorized"}

        request = supabase_client.get_pending_request(email)
        if not request:
            return {"success": False, "error": "User not found or already approved"}

        user = supabase_client.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "User not found"}

        password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

        supabase_client.update_user_status(email, "ACTIVE", password)
        supabase_client.update_request_status(request["ticket"], "APPROVED")
        supabase_client.create_approval(request["ticket"], "admin")

        supabase_client.log_audit(
            user_id=user["user_id"],
            action="approve",
            details={"email": email, "approved_by": "admin"},
            ip_address=params.get("ip", "unknown")
        )

        self._send_welcome_email(email, user["name"], password)

        return {
            "success": True,
            "message": f"User {email} approved",
            "password": password
        }

    def login_user(self, params):
        """Login user - verify credentials, return JWT"""
        email = params.get("email")
        password = params.get("password")

        if not email or not password:
            return {"success": False, "error": "Email and password required"}

        user = supabase_client.get_user_by_email(email)

        if not user:
            return {"success": False, "error": "Invalid credentials"}

        if user["status"] != 'ACTIVE':
            return {"success": False, "error": "Account not activated. Please contact admin."}

        if user["password"] != password:
            return {"success": False, "error": "Invalid credentials"}

        token = jwt.encode({
            'user_id': user["user_id"],
            'email': user["email"],
            'name': user["name"],
            'company': user["company"],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, self.secret_key, algorithm='HS256')

        supabase_client.log_audit(
            user_id=user["user_id"],
            action="login",
            details={"email": email},
            ip_address=params.get("ip", "unknown")
        )

        return {
            "success": True,
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "company": user["company"],
                "status": user["status"]
            }
        }

    def get_user_status(self, params):
        """Get user status"""
        email = params.get("email")
        user = supabase_client.get_user_by_email(email)
        if not user:
            return {"success": False, "error": "User not found"}
        return {"success": True, "status": user["status"]}

    def get_all_users(self, params=None):
        """Get all users"""
        users = supabase_client.get_all_users()
        return {"success": True, "users": users}

    def query_insurance(self, params):
        """Query insurance RAG system"""
        query = params.get("query")
        if not query:
            return {"success": False, "error": "Query required"}

        # ✅ Try Kaggle RAG first
        kaggle_result = self._call_kaggle_rag(query)
        if kaggle_result and kaggle_result.get("success"):
            return {
                "success": True,
                "response": kaggle_result.get("response", ""),
                "sources": kaggle_result.get("sources", [])
            }

        # Fallback to local Ollama
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"You are an insurance assistant. Answer: {query}",
                    "stream": False,
                    "options": {"temperature": 0.7, "max_tokens": 500}
                },
                timeout=5
            )
            if response.ok:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", "No response generated"),
                }
        except:
            pass

        # Fallback response
        return {
            "success": True,
            "response": f"Processed query: '{query}'. (Standard RAG response via Cloud Gateway)",
        }

    def _send_approval_email(self, email, name, user_id, company, request_date, ticket):
        """Send approval email to admin via n8n"""
        try:
            print(f"📧 Sending approval email for: {email}")
            print(f"   Data: name={name}, user_id={user_id}, company={company}, ticket={ticket}")
            
            response = requests.post(
                f"{self.n8n_url}/webhook/send-approval-email",
                json={
                    "user": {
                        "email": email,
                        "name": name,
                        "user_id": user_id,
                        "company": company,
                        "request_date": request_date,
                        "ticket": ticket
                    }
                },
                timeout=10
            )
            
            print(f"✅ n8n approval response: {response.status_code}")
            print(f"   Response text: {response.text}")
            
            if response.status_code != 200:
                print(f"❌ n8n returned error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"❌ n8n approval webhook TIMEOUT for {email}")
        except requests.exceptions.ConnectionError:
            print(f"❌ n8n approval webhook CONNECTION ERROR for {email}")
        except Exception as e:
            print(f"❌ n8n approval webhook failed: {e}")

    def _send_welcome_email(self, email, name, password):
        """Send welcome email to user via n8n"""
        try:
            print(f"📧 Sending welcome email for: {email}")
            print(f"   Data: name={name}, password={password}")
            
            response = requests.post(
                f"{self.n8n_url}/webhook/send-welcome-email",
                json={
                    "user": {
                        "email": email,
                        "name": name,
                        "password": password
                    }
                },
                timeout=10
            )
            
            print(f"✅ n8n welcome response: {response.status_code}")
            print(f"   Response text: {response.text}")
            
            if response.status_code != 200:
                print(f"❌ n8n returned error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"❌ n8n welcome webhook TIMEOUT for {email}")
        except requests.exceptions.ConnectionError:
            print(f"❌ n8n welcome webhook CONNECTION ERROR for {email}")
        except Exception as e:
            print(f"❌ n8n welcome webhook failed: {e}")

    async def execute_tool(self, tool_name, params):
        """Execute a tool by name - handles both sync and async tools"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}

        try:
            result = self.tools[tool_name](params)
            # ✅ If result is async, await it
            if hasattr(result, '__await__'):
                result = await result
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}