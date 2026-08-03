# app/mcp/n8n_webhooks.py
"""
n8n Webhook Endpoints for MCP Integration
Allows n8n to call MCP tools
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.smart_router import SmartRouter
from app.core.agent_tools import InsuranceTools

router = APIRouter(prefix="/n8n", tags=["n8n"])

class N8NRequest(BaseModel):
    action: str
    data: Dict[str, Any]
    webhook_key: Optional[str] = None

# ============ Webhook Endpoints ============

@router.post("/webhook/{workflow_id}")
async def n8n_webhook(workflow_id: str, request: N8NRequest):
    """
    Webhook endpoint for n8n to call MCP tools
    """
    try:
        # Verify webhook key
        if request.webhook_key != os.getenv('N8N_WEBHOOK_KEY', 'n8n-webhook-key'):
            raise HTTPException(status_code=401, detail="Invalid webhook key")
        
        router = SmartRouter()
        tools = InsuranceTools()
        
        # Route to appropriate tool
        if request.action == "calculate_premium":
            result = tools.calculate_premium(
                age=request.data.get("age", 30),
                car_value=request.data.get("car_value", 35000),
                coverage_type=request.data.get("coverage_type", "comprehensive")
            )
            return {"status": "success", "result": result}
        
        elif request.action == "check_claim":
            result = tools.check_claim_status(
                claim_id=request.data.get("claim_id", "CL-12345")
            )
            return {"status": "success", "result": result}
        
        elif request.action == "compare_policies":
            result = tools.compare_policies(
                policy_types=request.data.get("policy_types", ["auto", "renters"])
            )
            return {"status": "success", "result": result}
        
        elif request.action == "search_policies":
            # Use RAG search
            from app.core.vector_search import VectorSearch
            vector_search = VectorSearch()
            vector_search.load_index()
            results, scores = vector_search.hybrid_search(
                request.data.get("query", ""),
                k=request.data.get("limit", 5)
            )
            return {"status": "success", "result": results}
        
        else:
            return {
                "status": "error", 
                "message": f"Unknown action: {request.action}"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/health")
async def n8n_health():
    """Health check for n8n integration"""
    from app.mcp.n8n_workflows import n8n
    return {
        "status": "healthy",
        "n8n_available": n8n.available,
        "timestamp": datetime.now().isoformat()
    }