# sap_mock.py
"""
SAP Integration Connector (Mock)
Shows how SAP would integrate with your RAG system
No SAP license needed - just the integration pattern!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import subprocess
from datetime import datetime

app = FastAPI(
    title="SAP Insurance Connector",
    description="Connects SAP systems to Insurance RAG MCP Gateway",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ Request/Response Models ============

class SAPRequest(BaseModel):
    """Request from SAP"""
    action: str  # get_policy, check_claim, calculate_premium, etc.
    data: Dict[str, Any]
    sap_user: Optional[str] = None
    sap_system: str = "S4HANA"

class SAPResponse(BaseModel):
    """Response to SAP"""
    status: str  # success, error
    message: str
    data: Optional[Dict[str, Any]] = None
    sap_timestamp: str
    reference_id: str

class PolicyData(BaseModel):
    """SAP Policy Data Structure"""
    policy_number: str
    policy_type: str
    customer_id: str
    effective_date: str
    expiry_date: str
    premium_amount: float
    coverage_details: Dict[str, Any]

# ============ Mock Data ============

MOCK_POLICIES = {
    "POL-001": {
        "policy_number": "POL-001",
        "policy_type": "auto",
        "customer_id": "CUST-1001",
        "effective_date": "2024-01-01",
        "expiry_date": "2024-12-31",
        "premium_amount": 150.00,
        "coverage_details": {
            "liability": "250000/500000",
            "collision_deductible": 1000,
            "comprehensive_deductible": 500
        }
    },
    "POL-002": {
        "policy_number": "POL-002",
        "policy_type": "renters",
        "customer_id": "CUST-1002",
        "effective_date": "2024-01-01",
        "expiry_date": "2024-12-31",
        "premium_amount": 30.00,
        "coverage_details": {
            "personal_property": 20000,
            "liability": 100000,
            "deductible": 500
        }
    },
    "POL-003": {
        "policy_number": "POL-003",
        "policy_type": "health",
        "customer_id": "CUST-1003",
        "effective_date": "2024-01-01",
        "expiry_date": "2024-12-31",
        "premium_amount": 450.00,
        "coverage_details": {
            "deductible": 1500,
            "out_of_pocket_max": 5000,
            "er_copay": 150
        }
    }
}

MOCK_CLAIMS = {
    "CL-001": {
        "claim_id": "CL-001",
        "policy_number": "POL-001",
        "status": "Approved",
        "amount": 2500.00,
        "filed_date": "2024-06-01"
    },
    "CL-002": {
        "claim_id": "CL-002",
        "policy_number": "POL-002",
        "status": "Pending Review",
        "amount": 500.00,
        "filed_date": "2024-06-15"
    }
}

# ============ MCP Client ============

def call_mcp(tool_name: str, arguments: dict) -> dict:
    """Call the MCP server"""
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 1
    }
    
    try:
        process = subprocess.Popen(
            ["python", "run_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        stdout, stderr = process.communicate(input=json.dumps(request) + "\n", timeout=120)
        
        if stdout:
            lines = stdout.strip().split('\n')
            for line in reversed(lines):
                try:
                    return json.loads(line)
                except:
                    continue
        
        return {"error": "No response from MCP"}
    except Exception as e:
        return {"error": str(e)}

# ============ SAP Endpoints ============

@app.post("/sap")
async def handle_sap(request: SAPRequest) -> SAPResponse:
    """
    Main SAP integration endpoint
    
    How SAP integrates:
    1. SAP calls this endpoint via HTTP/REST
    2. This endpoint routes to MCP tools
    3. Response goes back to SAP
    """
    
    print(f"📨 SAP received: {request.action} from {request.sap_user}")
    
    try:
        if request.action == "get_policy":
            result = await get_policy(request.data)
        elif request.action == "check_claim":
            result = await check_claim(request.data)
        elif request.action == "calculate_premium":
            result = await calculate_premium(request.data)
        elif request.action == "compare_policies":
            result = await compare_policies(request.data)
        elif request.action == "search_policies":
            result = await search_policies(request.data)
        else:
            return SAPResponse(
                status="error",
                message=f"Unknown action: {request.action}",
                data={},
                sap_timestamp=datetime.now().isoformat(),
                reference_id=f"SAP-REF-{datetime.now().timestamp()}"
            )
        
        return SAPResponse(
            status="success",
            message=f"Action {request.action} completed",
            data=result,
            sap_timestamp=datetime.now().isoformat(),
            reference_id=f"SAP-REF-{datetime.now().timestamp()}"
        )
    
    except Exception as e:
        return SAPResponse(
            status="error",
            message=str(e),
            data={},
            sap_timestamp=datetime.now().isoformat(),
            reference_id=f"SAP-REF-{datetime.now().timestamp()}"
        )

# ============ SAP Action Handlers ============

async def get_policy(data: Dict[str, Any]) -> Dict[str, Any]:
    """Get policy from SAP system"""
    policy_number = data.get("policy_number")
    
    if policy_number in MOCK_POLICIES:
        return {
            "policy": MOCK_POLICIES[policy_number],
            "source": "SAP S4HANA",
            "retrieved_at": datetime.now().isoformat()
        }
    
    # Try MCP if not found in mock
    result = call_mcp("search_policies", {
        "query": f"policy {policy_number}",
        "limit": 1
    })
    
    return {
        "policy": {"policy_number": policy_number, "source": "MCP Gateway"},
        "source": "MCP Gateway",
        "mcp_response": result
    }

async def check_claim(data: Dict[str, Any]) -> Dict[str, Any]:
    """Check claim status from SAP"""
    claim_id = data.get("claim_id")
    
    if claim_id in MOCK_CLAIMS:
        return {
            "claim": MOCK_CLAIMS[claim_id],
            "source": "SAP S4HANA"
        }
    
    # Use MCP
    result = call_mcp("check_claim_status", {"claim_id": claim_id})
    return {
        "claim": result,
        "source": "MCP Gateway"
    }

async def calculate_premium(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate premium from SAP"""
    age = data.get("age", 30)
    car_value = data.get("car_value", 35000)
    
    # Use MCP
    result = call_mcp("calculate_insurance_premium", {
        "age": age,
        "car_value": car_value
    })
    
    return {
        "calculation": result,
        "source": "MCP Gateway",
        "sap_integration": True
    }

