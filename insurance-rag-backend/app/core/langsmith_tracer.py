# src/langsmith_tracer.py
"""
LangSmith Tracing Integration for RAG Pipeline
Monitors and traces all RAG operations
"""

import os
from langsmith import Client
from langsmith.run_helpers import traceable
from datetime import datetime

class LangSmithTracer:
    def __init__(self):
        """Initialize LangSmith client"""
        self.api_key = os.getenv('LANGSMITH_API_KEY')
        self.project = os.getenv('LANGSMITH_PROJECT', 'lemonade-ai-prod')
        
        if self.api_key:
            try:
                self.client = Client(api_key=self.api_key)
                self.available = True
                print(f"✅ LangSmith initialized - Project: {self.project}")
                print(f"📊 Dashboard: https://smith.langchain.com/projects/{self.project}")
            except Exception as e:
                print(f"⚠️ LangSmith init error: {e}")
                self.available = False
                self.client = None
        else:
            self.available = False
            self.client = None
            print("⚠️ LangSmith not configured - add LANGSMITH_API_KEY to .env")
    
    @traceable(run_type="retriever")
    def trace_search(self, query: str, results: list, scores: list, latency_ms: float):
        """
        Trace hybrid search operation - uses @traceable decorator
        """
        if not self.available:
            return
        # The @traceable decorator automatically handles the tracing
        # Return the results so the decorator can capture them
        return {
            "query": query,
            "num_results": len(results),
            "top_score": scores[0] if scores else 0,
            "latency_ms": latency_ms
        }
    
    @traceable(run_type="tool")
    def trace_tool_call(self, tool_name: str, inputs: dict, outputs: dict, latency_ms: float):
        """
        Trace agent tool calls - uses @traceable decorator
        """
        if not self.available:
            return
        # The @traceable decorator automatically handles the tracing
        return {
            "tool": tool_name,
            "inputs": inputs,
            "outputs": outputs,
            "latency_ms": latency_ms
        }
    
    @traceable(run_type="chain")
    def trace_rag_query(self, query: str, answer: str, contexts: list, latency_ms: float):
        """
        Trace a complete RAG query - uses @traceable decorator
        """
        if not self.available:
            return answer
        
        # The @traceable decorator automatically captures inputs/outputs
        # We just need to return the answer
        return answer
    
    def get_trace_url(self) -> str:
        """Get URL to view traces in LangSmith"""
        if not self.available:
            return ""
        return f"https://smith.langchain.com/projects/{self.project}?time_interval=7d"

# Singleton instance
_tracer_instance = None

def get_tracer() -> LangSmithTracer:
    """Get or create LangSmith tracer singleton"""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = LangSmithTracer()
    return _tracer_instance
