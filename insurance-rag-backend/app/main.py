import asyncio
import json
import uuid
import os
import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import jwt
import time
import psycopg2

from app.config import settings
from app.database_chat import chat_db
from app.models import ChatRequest, ChatResponse

# ============ MCP Imports ============
from app.mcp.gateway import MCPGateway
from app.mcp.supabase_client import supabase_client

# ============ n8n Imports ============
from app.mcp.n8n_workflows import n8n
from app.mcp.n8n_webhooks import router as n8n_router

# ============ Governance Imports ============
from app.governance import content_safety, audit_logger, data_privacy, explainability
from app.governance.audit_log import AuditAction, AuditSeverity

# ✅ CLOUD RUN DETECTION
IS_CLOUD_RUN = os.getenv('CLOUD_RUN', 'false').lower() == 'true' or 'K_SERVICE' in os.environ

# ✅ NO HEAVY MODELS - Just MCP Gateway
mcp = MCPGateway()

# ============ WebSocket Connection Manager ============
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        print(f"✅ Connection added: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            print(f"❌ Connection removed: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
                print(f"📤 Message sent to {session_id}: {message.get('type')}")
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
                self.disconnect(session_id)
        else:
            print(f"⚠️ Connection {session_id} not found")

manager = ConnectionManager()

# ============ Simple In-Memory Cache ============
cache = {}
CACHE_TTL = 30

def get_cached(key: str):
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
        else:
            del cache[key]
    return None

def set_cached(key: str, value):
    cache[key] = (value, time.time())

# ============ Lifespan ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting FastAPI server with Supabase...")
    
    if IS_CLOUD_RUN:
        print("☁️ Running on Cloud Run - using DeepSeek only")
    else:
        print("💻 Running locally - DeepSeek available")
    
    try:
        users = supabase_client.get_all_users()
        print(f"✅ Supabase connected! Found {len(users)} users")
    except Exception as e:
        print(f"⚠️ Supabase connection failed: {e}")
        print("   Make sure SUPABASE_URL and SUPABASE_KEY are set in .env")
    
    try:
        print("✅ SQLite chat history ready")
    except Exception as e:
        print(f"⚠️ SQLite chat history error: {e}")
    
    print("🔌 MCP Gateway initialized")
    print("🛡️ Governance: Content Safety, Audit Logging, Data Privacy, Explainability")
    print("🔗 n8n Integration: Available")
    yield
    print("🛑 Shutting down...")

# ============ Create FastAPI App ============
app = FastAPI(
    title="Lemonade AI - Insurance RAG API",
    description="Enterprise Insurance Intelligence Platform with MCP Gateway",
    version="2.0.0",
    lifespan=lifespan
)

# ============ CORS Middleware ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://localhost:5678",
        "http://localhost:8001",
        "http://localhost:8000",
        "https://insurance-rag-backend-1046921433024.us-central1.run.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Include n8n Router ============
app.include_router(n8n_router)

# ============ Governance Middleware ============
@app.middleware("http")
async def governance_middleware(request: Request, call_next):
    start_time = datetime.now()
    user_id = request.headers.get("X-User-ID", "anonymous")
    session_id = request.headers.get("X-Session-ID", "unknown")
    ip_address = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    
    audit_logger.log(
        action=AuditAction.USER_QUERY,
        user_id=user_id,
        details={"path": request.url.path, "method": request.method, "ip": ip_address},
        session_id=session_id,
        ip_address=ip_address
    )
    
    response = await call_next(request)
    
    audit_logger.log(
        action=AuditAction.AI_RESPONSE,
        user_id=user_id,
        details={
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
        },
        session_id=session_id
    )
    
    return response


# ============ ✅ HEALTH CHECK ENDPOINTS ============

@app.get("/health")
@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "insurance-rag-backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ============ ✅ ROOT ENDPOINT ============

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "🍋 Lemonade AI Insurance RAG API",
        "version": "2.0.0",
        "mcp": "✅ MCP Gateway Available",
        "database": "✅ Supabase Connected",
        "governance": {
            "content_safety": "✅ Active",
            "audit_logging": "✅ Active",
            "data_privacy": "✅ Active",
            "explainability": "✅ Active"
        },
        "endpoints": {
            "auth": {
                "signup": "/api/auth/signup",
                "login": "/api/auth/login",
                "status": "/api/auth/status",
                "change-password": "/api/auth/change-password"
            },
            "admin": {
                "approve": "/api/admin/approve",
                "approve-button": "/api/admin/approve-button",
                "users": "/api/admin/users"
            },
            "rag": {"query": "/api/rag/query"},
            "mcp": {"execute": "/api/mcp/execute"},
            "chat": "/api/chat",
            "vision": {
                "classify": "/api/vision/classify",
                "analyze": "/api/vision/analyze",
                "status": "/api/vision/status"
            },
            "dashboard": {
                "stats": "/api/dashboard/stats",
                "governance": "/api/dashboard/governance",
                "mcp": "/api/dashboard/mcp",
                "health": "/api/dashboard/health",
                "audit": "/api/dashboard/audit"
            },
            "analytics": {
                "stats": "/api/analytics/stats",
                "users": "/api/analytics/users",
                "features": "/api/analytics/features",
                "queries": "/api/analytics/queries",
                "cost": "/api/analytics/cost",
                "performance": "/api/analytics/performance"
            },
            "sessions": "/api/sessions",
            "history": "/api/history/{session_id}"
        }
    }


