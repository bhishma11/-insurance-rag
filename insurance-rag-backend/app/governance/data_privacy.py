# app/governance/data_privacy.py
"""
AI Governance: Data Privacy & PII Protection
"""
import re
from typing import Dict, List
from datetime import datetime
import hashlib

class DataPrivacy:
    """Data privacy controls for AI governance"""
    
    PII_PATTERNS = {
        "email": {"pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "sensitivity": "HIGH", "mask": "[EMAIL_REDACTED]"},
        "phone": {"pattern": r'\b(\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b', "sensitivity": "HIGH", "mask": "[PHONE_REDACTED]"},
        "ssn": {"pattern": r'\b\d{3}-\d{2}-\d{4}\b', "sensitivity": "CRITICAL", "mask": "[SSN_REDACTED]"},
        "credit_card": {"pattern": r'\b(?:\d{4}[- ]?){3}\d{4}\b', "sensitivity": "CRITICAL", "mask": "[CC_REDACTED]"}
    }
    
    def __init__(self):
        self.pii_detection_log = []
    
    def detect_pii(self, text: str) -> Dict:
        detected = {"has_pii": False, "total_pii_count": 0, "critical_count": 0, "items": [], "risk_level": "LOW"}
        for pii_type, config in self.PII_PATTERNS.items():
            matches = re.findall(config["pattern"], text, re.IGNORECASE)
            if matches:
                detected["has_pii"] = True
                detected["total_pii_count"] += len(matches)
                if config["sensitivity"] in ["HIGH", "CRITICAL"]:
                    detected["critical_count"] += len(matches)
                detected["items"].append({"type": pii_type, "count": len(matches), "sensitivity": config["sensitivity"], "sample": matches[0] if matches else ""})
        if detected["critical_count"] > 0:
            detected["risk_level"] = "CRITICAL"
        elif detected["total_pii_count"] > 5:
            detected["risk_level"] = "HIGH"
        elif detected["total_pii_count"] > 0:
            detected["risk_level"] = "MEDIUM"
        self._log_pii_detection(detected)
        return detected
    
    def redact_pii(self, text: str, mask_level: str = "HIGH") -> str:
        redacted = text
        sensitivity_levels = {"LOW": ["LOW"], "HIGH": ["MEDIUM", "HIGH"], "CRITICAL": ["CRITICAL"]}
        for pii_type, config in self.PII_PATTERNS.items():
            if config["sensitivity"] in sensitivity_levels.get(mask_level, ["HIGH", "CRITICAL"]):
                redacted = re.sub(config["pattern"], config["mask"], redacted, flags=re.IGNORECASE)
        return redacted
    
    def _log_pii_detection(self, detection: Dict):
        self.pii_detection_log.append({"timestamp": datetime.now().isoformat(), "detection": detection})
        if len(self.pii_detection_log) > 1000:
            self.pii_detection_log = self.pii_detection_log[-1000:]
    
    def get_privacy_report(self) -> Dict:
        if not self.pii_detection_log:
            return {"message": "No privacy checks performed"}
        total_checks = len(self.pii_detection_log)
        pii_detected = sum(1 for l in self.pii_detection_log if l["detection"]["has_pii"])
        return {"total_checks": total_checks, "pii_detected_percentage": (pii_detected / total_checks * 100) if total_checks > 0 else 0, "critical_incidents": sum(1 for l in self.pii_detection_log if l["detection"]["risk_level"] == "CRITICAL"), "avg_pii_per_request": sum(l["detection"]["total_pii_count"] for l in self.pii_detection_log) / total_checks if total_checks > 0 else 0}

# Singleton instance
data_privacy = DataPrivacy()