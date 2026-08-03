# app/governance/explainability.py
"""
AI Governance: Explainability & Transparency
"""
from typing import Dict, List
from datetime import datetime

class Explainability:
    """Provides explanations for AI decisions"""
    
    def __init__(self):
        self.explanation_history = []
    
    def explain_premium_calculation(self, age: int, car_value: float, result: Dict) -> Dict:
        explanation = {"timestamp": datetime.now().isoformat(), "type": "premium_calculation", "inputs": {"age": age, "car_value": car_value}, "output": result, "reasoning": self._get_premium_reasoning(age, car_value, result), "factors": self._get_premium_factors(age, car_value), "confidence_score": 0.85}
        self._log_explanation(explanation)
        return explanation
    
    def _get_premium_reasoning(self, age: int, car_value: float, result: Dict) -> str:
        risk = "low" if age < 60 else "standard"
        return f"Age ({age}): {risk} risk. Car value (${car_value:,}): {(car_value/20000):.1f}x factor. Monthly premium: ${result.get('monthly_premium', 0):.2f}"
    
    def _get_premium_factors(self, age: int, car_value: float) -> List[Dict]:
        return [{"factor": "Age", "value": age, "impact": "Low risk" if age < 60 else "Standard risk", "weight": 0.3}, {"factor": "Car Value", "value": car_value, "impact": f"{(car_value/20000):.1f}x multiplier", "weight": 0.4}, {"factor": "Coverage Type", "value": "Comprehensive", "impact": "1.5x multiplier", "weight": 0.3}]
    
    def _log_explanation(self, explanation: Dict):
        self.explanation_history.append(explanation)
        if len(self.explanation_history) > 1000:
            self.explanation_history = self.explanation_history[-1000:]
    
    def get_explainability_report(self) -> Dict:
        if not self.explanation_history:
            return {"message": "No explanations generated"}
        return {"total_explanations": len(self.explanation_history), "types": {"premium_calculation": sum(1 for e in self.explanation_history if e["type"] == "premium_calculation"), "claim_status": sum(1 for e in self.explanation_history if e["type"] == "claim_status"), "policy_recommendation": sum(1 for e in self.explanation_history if e["type"] == "policy_recommendation")}, "avg_confidence": sum(e.get("confidence_score", 0) for e in self.explanation_history) / len(self.explanation_history) if self.explanation_history else 0}

# Singleton instance
explainability = Explainability()