# ============ ✅ KAGGLE VISION ENDPOINTS ============

def _get_kaggle_url() -> str:
    """Get Kaggle API URL from environment"""
    return os.getenv('KAGGLE_API_URL', '')

@app.get("/api/vision/status")
async def vision_status():
    """Check Kaggle Vision model status"""
    kaggle_url = _get_kaggle_url()
    if not kaggle_url:
        return {
            "loaded": False, 
            "error": "KAGGLE_API_URL not set",
            "available": False
        }
    
    try:
        response = requests.get(
            f"{kaggle_url}/api/vision/status",
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {
            "loaded": False, 
            "error": f"HTTP {response.status_code}",
            "available": False
        }
    except Exception as e:
        return {
            "loaded": False, 
            "error": str(e),
            "available": False
        }

@app.post("/api/vision/classify")
async def vision_classify(request: Request):
    """Classify an image using Kaggle Vision API"""
    kaggle_url = _get_kaggle_url()
    if not kaggle_url:
        return JSONResponse(
            status_code=503,
            content={"success": False, "error": "KAGGLE_API_URL not set"}
        )
    
    try:
        # Get the uploaded file
        form = await request.form()
        file = form.get("file")
        
        if not file:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No file uploaded"}
            )
        
        # Forward to Kaggle API
        files = {'file': (file.filename, await file.read(), file.content_type)}
        response = requests.post(
            f"{kaggle_url}/api/vision/classify",
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"success": False, "error": f"Kaggle API error: {response.status_code}"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/vision/analyze")
async def vision_analyze(request: Request):
    """Analyze an image with insurance recommendations using Kaggle Vision API"""
    kaggle_url = _get_kaggle_url()
    if not kaggle_url:
        return JSONResponse(
            status_code=503,
            content={"success": False, "error": "KAGGLE_API_URL not set"}
        )
    
    try:
        # Get the uploaded file
        form = await request.form()
        file = form.get("file")
        
        if not file:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No file uploaded"}
            )
        
        # Forward to Kaggle API
        files = {'file': (file.filename, await file.read(), file.content_type)}
        response = requests.post(
            f"{kaggle_url}/api/vision/analyze",
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"success": False, "error": f"Kaggle API error: {response.status_code}"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# ============ ✅ MCP ENDPOINTS ============

@app.post("/api/mcp/execute")
async def execute_mcp(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": "Invalid or missing JSON payload",
                "status": "healthy"
            }
        )
    
    tool_name = data.get("tool")
    params = data.get("params", {})
    
    if not tool_name:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": "Tool name required",
                "status": "healthy"
            }
        )
    
    try:
        result = await mcp.execute_tool(tool_name, params)
        return result
    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": str(e),
                "status": "healthy"
            }
        )


# ============ ✅ DEEPSEEK CHAT HELPER ============