async def compare_policies(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare policies from SAP"""
    policy_types = data.get("policy_types", ["auto", "renters"])
    
    # Use MCP
    result = call_mcp("compare_insurance_policies", {
        "policy_types": policy_types
    })
    
    return {
        "comparison": result,
        "source": "MCP Gateway"
    }

async def search_policies(data: Dict[str, Any]) -> Dict[str, Any]:
    """Search policies from SAP"""
    query = data.get("query", "")
    
    # Use MCP
    result = call_mcp("search_policies", {
        "query": query,
        "limit": 5
    })
    
    return {
        "results": result,
        "source": "MCP Gateway"
    }

# ============ SAP Connector Info ============

@app.get("/sap/connector-info")
async def sap_connector_info():
    """Information about the SAP connector"""
    return {
        "name": "SAP Insurance Connector",
        "version": "1.0.0",
        "description": "Connects SAP S4HANA to Insurance RAG MCP Gateway",
        "actions": [
            {
                "name": "get_policy",
                "description": "Get policy details",
                "required_fields": ["policy_number"]
            },
            {
                "name": "check_claim",
                "description": "Check claim status",
                "required_fields": ["claim_id"]
            },
            {
                "name": "calculate_premium",
                "description": "Calculate insurance premium",
                "required_fields": ["age", "car_value"]
            },
            {
                "name": "compare_policies",
                "description": "Compare policies",
                "required_fields": ["policy_types"]
            },
            {
                "name": "search_policies",
                "description": "Search policies",
                "required_fields": ["query"]
            }
        ],
        "sap_integration_pattern": {
            "step_1": "SAP system makes HTTP POST to /sap",
            "step_2": "Request contains action and data",
            "step_3": "Connector routes to appropriate MCP tool",
            "step_4": "Response returned to SAP"
        }
    }

@app.get("/sap/health")
async def sap_health():
    """Health check for SAP connector"""
    return {
        "status": "healthy",
        "sap_systems": ["S4HANA", "ECC"],
        "mock_data": len(MOCK_POLICIES),
        "timestamp": datetime.now().isoformat()
    }

# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 SAP Connector")
    print("📡 Endpoint: http://localhost:8083/sap")
    print("📡 Info: http://localhost:8083/sap/connector-info")
    print("📡 Health: http://localhost:8083/sap/health")
    print("=" * 50)
    print("Mock SAP data loaded:")
    print(f"  - Policies: {len(MOCK_POLICIES)}")
    print(f"  - Claims: {len(MOCK_CLAIMS)}")
    uvicorn.run(app, host="0.0.0.0", port=8083)