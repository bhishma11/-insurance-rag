# app/governance/audit_log.py
"""
AI Governance: Complete Audit Logging System
"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import hashlib

class AuditAction(Enum):
    USER_QUERY = "user_query"
    AI_RESPONSE = "ai_response"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    AUTHENTICATION = "authentication"
    PERMISSION_CHECK = "permission_check"
    PII_DETECTION = "pii_detection"
    DATA_ACCESS = "data_access"
    SYSTEM_CONFIG = "system_config"
    ADMIN_ACTION = "admin_action"

class AuditSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditLogger:
    """Comprehensive audit logging for AI governance"""
    
    def __init__(self, log_file: str = "audit.log", include_console: bool = True):
        self.log_file = log_file
        self.logs = []
        self.logger = logging.getLogger("audit")
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        if include_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(console_handler)
    
    def log(self, action: AuditAction, user_id: str, details: Dict[str, Any],
            severity: AuditSeverity = AuditSeverity.INFO, session_id: Optional[str] = None,
            ip_address: Optional[str] = None) -> str:
        log_entry = {
            "log_id": f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:4]}",
            "timestamp": datetime.now().isoformat(),
            "action": action.value if isinstance(action, AuditAction) else action,
            "user_id": user_id,
            "session_id": session_id or "anonymous",
            "ip_address": ip_address or "unknown",
            "severity": severity.value if isinstance(severity, AuditSeverity) else severity,
            "details": details
        }
        self.logs.append(log_entry)
        if len(self.logs) > 10000:
            self.logs = self.logs[-10000:]
        self.logger.info(json.dumps({"action": log_entry["action"], "user": log_entry["user_id"], "details": json.dumps(log_entry["details"])[:200]}))
        return log_entry["log_id"]
    
    def get_logs(self, user_id: Optional[str] = None, action: Optional[str] = None,
                 severity: Optional[str] = None, limit: int = 100) -> List[Dict]:
        filtered = self.logs
        if user_id:
            filtered = [l for l in filtered if l["user_id"] == user_id]
        if action:
            filtered = [l for l in filtered if l["action"] == action]
        if severity:
            filtered = [l for l in filtered if l["severity"] == severity]
        return filtered[-limit:]
    
    def get_audit_report(self, days: int = 7) -> Dict:
        recent_logs = self.get_logs(limit=1000)
        if not recent_logs:
            return {"message": "No logs available"}
        action_counts = {}
        severity_counts = {}
        for log in recent_logs:
            action_counts[log["action"]] = action_counts.get(log["action"], 0) + 1
            severity_counts[log["severity"]] = severity_counts.get(log["severity"], 0) + 1
        user_counts = {}
        for log in recent_logs:
            user_counts[log["user_id"]] = user_counts.get(log["user_id"], 0) + 1
        top_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return {"total_logs": len(recent_logs), "action_counts": action_counts, "severity_counts": severity_counts, "top_users": [{"user": u[0], "actions": u[1]} for u in top_users], "report_period": f"Last {days} days"}

# Singleton instance
audit_logger = AuditLogger()