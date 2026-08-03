# mcp_http_server.py
"""
HTTP API Wrapper for MCP Server
Exposes all MCP tools as REST endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import subprocess
import json
import uvicorn
import threading
import queue
import time
import sys
import os

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

app = FastAPI(
    title="Insurance RAG MCP API",
    description="Enterprise Insurance Intelligence Platform - MCP Gateway",
    version="2.0.0"
)

# CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Request/Response Models ============

class PremiumRequest(BaseModel):
    age: int
    car_value: float
    coverage_type: str = "comprehensive"

class ClaimRequest(BaseModel):
    claim_id: str

class CompareRequest(BaseModel):
    policy_types: List[str]

class CoverageRequest(BaseModel):
    policy_type: str
    coverage_question: str

class ClaimFileRequest(BaseModel):
    incident_type: str
    policy_type: str

class DefinitionRequest(BaseModel):
    term: str

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class ScheduleRequest(BaseModel):
    phone: str
    preferred_time: str
    reason: str = "general"

class AnalyzeRequest(BaseModel):
    claim_type: str
    policy_type: str
    details: Optional[str] = ""

# ============ MCP Client ============

class MCPClient:
    """MCP client that runs server as a subprocess per request"""
    
    def call(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call MCP method - starts a new process each time"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        try:
            # Run the MCP server as a subprocess
            process = subprocess.Popen(
                ["python", "run_mcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Send request
            request_json = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=request_json, timeout=120)
            
            # Parse the last valid JSON from stdout
            if stdout:
                lines = stdout.strip().split('\n')
                for line in reversed(lines):
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            return {"error": "No valid JSON response", "stderr": stderr}
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "MCP server timeout after 120 seconds"}
        except Exception as e:
            return {"error": str(e)}

# Create global MCP client
mcp_client = MCPClient()

# ============ Health & Info Endpoints ============

@app.get("/")
async def root():
    """API root - system info"""
    return {
        "name": "Insurance RAG MCP API",
        "version": "2.0.0",
        "status": "online",
        "endpoints": [
            "/docs - Swagger UI",
            "/health - Health check",
            "/tools - List all tools",
            "/premium - Calculate premium",
            "/claim - Check claim status",
            "/compare - Compare policies",
            "/coverage - Get coverage info",
            "/claim-file - Get claim instructions",
            "/definition - Get insurance definition",
            "/search - Search policies",
            "/schedule - Schedule callback",
            "/analyze - Analyze claim outcome"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return mcp_client.call("health/check")

@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return mcp_client.call("tools/list")

@app.get("/analytics")
async def get_analytics():
    """Get MCP usage analytics"""
    return mcp_client.call("analytics/get")

# ============ Tool Endpoints ============

@app.post("/premium")
async def calculate_premium(request: PremiumRequest):
    """Calculate auto insurance premium"""
    return mcp_client.call("tools/call", {
        "name": "calculate_insurance_premium",
        "arguments": {
            "age": request.age,
            "car_value": request.car_value,
            "coverage_type": request.coverage_type
        }
    })

@app.post("/claim")
async def check_claim(request: ClaimRequest):
    """Check claim status"""
    return mcp_client.call("tools/call", {
        "name": "check_claim_status",
        "arguments": {
            "claim_id": request.claim_id
        }
    })

@app.post("/compare")
async def compare_policies(request: CompareRequest):
    """Compare insurance policies"""
    return mcp_client.call("tools/call", {
        "name": "compare_insurance_policies",
        "arguments": {
            "policy_types": request.policy_types
        }
    })

@app.post("/coverage")
async def get_coverage(request: CoverageRequest):
    """Get policy coverage information"""
    return mcp_client.call("tools/call", {
        "name": "get_policy_coverage",
        "arguments": {
            "policy_type": request.policy_type,
            "coverage_question": request.coverage_question
        }
    })

@app.post("/claim-file")
async def file_claim(request: ClaimFileRequest):
    """Get claim filing instructions"""
    return mcp_client.call("tools/call", {
        "name": "file_claim_instructions",
        "arguments": {
            "incident_type": request.incident_type,
            "policy_type": request.policy_type
        }
    })

@app.post("/definition")
async def get_definition(request: DefinitionRequest):
    """Get insurance term definition"""
    return mcp_client.call("tools/call", {
        "name": "get_insurance_definition",
        "arguments": {
            "term": request.term
        }
    })

@app.post("/search")
async def search_policies(request: SearchRequest):
    """Search policy documents"""
    return mcp_client.call("tools/call", {
        "name": "search_policies",
        "arguments": {
            "query": request.query,
            "limit": request.limit
        }
    })

@app.post("/schedule")
async def schedule_callback(request: ScheduleRequest):
    """Schedule an agent callback"""
    return mcp_client.call("tools/call", {
        "name": "schedule_callback",
        "arguments": {
            "phone": request.phone,
            "preferred_time": request.preferred_time,
            "reason": request.reason
        }
    })

@app.post("/analyze")
async def analyze_claim(request: AnalyzeRequest):
    """Analyze claim outcome"""
    return mcp_client.call("tools/call", {
        "name": "analyze_claim_outcome",
        "arguments": {
            "claim_type": request.claim_type,
            "policy_type": request.policy_type,
            "details": request.details
        }
    })

# ============ Run Server ============

if __name__ == "__main__":
    print("🚀 Starting Insurance RAG MCP HTTP API...")
    print("📡 Swagger UI: http://localhost:8080/docs")
    print("📡 ReDoc: http://localhost:8080/redoc")
    print("=" * 50)
    print("⏳ Note: First request will take 30-40 seconds to load QLoRA model...")
    uvicorn.run(app, host="0.0.0.0", port=8080)