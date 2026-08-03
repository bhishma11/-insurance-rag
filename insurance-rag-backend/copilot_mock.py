# copilot_mock.py
"""
Microsoft Copilot Studio Custom Connector (Mock)
Shows how Copilot would call your MCP tools
No Copilot license needed - just the integration pattern!
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import subprocess
import os

app = FastAPI(
    title="Copilot Studio Connector",
    description="Connects Microsoft Copilot Studio to Insurance RAG MCP Gateway",
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

class CopilotRequest(BaseModel):
    """Request from Copilot Studio"""
    text: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class CopilotResponse(BaseModel):
    """Response to Copilot Studio"""
    text: str
    session_id: str
    tool_used: str
    status: str = "success"
    channel: str = "Copilot Studio"

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
        
        return {"error": "No response from MCP", "stderr": stderr}
    except Exception as e:
        return {"error": str(e)}

# ============ Tool Parsing ============

def parse_user_intent(text: str) -> dict:
    """Parse what the user wants to do"""
    text_lower = text.lower()
    
    # Premium Calculation
    if any(word in text_lower for word in ['premium', 'calculate', 'cost', 'quote', 'monthly']):
        # Extract age
        import re
        age_match = re.search(r'(\d+)\s*(?:years? old|year old|yo|years?|yr)', text)
        age = int(age_match.group(1)) if age_match else 30
        
        # Extract car value
        car_match = re.search(r'\$?(\d+(?:,\d+)?)\s*(?:k|thousand)?', text)
        if car_match:
            val = car_match.group(1).replace(',', '')
            try:
                car_value = float(val)
                if 'k' in text_lower or 'thousand' in text_lower:
                    car_value = car_value * 1000
                elif car_value < 1000:
                    car_value = car_value * 1000
            except:
                car_value = 35000
        else:
            car_value = 35000
        
        return {
            "tool": "calculate_insurance_premium",
            "arguments": {
                "age": age,
                "car_value": car_value,
                "coverage_type": "comprehensive"
            },
            "intent": "premium_calculation"
        }
    
    # Claim Status
    elif any(word in text_lower for word in ['claim', 'status', 'claim status']):
        import re
        claim_match = re.search(r'CL-\d+', text.upper())
        claim_id = claim_match.group() if claim_match else "CL-12345"
        
        return {
            "tool": "check_claim_status",
            "arguments": {"claim_id": claim_id},
            "intent": "claim_status"
        }
    
    # Policy Comparison
    elif any(word in text_lower for word in ['compare', 'vs', 'versus', 'difference']):
        policies = []
        if 'auto' in text_lower:
            policies.append('auto')
        if 'renters' in text_lower:
            policies.append('renters')
        if 'health' in text_lower:
            policies.append('health')
        if not policies:
            policies = ['auto', 'renters']
        
        return {
            "tool": "compare_insurance_policies",
            "arguments": {"policy_types": policies},
            "intent": "policy_comparison"
        }
    
    # Search / Coverage
    else:
        return {
            "tool": "search_policies",
            "arguments": {"query": text, "limit": 5},
            "intent": "search"
        }

# ============ Copilot Endpoint ============

@app.post("/copilot")
async def handle_copilot(request: CopilotRequest) -> CopilotResponse:
    """
    Main endpoint for Copilot Studio
    
    How Copilot Studio connects:
    1. Create Custom Connector in Copilot Studio
    2. Point it to: http://your-server/copilot
    3. Copilot sends user questions here
    4. This endpoint routes to MCP tools
    5. Response goes back to Copilot
    """
    
    print(f"📨 Copilot received: {request.text}")
    
    # Parse intent
    intent = parse_user_intent(request.text)
    print(f"🔍 Intent: {intent['intent']} → Tool: {intent['tool']}")
    
    # Call MCP
    result = call_mcp(intent["tool"], intent["arguments"])
    print(f"📤 MCP response: {result.get('result', {}).get('content', [{}])[0].get('text', '')[:100]}...")
    
    # Extract text response
    response_text = "I processed your request."
    if result.get("result", {}).get("content"):
        response_text = result["result"]["content"][0].get("text", response_text)
    elif result.get("error"):
        response_text = f"❌ Error: {result['error']}"
    
    return CopilotResponse(
        text=response_text,
        session_id=request.session_id or "copilot-session",
        tool_used=intent["tool"]
    )

# ============ Copilot Connector Info ============

@app.get("/copilot/connector-info")
async def connector_info():
    """Information about the Copilot connector"""
    return {
        "name": "Insurance RAG Copilot Connector",
        "version": "1.0.0",
        "description": "Connects Microsoft Copilot Studio to Insurance RAG MCP Gateway",
        "tools_available": [
            {
                "name": "calculate_insurance_premium",
                "description": "Calculate auto insurance premium",
                "example": "Calculate my premium for 30 year old with $35,000 car"
            },
            {
                "name": "check_claim_status",
                "description": "Check claim status",
                "example": "Check claim status for CL-12345"
            },
            {
                "name": "compare_insurance_policies",
                "description": "Compare policies",
                "example": "Compare auto and renters insurance"
            },
            {
                "name": "search_policies",
                "description": "Search policy documents",
                "example": "What does auto insurance cover?"
            }
        ],
        "how_to_configure": {
            "step_1": "Create Custom Connector in Copilot Studio",
            "step_2": "Set endpoint to: http://your-server/copilot",
            "step_3": "Add actions for each tool",
            "step_4": "Test with sample queries"
        }
    }

# ============ Run Server ============

if __name__ == "__main__":
    import uvicorn
    print("🚀 Copilot Studio Connector")
    print("📡 Endpoint: http://localhost:8082/copilot")
    print("📡 Info: http://localhost:8082/copilot/connector-info")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8082)