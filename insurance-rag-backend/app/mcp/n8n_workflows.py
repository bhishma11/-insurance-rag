# app/mcp/n8n_workflows.py
"""
MCP + n8n Integration
Allows MCP tools to trigger n8n workflows
"""

import os
import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.governance.audit_log import audit_logger

class N8NIntegration:
    """Connect MCP tools to n8n workflows"""
    
    def __init__(self):
        self.n8n_url = os.getenv('N8N_URL', 'http://localhost:5678')
        self.webhook_key = os.getenv('N8N_WEBHOOK_KEY', 'n8n-webhook-key')
        self.basic_auth_user = os.getenv('N8N_BASIC_AUTH_USER', 'admin')
        self.basic_auth_pass = os.getenv('N8N_BASIC_AUTH_PASSWORD', 'admin123')
        self.available = self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check if n8n is running"""
        try:
            import requests
            response = requests.get(
                f"{self.n8n_url}/healthz",
                timeout=5
            )
            if response.status_code == 200:
                print("✅ n8n is running")
                return True
            return False
        except:
            print("⚠️ n8n not available (workflows will be skipped)")
            return False
    
    async def trigger_webhook(
        self, 
        workflow_id: str, 
        data: Dict[str, Any],
        auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trigger an n8n workflow via webhook
        
        Args:
            workflow_id: The workflow ID (from n8n)
            data: Data to send to the workflow
            auth_token: Optional authentication token
        
        Returns:
            Workflow response
        """
        if not self.available:
            return {"error": "n8n not available", "workflow_id": workflow_id}
        
        try:
            headers = {"Content-Type": "application/json"}
            
            # Add auth if provided
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            
            # Use basic auth if no token
            if not auth_token and self.basic_auth_user:
                import base64
                credentials = f"{self.basic_auth_user}:{self.basic_auth_pass}"
                encoded = base64.b64encode(credentials.encode()).decode()
                headers["Authorization"] = f"Basic {encoded}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.n8n_url}/webhook/{workflow_id}",
                    json=data,
                    headers=headers,
                    timeout=60
                )
                
                # Log the trigger
                audit_logger.log(
                    action="n8n_workflow_trigger",
                    user_id="system",
                    details={
                        "workflow_id": workflow_id,
                        "status_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                if response.status_code == 200:
                    return {
                        "status": "success",
                        "workflow_id": workflow_id,
                        "data": response.json() if response.text else {}
                    }
                else:
                    return {
                        "status": "error",
                        "workflow_id": workflow_id,
                        "error": f"HTTP {response.status_code}",
                        "detail": response.text
                    }
                    
        except httpx.TimeoutException:
            return {"error": "Workflow timeout", "workflow_id": workflow_id}
        except Exception as e:
            return {"error": str(e), "workflow_id": workflow_id}
    
    # ============ Specific Workflow Triggers ============
    
    async def process_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a claim using n8n workflow
        """
        return await self.trigger_webhook(
            workflow_id="claim-processing",
            data={
                "action": "process_claim",
                "claim": claim_data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def send_email(self, email: str, subject: str, message: str) -> Dict[str, Any]:
        """
        Send email via n8n workflow
        """
        return await self.trigger_webhook(
            workflow_id="email-notification",
            data={
                "action": "send_email",
                "to": email,
                "subject": subject,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def send_ticket_email(self, email: str, ticket: str, user_id: str) -> Dict[str, Any]:
        """
        Send ticket email via n8n
        """
        return await self.trigger_webhook(
            workflow_id="ticket-email",
            data={
                "action": "send_ticket",
                "to": email,
                "ticket": ticket,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def process_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document via n8n workflow
        """
        return await self.trigger_webhook(
            workflow_id="document-processing",
            data={
                "action": "process_document",
                "document": document_data,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def get_analytics(self, date_range: str = "7d") -> Dict[str, Any]:
        """
        Get analytics via n8n workflow
        """
        return await self.trigger_webhook(
            workflow_id="analytics-report",
            data={
                "action": "get_analytics",
                "date_range": date_range,
                "timestamp": datetime.now().isoformat()
            }
        )

# Singleton instance
n8n = N8NIntegration()