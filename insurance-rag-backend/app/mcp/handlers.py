# app/mcp/handlers.py
from typing import Dict, Any, Optional
from app.core.agent_tools import InsuranceTools
from app.core.smart_router import SmartRouter


class MCPHandlers:
    """Smart MCP tool handlers with enhanced responses and logging."""

    def __init__(self):
        self.router = SmartRouter()
        self.tools = InsuranceTools()
        self._vector_search = None  # ✅ Lazy loaded
        self.gateway = None  # ✅ Will be set by MCPGateway

    @property
    def vector_search(self):
        """Lazy load VectorSearch only when needed"""
        if self._vector_search is None:
            from app.core.vector_search import VectorSearch
            self._vector_search = VectorSearch()
            self._vector_search.load_index()
        return self._vector_search

    def _format_response(
        self, title: str, content: str, emoji: str = "📋"
    ) -> Dict[str, Any]:
        """Format response consistently for MCP tool output."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"{emoji} **{title}**\n\n{content}",
                }
            ]
        }

    def _format_error(self, message: str, action_hint: str = "") -> Dict[str, Any]:
        """Format error payloads consistently."""
        text = f"❌ **Error**\n\n{message}"
        if action_hint:
            text += f"\n\n{action_hint}"
        return {
            "content": [{"type": "text", "text": text}],
            "isError": True,
        }

    def _try_kaggle_first(self, query: str) -> Optional[str]:
        """Try Kaggle QLoRA first, return response if available"""
        if self.gateway:
            return self.gateway._call_kaggle_qlora(query)
        return None

    async def handle_calculate_premium(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle calculate_insurance_premium with detailed breakdown."""
        try:
            age = int(args.get("age", 0))
            car_value = float(args.get("car_value", 0.0))
            coverage_type = str(args.get("coverage_type", "comprehensive"))

            if age <= 0 or car_value <= 0:
                return self._format_error(
                    "Invalid inputs provided.",
                    "Please provide a valid age (e.g. 25) and car value (e.g. 20000).",
                )

            # ✅ Try Kaggle QLoRA first
            query = f"Calculate my premium for {age} years old with ${car_value:,.0f} car and {coverage_type} coverage"
            kaggle_response = self._try_kaggle_first(query)
            
            if kaggle_response:
                return self._format_response(
                    "Premium Calculated (Kaggle QLoRA)", kaggle_response, "💰"
                )

            # Fallback to local calculation
            result = self.tools.calculate_premium(
                age, car_value, coverage_type
            )

            risk_category = result.get("risk_category", "standard").lower()
            risk_emoji = {
                "low": "🟢",
                "standard": "🟡",
                "high": "🔴",
            }.get(risk_category, "🟡")

            monthly_premium = result.get("monthly_premium", 0.0)
            yearly_premium = result.get(
                "yearly_premium", monthly_premium * 12
            )

            response = f"""## 💰 Insurance Premium Calculation

### 📊 Monthly Premium
**${monthly_premium:.2f}**

### 📈 Yearly Premium  
**${yearly_premium:.2f}**

---

### 🔢 Calculation Breakdown

| Factor | Value | Impact |
|--------|-------|--------|
| Base Rate | ${result.get('base_rate', 0.0):.2f} | Standard rate for vehicle class |
| Age Factor | × {result.get('age_factor', 1.0):.1f} | Age: {age} years old |
| Vehicle Value | × {result.get('value_factor', 1.0):.2f} | Vehicle valued at ${car_value:,.2f} |
| Coverage Type | × {result.get('coverage_factor', 1.0):.1f} | {coverage_type.title()} coverage |

**Calculation:** ${result.get('base_rate', 0.0):.2f} × {result.get('age_factor', 1.0):.1f} × {result.get('value_factor', 1.0):.2f} × {result.get('coverage_factor', 1.0):.1f} = **${monthly_premium:.2f}**

---

### {risk_emoji} Risk Category
**{risk_category.title()} Risk**
- {age} years old
- Vehicle value: ${car_value:,.2f}
- Coverage: {coverage_type.title()}

---

### 💡 Money-Saving Tips
1. **Increase your deductible** - Higher deductible = Lower monthly premium
2. **Bundle policies** - Combine auto + home for multi-policy discount
3. **Maintain clean driving record** - Safe drivers get better rates
4. **Pay annually** - Save up to 10% by paying yearly instead of monthly

---

*Need a more specific quote? Contact a live agent for personalized rates.*"""

            return self._format_response(
                "Premium Calculated Successfully!", response, "💰"
            )

        except Exception as e:
            return self._format_error(
                f"Error calculating premium: {str(e)}",
                "Please check the age and car value and try again.",
            )

    async def handle_check_claim(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle check_claim_status with detailed status info."""
        try:
            claim_id = args.get("claim_id")
            if not claim_id:
                return self._format_error(
                    "Missing claim ID.",
                    "Please provide a valid claim ID (e.g. CL-12345).",
                )

            # ✅ Try Kaggle QLoRA first
            query = f"Check claim status for {claim_id}"
            kaggle_response = self._try_kaggle_first(query)
            
            if kaggle_response:
                return self._format_response(
                    f"Claim {claim_id} - Status (Kaggle QLoRA)", kaggle_response, "✅"
                )

            # Fallback to local tool
            result = self.tools.check_claim_status(claim_id)
            status = result.get("status", "Unknown")

            status_emoji = {
                "Approved": "✅",
                "Pending Review": "⏳",
                "Processing": "🔄",
                "Paid": "💰",
                "Denied": "❌",
            }.get(status, "📋")

            status_color = {
                "Approved": "🟢",
                "Pending Review": "🟡",
                "Processing": "🔵",
                "Paid": "🟢",
                "Denied": "🔴",
            }.get(status, "⚪")

            payment_date_section = ""
            if result.get("estimated_payment_date"):
                payment_date_section = (
                    f"### 💰 Estimated Payment Date\n"
                    f"{result['estimated_payment_date']}\n\n"
                )

            response = f"""## {status_emoji} Claim Status: {claim_id}

### Current State: {status} {status_color}

---

### 📋 Next Steps
{result.get('next_steps', 'No immediate steps required.')}

{payment_date_section}---

### 📞 Need Help?
- **Claim Hotline:** 1-800-555-0123
- **Email:** claims@insurance.ai
- **Live Chat:** Available 24/7 on our website

---

*Keep this claim ID ({claim_id}) for future reference.*"""

            return self._format_response(
                f"Claim {claim_id} - {status}", response, status_emoji
            )

        except Exception as e:
            return self._format_error(
                f"Error checking claim status: {str(e)}",
                "Please verify the claim ID format (CL-XXXXX) and try again.",
            )

    async def handle_compare_policies(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle compare_insurance_policies with rich comparison table."""
        try:
            policy_types = args.get("policy_types", [])
            if not policy_types:
                return self._format_error(
                    "No policy types provided.",
                    "Provide at least two policy types to compare (e.g., ['auto', 'renters']).",
                )

            # ✅ Try Kaggle QLoRA first
            query = f"Compare {', '.join(policy_types)} insurance policies with detailed breakdown of coverage, costs, and recommendations"
            kaggle_response = self._try_kaggle_first(query)
            
            if kaggle_response:
                return self._format_response(
                    "Policy Comparison (Kaggle QLoRA)", kaggle_response, "📊"
                )

            # Fallback to local comparison
            result = self.tools.compare_policies(policy_types)
            comparison_data = result.get("comparison", {})

            if not comparison_data:
                return self._format_error(
                    "Unable to retrieve policy comparison data."
                )

            comparison_text = "## 📊 Policy Comparison\n\n"

            # Header row
            headers = [p.title() for p in comparison_data.keys()]
            comparison_text += "| Feature | " + " | ".join(headers) + " |\n"
            comparison_text += (
                "|---------|" + "|".join(["---------"] * len(headers)) + "|\n"
            )

            # Rows
            features = [
                ("monthly_premium", "Monthly Cost"),
                ("deductible", "Deductible"),
                ("coverage_limit", "Coverage Limit"),
                ("best_for", "Best For"),
            ]

            for feat_key, feat_label in features:
                row = f"| **{feat_label}** "
                for details in comparison_data.values():
                    val = details.get(feat_key, "N/A")
                    row += f"| {val} "
                row += "|\n"
                comparison_text += row

            comparison_text += "\n### 📋 Detailed Breakdown\n\n"

            for p_type, details in comparison_data.items():
                name = details.get("name", p_type.title())
                icon = details.get("icon", "📋")

                comparison_text += f"#### {name} {icon}\n\n"
                comparison_text += f"**Monthly Premium:** {details.get('monthly_premium', 'N/A')}\n"
                comparison_text += f"**Deductible:** {details.get('deductible', 'N/A')}\n"
                comparison_text += f"**Coverage Limit:** {details.get('coverage_limit', 'N/A')}\n\n"

                coverages = details.get("key_coverages", [])
                if coverages:
                    comparison_text += "**Key Coverages:**\n"
                    for cov in coverages[:3]:
                        comparison_text += f"- ✅ {cov}\n"
                    comparison_text += "\n"

                exclusions = details.get("exclusions", [])
                if exclusions:
                    comparison_text += "**Exclusions:**\n"
                    for exc in exclusions[:2]:
                        comparison_text += f"- ❌ {exc}\n"
                    comparison_text += "\n"

            if result.get("recommendation"):
                comparison_text += (
                    f"### 💡 Recommendation\n\n{result['recommendation']}\n\n"
                )

            comparison_text += "---\n\n*Want a personalized recommendation? Contact a live agent for expert advice.*"

            return self._format_response(
                "Policy Comparison Complete", comparison_text, "📊"
            )

        except Exception as e:
            return self._format_error(
                f"Error comparing policies: {str(e)}",
                "Please try different policy types (auto, renters, health, life).",
            )

    async def handle_get_coverage(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_policy_coverage with detailed coverage info."""
        try:
            policy_type = args.get("policy_type")
            question = args.get("coverage_question")

            if not policy_type or not question:
                return self._format_error(
                    "Missing arguments.",
                    "Please specify both 'policy_type' and 'coverage_question'.",
                )

            # ✅ Try Kaggle QLoRA first
            kaggle_query = f"Does {policy_type} insurance {question}? Please provide a detailed answer with specific coverage details."
            kaggle_response = self._try_kaggle_first(kaggle_query)
            
            if kaggle_response:
                return self._format_response(
                    f"{policy_type.title()} Insurance Coverage (Kaggle QLoRA)",
                    kaggle_response,
                    "📋"
                )

            # Fallback to DeepSeek
            response, _, _ = self.router.ask(
                kaggle_query, use_deepseek_only=True
            )

            if not response:
                response = "No detailed coverage information could be retrieved at this time."

            return self._format_response(
                f"{policy_type.title()} Insurance Coverage", response, "📋"
            )

        except Exception as e:
            return self._format_error(
                f"Error getting coverage information: {str(e)}",
                "Please specify a policy type (auto, renters, health, life) and your coverage question.",
            )

    async def handle_file_claim(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file_claim_instructions with step-by-step guide."""
        try:
            incident_type = args.get("incident_type", "incident")
            policy_type = args.get("policy_type", "general")

            incident_display = incident_type.replace("_", " ").title()
            
            # ✅ Try Kaggle QLoRA first
            kaggle_query = f"Provide a detailed, step-by-step guide for filing a claim for {incident_type} with {policy_type} insurance. Include required documents, timeline, and important tips."
            kaggle_response = self._try_kaggle_first(kaggle_query)
            
            if kaggle_response:
                return self._format_response(
                    f"Filing a Claim for {incident_display} (Kaggle QLoRA)",
                    kaggle_response,
                    "📋"
                )

            # Fallback to DeepSeek
            response = self.tools._ask_deepseek(kaggle_query)
            if not response:
                response = "Instructions for filing a claim are currently unavailable. Please reach out directly to customer support."

            return self._format_response(
                f"Filing a Claim for {incident_display}", response, "📋"
            )

        except Exception as e:
            return self._format_error(
                f"Error getting claim instructions: {str(e)}",
                "Please specify the incident type and policy type.",
            )

    async def handle_get_definition(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get_insurance_definition with clear explanations."""
        try:
            term = args.get("term")
            if not term:
                return self._format_error(
                    "Missing insurance term.",
                    "Please specify the term you want defined.",
                )

            # ✅ Try Kaggle QLoRA first
            kaggle_query = f"Provide a clear, detailed definition of '{term}' in insurance terms. Include examples and why it matters to policyholders."
            kaggle_response = self._try_kaggle_first(kaggle_query)
            
            if kaggle_response:
                return self._format_response(
                    f"Insurance Term: {term.title()} (Kaggle QLoRA)",
                    kaggle_response,
                    "📖"
                )

            # Fallback to DeepSeek
            response = self.tools._ask_deepseek(kaggle_query)

            if not response:
                response = f"Could not retrieve definition for '{term}'."

            return self._format_response(
                f"Insurance Term: {term.title()}", response, "📖"
            )

        except Exception as e:
            return self._format_error(
                f"Error getting definition: {str(e)}",
                "Please specify the insurance term you want defined.",
            )

    async def handle_search_policies(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle search_policies with RAG search."""
        try:
            query = args.get("query")
            if not query:
                return self._format_error(
                    "Missing search query.",
                    "Please provide a search term (e.g. 'water damage deductible').",
                )

            limit = int(args.get("limit", 5))

            # ✅ Try Kaggle RAG first
            kaggle_result = self.gateway._call_kaggle_rag(query, limit) if self.gateway else None
            if kaggle_result and kaggle_result.get("success"):
                sources = kaggle_result.get("sources", [])
                response_text = f"""## 🔍 Policy Search Results (Kaggle RAG)

Found {len(sources)} results for: "{query}"

"""
                for i, source in enumerate(sources, 1):
                    response_text += f"""### {i}. {source.get('instruction', 'Unknown Question')}
**Similarity:** {source.get('similarity', 0):.0%}

{source.get('response', '')}

---
"""
                return self._format_response(
                    "Policy Search Results", response_text, "🔍"
                )

            # Fallback to local vector search
            results, scores = self.vector_search.hybrid_search(
                query, k=limit
            )

            if not results:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f'🔍 **No results found**\n\nCould not find any policy information matching: "{query}"\n\nTry rephrasing your search or using broader terms.',
                        }
                    ]
                }

            response = f'## 🔍 Policy Search Results\n\nFound {len(results)} results for: "{query}"\n\n'

            for i, result in enumerate(results):
                filename = result.get("filename", "Unknown Document")
                text = result.get("text", "")[:300]
                score = scores[i] if i < len(scores) else 0.0

                response += f"### {i + 1}. {filename}\n"
                response += f"**Relevance:** {score:.0%}\n\n"
                response += f"{text}...\n\n"
                response += "---\n\n"

            response += "*Need more details? Ask a specific question about any of these policies.*"

            return self._format_response(
                "Policy Search Results", response, "🔍"
            )

        except Exception as e:
            return self._format_error(
                f"Error searching policies: {str(e)}",
                "Please try a different search query.",
            )

    async def handle_schedule_callback(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle schedule_callback with confirmation."""
        try:
            phone = args.get("phone")
            preferred_time = args.get("preferred_time")
            reason = args.get("reason", "general")

            if not phone or not preferred_time:
                return self._format_error(
                    "Missing contact information.",
                    "Please provide a phone number and a preferred time for the callback.",
                )

            # ✅ Try Kaggle QLoRA first
            kaggle_query = f"Schedule a callback for {phone} at {preferred_time} for {reason} insurance"
            kaggle_response = self._try_kaggle_first(kaggle_query)
            
            if kaggle_response:
                return self._format_response(
                    "Callback Scheduled (Kaggle QLoRA)", kaggle_response, "📞"
                )

            # Fallback to local scheduling
            result = self.tools.schedule_callback(phone, preferred_time)
            callback_id = result.get("callback_id", "CB-UNKNOWN")

            response = f"""## 📞 Callback Scheduled!

### ✅ Confirmation
**Callback ID:** {callback_id}

### 📋 Details
- **Phone:** {phone}
- **Time:** {preferred_time}
- **Reason:** {reason.title()}

### 📱 What Happens Next
1. An agent will call you at the scheduled time
2. Have your policy number ready
3. Prepare any questions you have

### 💡 Tips
- Keep your phone nearby
- Add our number to your contacts: 1-800-555-0123
- If you need to reschedule, call 1-800-555-0123

---

*Reference ID: {callback_id}*"""

            return self._format_response(
                "Callback Scheduled Successfully!", response, "📞"
            )

        except Exception as e:
            return self._format_error(
                f"Error scheduling callback: {str(e)}",
                "Please provide a valid phone number and preferred time.",
            )

    async def handle_analyze_claim(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle analyze_claim_outcome with predictive analysis."""
        try:
            claim_type = args.get("claim_type")
            policy_type = args.get("policy_type")
            details = args.get("details", "")

            if not claim_type or not policy_type:
                return self._format_error(
                    "Missing claim details.",
                    "Please provide both 'claim_type' and 'policy_type'.",
                )

            # ✅ Try Kaggle QLoRA first
            kaggle_query = f"""Analyze this claim and predict the likely outcome:

Claim Type: {claim_type}
Policy Type: {policy_type}
Details: {details}

Provide:
1. **Likelihood of Approval** (percentage)
2. **Key Factors** that will influence the decision
3. **Potential Issues** to watch out for
4. **Recommended Actions** to improve chances

Be realistic and helpful."""
            
            kaggle_response = self._try_kaggle_first(kaggle_query)
            
            if kaggle_response:
                return self._format_response(
                    "Claim Outcome Analysis (Kaggle QLoRA)", kaggle_response, "🔮"
                )

            # Fallback to DeepSeek
            response = self.tools._ask_deepseek(kaggle_query)
            if not response:
                response = "Unable to complete predictive analysis for this claim at present."

            return self._format_response(
                "Claim Outcome Analysis", response, "🔮"
            )

        except Exception as e:
            return self._format_error(
                f"Error analyzing claim: {str(e)}",
                "Please provide the claim type, policy type, and details.",
            )