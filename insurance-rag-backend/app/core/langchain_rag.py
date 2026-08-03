# src/langchain_rag.py
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from app.core.langsmith_tracer import get_tracer
import os
import time

class SimpleMemory:
    """Simple conversation memory"""
    def __init__(self):
        self.chat_history = []
    
    def add_user_message(self, message: str):
        self.chat_history.append(("user", message))
    
    def add_ai_message(self, message: str):
        self.chat_history.append(("ai", message))
    
    def get_history(self, limit: int = 6):
        return self.chat_history[-limit:] if self.chat_history else []
    
    def clear(self):
        self.chat_history = []

class LangChainRAG:
    def __init__(self, hybrid_search):
        self.hybrid_search = hybrid_search
        self.memory = SimpleMemory()
        
        # Get tracer (don't use property setter)
        self._tracer = get_tracer()
        
        # Initialize DeepSeek via OpenAI-compatible API
        self.llm = ChatOpenAI(
            base_url="https://api.deepseek.com",
            api_key=os.getenv('DEEPSEEK_API_KEY'),
            model="deepseek-chat",
            temperature=0.3
        )
        
        if self._tracer.available:
            print("✅ LangChain RAG with LangSmith tracing available")
        else:
            print("⚠️ LangChain RAG running without tracing")
    
    @property
    def tracer(self):
        """Get tracer instance"""
        return self._tracer
    
    def ask(self, question: str) -> str:
        """Ask question with RAG and conversation memory - traced with LangSmith"""
        
        # Start timing for latency tracking
        start_time = time.time()
        
        # Step 1: Hybrid Search (trace separately)
        search_start = time.time()
        results, confidences = self.hybrid_search.hybrid_search(question, k=3)
        search_latency = (time.time() - search_start) * 1000
        
        # Trace the search operation
        if self._tracer.available:
            self._tracer.trace_search(question, results, confidences, search_latency)
        
        if not results:
            return "No relevant policy information found in your documents."
        
        # Build context from retrieved chunks
        context_parts = []
        for r in results:
            context_parts.append(f"[From {r['filename']}]\n{r['text'][:500]}")
        context = "\n\n---\n\n".join(context_parts)
        
        # Get conversation history
        history = self.memory.get_history()
        history_text = ""
        if history:
            history_text = "Previous conversation:\n"
            for role, msg in history:
                history_text += f"{'User' if role == 'user' else 'Assistant'}: {msg}\n"
            history_text += "\n"
        
        # Build prompt
        prompt = f"""{history_text}Policy information:
{context}

User question: {question}

Answer as an expert insurance adjuster. Be specific about:
- Coverage amounts and limits
- Deductibles
- Exclusions or conditions
- Recommended next steps

Answer:"""

        # Step 2: LLM Call
        llm_start = time.time()
        response = self.llm.invoke(prompt)
        llm_latency = (time.time() - llm_start) * 1000
        answer = response.content
        
        # Store in memory
        self.memory.add_user_message(question)
        self.memory.add_ai_message(answer[:300])
        
        # Step 3: Trace the entire RAG query
        total_latency = (time.time() - start_time) * 1000
        
        # Extract contexts for tracing
        contexts = []
        for i, r in enumerate(results[:3]):
            contexts.append({
                'text': r.get('text', ''),
                'filename': r.get('filename', 'unknown'),
                'score': confidences[i] if i < len(confidences) else 0
            })
        
        if self._tracer.available:
            self._tracer.trace_rag_query(
                query=question,
                answer=answer,
                contexts=contexts,
                latency_ms=total_latency
            )
            
            # # Add additional metadata to the current trace
            # run = self._tracer.client.current_run()
            # if run:
                # # Get token info if available
                # token_info = {}
                # if hasattr(response, 'response_metadata'):
                    # token_info = response.response_metadata.get('token_usage', {})
                # run.outputs.update({
                    # "search_latency_ms": search_latency,
                    # "llm_latency_ms": llm_latency,
                    # "num_contexts": len(results),
                    # "total_tokens": token_info
                # })
        
        return answer
    
    def clear_memory(self):
        """Clear conversation history"""
        self.memory.clear()
        print("🗑️ Conversation memory cleared")
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation"""
        history = self.memory.get_history()
        if not history:
            return "No conversation yet."
        
        summary_lines = []
        for role, msg in history[-4:]:
            prefix = "👤 User:" if role == "user" else "🤖 AI:"
            summary_lines.append(f"{prefix} {msg[:100]}...")
        
        return "\n".join(summary_lines)
    
    def get_stats(self) -> dict:
        """Get statistics about the RAG system"""
        return {
            "conversation_length": len(self.memory.get_history()),
            "tracer_enabled": self._tracer.available,
            "trace_url": self._tracer.get_trace_url() if self._tracer.available else None
        }
