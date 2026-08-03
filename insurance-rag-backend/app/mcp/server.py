# app/mcp/server.py
import json
import sys
from typing import Dict, Any
from .gateway import MCPGateway

class MCPServer:
    """MCP Server with smart gateway integration"""
    
    def __init__(self):
        self.gateway = MCPGateway()
    
    async def run_stdio(self):
        """Run MCP server over stdio (for Claude Desktop)"""
        # Use simple ASCII messages for Windows compatibility
        print("Smart Insurance RAG MCP Gateway", file=sys.stderr)
        print("Version: 2.0.0", file=sys.stderr)
        print("Rate limiting: 60 requests/minute", file=sys.stderr)
        print("Analytics: Enabled", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print("Ready for requests...", file=sys.stderr)
        
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            
            try:
                request = json.loads(line)
                response = await self.gateway.handle_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": f"Server error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()