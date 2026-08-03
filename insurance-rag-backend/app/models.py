from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    use_hyde: bool = True
    use_memory: bool = True
    temperature: float = 0.7
    use_deepseek_only: bool = False  # ← ADD THIS

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    calculation_steps: Optional[List[Dict[str, Any]]] = None
    premium_data: Optional[Dict[str, Any]] = None  # ← ADD THIS
    model_used: Optional[str] = None  # ← ADD THIS

class PremiumRequest(BaseModel):
    age: int
    car_value: float
    deductible: int = 500

class PremiumResponse(BaseModel):
    monthly_premium: float
    annual_premium: float
    breakdown: Dict[str, float]

class SessionResponse(BaseModel):
    session_id: str
    title: str
    timestamp: datetime
    first_query: str