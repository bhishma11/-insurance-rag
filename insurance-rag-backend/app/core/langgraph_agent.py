import json
import re
import random
from typing import TypedDict, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.core.agent_tools import InsuranceTools
import os

# Define agent state
class InsuranceAgentState(TypedDict):
    query: str
    intent: Literal["premium", "claim_status", "claim_process", "schedule", "compare", "general"]
    tool_result: Dict[str, Any]
    answer: str
    needs_tool: bool
    messages: List[Dict]

class InsuranceAgent:
    def __init__(self, rag_search_function, llm_function):
        self.tools = InsuranceTools()
        self.rag_search = rag_search_function
        self.llm_answer = llm_function
        self.llm = ChatOpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            model="deepseek-chat",
            temperature=0.5
        )
        self.app = self._build_graph()
        self._premium_data = {}
    
    def _build_graph(self):
        workflow = StateGraph(InsuranceAgentState)
        workflow.add_node("classify_intent", self.classify_intent)
        workflow.add_node("execute_tool", self.execute_tool)
        workflow.add_node("generate_answer", self.generate_answer)
        workflow.set_entry_point("classify_intent")
        workflow.add_conditional_edges(
            "classify_intent",
            self.should_use_tool,
            {
                "use_tool": "execute_tool",
                "direct_answer": "generate_answer"
            }
        )
        workflow.add_edge("execute_tool", "generate_answer")
        workflow.add_edge("generate_answer", END)
        return workflow.compile()
    
    def classify_intent(self, state: InsuranceAgentState) -> InsuranceAgentState:
        """Use LLM to classify intent with better distinction"""
        query = state["query"]
        
        prompt = f"""You are an insurance assistant. Analyze this user question and classify it into ONE category.

User Question: "{query}"

Categories and examples:
- "premium": Asking for insurance quote, premium calculation, or cost estimate
  Examples: "Calculate my premium", "How much is insurance", "Quote for 30 year old"
  
- "claim_status": Asking to CHECK the status of an existing claim (has claim ID or asks "status")
  Examples: "Check claim status for CL-12345", "Is my claim approved?", "Status of claim CL-67890"
  
- "claim_process": Asking HOW to file a claim, what to do after an accident, or if something is covered
  Examples: "How do I claim money for motorcycle accident?", "Can I claim for car damage?", "What to do after accident?"
  
- "schedule": Wanting to schedule a callback or appointment
  Examples: "Schedule a callback", "Call me back"
  
- "compare": Asking to compare different policies
  Examples: "Compare auto and renters", "Difference between health and auto", "Compare auto, renters, and health"
  
- "general": Questions about coverage, policy details, what's covered, etc.
  Examples: "What does my auto policy cover?", "Does renters cover theft?"

IMPORTANT RULES:
- If they ask HOW to claim or what to do → classify as "claim_process" (use RAG, NOT tool)
- If they ask for claim STATUS or have CL-XXXX → classify as "claim_status" (use tool)
- If they mention motorcycle, injury, accident without CL-XXXX → classify as "claim_process"
- For comparisons with 2, 3, or 4 policies → classify as "compare"

Return ONLY the category name (premium, claim_status, claim_process, schedule, compare, general)."""
        
        try:
            response = self.llm.invoke(prompt)
            intent = response.content.strip().lower()
            valid_intents = ["premium", "claim_status", "claim_process", "schedule", "compare", "general"]
            if intent in valid_intents:
                state["intent"] = intent
                state["needs_tool"] = intent in ["premium", "claim_status", "schedule", "compare"]
                print(f"🤖 LLM Classified as: {intent}")
            else:
                state["intent"] = "general"
                state["needs_tool"] = False
        except Exception as e:
            print(f"⚠️ LLM classification failed: {e}")
            state["intent"] = "general"
            state["needs_tool"] = False
        
        return state
    
    def should_use_tool(self, state: InsuranceAgentState) -> str:
        return "use_tool" if state["needs_tool"] else "direct_answer"
    
    def execute_tool(self, state: InsuranceAgentState) -> InsuranceAgentState:
        """Execute the appropriate tool - LLM extracts parameters"""
        query = state["query"]
        intent = state["intent"]
        
        print(f"[DEBUG] Executing tool for intent: {intent}")
        
        if intent == "premium":
            print(f"[DEBUG] 🔧 Running premium calculator...")
            
            extract_prompt = f"""Extract insurance premium details from this user question:
User Question: "{query}"

Return a JSON object with:
- age: (number, default 30 if not found)
- car_value: (number in dollars, default 25000 if not found)
- coverage_type: ("basic" or "comprehensive", default "comprehensive")

Return ONLY valid JSON."""
            
            try:
                response = self.llm.invoke(extract_prompt)
                params = json.loads(response.content)
                age = params.get('age', 30)
                car_value = params.get('car_value', 25000)
                coverage_type = params.get('coverage_type', 'comprehensive')
                print(f"[DEBUG] LLM extracted: age={age}, car_value=${car_value}, coverage={coverage_type}")
            except Exception as e:
                print(f"[DEBUG] LLM extraction failed, using defaults: {e}")
                age, car_value, coverage_type = 30, 25000, "comprehensive"
            
            result = self.tools.calculate_premium(age, car_value, coverage_type)
            self._premium_data = result
            state["tool_result"] = result
            
        elif intent == "claim_status":
            print(f"[DEBUG] 🔧 Running claim checker...")
            claim_id_match = re.search(r'CL-\d+', query.upper())
            if claim_id_match:
                claim_id = claim_id_match.group()
            else:
                extract_prompt = f"""Extract the claim ID from this user question.
User Question: "{query}"

If no claim ID is found, return a random one like "CL-1234".
Return ONLY the claim ID (format: CL-XXXX)."""
                try:
                    response = self.llm.invoke(extract_prompt)
                    claim_id = response.content.strip()
                except:
                    claim_id = f"CL-{random.randint(1000, 9999)}"
            
            result = self.tools.check_claim_status(claim_id)
            state["tool_result"] = result
            
        elif intent == "claim_process":
            print(f"[DEBUG] 📚 Claim process question - using RAG")
            state["needs_tool"] = False
            state["tool_result"] = None
            
        elif intent == "schedule":
            print(f"[DEBUG] 🔧 Running callback scheduler...")
            phone_match = re.search(r'(\d{8,11})', query)
            if phone_match:
                phone = phone_match.group()
            else:
                phone = "pending"
            result = self.tools.schedule_callback(phone, "ASAP")
            state["tool_result"] = result
            
        elif intent == "compare":
            print(f"[DEBUG] 🔧 Running policy comparator...")
            compare_prompt = f"""Extract which policies to compare from this question.
User Question: "{query}"

Return a JSON array of policy types (renters, health, auto, life).
Examples: 
- ["auto", "renters"]
- ["health", "auto", "renters"]
- ["auto", "renters", "health", "life"]

If the user mentions "all policies" or "all", return ["auto", "renters", "health", "life"].

Return ONLY valid JSON."""
            
            try:
                response = self.llm.invoke(compare_prompt)
                policy_types = json.loads(response.content)
                if not isinstance(policy_types, list) or not policy_types:
                    # Try to extract from query
                    policy_types = self._extract_policies_from_query(query)
            except:
                # Fallback: extract from query
                policy_types = self._extract_policies_from_query(query)
            
            # Ensure we have at least 2 policies
            if len(policy_types) < 2:
                # Add default policies based on what's mentioned
                if "renters" in query.lower() or "health" in query.lower() or "auto" in query.lower():
                    policy_types = self._extract_policies_from_query(query)
                if len(policy_types) < 2:
                    policy_types = ["auto", "renters"]
            
            print(f"[DEBUG] Comparing policies: {policy_types}")
            result = self.tools.compare_policies(policy_types)
            state["tool_result"] = result
        
        return state
    
    def _extract_policies_from_query(self, query: str) -> list:
        """Extract policy types from query string"""
        query_lower = query.lower()
        policies = []
        if "auto" in query_lower or "car" in query_lower or "vehicle" in query_lower:
            policies.append("auto")
        if "renters" in query_lower or "rental" in query_lower or "tenant" in query_lower:
            policies.append("renters")
        if "health" in query_lower or "medical" in query_lower or "hospital" in query_lower:
            policies.append("health")
        if "life" in query_lower:
            policies.append("life")
        return policies if policies else ["auto", "renters"]
    
    def generate_answer(self, state: InsuranceAgentState) -> InsuranceAgentState:
        """Generate answer using LLM with Markdown formatting"""
        print(f"[DEBUG] Generating answer, tool_result exists: {state.get('tool_result') is not None}")
        
        if state.get("tool_result"):
            result = state["tool_result"]
            
            if "monthly_premium" in result:
                age_factor = result.get('age_factor', 1.0)
                vehicle_factor = result.get('value_factor', 1.0)
                coverage_factor = result.get('coverage_factor', 1.5)
                age = result.get('age', 30)
                car_value = result.get('car_value', 25000)
                monthly = result.get('monthly_premium', 0)
                yearly = result.get('yearly_premium', 0)
                coverage_type = result.get('coverage_type', 'comprehensive')
                
                state["answer"] = json.dumps({
                    "type": "premium_calculation",
                    "data": {
                        "monthly": monthly,
                        "yearly": yearly,
                        "breakdown": [
                            {"step": 1, "label": "Base Rate", "value": f"${500:.2f}", "description": "Standard rate for your vehicle class"},
                            {"step": 2, "label": "Age Factor", "value": f"× {age_factor:.1f}", "description": f"You're {age} years old - {'low risk' if age_factor < 1 else 'standard risk'}"},
                            {"step": 3, "label": "Vehicle Value", "value": f"× {vehicle_factor:.2f}", "description": f"Vehicle valued at ${car_value:,.2f}"},
                            {"step": 4, "label": "Coverage Type", "value": f"× {coverage_factor:.1f}", "description": f"{coverage_type.title()} coverage selected"}
                        ],
                        "summary": f"Your age ({age}) puts you in a {'low' if age_factor < 1 else 'standard'} risk category, and your vehicle value of ${car_value:,.2f} results in a premium of ${monthly:.2f}/month.",
                        "tip": "💡 Tip: Increasing your deductible could lower your monthly premium by up to 15%."
                    }
                })
                
            elif "claim_id" in result:
                state["answer"] = json.dumps({
                    "type": "claim_status",
                    "data": {
                        "claim_id": result['claim_id'],
                        "status": result['status'],
                        "estimated_payment_date": result.get('estimated_payment_date'),
                        "next_steps": result['next_steps']
                    }
                })
                
            elif "callback_id" in result:
                state["answer"] = json.dumps({
                    "type": "callback_scheduled",
                    "data": {
                        "callback_id": result['callback_id'],
                        "phone": result['phone'],
                        "scheduled_time": result['scheduled_time'],
                        "message": result['message']
                    }
                })
                
            elif "comparison" in result:
                compare_data = {}
                for policy, details in result["comparison"].items():
                    compare_data[policy] = {
                        "name": details.get('name', policy.title()),
                        "icon": details.get('icon', '📋'),
                        "deductible": details['deductible'],
                        "coverage_limit": details['coverage_limit'],
                        "monthly_premium": details.get('monthly_premium', 'N/A'),
                        "annual_premium": details.get('annual_premium', 'N/A'),
                        "key_coverages": details['key_coverages'],
                        "exclusions": details['exclusions'],
                        "best_for": details.get('best_for', ''),
                        "coverage_score": details.get('coverage_score', 0),
                        "value_score": details.get('value_score', 0),
                        "claims_process": details.get('claims_process', ''),
                        "avg_claim_time": details.get('avg_claim_time', ''),
                        "discounts": details.get('discounts', [])
                    }
                
                state["answer"] = json.dumps({
                    "type": "policy_comparison",
                    "data": {
                        "comparison": compare_data,
                        "recommendation": result.get('recommendation', ''),
                        "total_policies": result.get('total_policies', len(compare_data)),
                        "policy_types": list(compare_data.keys())
                    }
                })
                
        else:
            print(f"[DEBUG] Using RAG for query: {state['query']}")
            results, _ = self.rag_search(state["query"], k=5)
        
            context_parts = []
            for i, r in enumerate(results[:3]):
                if isinstance(r, dict):
                    text = r.get('text', '')
                    filename = r.get('filename', 'unknown')
                    context_parts.append(f"Source {i+1} ({filename}):\n{text[:600]}")
            context = "\n\n".join(context_parts)
        
            explanation_prompt = f"""You are an expert insurance claims adjuster with a warm, professional personality. Answer this user question using the policy information provided.

User Question: "{state['query']}"

Policy Information:
{context}

ADAPT YOUR RESPONSE BASED ON THE QUESTION:

1. If user says "hello", "hi", or simple greeting:
   - Keep it warm and friendly
   - Briefly introduce yourself
   - Ask what they need help with
   - 2-3 sentences max

2. If user asks a specific question (like "Does my auto policy cover windshield damage?"):
   - Provide a comprehensive, detailed answer
   - Use proper Markdown formatting with #, ##, ###
   - Include a table for coverage summary
   - Provide step-by-step next steps
   - Use emojis naturally to enhance readability

3. If user asks a broad question (like "What does my policy cover?"):
   - Give an overview of all policies
   - Highlight key coverages
   - Suggest asking specific questions for more details

GUIDELINES FOR ALL RESPONSES:
- Use ## for main sections
- Use ### for policy names
- Use **bold** for key terms and policy numbers
- Use tables with |---| for comparisons
- Use bullet points for lists
- Use numbered lists for steps
- Add emojis naturally where they enhance understanding
- Always put TWO blank lines between sections
- Be conversational and helpful, not robotic
- For specific questions, provide 4-6 paragraphs of detailed explanation

FORMAT FOR DETAILED ANSWERS:

# [Question-based Title]

## 1. Policy Analysis

### [Policy Name]

- **Insurer:** [value]
- **Vehicle:** [value]  
- **Policy Number:** [value]

**Key Finding:** [Your detailed finding here]

---

## 2. Coverage Summary

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |

---

## 3. Next Steps

1. Step one with detailed explanation
2. Step two with detailed explanation
3. Step three with detailed explanation

---

**Final Answer:** [Your detailed conclusion]

Return ONLY the formatted Markdown answer."""
        
            try:
                response = self.llm.invoke(explanation_prompt)
                answer = response.content
            except Exception as e:
                print(f"⚠️ LLM explanation failed: {e}")
                answer = self.llm_answer(state["query"])
        
            state["answer"] = json.dumps({
                "type": "rag_response",
                "data": {
                    "response": answer,
                    "sources": [{"filename": r.get('filename', 'unknown')} for r in results[:3]]
                }
            })
    
        return state

    def ask(self, query: str) -> str:
        """Process a user query through the agent"""
        initial_state = {
            "query": query,
            "intent": "general",
            "tool_result": None,
            "answer": "",
            "needs_tool": False,
            "messages": []
        }
        result = self.app.invoke(initial_state)
        return result["answer"]

    def generate_response(self, query: str, context: str, history: list = None, temperature: float = 0.7) -> dict:
        """Generate a response using the agent"""
        initial_state = {
            "query": query,
            "intent": "general",
            "tool_result": None,
            "answer": "",
            "needs_tool": False,
            "messages": history or []
        }
        result = self.app.invoke(initial_state)
        return {
            "answer": result["answer"],
            "steps": []
        }