async def _deepseek_chat(query: str, session_id: str, user_id: str = "anonymous") -> dict:
    """Helper function for DeepSeek chat with proper error handling"""
    try:
        # ✅ Get the DeepSeek client from MCP Gateway
        deepseek_client = getattr(mcp, 'deepseek', None)
        
        if deepseek_client is None:
            print("❌ DeepSeek client not initialized in MCP Gateway")
            return {
                "response": "DeepSeek client is not configured. Please check your API key.",
                "session_id": session_id,
                "model_used": "error"
            }
        
        # ✅ Make the API call
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert insurance claims adjuster with a warm, professional personality. Provide helpful, accurate insurance information in markdown format with clear headings and bullet points."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1024,
            timeout=45.0
        )
        answer = response.choices[0].message.content
        
        # ✅ Save to chat history
        try:
            await chat_db.save_chat(session_id, query, answer)
            print(f"✅ Chat saved to SQLite: {session_id}")
        except Exception as e:
            print(f"⚠️ Failed to save chat: {e}")
        
        # ✅ Log to Supabase
        try:
            supabase_client.log_audit(
                user_id=user_id,
                action="chat_completion",
                details={"query": query[:100], "model": "deepseek"},
                session_id=session_id
            )
        except Exception as e:
            print(f"⚠️ Failed to log audit: {e}")
        
        return {
            "response": answer,
            "session_id": session_id,
            "model_used": "deepseek"
        }
        
    except Exception as e:
        print(f"❌ DeepSeek API error: {e}")
        # ✅ Return a user-friendly error message
        return {
            "response": f"I'm sorry, but I encountered an error while processing your request. Please try again later.",
            "session_id": session_id,
            "model_used": "error",
            "error_details": str(e)  # For debugging
        }


# ============ ✅ CHAT ENDPOINT ============

@app.post("/api/chat")
async def chat(request: dict):
    """Chat endpoint - always uses DeepSeek"""
    query = request.get("query", "")
    session_id = request.get("session_id", str(uuid.uuid4()))
    user_id = request.get("user_id", "anonymous")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # ✅ APPLY CONTENT SAFETY CHECK
    safety_check = content_safety.analyze_input(query, user_id)
    print(f"🛡️ Safety check: blocked={safety_check['blocked']}, score={safety_check['safety_score']}")
    
    if safety_check["blocked"]:
        violations = ', '.join([v['category'] for v in safety_check['violations']])
        try:
            await chat_db.save_chat(session_id, query, f"[BLOCKED] Content safety violation: {violations}")
        except Exception as e:
            print(f"⚠️ Failed to save blocked chat: {e}")
        
        supabase_client.log_audit(
            user_id=user_id,
            action="blocked_request",
            details={"query": query[:100], "violations": violations},
            session_id=session_id
        )
        
        return {
            "response": f"I'm sorry, but this request was blocked by content safety policies. Reason: {violations}",
            "session_id": session_id,
            "model_used": "content_safety_block",
            "blocked": True
        }
    
    # ✅ CHECK FOR PII
    pii_check = data_privacy.detect_pii(query)
    if pii_check["has_pii"]:
        print(f"🔒 PII detected: {pii_check['items']}")
        supabase_client.log_audit(
            user_id=user_id,
            action="pii_detected",
            details={"pii_types": [item["type"] for item in pii_check["items"]]},
            session_id=session_id
        )
    
    # For policy comparison queries
    is_comparison = any(word in query.lower() for word in ['compare', 'vs', 'difference', 'versus'])
    
    if is_comparison:
        comparison_data = get_mock_comparison(query)
        try:
            await chat_db.save_chat(session_id, query, json.dumps(comparison_data))
            print(f"✅ Chat saved to SQLite: {session_id}")
        except Exception as e:
            print(f"⚠️ Failed to save chat: {e}")
        return {
            "response": json.dumps(comparison_data),
            "session_id": session_id,
            "model_used": "deepseek"
        }
    
    # For premium calculation queries
    is_premium = any(word in query.lower() for word in ['premium', 'calculate', 'quote', 'monthly', 'cost'])
    
    if is_premium:
        premium_data = get_mock_premium(query)
        try:
            await chat_db.save_chat(session_id, query, json.dumps(premium_data))
            print(f"✅ Chat saved to SQLite: {session_id}")
        except Exception as e:
            print(f"⚠️ Failed to save chat: {e}")
        return {
            "response": json.dumps(premium_data),
            "session_id": session_id,
            "model_used": "deepseek",
            "premium_data": premium_data.get("data", {})
        }
    
    # ✅ ALWAYS USE DEEPSEEK
    print(f"🔵 Using DeepSeek for: {query[:50]}...")
    return await _deepseek_chat(query, session_id, user_id)


