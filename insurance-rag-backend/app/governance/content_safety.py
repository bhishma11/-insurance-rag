"""
AI Governance: Content Safety, Guardrails, and Responsible AI
"""

import re
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

class SafetySeverity(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ContentSafety:
    """
    Multi-layer content safety for AI inputs and outputs
    Implements responsible AI principles
    """
    
    # ✅ HARD-CODED BLOCK LIST - ALWAYS BLOCKS THESE
    BLOCKED_PHRASES = [
        "hate everyone",
        "hate all",
        "kill you",
        "kill all",
        "hurt you",
        "hurt all",
        "attack you",
        "attack all",
        "stupid and dumb",
        "drop table",
        "delete from",
        "insert into",
        "update set",
        "exec ",
        "alter table",
        "threaten you",
        "abuse you",
        "bully you",
        "i hate",
        "i want to kill",
        "you are stupid",
        "you are dumb",
        "everyone should die",
        "kill yourself",
        "die you",
        "death to"
    ]
    
    def __init__(self):
        self.content_filter_results = []
        self.safety_threshold = 70
    
    def analyze_input(self, text: str, user_id: str = "anonymous") -> Dict:
        """Analyze user input for safety violations"""
        text_lower = text.lower()
        
        # ✅ FIRST: Check hard-coded block list
        blocked = False
        violations = []
        
        for phrase in self.BLOCKED_PHRASES:
            if phrase in text_lower:
                blocked = True
                violations.append({
                    "category": "blocked_content",
                    "severity": "CRITICAL",
                    "details": f"Contains blocked phrase: '{phrase}'"
                })
                break  # Stop checking once blocked
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "text_preview": text[:100],
            "safety_score": 100,
            "violations": violations,
            "blocked": blocked,
            "requires_review": False,
            "categories": {
                "hate_speech": self._check_hate_speech(text),
                "harassment": self._check_harassment(text),
                "pii_detected": self._check_pii(text),
                "injection_attempt": self._check_injection(text),
                "financial_scam": self._check_financial_scam(text)
            }
        }
        
        # Calculate safety score from category checks
        for category, result in assessment["categories"].items():
            if result["detected"]:
                assessment["safety_score"] -= result["severity_score"]
                assessment["violations"].append({
                    "category": category,
                    "severity": result["severity"],
                    "details": result["details"]
                })
                if result["severity"] in ["HIGH", "CRITICAL"]:
                    assessment["blocked"] = True
        
        # ✅ Force block if any BLOCKED_PHRASE was found
        if blocked:
            assessment["safety_score"] = 0
            assessment["blocked"] = True
        
        assessment["requires_review"] = 50 <= assessment["safety_score"] < 70
        
        self._log_safety_check(assessment)
        return assessment
    
    def analyze_output(self, text: str, user_id: str = "anonymous") -> Dict:
        """Analyze AI output before sending to user"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "text_preview": text[:100],
            "safety_score": 100,
            "violations": [],
            "blocked": False,
            "requires_review": False,
            "categories": {
                "medical_disclaimer": self._check_medical_advice(text),
                "legal_disclaimer": self._check_legal_advice(text),
                "hallucination_risk": self._check_hallucination_risk(text),
                "pii_leak": self._check_pii(text),
                "misinformation": self._check_misinformation(text)
            }
        }
        
        for category, result in assessment["categories"].items():
            if result["detected"]:
                assessment["safety_score"] -= result["severity_score"]
                assessment["violations"].append({
                    "category": category,
                    "severity": result["severity"],
                    "details": result["details"]
                })
        
        assessment["blocked"] = assessment["safety_score"] < 50
        self._log_safety_check(assessment, "output")
        return assessment
    
    def _check_hate_speech(self, text: str) -> Dict:
        explicit_hate = [
            r'\b(hate speech|racist|sexist|homophobic|transphobic)\b',
            r'\b(slur|discriminate|bigot|supremacist)\b',
            r'\b(kill all|hurt all|attack all)\s+\w+\b'
        ]
        detected = any(re.search(p, text.lower()) for p in explicit_hate)
        return {
            "detected": detected,
            "severity": "HIGH" if detected else "NONE",
            "severity_score": 40 if detected else 0,
            "details": "Explicit hate speech detected" if detected else "Safe"
        }
    
    def _check_harassment(self, text: str) -> Dict:
        explicit_harassment = [
            r'\b(threat|attack|harm|kill|hurt|abuse)\s+(you|your|me|us)\b',
            r'\b(stalk|bully|intimidate|menace)\s+(you|your)\b'
        ]
        detected = any(re.search(p, text.lower()) for p in explicit_harassment)
        return {
            "detected": detected,
            "severity": "HIGH" if detected else "NONE",
            "severity_score": 30 if detected else 0,
            "details": "Harassment detected" if detected else "Safe"
        }
    
    def _check_pii(self, text: str) -> Dict:
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+?\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b(?:\d{4}[- ]?){3}\d{4}\b'
        }
        detected_pii = []
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected_pii.append(pii_type)
        return {
            "detected": len(detected_pii) > 0,
            "severity": "MEDIUM" if detected_pii else "NONE",
            "severity_score": 15 if detected_pii else 0,
            "details": f"PII detected: {', '.join(detected_pii)}" if detected_pii else "No PII"
        }
    
    def _check_injection(self, text: str) -> Dict:
        injection_patterns = [
            r'\b(DROP\s+TABLE|DELETE\s+FROM|INSERT\s+INTO|UPDATE\s+SET|EXEC\s+|ALTER\s+TABLE)\b',
            r"'\s*OR\s*'1'\s*=\s*'1"
        ]
        detected = any(re.search(p, text, re.IGNORECASE) for p in injection_patterns)
        return {
            "detected": detected,
            "severity": "CRITICAL" if detected else "NONE",
            "severity_score": 50 if detected else 0,
            "details": "Potential injection attack detected" if detected else "Safe"
        }
    
    def _check_financial_scam(self, text: str) -> Dict:
        scam_patterns = [
            r'\b(credit card|bank account|wire transfer|investment opportunity)\b',
            r'\b(guaranteed|risk-free|limited time|act now)\b'
        ]
        detected = any(re.search(p, text.lower()) for p in scam_patterns)
        return {
            "detected": detected,
            "severity": "LOW" if detected else "NONE",
            "severity_score": 5 if detected else 0,
            "details": "Potential financial scam detected" if detected else "Safe"
        }
    
    def _check_medical_advice(self, text: str) -> Dict:
        medical_patterns = [
            r'\b(diagnosis|treatment|cure|heal|remedy)\s+(you|your|for)\b',
            r'\b(medication|prescription|dosage|side effect)\s+(you|your)\b'
        ]
        detected = any(re.search(p, text.lower()) for p in medical_patterns)
        return {
            "detected": detected,
            "severity": "LOW" if detected else "NONE",
            "severity_score": 5 if detected else 0,
            "details": "Medical advice - ensure disclaimer present" if detected else "Safe"
        }
    
    def _check_legal_advice(self, text: str) -> Dict:
        legal_patterns = [
            r'\b(legal|attorney|lawyer|court|lawsuit|settlement)\s+(you|your|for)\b',
            r'\b(contract|agreement|liability|indemnify)\s+(you|your)\b'
        ]
        detected = any(re.search(p, text.lower()) for p in legal_patterns)
        return {
            "detected": detected,
            "severity": "LOW" if detected else "NONE",
            "severity_score": 5 if detected else 0,
            "details": "Legal advice - ensure disclaimer present" if detected else "Safe"
        }
    
    def _check_hallucination_risk(self, text: str) -> Dict:
        hallucination_patterns = [
            r'\b(always|never|100%|guaranteed|definitely)\s+(you|your|this|that)\b'
        ]
        detected = any(re.search(p, text.lower()) for p in hallucination_patterns)
        return {
            "detected": detected,
            "severity": "LOW" if detected else "NONE",
            "severity_score": 5 if detected else 0,
            "details": "Potential overconfidence - verify facts" if detected else "Safe"
        }
    
    def _check_misinformation(self, text: str) -> Dict:
        misinformation_patterns = [
            r'\b(fake|false|incorrect|misleading|rumor)\s+(news|information|claim|statement)\b',
            r'\b(conspiracy|cover-up)\s+(theory|about)\b'
        ]
        detected = any(re.search(p, text.lower()) for p in misinformation_patterns)
        return {
            "detected": detected,
            "severity": "MEDIUM" if detected else "NONE",
            "severity_score": 10 if detected else 0,
            "details": "Potential misinformation detected" if detected else "Safe"
        }
    
    def _log_safety_check(self, assessment: Dict, check_type: str = "input"):
        self.content_filter_results.append({
            "type": check_type,
            "assessment": assessment
        })
        if len(self.content_filter_results) > 1000:
            self.content_filter_results = self.content_filter_results[-1000:]
    
    def get_safety_report(self) -> Dict:
        total_checks = len(self.content_filter_results)
        if total_checks == 0:
            return {"message": "No safety checks performed yet"}
        blocked = sum(1 for r in self.content_filter_results if r["assessment"].get("blocked", False))
        reviews = sum(1 for r in self.content_filter_results if r["assessment"].get("requires_review", False))
        return {
            "total_checks": total_checks,
            "blocked_percentage": (blocked / total_checks * 100) if total_checks > 0 else 0,
            "review_required_percentage": (reviews / total_checks * 100) if total_checks > 0 else 0,
            "safety_score_avg": sum(r["assessment"].get("safety_score", 100) for r in self.content_filter_results) / total_checks if total_checks > 0 else 100
        }

# Singleton instance
content_safety = ContentSafety()