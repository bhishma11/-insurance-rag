import random
from datetime import datetime, timedelta
import time
from app.core.langsmith_tracer import get_tracer

class InsuranceTools:
    """Collection of tools for the insurance agent - returns raw data, not HTML"""
    
    @staticmethod
    def calculate_premium(age: int, car_value: float, coverage_type: str = "comprehensive") -> dict:
        """Calculate auto insurance premium based on driver age and car value"""
        tracer = get_tracer()
        start_time = time.time()
        
        inputs = {
            "age": age,
            "car_value": car_value,
            "coverage_type": coverage_type
        }
        
        try:
            # Base calculation
            base_rate = 500
            age_factor = 1.2 if age < 25 else 0.8 if age < 60 else 1.3
            value_factor = car_value / 20000
            coverage_factor = 1.0 if coverage_type == "basic" else 1.5
            
            monthly = base_rate * age_factor * value_factor * coverage_factor
            yearly = monthly * 12
            
            result = {
                "monthly_premium": round(monthly, 2),
                "yearly_premium": round(yearly, 2),
                "age": age,
                "car_value": car_value,
                "coverage_type": coverage_type,
                "age_factor": age_factor,
                "value_factor": value_factor,
                "coverage_factor": coverage_factor,
                "base_rate": base_rate
            }
            
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("calculate_premium", inputs, result, latency_ms)
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("calculate_premium", inputs, {"error": str(e)}, latency_ms)
            raise
    
    @staticmethod
    def check_claim_status(claim_id: str) -> dict:
        """Check status of an existing claim"""
        tracer = get_tracer()
        start_time = time.time()
        
        inputs = {"claim_id": claim_id}
        
        try:
            statuses = ["Approved", "Pending Review", "Processing", "Paid", "Denied"]
            weights = [0.3, 0.3, 0.2, 0.1, 0.1]
            status = random.choices(statuses, weights=weights)[0]
            
            payment_date = None
            next_steps = ""
            
            if status == "Approved":
                payment_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                next_steps = "Payment will be processed within 7 days"
            elif status == "Pending Review":
                next_steps = "Additional documentation may be required"
            elif status == "Processing":
                next_steps = "Claim is being reviewed by adjuster"
            elif status == "Paid":
                payment_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
                next_steps = "Payment has been issued"
            else:
                next_steps = "Appeal process available within 30 days"
            
            result = {
                "claim_id": claim_id,
                "status": status,
                "estimated_payment_date": payment_date,
                "next_steps": next_steps
            }
            
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("check_claim_status", inputs, result, latency_ms)
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("check_claim_status", inputs, {"error": str(e)}, latency_ms)
            raise
    
    @staticmethod
    def schedule_callback(phone: str, preferred_time: str) -> dict:
        """Schedule a callback from an insurance agent"""
        tracer = get_tracer()
        start_time = time.time()
        
        inputs = {
            "phone": phone,
            "preferred_time": preferred_time
        }
        
        try:
            callback_id = f"CB-{random.randint(10000, 99999)}"
            
            result = {
                "callback_id": callback_id,
                "phone": phone,
                "scheduled_time": preferred_time,
                "message": f"Callback scheduled for {preferred_time}. Agent will call {phone}"
            }
            
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("schedule_callback", inputs, result, latency_ms)
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("schedule_callback", inputs, {"error": str(e)}, latency_ms)
            raise
    
    @staticmethod
    def compare_policies(policy_types: list) -> dict:
        """Compare different policy types side-by-side with detailed metrics
        
        Supports 2, 3, or 4 policies at once.
        """
        tracer = get_tracer()
        start_time = time.time()
        
        inputs = {"policy_types": policy_types}
        
        try:
            # Comprehensive policy data with detailed comparison metrics
            policy_data = {
                "renters": {
                    "name": "Renters Insurance",
                    "icon": "🏠",
                    "deductible": "$500",
                    "coverage_limit": "$20,000",
                    "monthly_premium": "$30",
                    "annual_premium": "$360",
                    "key_coverages": [
                        "Personal property theft",
                        "Fire damage",
                        "Vandalism",
                        "Water damage (burst pipes)",
                        "Liability protection",
                        "Loss of use (hotel costs)"
                    ],
                    "exclusions": [
                        "Flood damage",
                        "Earthquake",
                        "Roommate's property",
                        "Business equipment",
                        "Vehicle damage",
                        "Intentional damage"
                    ],
                    "best_for": "Renters and tenants",
                    "coverage_score": 7,
                    "value_score": 8,
                    "claims_process": "File online or via app",
                    "avg_claim_time": "3-5 business days",
                    "discounts": ["Multi-policy", "Safety devices", "No claims"]
                },
                "health": {
                    "name": "Health Insurance",
                    "icon": "🏥",
                    "deductible": "$1,500",
                    "coverage_limit": "$5,000 out-of-pocket max",
                    "monthly_premium": "$450",
                    "annual_premium": "$5,400",
                    "key_coverages": [
                        "Hospitalization (80%)",
                        "ER visits ($150 copay)",
                        "Therapy ($30 copay)",
                        "Prescription drugs",
                        "Preventive care",
                        "Specialist visits"
                    ],
                    "exclusions": [
                        "Cosmetic surgery",
                        "Experimental treatments",
                        "Dental (separate plan)",
                        "Vision (separate plan)",
                        "Alternative medicine",
                        "Elective procedures"
                    ],
                    "best_for": "Individuals and families",
                    "coverage_score": 8,
                    "value_score": 7,
                    "claims_process": "Contact provider or use app",
                    "avg_claim_time": "5-10 business days",
                    "discounts": ["Wellness programs", "Non-smoker", "Annual checkup"]
                },
                "auto": {
                    "name": "Auto Insurance",
                    "icon": "🚗",
                    "deductible": "$1,000 (collision) / $500 (comprehensive)",
                    "coverage_limit": "$250,000/$500,000 liability",
                    "monthly_premium": "$150",
                    "annual_premium": "$1,800",
                    "key_coverages": [
                        "Collision damage",
                        "Comprehensive coverage",
                        "Uninsured motorist",
                        "Glass ($0 deductible)",
                        "Roadside assistance",
                        "Rental car reimbursement"
                    ],
                    "exclusions": [
                        "Wear and tear",
                        "Mechanical breakdown",
                        "Commercial use",
                        "Intentional damage",
                        "Racing",
                        "Normal maintenance"
                    ],
                    "best_for": "Vehicle owners",
                    "coverage_score": 9,
                    "value_score": 8,
                    "claims_process": "Call hotline or use mobile app",
                    "avg_claim_time": "2-4 business days",
                    "discounts": ["Safe driver", "Good student", "Multiple vehicles"]
                },
                "life": {
                    "name": "Life Insurance",
                    "icon": "🛡️",
                    "deductible": "N/A",
                    "coverage_limit": "$500,000+",
                    "monthly_premium": "$50",
                    "annual_premium": "$600",
                    "key_coverages": [
                        "Death benefit",
                        "Accidental death",
                        "Critical illness rider",
                        "Disability rider",
                        "Term life (10-30 years)",
                        "Whole life (permanent)"
                    ],
                    "exclusions": [
                        "Suicide (first 2 years)",
                        "High-risk activities",
                        "Pre-existing conditions (some)",
                        "Act of war",
                        "Criminal activity"
                    ],
                    "best_for": "Individuals with dependents",
                    "coverage_score": 9,
                    "value_score": 7,
                    "claims_process": "Submit claim with death certificate",
                    "avg_claim_time": "10-14 business days",
                    "discounts": ["Non-smoker", "Healthy lifestyle", "Annual payment"]
                }
            }
            
            # Build comparison result - include ALL requested policies
            comparison = {}
            for ptype in policy_types:
                ptype_lower = ptype.lower()
                if ptype_lower in policy_data:
                    comparison[ptype_lower] = policy_data[ptype_lower]
                else:
                    # Handle unknown policy type with default
                    comparison[ptype_lower] = {
                        "name": f"{ptype.title()} Insurance",
                        "icon": "📋",
                        "deductible": "Varies",
                        "coverage_limit": "Varies",
                        "monthly_premium": "Varies",
                        "annual_premium": "Varies",
                        "key_coverages": ["Contact provider for details"],
                        "exclusions": ["Contact provider for details"],
                        "best_for": "Contact provider",
                        "coverage_score": 5,
                        "value_score": 5,
                        "claims_process": "Contact provider",
                        "avg_claim_time": "Varies",
                        "discounts": ["Contact provider"]
                    }

            # Generate smart recommendation based on policies compared
            recommendation = ""
            if len(comparison) >= 2:
                # Find the best policy based on combined score
                best_policy = max(
                    comparison.items(),
                    key=lambda x: x[1].get('coverage_score', 0) + x[1].get('value_score', 0)
                )
                best_name = best_policy[1].get('name', best_policy[0].title())
                best_score = best_policy[1].get('coverage_score', 0) + best_policy[1].get('value_score', 0)

                # Build recommendation based on number of policies
                if len(comparison) == 2:
                    recommendation = f"**{best_name}** offers the best value with a combined score of {best_score}/20. "
                    recommendation += f"Monthly premium starts at {best_policy[1].get('monthly_premium', '$0')} "
                    recommendation += f"with {best_policy[1].get('coverage_limit', 'customizable')} coverage limit."

                    # Add specific advice based on policy type
                    advice_map = {
                        "auto": " Great for vehicle owners who need comprehensive protection.",
                        "health": " Excellent for individuals and families needing medical coverage.",
                        "renters": " Ideal for tenants protecting personal belongings.",
                        "life": " Essential for those with dependents or financial obligations."
                    }
                    recommendation += advice_map.get(best_policy[0], "")

                elif len(comparison) == 3:
                    recommendation = f"**{best_name}** is the top choice with {best_score}/20 combined score. "
                    recommendation += f"Monthly premium starts at {best_policy[1].get('monthly_premium', '$0')}.\n\n"
                    recommendation += "**Comparison Summary:**\n"
                    for ptype, details in comparison.items():
                        score = details.get('coverage_score', 0) + details.get('value_score', 0)
                        recommendation += f"- **{details.get('name', ptype.title())}**: {score}/20 score, {details.get('monthly_premium', 'N/A')}/month\n"
                    recommendation += "\n**Recommendation:** Choose based on your primary needs. Consider bundling for better value."

                else:  # 4 or more policies
                    recommendation = f"**{best_name}** is the best overall with {best_score}/20.\n\n"
                    recommendation += "**Quick Comparison:**\n"
                    for ptype, details in comparison.items():
                        score = details.get('coverage_score', 0) + details.get('value_score', 0)
                        recommendation += f"- **{details.get('name', ptype.title())}**: {score}/20\n"
                    recommendation += "\n**Tip:** Consider your specific needs and budget when choosing."

            output = {
                "comparison": comparison,
                "recommendation": recommendation,
                "total_policies": len(comparison),
                "policy_types": list(comparison.keys())
            }

            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("compare_policies", inputs, output, latency_ms)

            return output

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            if tracer.available:
                tracer.trace_tool_call("compare_policies", inputs, {"error": str(e)}, latency_ms)
            raise
    
    @staticmethod
    def get_all_tools() -> list:
        """Return list of available tools with descriptions"""
        return [
            {
                "name": "calculate_premium",
                "description": "Calculate auto insurance premium based on age, car value, and coverage type",
                "parameters": ["age (int)", "car_value (float)", "coverage_type (str: basic/comprehensive)"]
            },
            {
                "name": "check_claim_status",
                "description": "Check the status of a claim using claim ID",
                "parameters": ["claim_id (str)"]
            },
            {
                "name": "schedule_callback",
                "description": "Schedule a callback from an insurance agent",
                "parameters": ["phone (str)", "preferred_time (str)"]
            },
            {
                "name": "compare_policies",
                "description": "Compare different insurance policies side-by-side with detailed metrics",
                "parameters": ["policy_types (list: renters, health, auto, life)"]
            }
        ]