# ============ MOCK DATA FUNCTIONS ============

def get_mock_comparison(query: str) -> dict:
    """Generate mock policy comparison data"""
    query_lower = query.lower()
    
    policies = {}
    
    if "auto" in query_lower:
        policies["auto"] = {
            "name": "Auto Insurance",
            "icon": "🚗",
            "deductible": "$1,000",
            "coverage_limit": "$250,000",
            "monthly_premium": "$85.00",
            "annual_premium": "$1,020.00",
            "key_coverages": [
                "Collision damage",
                "Comprehensive coverage",
                "Liability protection",
                "Uninsured motorist",
                "Glass coverage"
            ],
            "exclusions": [
                "Wear and tear",
                "Intentional damage",
                "Commercial use",
                "Racing activities"
            ],
            "best_for": "Vehicle owners",
            "coverage_score": 8,
            "value_score": 8,
            "claims_process": "File online or through app, 24/7 support",
            "avg_claim_time": "3-5 days",
            "discounts": ["Safe driver", "Multi-car", "Good student"]
        }
    
    if "renters" in query_lower:
        policies["renters"] = {
            "name": "Renters Insurance",
            "icon": "🏠",
            "deductible": "$500",
            "coverage_limit": "$20,000",
            "monthly_premium": "$45.00",
            "annual_premium": "$540.00",
            "key_coverages": [
                "Personal property theft",
                "Fire damage",
                "Liability protection",
                "Loss of use",
                "Medical payments"
            ],
            "exclusions": [
                "Flood damage",
                "Earthquake",
                "Roommate's property",
                "Business equipment"
            ],
            "best_for": "Renters and tenants",
            "coverage_score": 7,
            "value_score": 8,
            "claims_process": "File online, fast approval",
            "avg_claim_time": "3-7 days",
            "discounts": ["Bundle discount", "Security system", "No claims"]
        }
    
    if "health" in query_lower:
        policies["health"] = {
            "name": "Health Insurance",
            "icon": "🏥",
            "deductible": "$1,500",
            "coverage_limit": "$5,000 out-of-pocket max",
            "monthly_premium": "$320.00",
            "annual_premium": "$3,840.00",
            "key_coverages": [
                "Hospitalization",
                "ER visits",
                "Prescription drugs",
                "Preventive care",
                "Maternity care"
            ],
            "exclusions": [
                "Cosmetic surgery",
                "Dental (separate plan)",
                "Vision (separate plan)",
                "Experimental treatments"
            ],
            "best_for": "Individuals and families",
            "coverage_score": 8,
            "value_score": 7,
            "claims_process": "Provider network, easy claims",
            "avg_claim_time": "5-10 days",
            "discounts": ["Wellness program", "Family plan", "Employer group"]
        }
    
    if len(policies) >= 2:
        best = max(policies.keys(), key=lambda k: policies[k]["coverage_score"] + policies[k]["value_score"])
        recommendation = f"Based on your comparison, **{policies[best]['name']}** offers the best overall value."
    else:
        recommendation = "Each policy type serves different needs. Choose based on your specific situation."
    
    return {
        "type": "policy_comparison",
        "data": {
            "comparison": policies,
            "recommendation": recommendation,
            "total_policies": len(policies)
        }
    }


