# app/mcp/tools.py
from typing import List, Dict, Any

class MCPTools:
    """Smart MCP tool definitions with descriptions and examples"""
    
    @staticmethod
    def get_tool_definitions() -> List[Dict[str, Any]]:
        """Return all tool definitions for MCP with rich metadata"""
        return [
            {
                "name": "calculate_insurance_premium",
                "description": "Calculate auto insurance premium with detailed breakdown including monthly/yearly cost, risk category, and money-saving tips",
                "examples": [
                    "Calculate my premium for 30 year old with $35,000 car",
                    "What's my monthly premium for a 45-year-old with a $50,000 Tesla?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "age": {
                            "type": "integer",
                            "description": "Driver's age in years",
                            "minimum": 16,
                            "maximum": 100
                        },
                        "car_value": {
                            "type": "number",
                            "description": "Car value in dollars",
                            "minimum": 1000,
                            "maximum": 500000
                        },
                        "coverage_type": {
                            "type": "string",
                            "enum": ["basic", "comprehensive"],
                            "description": "Type of coverage",
                            "default": "comprehensive"
                        }
                    },
                    "required": ["age", "car_value"]
                }
            },
            {
                "name": "check_claim_status",
                "description": "Check the status of an insurance claim with detailed next steps",
                "examples": [
                    "Check claim status for CL-12345",
                    "What's the status of claim CL-67890?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "claim_id": {
                            "type": "string",
                            "description": "Claim ID (format: CL-XXXXX)",
                            "pattern": "^CL-\\d+$"
                        }
                    },
                    "required": ["claim_id"]
                }
            },
            {
                "name": "compare_insurance_policies",
                "description": "Compare different insurance policies side-by-side with coverage details, costs, and recommendations",
                "examples": [
                    "Compare auto and renters insurance",
                    "What's the difference between health and auto?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "policy_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["auto", "renters", "health", "life"]
                            },
                            "description": "List of policy types to compare",
                            "minItems": 2,
                            "maxItems": 4
                        }
                    },
                    "required": ["policy_types"]
                }
            },
            {
                "name": "get_policy_coverage",
                "description": "Get detailed coverage information for a specific policy type with explanations",
                "examples": [
                    "Does auto insurance cover windshield damage?",
                    "What does renters insurance cover?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "policy_type": {
                            "type": "string",
                            "enum": ["auto", "renters", "health", "life"],
                            "description": "Type of policy"
                        },
                        "coverage_question": {
                            "type": "string",
                            "description": "Specific question about coverage"
                        }
                    },
                    "required": ["policy_type", "coverage_question"]
                }
            },
            {
                "name": "file_claim_instructions",
                "description": "Get step-by-step instructions for filing a claim with required documents",
                "examples": [
                    "How do I file a claim for a car accident?",
                    "What do I do if I got into a motorcycle accident?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "incident_type": {
                            "type": "string",
                            "enum": ["car_accident", "theft", "fire_damage", "flood_damage", "windshield_damage", "motorcycle_accident"],
                            "description": "Type of incident"
                        },
                        "policy_type": {
                            "type": "string",
                            "enum": ["auto", "renters", "health", "life"],
                            "description": "Type of policy"
                        }
                    },
                    "required": ["incident_type", "policy_type"]
                }
            },
            {
                "name": "get_insurance_definition",
                "description": "Get clear definition of insurance terms with examples",
                "examples": [
                    "What is comprehensive coverage?",
                    "What is liability insurance?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": "Insurance term to define"
                        }
                    },
                    "required": ["term"]
                }
            },
            {
                "name": "search_policies",
                "description": "Search through all policy documents for specific information",
                "examples": [
                    "Find information about collision coverage",
                    "Search for deductibles in auto policy"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for policy documents"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5,
                            "maximum": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "schedule_callback",
                "description": "Schedule a callback from a live insurance agent",
                "examples": [
                    "I need to speak with an agent",
                    "Can someone call me about my claim?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "phone": {
                            "type": "string",
                            "description": "Phone number for callback"
                        },
                        "preferred_time": {
                            "type": "string",
                            "description": "Preferred callback time (e.g., '2pm tomorrow')"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for callback",
                            "enum": ["claim", "quote", "policy_change", "general"]
                        }
                    },
                    "required": ["phone", "preferred_time"]
                }
            },
            {
                "name": "analyze_claim_outcome",
                "description": "Predict the likely outcome of a claim based on policy details",
                "examples": [
                    "Will my claim be approved?",
                    "What's the chance my claim gets paid?"
                ],
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "claim_type": {
                            "type": "string",
                            "enum": ["car_accident", "theft", "fire_damage", "flood_damage"],
                            "description": "Type of claim"
                        },
                        "policy_type": {
                            "type": "string",
                            "enum": ["auto", "renters", "health", "life"],
                            "description": "Type of policy"
                        },
                        "details": {
                            "type": "string",
                            "description": "Additional details about the claim"
                        }
                    },
                    "required": ["claim_type", "policy_type"]
                }
            }
        ]