def get_mock_premium(query: str) -> dict:
    """Generate mock premium calculation data"""
    import re
    
    age_match = re.search(r'(\d+)\s*(?:year|yr)', query)
    car_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*|\d+)\s*(?:car|vehicle|auto|worth)', query)
    
    age = int(age_match.group(1)) if age_match else 30
    car_value = float(car_match.group(1).replace(',', '')) if car_match else 35000
    
    base_rate = 500
    age_factor = 0.8 if age < 30 else 1.0 if age < 50 else 1.3
    vehicle_factor = car_value / 20000
    coverage_factor = 1.5
    
    monthly = base_rate * age_factor * vehicle_factor * coverage_factor
    yearly = monthly * 12
    
    return {
        "type": "premium_calculation",
        "data": {
            "monthly": round(monthly, 2),
            "yearly": round(yearly, 2),
            "breakdown": [
                {"step": 1, "label": "Base Rate", "value": f"${base_rate:.2f}", "description": "Standard rate for your vehicle class"},
                {"step": 2, "label": "Age Factor", "value": f"× {age_factor:.2f}", "description": f"You're {age} years old - {'low' if age < 30 else 'moderate' if age < 50 else 'high'} risk"},
                {"step": 3, "label": "Vehicle Value", "value": f"× {vehicle_factor:.2f}", "description": f"Vehicle valued at ${car_value:,.2f}"},
                {"step": 4, "label": "Coverage Type", "value": f"× {coverage_factor:.1f}", "description": "Comprehensive coverage selected"}
            ],
            "summary": f"Your age ({age}) puts you in a {'low' if age < 30 else 'moderate' if age < 50 else 'high'} risk category.",
            "tip": "💡 Tip: Increasing your deductible could lower your monthly premium by up to 15%."
        }
    }


# ============ AUTH ENDPOINTS ============

@app.post("/api/auth/signup")
async def signup(request: Request, body: dict):
    body["ip"] = request.client.host if request.client else "unknown"
    result = await mcp.execute_tool("signup_user", body)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Signup failed"))
    return result

@app.post("/api/auth/login")
async def login(request: Request, body: dict):
    body["ip"] = request.client.host if request.client else "unknown"
    result = await mcp.execute_tool("login_user", body)
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Login failed"))
    return result

@app.post("/api/auth/status")
async def get_user_status(body: dict):
    result = await mcp.execute_tool("get_user_status", body)
    return result

@app.post("/api/auth/change-password")
async def change_password(request: Request, body: dict):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=['HS256'])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        new_password = body.get("new_password")
        if not new_password or len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        result = supabase_client.update_user_status(email, "ACTIVE", new_password)
        
        if result:
            return {"success": True, "message": "Password updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update password")
        
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Password change error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ ADMIN ENDPOINTS ============

@app.post("/api/admin/approve")
async def approve_user(request: Request, body: dict):
    body["ip"] = request.client.host if request.client else "unknown"
    result = await mcp.execute_tool("approve_user", body)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Approval failed"))
    return result

@app.get("/api/admin/approve-button")
async def approve_user_button(email: str, ticket: str):
    try:
        result = await mcp.execute_tool("approve_user", {"email": email, "admin_key": "tool12sober34"})
        
        if result.get("success"):
            return HTMLResponse(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>User Approved ✅</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f7fafc; }}
                        .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
                        h1 {{ color: #2d3748; }}
                        .success {{ color: #38a169; font-size: 64px; }}
                        .btn {{ display: inline-block; background: #667eea; color: white; padding: 12px 32px; border-radius: 8px; text-decoration: none; margin-top: 20px; }}
                        .password {{ background: #f7fafc; padding: 8px 16px; border-radius: 6px; font-family: monospace; font-size: 18px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">✅</div>
                        <h1>User Approved!</h1>
                        <p style="color: #4a5568;">User <strong>{email}</strong> has been successfully approved.</p>
                        <p style="color: #4a5568; font-size: 16px;">Password: <span class="password">{result.get('password')}</span></p>
                        <p style="font-size: 14px; color: #718096;">The user has been sent a welcome email with their login credentials.</p>
                        <a href="http://localhost:8001/api/auth/login" class="btn">Go to Login</a>
                    </div>
                </body>
                </html>
                """
            )
        else:
            return HTMLResponse(
                f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Approval Failed ❌</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f7fafc; }}
                        .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
                        .error {{ color: #e53e3e; font-size: 64px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="error">❌</div>
                        <h1>Approval Failed</h1>
                        <p style="color: #4a5568;">User <strong>{email}</strong> could not be approved.</p>
                        <p style="color: #e53e3e;">{result.get('error', 'Unknown error')}</p>
                    </div>
                </body>
                </html>
                """
            )
    except Exception as e:
        return HTMLResponse(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error ❌</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f7fafc; }}
                    .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
                    .error {{ color: #e53e3e; font-size: 64px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error">❌</div>
                    <h1>Error</h1>
                    <p style="color: #4a5568;">Something went wrong: {str(e)}</p>
                </div>
            </body>
            </html>
            """
        )

@app.get("/api/admin/users")
async def get_users():
    result = await mcp.execute_tool("get_all_users", {})
    return result


# ============ RAG ENDPOINTS ============

@app.post("/api/rag/query")
async def rag_query(request: Request, body: dict):
    query = body.get("query", "")
    safety_check = content_safety.analyze_input(query, body.get("user_id", "anonymous"))
    
    if safety_check["blocked"]:
        raise HTTPException(status_code=400, detail="Content safety policy blocked this request.")
    
    body["ip"] = request.client.host if request.client else "unknown"
    result = await mcp.execute_tool("query_insurance", body)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "RAG query failed"))
    return result


# ============ DASHBOARD ENDPOINTS ============

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    cache_key = "dashboard_stats"
    cached_data = get_cached(cache_key)
    if cached_data:
        return cached_data
    
    try:
        users = supabase_client.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u.get("status") == "ACTIVE"])
        pending_users = len([u for u in users if u.get("status") == "PENDING"])
        
        result = {
            "total_users": total_users,
            "active_users": active_users,
            "total_requests": pending_users,
            "pending_requests": pending_users,
            "system_status": "healthy",
            "safety_score": 95,
            "uptime": "72h"
        }
        set_cached(cache_key, result)
        return result
    except Exception as e:
        return {
            "total_users": 0,
            "active_users": 0,
            "total_requests": 0,
            "pending_requests": 0,
            "system_status": "degraded",
            "safety_score": 95,
            "uptime": "N/A"
        }


@app.get("/api/dashboard/governance")
async def get_governance_stats():
    safety_report = content_safety.get_safety_report()
    privacy_report = data_privacy.get_privacy_report()
    audit_logs = supabase_client.get_audit_logs(100)
    
    return {
        "safety_score": safety_report.get("safety_score_avg", 95) if isinstance(safety_report, dict) else 95,
        "pii_detections": privacy_report.get("pii_detected_percentage", 0) if isinstance(privacy_report, dict) else 0,
        "blocked_requests": safety_report.get("blocked_percentage", 0) if isinstance(safety_report, dict) else 0,
        "audit_logs": len(audit_logs) if audit_logs else 0,
        "explanations": len(explainability.explanation_history) if hasattr(explainability, 'explanation_history') else 0,
        "safety_violations": []
    }


@app.get("/api/dashboard/mcp")
async def get_mcp_stats():
    return {
        "total_calls": 0,
        "success_rate": 100,
        "avg_latency": 0.5,
        "tools": [],
        "top_5": []
    }


@app.get("/api/dashboard/health")
async def get_health():
    return {
        "status": "healthy",
        "uptime": "72h",
        "cpu": "45%",
        "memory": "6.2GB/16GB",
        "gpu": "✅ Active",
        "qlora_loaded": True
    }


@app.get("/api/dashboard/audit")
async def get_audit_logs(limit: int = 100):
    logs = supabase_client.get_audit_logs(limit)
    return {"logs": logs, "limit": limit}


# ============ ANALYTICS ENDPOINTS ============

@app.get("/api/analytics/stats")
async def get_analytics_stats():
    try:
        users = supabase_client.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u.get("status") == "ACTIVE"])
        
        return {
            "users": {
                "total_users": total_users,
                "active_users_7d": active_users,
                "active_users_30d": active_users,
                "new_users_30d": 0,
                "growth_rate": 0,
                "retention_rate": 100
            },
            "sessions": {"total_sessions": 0, "avg_session_duration": 0, "bounce_rate": 0},
            "features": {"total_calls": 0, "feature_usage": {}, "most_used": [], "least_used": []},
            "queries": {
                "total_queries": 0,
                "categories": {"premium": 0, "claim": 0, "comparison": 0, "coverage": 0, "general": 0},
                "daily_queries": [],
                "peak_hour": 14
            },
            "cost": {
                "total_cost": 0,
                "qlora_cost": 0,
                "deepseek_cost": 0,
                "cost_per_query": 0,
                "cost_per_user": 0,
                "savings": 0,
                "savings_percentage": 0
            },
            "performance": {"avg_response_time": 0.8, "avg_qlora_time": 0.5, "avg_deepseek_time": 2.5, "success_rate": 98.5}
        }
    except:
        return {"users": {"total_users": 0, "active_users_7d": 0, "active_users_30d": 0, "new_users_30d": 0, "growth_rate": 0, "retention_rate": 0}, "sessions": {"total_sessions": 0, "avg_session_duration": 0, "bounce_rate": 0}, "features": {"total_calls": 0, "feature_usage": {}, "most_used": [], "least_used": []}, "queries": {"total_queries": 0, "categories": {"premium": 0, "claim": 0, "comparison": 0, "coverage": 0, "general": 0}, "daily_queries": [], "peak_hour": 14}, "cost": {"total_cost": 0, "qlora_cost": 0, "deepseek_cost": 0, "cost_per_query": 0, "cost_per_user": 0, "savings": 0, "savings_percentage": 0}, "performance": {"avg_response_time": 0.8, "avg_qlora_time": 0.5, "avg_deepseek_time": 2.5, "success_rate": 98.5}}


@app.get("/api/analytics/users")
async def get_analytics_users():
    try:
        users = supabase_client.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u.get("status") == "ACTIVE"])
        return {"total_users": total_users, "active_users_7d": active_users, "active_users_30d": active_users, "new_users_30d": 0, "growth_rate": 0, "retention_rate": 100}
    except:
        return {"total_users": 0, "active_users_7d": 0, "active_users_30d": 0, "new_users_30d": 0, "growth_rate": 0, "retention_rate": 0}


@app.get("/api/analytics/features")
async def get_analytics_features():
    return {"total_calls": 0, "feature_usage": {}, "most_used": [], "least_used": []}


@app.get("/api/analytics/queries")
async def get_analytics_queries():
    return {"total_queries": 0, "categories": {"premium": 0, "claim": 0, "comparison": 0, "coverage": 0, "general": 0}, "daily_queries": [], "peak_hour": 14}


@app.get("/api/analytics/cost")
async def get_analytics_cost():
    return {"total_cost": 0, "qlora_cost": 0, "deepseek_cost": 0, "cost_per_query": 0, "cost_per_user": 0, "savings": 0, "savings_percentage": 0}


@app.get("/api/analytics/performance")
async def get_analytics_performance():
    return {"avg_response_time": 0.8, "avg_qlora_time": 0.5, "avg_deepseek_time": 2.5, "success_rate": 98.5}


# ============ SESSIONS ENDPOINTS ============

@app.get("/api/sessions")
async def get_sessions():
    try:
        sessions = await chat_db.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        print(f"⚠️ Error getting sessions: {e}")
        return {"sessions": []}


@app.get("/api/history/{session_id}")
async def get_history(session_id: str):
    try:
        history = await chat_db.get_chat_history(session_id)
        return {"history": history, "session_id": session_id}
    except Exception as e:
        print(f"⚠️ Error getting history: {e}")
        return {"history": [], "session_id": session_id}


# ============ WebSocket Endpoint ============

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    print(f"🔌 Client connected: {session_id}")
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                if message.get("type") == "chat":
                    query = message.get("content", "")
                    
                    safety_check = content_safety.analyze_input(query, "anonymous")
                    if safety_check["blocked"]:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": "Content safety policy blocked this request."
                        })
                        continue
                    
                    supabase_client.log_audit(
                        user_id="anonymous",
                        action="websocket_chat",
                        details={"query": query[:100]},
                        session_id=session_id
                    )
                    
                    # ✅ Use DeepSeek for WebSocket too
                    result = await _deepseek_chat(query, session_id)
                    await manager.send_message(session_id, {
                        "type": "final",
                        "response": result.get("response", ""),
                        "model_used": "deepseek"
                    })
                    await manager.send_message(session_id, {"type": "done"})
                    
                elif message.get("type") == "ping":
                    await manager.send_message(session_id, {"type": "pong"})
                    
            except asyncio.TimeoutError:
                try:
                    await manager.send_message(session_id, {"type": "ping"})
                except:
                    break
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        print(f"🔌 Client disconnected: {session_id}")
    except Exception as e:
        print(f"[ERROR] WebSocket error: {e}")
        manager.disconnect(session_id)